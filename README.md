# Oracle Radio v0.1 alpha

Minimal prototype: zap between live internet radio streams, play snippets, transcribe fragments.

## Run

```powershell
cd cli\oracle-radio
python oracle.py
```

Stop with Ctrl+C.

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

10 public live stations built in (BBC, NHK, Radio Paradise, etc). Edit `STATIONS` in `oracle.py` to customize.

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
