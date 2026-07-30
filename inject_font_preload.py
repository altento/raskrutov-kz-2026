# -*- coding: utf-8 -*-
"""Preload 6 critical woff fonts + drop unused preconnect to old CDN."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
mapping = json.loads(Path("url_mapping.json").read_text(encoding="utf-8"))

FONTS = [
    "montserrat/montserrat_normal.woff",
    "montserrat/montserrat_medium.woff",
    "montserrat/montserrat_bold.woff",
    "inter/inter_normal.woff",
    "inter/inter_bold.woff",
    "open_sans/open_sans_normal.woff",
]
BASE = "assets/m-files.cdn1.cc/web/user/fonts/"

PAGES = [(ROOT / "index.html", "")] + [(ROOT / b / "index.html", b) for b in mapping.values()]
inj = rem = 0
for page, beaut in PAGES:
    t = page.read_text(encoding="utf-8")
    # remove unused preconnect
    t, n = re.subn(r'\s*<link rel="preconnect" href="https://m-files\.cdn1\.cc/?"\s*/?>', "", t)
    rem += n
    if 'as="font"' in t:
        page.write_text(t, encoding="utf-8")
        continue
    prefix = "" if not beaut else "../" * (beaut.count("/") + 1)
    links = "".join(
        f'<link rel="preload" href="{prefix}{BASE}{f}" as="font" type="font/woff" crossorigin>\n'
        for f in FONTS
    )
    # insert right after the css bundle preload
    m = re.search(r'<link rel="preload" as="style"[^>]*>\n?', t)
    if m:
        t = t[:m.end()] + links + t[m.end():]
        inj += 1
    else:
        print("NO CSS-PRELOAD ANCHOR:", beaut or "(root)")
    page.write_text(t, encoding="utf-8")
print("font preloads injected on pages:", inj, " preconnects removed:", rem)
