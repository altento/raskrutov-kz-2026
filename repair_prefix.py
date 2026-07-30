# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

tot = 0
for p in PAGES:
    t = p.read_text(encoding="utf-8", errors="ignore")
    n = t.count("../https://")
    if n:
        t = t.replace("../https://", "https://")
        p.write_text(t, encoding="utf-8")
        tot += n
print("repaired:", tot)

bad = 0
for p in PAGES:
    t = p.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'(?:href|src|data-page-link|data-original-url)="(\.{0,2}/https://[^"]*)"', t):
        print("RESIDUAL", p.name, m.group(1)[:90])
        bad += 1
print("residual:", bad)
