# Oracle Radio — Roadmap

Status snapshot: 2026-07-09. Feature "select language + category" is built
and committed (`209f6fe`). Remaining work below.

## Now (blocking correctness)

- [x] **Fix broken stream URLs in `stations.py`**
  - [x] SomaFM: `.pls` → direct ICE mounts (verified 206). Also NHK mislabeled
        `ja` → `en` (mount is the English service, drives Whisper lang now).
  - [x] `Pitchfork Advanced` (dead mount) → replaced with SomaFM Underground 80s.
  - [x] German (Deutschlandfunk, DLF Nova) — kept; 302-redirects to a signed CDN
        URL, ffmpeg follows redirects so they work. Roadmap note was stale.
  - [ ] Spanish news — RNE still dead (`000`, geo/DNS). No open replacement found;
        leave in list or drop later.
- [x] **Wire `--language` into Whisper** — `transcribe_clip(..., lang)` passes
  `--language <code>` from the station's `lang` field.

## Verified working (keep)

- BBC World Service, NPR, NHK World, all France Radio, Los40 (es/music)

## Next (usability)

- [x] One language per session (rule 1): `--lang` single-choice + interactive
      numbered picker when omitted.
- [x] Many more stations, incl. ru/zh/pt/it/ar — pulled live (~25/lang) from
      radio-browser.org API instead of a hardcoded list. `hidebroken=true`
      already skips dead streams, so no separate health-check needed.
- [ ] Show a legend line: current language + station count.
- [ ] Accept aliases in picker like "español" → `es`.

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
