# Oracle Radio — Roadmap

Status snapshot: 2026-07-11. Stations are now pulled from the radio-browser.org
API and cached locally; most early hardcoded-URL work is obsolete.

## Next (usability)

- [ ] Whisper model selectable (`--model`, default `tiny`).
- [ ] Volume / clip-duration flags.

## Done

- [x] Normalize categories to a minimal vocabulary (news/talk/sports/classical/
      culture/religion/music); `--category` exact match, `--categories` lists
      counts; Whisper auto-detects for music/classical — `ac6911a`
- [x] Store canonical category in cache; drop misleading empty-result fallback — `623a575`
- [x] Single language per session (rule 1): `--lang` single-choice + interactive
      picker. Legend line shows language + station count — `be6762f` + this snapshot
- [x] Stations from radio-browser.org API (~50/lang, 10 langs incl ru/zh/pt/it/ar),
      cached in `stations.json`; `--refresh` rebuilds. `hidebroken=true` drops dead
      streams (no separate health-check needed) — `be6762f`
- [x] Shuffled deck: every station plays once before repeats — `be6762f`
- [x] Transcript log to file (`--log FILE`, live-appended) — `be6762f`
- [x] Wire `--language` into Whisper from station `lang` — `be6762f`
- [x] Fix transcription pipeline (queue drain, attribution, UTF-8, tiny model) — `e4d1dc8`
- [x] Split stations into `stations.py`; fail fast on missing tools — `343e3e1`

## Known constraints

- Sandbox network blocks some streams (geo/DNS) — verify URLs from a normal
  connection before deciding a stream is dead.
- `.pls`/`.m3u8` playlists: prefer direct stream URLs; ffmpeg handles those
  reliably. The API's `url_resolved` already gives direct streams.
- Music/classical lyrics transcribe poorly (expected) — filtered to ≥3 words.
