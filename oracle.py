#!/usr/bin/env python3
"""
Oracle Radio v0.1 alpha
Zap between live radio streams, capture fragments, transcribe in parallel.
"""

import sys
import random
import subprocess
import tempfile
import time
from pathlib import Path
from threading import Thread
from queue import Queue, Empty

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

STATIONS = [
    ("BBC World Service", "http://bbcwssc.ic.llnwd.net/stream/bbcwssc_mp1_ws_open_icy"),
    ("NHK World", "https://nhkwlive-xjp.akamaized.net/hls/live/2003458/nhkwlive-xjp-en/index.m3u8"),
    ("Radio Paradise", "https://stream.radioparadise.com/mp3-128"),
    ("WFMU 91.1 FM", "http://stream.wfmu.org/freeform"),
    ("SOMA FM Ambient", "https://somafm.com/ambient.pls"),
    ("JazzRadio 24/7", "http://stream.jazzradio.com/"),
    ("France Info", "https://stream.radiofrance.fr/franceinfo/franceinfo.m3u8"),
    ("Radio Classique", "https://stream.radiofrance.fr/radioclassique/radioclassique.m3u8"),
    ("Pitchfork Advanced", "http://somafm.com/pithf.pls"),
    ("Secret Agent", "http://somafm.com/secretagent130.m3u8"),
]

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

def transcribe_clip(clip_file, station_name, queue):
    """Transcribe clip in background thread."""
    try:
        subprocess.run(
            ["whisper", clip_file, "--output_format", "txt",
             "--output_dir", str(Path(clip_file).parent), "--model", "tiny"],
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

def main():
    print("🎙️  ORACLE RADIO v0.1 alpha")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    tmpdir = Path(tempfile.gettempdir()) / "oracle-radio"
    tmpdir.mkdir(exist_ok=True)

    last_station = None
    transcript_queue = Queue()

    try:
        while True:
            # Pick random station (avoid immediate repeat)
            while True:
                station_name, stream_url = random.choice(STATIONS)
                if station_name != last_station:
                    break
            last_station = station_name

            # Random duration 2-5 seconds
            duration = random.randint(2, 5)

            print(f"● LIVE — {station_name} ({duration}s)")

            # Capture and play
            clip_file = str(tmpdir / f"clip-{int(time.time() * 1e6)}.wav")
            capture_and_play(stream_url, clip_file, duration)

            # Transcribe in parallel
            Thread(target=transcribe_clip, args=(clip_file, station_name, transcript_queue), daemon=True).start()

            print()

            # Drain any transcripts that finished (whisper lags ~10-30s behind)
            while True:
                try:
                    station, transcript = transcript_queue.get_nowait()
                except Empty:
                    break
                print(f'   ↳ [{station}] "{transcript}"\n')
    except KeyboardInterrupt:
        print("\n🛑 Stopping.")
        sys.exit(0)

if __name__ == "__main__":
    main()
