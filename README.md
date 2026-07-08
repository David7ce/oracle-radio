# Oracle Radio v0.1 alpha

Minimal prototype: zap between live internet radio streams, play snippets, transcribe fragments.

## Build

```powershell
cd oracle-radio
go build -o oracle.exe
```

## Run

```powershell
./oracle.exe
```

## Requirements

- **Go 1.23+**
- **FFmpeg** (for capture/playback): `ffmpeg` and `ffplay` must be in PATH
- **Whisper** (for transcription): `whisper` command or `faster_whisper` for faster inference
  - Install: `pip install openai-whisper` or `pip install faster-whisper`

## How it works

1. Picks random radio station every 2–8 seconds
2. Streams 2–5 second clip and plays it live
3. Hard cut to next station
4. Parallel: transcribes via Whisper, displays subtitle when ready
5. Loops forever

## Radio streams

10 public live stations built in (BBC, NHK, Radio Paradise, etc). Add/remove in `stations` slice.

## Architecture

- Single `main.go` — zapping orchestration + audio capture/playback
- Leverages FFmpeg for audio capture and playback
- Leverages Whisper for STT (subprocess calls)
- No custom audio processing — all delegated to mature tools

## Notes

- Requires internet connection for live streams
- Transcription happens in parallel; subtitles appear after recognition finishes
- Empty or <3-word transcriptions are filtered
- Clips stored temporarily in `%TEMP%\oracle-radio\`
