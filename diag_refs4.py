# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")

uniq = {}
for p in [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'(href|src|data-page-link|data-original-url)="([^"]*index\.htmlindex\.html[^"]*)"', t):
        key = (m.group(1), m.group(2))
        uniq.setdefault(key, 0)
        uniq[key] += 1

print("unique attribute values containing index.htmlindex.html:")
for (attr, val), cnt in sorted(uniq.items(), key=lambda x: -x[1]):
    print(f"  x{cnt:4d}  {attr} = {val[:150]}")
