# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")

print("=== 1. crm.html data-page-link values (static menu etc.) ===")
html = (ROOT / "pages/crm.html").read_text(encoding="utf-8")
vals = sorted(set(re.findall(r'data-page-link="([^"]*)"', html)))
for v in vals[:15]:
    print("  ", v)

print()
print("=== 2. keysy_prodvizhenie: markup around mangled raki.kz link ===")
k = (ROOT / "pages/keysy_prodvizhenie.html").read_text(encoding="utf-8")
m = re.search(r".{200}raki\.kz/index\.htmlindex\.html.{100}", k, re.S)
if m:
    print("  ", m.group(0).replace("\n", " ")[:380])

print()
print("=== 3. sozdanie-saitov.html bare href context (podderzhka) ===")
s = (ROOT / "pages/web-studiya_podderzhka-saytov.html").read_text(encoding="utf-8")
for m in re.finditer(r'href="sozdanie-saitov\.html"', s):
    ctx = s[max(0, m.start() - 150):m.end() + 80].replace("\n", " ")
    print("  ", ctx[-260:])

print()
print("=== 4. count affected patterns across all pages ===")
for p in [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    a = len(re.findall(r'(?:href|src)="assets/', t))
    b = len(re.findall(r'href="index\.html"', t))
    c = len(re.findall(r'href="pages/', t))
    d = len(re.findall(r'\.\./assets/\.\./assets/', t))
    e = len(re.findall(r'href="sozdanie-saitov\.html"', t))
    if a or b or c or d or e:
        print(f"   {p.name}: assets-prefix={a} index.html={b} pages/={c} double-assets={d} sozdanie={e}")
