# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")

for fname in ["index.html", "pages/crm.html"]:
    t = (ROOT / fname).read_text(encoding="utf-8")
    print("=====", fname)
    seen = set()
    for m in re.finditer(r".{110}index\.htmlindex\.html.{40}", t, re.S):
        ctx = " ".join(m.group(0).split())
        key = ctx[:100]
        if key in seen:
            continue
        seen.add(key)
        print("  ...", ctx[:200])
    # mangled dpl
    for m in re.finditer(r'(?:data-page-link|data-original-url)="(assets/[^"]*)"', t):
        print("  MANGLED:", m.group(0)[:120])
    print()
