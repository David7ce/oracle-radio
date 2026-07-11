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
    "ar": ("arabic", "العربية"),
    "de": ("german", "Deutsch"),
    "en": ("english", "English"),
    "es": ("spanish", "Español"),
    "fr": ("french", "Français"),
    "ja": ("japanese", "日本語"),
    "it": ("italian", "Italiano"),
    "pt": ("portuguese", "Português"),
    "ru": ("russian", "Русский"),
    "zh": ("chinese", "中文"),
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


# Minimal controlled vocabulary so `--category news,talk` is clean from the CLI.
# radio-browser's freeform tags get squashed to exactly one of these.
CATEGORIES = ["news", "talk", "sports", "classical", "culture", "religion", "music"]

# Checked in order; first keyword hit wins. Default is "music" (most radio is).
_CANON_RULES = [
    ("news",      ("news", "noticias", "info", "actualidad", "jornal", "nachrichten")),
    ("sports",    ("sport", "deporte", "futbol", "football")),
    ("talk",      ("talk", "spoken", "hablado", "podcast", "discussion", "reden")),
    ("classical", ("classical", "clásica", "classica", "klassik", "opera", "sinfon")),
    ("religion",  ("religio", "christian", "gospel", "quran", "coran", "islam", "cristian", "catholic")),
    ("culture",   ("culture", "cultural", "kultur")),
]


def _canon(tags):
    """Freeform radio-browser tags -> one CATEGORIES value. Music is the default."""
    t = (tags or "").lower()
    for cat, keys in _CANON_RULES:
        if any(k in t for k in keys):
            return cat
    return "music"


def languages():
    return list(LANGS)


def fetch(lang, limit=25):
    """Live stations for one ISO 639-1 lang from radio-browser, MP3/AAC only.

    Falls back to SEED (filtered by lang) on any network/parse error so the app
    never hard-fails offline. Category filtering is done by load(), not here.
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
        if stream in seen:
            continue
        seen.add(stream)
        out.append({"name": name, "url": stream, "lang": lang, "category": _canon(tags)})
        if len(out) >= limit:
            break
    return out or [s for s in SEED if s["lang"] == lang] or list(SEED)


CACHE_VERSION = 3
STALE_DAYS = 30


def _slim(stations):
    """Cache form: drop redundant `lang` (it's the dict key)."""
    return [{"name": s["name"], "url": s["url"], "category": s["category"]} for s in stations]


def _match(station, category):
    """True if the station's canonical category is one of the comma-separated
    terms in `category`. Empty category matches everything."""
    if not category:
        return True
    want = {t.strip().lower() for t in category.split(",") if t.strip()}
    return station.get("category", "") in want


def categories(lang):
    """Canonical categories present for a language (with the cache built)."""
    data, _ = _read()
    return sorted({s["category"] for s in data.get(lang, [])}) or CATEGORIES


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
        st = slim
    else:
        st = _slim(fetch(lang))
        data[lang] = st
        _write(data)
    st = [{**s, "lang": lang} for s in st]   # re-attach lang for callers
    return [s for s in st if _match(s, category)]


if __name__ == "__main__":
    # Self-check / cache builder: every language returns stations.
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    # _canon must only ever emit the controlled vocabulary.
    assert _canon("news talk,spanish") == "news"
    assert _canon("jazz,chillout") == "music"
    assert _canon("") == "music"
    counts = refresh(per_lang=50)
    for code, n in counts.items():
        assert n, f"no stations for {code}"
        print(f"{code}: {n:2d} stations, cats: {', '.join(categories(code))}")
    print(f"cached -> {CACHE}")
