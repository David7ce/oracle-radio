"""Live radio stream sources.

One language per session (rule 1). Stations are pulled live from the open
radio-browser.org API (no API key, MP3/AAC, popularity-ranked, broken ones
hidden). If the network is down we fall back to the small hardcoded SEED below.

Each station is a dict: name, url, lang (ISO 639-1), category.
"""

import sys
import json
import datetime
import urllib.parse
import urllib.request
from pathlib import Path

# Local cache so you get a big, stable, offline list. Rebuild with --refresh.
CACHE = Path(__file__).with_name("stations.json")

# ISO 639-1 code -> (radio-browser language name, display label)
LANGS = {
    "en": ("english", "English"),
    "fr": ("french", "Français"),
    "de": ("german", "Deutsch"),
    "ja": ("japanese", "日本語"),
    "es": ("spanish", "Español"),
    "ru": ("russian", "Русский"),
    "zh": ("chinese", "中文"),
    "pt": ("portuguese", "Português"),
    "it": ("italian", "Italiano"),
    "ar": ("arabic", "العربية"),
}

# radio-browser mirror. If it's unreachable we use SEED.
API = "https://de1.api.radio-browser.info/json/stations/bylanguageexact/"

# Offline fallback: a few known-good streams per language so the app still runs
# with no network. The API supplies the "muchas más" (20+ per language) live.
SEED = [
    {"name": "BBC World Service", "url": "http://bbcwssc.ic.llnwd.net/stream/bbcwssc_mp1_ws_open_icy", "lang": "en", "category": "news"},
    {"name": "SomaFM Groove Salad", "url": "https://ice.somafm.com/groovesalad-128-mp3", "lang": "en", "category": "music"},
    {"name": "France Inter", "url": "https://stream.radiofrance.fr/franceinter/franceinter.m3u8", "lang": "fr", "category": "talk"},
    {"name": "FIP", "url": "https://stream.radiofrance.fr/fip/fip.m3u8", "lang": "fr", "category": "music"},
    {"name": "Deutschlandfunk", "url": "https://st01.sslstream.dlf.de/dlf/01/128/mp3/stream.mp3", "lang": "de", "category": "news"},
    {"name": "NHK World", "url": "https://nhkwlive-xjp.akamaized.net/hls/live/2003458/nhkwlive-xjp-en/index.m3u8", "lang": "ja", "category": "news"},
    {"name": "Radio Nacional España", "url": "https://rtvelivestream.akamaized.net/rtvesec/rne_r1_main.m3u8", "lang": "es", "category": "news"},
    {"name": "Вести ФМ", "url": "http://icecast.vgtrk.cdnvideo.ru/vestifm_mp3_192kbps", "lang": "ru", "category": "news"},
]


def languages():
    return list(LANGS)


def fetch(lang, limit=25, category=None):
    """Live stations for one ISO 639-1 lang from radio-browser, MP3/AAC only.

    Falls back to SEED (filtered by lang) on any network/parse error so the app
    never hard-fails offline. `category`, if given, keeps only stations tagged
    with that substring.
    """
    rb_name = LANGS.get(lang, (lang, lang))[0]
    q = urllib.parse.urlencode({
        "limit": limit * 2,          # over-fetch; we drop non-MP3/AAC below
        "order": "clickcount",
        "reverse": "true",
        "hidebroken": "true",
    })
    url = f"{API}{urllib.parse.quote(rb_name)}?{q}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "oracle-radio/0.1"})
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = json.load(r)
    except Exception:
        return [s for s in SEED if s["lang"] == lang] or list(SEED)

    out, seen = [], set()
    for s in raw:
        stream = s.get("url_resolved") or s.get("url")
        codec = (s.get("codec") or "").upper()
        name = (s.get("name") or "").strip()
        tags = s.get("tags", "")
        if not stream or codec not in ("MP3", "AAC", "AAC+") or not name:
            continue
        if category and category.lower() not in tags.lower():
            continue
        if stream in seen:
            continue
        seen.add(stream)
        out.append({"name": name, "url": stream, "lang": lang,
                    "category": tags.split(",")[0] if tags else "radio"})
        if len(out) >= limit:
            break
    return out or [s for s in SEED if s["lang"] == lang] or list(SEED)


CACHE_VERSION = 1
STALE_DAYS = 30


def _slim(stations):
    """Cache form: drop the redundant `lang` (it's the dict key)."""
    return [{"name": s["name"], "url": s["url"], "category": s["category"]} for s in stations]


def _write(data):
    doc = {
        "version": CACHE_VERSION,
        "generated": datetime.date.today().isoformat(),
        "stations": data,
    }
    CACHE.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")


def _read():
    """Return (stations_dict, generated_date_or_None). Empty if no/old cache."""
    if not CACHE.exists():
        return {}, None
    doc = json.loads(CACHE.read_text(encoding="utf-8"))
    if doc.get("version") != CACHE_VERSION:
        return {}, None            # shape changed -> ignore, refresh rebuilds
    gen = doc.get("generated")
    return doc.get("stations", {}), datetime.date.fromisoformat(gen) if gen else None


def refresh(per_lang=50):
    """Rebuild the local cache from the API for every language. Returns counts."""
    data = {code: _slim(fetch(code, limit=per_lang)) for code in LANGS}
    _write(data)
    return {code: len(v) for code, v in data.items()}


def load(lang, category=None):
    """Stations for one language from the local cache, else a live fetch (which
    also seeds the cache). Prints a stderr note if the cache is old."""
    data, gen = _read()
    if gen and (datetime.date.today() - gen).days > STALE_DAYS:
        print(f"note: station list is {(datetime.date.today() - gen).days} days old — run --refresh",
              file=sys.stderr)
    slim = data.get(lang)
    if slim:
        st = [{**s, "lang": lang} for s in slim]   # re-attach lang for callers
    else:
        st = fetch(lang, category=category)
        data[lang] = _slim(st)
        _write(data)
    if category:
        st = [s for s in st if category.lower() in s.get("category", "").lower()] or st
    return st


if __name__ == "__main__":
    # Self-check / cache builder: every language returns stations.
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    counts = refresh(per_lang=50)
    for code, n in counts.items():
        assert n, f"no stations for {code}"
        print(f"{code}: {n:2d} stations")
    print(f"cached -> {CACHE}")
