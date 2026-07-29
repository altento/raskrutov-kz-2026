# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")

print("=== 1. canonical tags in podderzhka ===")
s = (ROOT / "pages/web-studiya_podderzhka-saytov.html").read_text(encoding="utf-8")
for m in re.finditer(r'<link rel="canonical"[^>]*>', s):
    print("  ", m.group(0))

print("=== 2. index.htmlindex.html count per page ===")
tot = 0
for p in [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    n = t.count("index.htmlindex.html")
    if n:
        print(f"   {p.name}: {n}")
        tot += n
print("   TOTAL:", tot)

print("=== 3. mangled data-page-link (assets/assets, api.whatsapp etc.) across pages ===")
tot2 = 0
for p in [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    hits = re.findall(r'data-page-link="(assets/[^"]*)"', t)
    hits += re.findall(r"data-original-url=\"(assets/[^\"]*)\"", t)
    if hits:
        tot2 += len(hits)
        print(f"   {p.name}: {len(hits)} -> {sorted(set(hits))[:4]}")
print("   TOTAL:", tot2)

print("=== 4. pages/*.html with bare href=\"pages/ or href=\"index.html\" ===")
for p in sorted((ROOT / "pages").glob("*.html")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    a = len(re.findall(r'href="pages/', t))
    b = len(re.findall(r'href="index\.html"', t))
    c = len(re.findall(r'data-page-link="pages/', t))
    d = len(re.findall(r'data-page-link="index\.html"', t))
    if a or b or c or d:
        print(f"   {p.name}: href-pages={a} href-index={b} dpl-pages={c} dpl-index={d}")

print("=== 5. all canonical occurrences: pages with != 1 canonical or relative ===")
for p in [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    cans = re.findall(r'<link rel="canonical" href="([^"]*)"', t)
    if len(cans) != 1 or not (cans and cans[0].startswith("https://")):
        print(f"   {p.name}: {cans}")
