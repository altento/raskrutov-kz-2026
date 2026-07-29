# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")

print("=== 1. crm.html raw refs to css bundle / hero webp / index.html ===")
html = (ROOT / "pages/crm.html").read_text(encoding="utf-8")
for pat in [r'href="[^"]*public\.bundle[^"]*\.css"', r'src="[^"]*6eea3ed3[^"]*"', r'href="(pages/)?index\.html"', r'href="pages/web-studiya\.html"']:
    for m in re.finditer(pat, html):
        print("  ", m.group(0)[:130])
    print("  ---")

print("=== 2. what css bundle files exist on disk ===")
for f in (ROOT / "assets/m-files.cdn1.cc/web/build/pages").glob("*.css"):
    print("  ", f.name)
for f in (ROOT / "assets/m-files.cdn1.cc/web/build/pages").glob("*.js"):
    print("  ", f.name)

print("=== 3. keysy_prodvizhenie raw mangled links ===")
k = (ROOT / "pages/keysy_prodvizhenie.html").read_text(encoding="utf-8")
for m in re.finditer(r'(?:href|src)="([^"]*(?:index\.htmlindex\.html|\.\./assets/\.\./assets)[^"]*)"', k):
    print("  ", m.group(1)[:120])

print("=== 4. stub pages: context of sozdanie-saitov.html links ===")
s = (ROOT / "pages/web-studiya_podderzhka-saytov.html").read_text(encoding="utf-8")
for m in re.finditer(r'.{80}sozdanie-saitov\.html.{40}', s):
    print("  ", m.group(0).replace("\n", " ")[:160])

print("=== 5. do pages/*.html use ../assets or assets for the css bundle? count both ===")
import glob
cnt_a = cnt_b = 0
for p in (ROOT / "pages").glob("*.html"):
    t = p.read_text(encoding="utf-8", errors="ignore")
    a = len(re.findall(r'href="\.\./assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.css"', t))
    b = len(re.findall(r'href="assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.css"', t))
    cnt_a += a
    cnt_b += b
    if b:
        print("   BAD-PREFIX:", p.name, "x", b)
print("   ok(../assets):", cnt_a, " bad(assets/):", cnt_b)
