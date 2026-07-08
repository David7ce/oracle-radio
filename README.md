# Oracle Radio v0.1 alpha

Minimal prototype: zap between live internet radio streams, play snippets, transcribe fragments.

## Run

```powershell
pip install -r requirements.txt   # FFmpeg must also be in PATH (see Requirements)
python oracle.py                        # all stations
python oracle.py --lang fr,en           # only French + English
python oracle.py --category news,talk   # only news + talk
python oracle.py --lang fr --list       # list matches, don't play
```

Stop with Ctrl+C.

Stations carry a `lang` (ISO 639-1) and `category` (news, music, talk,
classical, ambient). Filter with `--lang` / `--category` (comma-separated,
both default to all). Edit `STATIONS` in `stations.py` to add your own.

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

20 public live stations in 5 languages (en, fr, de, ja, es) across news,
music, talk, classical, and ambient. Edit `STATIONS` in `stations.py` to
customize. Some URLs may rot over time — swap them as needed.

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
