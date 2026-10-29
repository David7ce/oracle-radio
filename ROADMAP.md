# Oracle Radio — Roadmap

Status snapshot: 2026-07-11. Stations are now pulled from the radio-browser.org
API and cached locally; most early hardcoded-URL work is obsolete.

## Known constraints

- Sandbox network blocks some streams (geo/DNS) — verify URLs from a normal
  connection before deciding a stream is dead.
- `.pls`/`.m3u8` playlists: prefer direct stream URLs; ffmpeg handles those
  reliably. The API's `url_resolved` already gives direct streams.
- Music/classical lyrics transcribe poorly (expected) — filtered to ≥3 words.
