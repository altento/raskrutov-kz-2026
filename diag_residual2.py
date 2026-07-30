# -*- coding: utf-8 -*-
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
mapping = json.loads(Path("url_mapping.json").read_text(encoding="utf-8"))

seen = set()
for b in list(mapping.values())[:5]:
    t = (ROOT / b / "index.html").read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'"((?:\.\./)*assets/[^"]*instagram[^"]*)"', t):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            print(repr(m.group(1)))
    for m in re.finditer(r'"((?:\.\./)*assets/[^"]*googletagmanager[^"]*)"', t):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            print(repr(m.group(1)))
    # context around instagram garbage
    m2 = re.search(r'.{160}assets/www\.[^"]{0,120}instagram.{160}', t, re.S)
    if m2 and "ctx" not in seen:
        seen.add("ctx")
        print("CTX:", " ".join(m2.group(0).split())[:400])
