#!/usr/bin/env python3
"""
Oracle Radio v0.1 alpha
Zap between live radio streams, capture fragments, transcribe in parallel.
"""

import sys
import argparse
import random
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from threading import Thread
from queue import Queue, Empty

from stations import load, refresh, languages, categories, LANGS, CATEGORIES

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def capture_and_play(stream_url, clip_file, duration):
    """Capture audio from stream and play it."""
    try:
        subprocess.run(
            ["ffmpeg", "-i", stream_url, "-t", str(duration),
             "-f", "wav", "-acodec", "pcm_s16le", "-y", clip_file],
            capture_output=True, timeout=duration + 5
        )
        if Path(clip_file).exists():
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-t", str(duration), clip_file],
                capture_output=True, timeout=duration + 2
            )
    except Exception as e:
        print(f"   (capture failed: {e})")

def transcribe_clip(clip_file, station_name, queue, lang=None, model="tiny"):
    """Transcribe clip in background thread."""
    try:
        # Passing the station's known language skips Whisper's auto-detect: faster + more accurate.
        lang_arg = ["--language", lang] if lang else []
        subprocess.run(
            ["whisper", clip_file, "--output_format", "txt",
             "--output_dir", str(Path(clip_file).parent), "--model", model, *lang_arg],
            capture_output=True, timeout=120
        )

        txt_file = Path(clip_file).with_suffix(".txt")
        if txt_file.exists():
            transcript = txt_file.read_text(encoding="utf-8").strip()
            if transcript and len(transcript.split()) >= 3:
                queue.put((station_name, transcript))
            txt_file.unlink()

        Path(clip_file).unlink(missing_ok=True)
    except Exception:
        pass

def require_tools(*tools):
    """Fail fast with a clear message if any external tool is missing from PATH."""
    missing = [t for t in tools if shutil.which(t) is None]
    if missing:
        sys.exit(f"Missing from PATH: {', '.join(missing)}. See README Requirements.")

def parse_args():
    p = argparse.ArgumentParser(description="Oracle Radio — zap live radio streams (one language per session).")
    p.add_argument("--lang", choices=languages(), help=f"single language. available: {', '.join(languages())}")
    p.add_argument("--category", help=f"comma-separated, from: {', '.join(CATEGORIES)}")
    p.add_argument("--list", action="store_true", help="list stations for the chosen language and exit")
    p.add_argument("--categories", action="store_true", help="list categories + station counts for the language and exit")
    p.add_argument("--log", metavar="FILE", help="append transcripts to FILE live (else a session log is saved on exit)")
    p.add_argument("--model", default="tiny", help="Whisper model: tiny, base, small, medium, large (default tiny)")
    p.add_argument("--refresh", action="store_true", help="rebuild local station cache from the API and exit")
    return p.parse_args()

def pick_language():
    """Interactive numbered picker when --lang is not given (rule 1: one lang)."""
    codes = languages()
    print("Choose a language:")
    for i, code in enumerate(codes, 1):
        print(f"  {i}. {LANGS[code][1]} ({code})")
    while True:
        choice = input("> ").strip().lower()
        if choice in codes:
            return choice
        if choice.isdigit() and 1 <= int(choice) <= len(codes):
            return codes[int(choice) - 1]
        print(f"Pick 1-{len(codes)} or a code ({', '.join(codes)}).")

def main():
    args = parse_args()

    if args.refresh:
        print("Rebuilding station cache from radio-browser.org…")
        for code, n in refresh().items():
            print(f"  {code}: {n} stations")
        return

    lang = args.lang or pick_language()

    if args.categories:
        from collections import Counter
        counts = Counter(s["category"] for s in load(lang))
        for cat in sorted(counts):
            print(f"{cat}: {counts[cat]}")
        return

    print(f"Loading {LANGS[lang][1]} stations…")
    stations = load(lang, category=args.category)
    if not stations:
        sys.exit(f"No stations for {lang}" + (f" / {args.category}" if args.category else "") + ".")

    if args.list:
        for s in stations:
            print(f"[{s['lang']}/{s['category']}] {s['name']}")
        return

    require_tools("ffmpeg", "ffplay", "whisper")

    print("🎙️  ORACLE RADIO v0.1 alpha")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    legend = f"{LANGS[lang][1]} · {len(stations)} stations"
    if args.category:
        legend += f" · {args.category}"
    print(legend)
    print()

    tmpdir = Path(tempfile.gettempdir()) / "oracle-radio"
    tmpdir.mkdir(exist_ok=True)

    transcript_queue = Queue()
    logf = open(args.log, "a", encoding="utf-8") if args.log else None
    session = []   # every transcript line, for the on-exit session log

    # Shuffled deck: every station plays once before any repeats (fixes clustering
    # you get from independent random.choice picks).
    deck = []
    last_name = None

    def next_station():
        nonlocal deck
        if not deck:
            deck = random.sample(stations, len(stations))
            # Avoid an immediate repeat across the reshuffle boundary.
            if len(stations) > 1 and deck[-1]["name"] == last_name:
                deck.insert(0, deck.pop())
        return deck.pop()

    try:
        while True:
            station = next_station()
            station_name, stream_url = station["name"], station["url"]
            last_name = station_name
            # Music/classical play songs that are often English regardless of the
            # station's language, so let Whisper auto-detect instead of forcing lang.
            wlang = None if station["category"] in ("music", "classical") else station["lang"]

            duration = random.randint(2, 5)
            print(f"● LIVE — {station_name} ({duration}s)")

            clip_file = str(tmpdir / f"clip-{int(time.time() * 1e6)}.wav")
            capture_and_play(stream_url, clip_file, duration)
            Thread(target=transcribe_clip, args=(clip_file, station_name, transcript_queue, wlang, args.model), daemon=True).start()

            print()

            # Drain any transcripts that finished (whisper lags ~10-30s behind)
            while True:
                try:
                    st_name, transcript = transcript_queue.get_nowait()
                except Empty:
                    break
                print(f'   ↳ [{st_name}] "{transcript}"\n')
                line = f'[{time.strftime("%H:%M:%S")}] [{st_name}] {transcript}\n'
                session.append(line)
                if logf:
                    logf.write(line)
                    logf.flush()   # ponytail: flush per line so the log is live-tailable
    except KeyboardInterrupt:
        print("\n🛑 Stopping.")
        if logf:
            logf.close()
        elif session:
            # No live --log given: dump the whole session to an auto-named file.
            path = Path.cwd() / f"oracle-{lang}-{time.strftime('%Y%m%d-%H%M%S')}.log"
            path.write_text("".join(session), encoding="utf-8")
            print(f"📝 Session log: {path} ({len(session)} lines)")
        sys.exit(0)

if __name__ == "__main__":
    main()
