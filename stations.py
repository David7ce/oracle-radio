"""Live radio stream sources + filtering.

Each station: name, url, lang (ISO 639-1), category.
Add your own freely — just keep the four keys.

Note: "podcast" is on-demand by nature and doesn't fit a live-zapping
tool, so spoken-word live streams live under "talk" instead.
"""

STATIONS = [
    # --- English ---
    {"name": "BBC World Service", "url": "http://bbcwssc.ic.llnwd.net/stream/bbcwssc_mp1_ws_open_icy", "lang": "en", "category": "news"},
    {"name": "NPR Program Stream", "url": "https://npr-ice.streamguys1.com/live.mp3", "lang": "en", "category": "news"},
    {"name": "WFMU 91.1 FM", "url": "http://stream.wfmu.org/freeform", "lang": "en", "category": "music"},
    {"name": "Radio Paradise", "url": "https://stream.radioparadise.com/mp3-128", "lang": "en", "category": "music"},
    {"name": "SomaFM Groove Salad", "url": "https://somafm.com/groovesalad.pls", "lang": "en", "category": "music"},
    {"name": "SomaFM Ambient", "url": "https://somafm.com/dronezone.pls", "lang": "en", "category": "ambient"},
    {"name": "SomaFM Indie Pop", "url": "https://somafm.com/indiepop.pls", "lang": "en", "category": "music"},
    {"name": "SomaFM DEF CON", "url": "https://somafm.com/defcon.pls", "lang": "en", "category": "talk"},
    {"name": "SomaFM Secret Agent", "url": "https://somafm.com/secretagent130.pls", "lang": "en", "category": "music"},
    {"name": "Pitchfork Advanced", "url": "https://somafm.com/pithf.pls", "lang": "en", "category": "music"},

    # --- French ---
    {"name": "France Info", "url": "https://stream.radiofrance.fr/franceinfo/franceinfo.m3u8", "lang": "fr", "category": "news"},
    {"name": "France Inter", "url": "https://stream.radiofrance.fr/franceinter/franceinter.m3u8", "lang": "fr", "category": "talk"},
    {"name": "FIP", "url": "https://stream.radiofrance.fr/fip/fip.m3u8", "lang": "fr", "category": "music"},
    {"name": "France Musique", "url": "https://stream.radiofrance.fr/francemusique/francemusique.m3u8", "lang": "fr", "category": "classical"},
    {"name": "Radio Classique", "url": "https://stream.radiofrance.fr/radioclassique/radioclassique.m3u8", "lang": "fr", "category": "classical"},

    # --- German ---
    {"name": "Deutschlandfunk", "url": "https://st01.sslstream.dlf.de/dlf/01/128/mp3/stream.mp3", "lang": "de", "category": "news"},
    {"name": "Deutschlandfunk Nova", "url": "https://st03.sslstream.dlf.de/dlf/03/128/mp3/stream.mp3", "lang": "de", "category": "talk"},

    # --- Japanese ---
    {"name": "NHK World", "url": "https://nhkwlive-xjp.akamaized.net/hls/live/2003458/nhkwlive-xjp-en/index.m3u8", "lang": "ja", "category": "news"},

    # --- Spanish ---
    {"name": "Radio Nacional España", "url": "https://rtvelivestream.akamaized.net/rtvesec/rne_r1_main.m3u8", "lang": "es", "category": "news"},
    {"name": "Radio Clásica RNE", "url": "https://rtvelivestream.akamaized.net/rtvesec/rne_r2_main.m3u8", "lang": "es", "category": "classical"},
]


def languages():
    return sorted({s["lang"] for s in STATIONS})


def categories():
    return sorted({s["category"] for s in STATIONS})


def select(langs=None, cats=None):
    """Filter stations. langs/cats are lists; None or empty = all."""
    return [
        s for s in STATIONS
        if (not langs or s["lang"] in langs)
        and (not cats or s["category"] in cats)
    ]
