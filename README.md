# Oracle Radio v0.1 alpha

Minimal prototype: zap between live internet radio streams, play snippets, transcribe fragments.

## Run

```powershell
pip install -r requirements.txt   # FFmpeg must also be in PATH (see Requirements)
python oracle.py                        # interactive language picker
python oracle.py --lang fr              # French only (one language per session)
python oracle.py --lang es --category news   # Spanish, tag filter "news"
python oracle.py --lang ja --list       # list stations, don't play
python oracle.py --lang de --log run.log     # append transcripts to run.log live
python oracle.py --refresh              # rebuild local station list from the API
```

Stop with Ctrl+C.

**One language per session** (rule 1): pick with `--lang` or the interactive
picker. Available: `en fr de ja es ru zh pt it ar`. The chosen language is also
passed to Whisper for faster, more accurate transcripts.

**Stations** live in a local `stations.json` (~50 per language, ~500 total),
built from the open [radio-browser.org](https://www.radio-browser.info) API
(MP3/AAC, popularity-ranked, dead ones hidden). Runs offline from the cache;
`--refresh` rebuilds it. A shuffled deck plays every station once before any
repeat. `--category` is an optional tag substring filter (`news`, `jazz`, …).

**Transcript log** (`--log FILE`): each subtitle is appended live
(`[HH:MM:SS] [Station] text`), flushed per line so you can `tail -f` it — both
a live feed and a full file at the end.

## Requirements

- **Python 3.8+**
- **FFmpeg** (for capture/playback): `ffmpeg` and `ffplay` must be in PATH
- **Whisper** (for transcription): `pip install openai-whisper`

## How it works

1. Picks random radio station (no immediate repeat)
2. Captures a 2–5 second clip and plays it
3. Hard cut to next station
4. Parallel: transcribes via Whisper (`tiny` model), prints subtitle when ready
5. Loops forever

## Radio streams

Fetched live from radio-browser.org: ~25 top stations for the chosen language
(10 supported: en, fr, de, ja, es, ru, zh, pt, it, ar). No network? Falls back
to the small hardcoded `SEED` in `stations.py`.

## Architecture

- Single `oracle.py` — zapping orchestration + audio capture/playback
- Leverages FFmpeg for audio capture and playback
- Leverages Whisper for STT (subprocess calls)
- No custom audio processing — all delegated to mature tools

## Notes

- Requires internet connection for live streams
- Transcription happens in parallel; subtitles appear a few iterations later (Whisper lags the live audio)
- First run downloads the Whisper `tiny` model (~75 MB)
- Empty or <3-word transcriptions are filtered
- Clips stored temporarily in `%TEMP%\oracle-radio\`
