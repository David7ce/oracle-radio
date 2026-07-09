# Oracle Radio — Roadmap

Status snapshot: 2026-07-09. Feature "select language + category" is built
and committed (`209f6fe`). Remaining work below.

## Now (blocking correctness)

- [ ] **Fix broken stream URLs in `stations.py`**
  - [ ] SomaFM: `.pls` playlists don't work with ffmpeg — swap to direct ICE:
    - `https://ice.somafm.com/groovesalad-128-mp3`
    - `https://ice.somafm.com/dronezone-128-mp3`
    - `https://ice.somafm.com/indiepop-128-mp3`
    - `https://ice.somafm.com/defcon-256-mp3`
    - `https://ice.somafm.com/secretagent-128-mp3`
    - `https://ice.somafm.com/u80s-128-mp3`
  - [ ] `Pitchfork Advanced` — ICE mount name wrong; find real channel or drop
  - [ ] German (Deutschlandfunk, DLF Nova) — both URLs fail, replace
  - [ ] Spanish news — RNE geo-blocked; find open stream (headline use case)
- [ ] **Wire `--language` into Whisper** — pass station `lang` to
  `transcribe_clip` → `whisper --language <code>` so transcription stops
  auto-detecting (more accurate, faster).

## Verified working (keep)

- BBC World Service, NPR, NHK World, all France Radio, Los40 (es/music)

## Next (usability)

- [ ] Interactive picker when no `--lang`/`--category` given (prompt with
      available options) — accept aliases like "español" → `es`.
- [ ] Prune/health-check stations at startup, skip dead ones.
- [ ] Show a legend line: current filter + station count.

## Later (nice to have)

- [ ] Whisper model selectable (`--model`), default `tiny`.
- [ ] Save transcript log to file (opt-in `--log`).
- [ ] Volume / clip-duration flags.
- [ ] More stations per language; community-editable list.

## Done

- [x] Fix transcription pipeline (queue drain, station attribution, UTF-8, drop `--quiet`, tiny model) — `e4d1dc8`
- [x] Split stations into `stations.py`; fail fast on missing tools — `343e3e1`
- [x] Multi-language stations with `--lang`/`--category` filtering + `--list` — `209f6fe`
- [x] Trim dead code / redundant comments — `9714d39`

## Known constraints

- Sandbox network blocks some streams (geo/DNS) — verify URLs from a normal
  connection before deciding a stream is dead.
- `.pls`/`.m3u8` playlists: prefer direct stream URLs; ffmpeg handles those
  reliably.
