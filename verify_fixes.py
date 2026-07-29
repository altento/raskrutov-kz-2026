# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
tot_bad = 0
for p in [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    bad = []
    if "index.htmlindex.html" in t:
        bad.append("double-suffix")
    for m in re.finditer(r'(?:data-page-link|data-original-url)="(assets/[^"]*)"', t):
        bad.append("mangled-dpl:" + m.group(1)[:60])
    if p.parent != ROOT:
        for m in re.finditer(r'(?:href|src)="assets/', t):
            bad.append("bare-assets:" + m.group(0)[:60])
        for m in re.finditer(r'href="pages/', t):
            bad.append("href-pages")
        for m in re.finditer(r'href="index\.html"', t):
            bad.append("href-index")
        cans = re.findall(r'<link rel="canonical" href="([^"]*)"', t)
        if len(cans) != 1 or not cans[0].startswith("https://"):
            bad.append("canon:" + str(cans))
    if bad:
        tot_bad += 1
        print(p.name, "->", bad[:3])
print("pages with remaining problems:", tot_bad)
