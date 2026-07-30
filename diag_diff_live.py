# -*- coding: utf-8 -*-
import re
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")

local = Path("site_mirror/index.html").read_text(encoding="utf-8")
live = fetch("https://raskrutov.kz/?nc=diff1")

print("local len:", len(local), " live len:", len(live))
checks = [
    ("garbage index.htmlindex.html", lambda t: t.count("index.htmlindex.html")),
    ('dpl pages/crm.html', lambda t: t.count('data-page-link="pages/crm.html"')),
    ('href pages/crm.html', lambda t: t.count('href="pages/crm.html"')),
    ('href="index.html"', lambda t: t.count('href="index.html"')),
    ("kinescope https", lambda t: t.count("https://player.kinescope.io")),
    ("kinescope assets/", lambda t: t.count("assets/player.kinescope.io")),
    ("youtube iframe_api.js.js", lambda t: t.count("iframe_api.js.js")),
    ("youtube iframe_api ok", lambda t: t.count("https://www.youtube.com/iframe_api")),
    ("t.me https", lambda t: t.count("https://t.me/Raskrutov_web")),
    ("t.me assets", lambda t: t.count("assets/t.me")),
    ("canonical", lambda t: len(re.findall(r'<link rel="canonical"', t))),
    ("favicon.ico", lambda t: t.count("favicon.ico")),
    ("lazy ymaps guard", lambda t: t.count("blk_yandex_map")),
    ("jsonld blocks", lambda t: t.count('application/ld+json')),
]
for name, fn in checks:
    print(f"{name:34s} local={fn(local):5d}  live={fn(live):5d}")
