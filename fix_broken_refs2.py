# -*- coding: utf-8 -*-
"""Fix residual corruption:
- any variants of the garbage mirror-rewrite URL inside quotes -> https://raskrutov.kz/
- double-mangled 'assets/https://...' attribute values -> clean https URL
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

GARBAGE_RE = re.compile(r'"(?:\.\./)*assets/(?:[\w./-]*?)?index\.html/index\.htmlindex\.html"')
DBL_RE = re.compile(r'="assets/(https://[^"]*)"')

g = d = 0
for page in PAGES:
    html = page.read_text(encoding="utf-8")
    html, n1 = GARBAGE_RE.subn('"https://raskrutov.kz/"', html)
    html, n2 = DBL_RE.subn(r'="\1"', html)
    if n1 or n2:
        page.write_text(html, encoding="utf-8")
        g += n1
        d += n2
        print(f"{page.name}: garbage={n1} dbl={n2}")
print("TOTAL garbage:", g, " dbl-mangled:", d)
