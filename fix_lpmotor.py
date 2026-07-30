# -*- coding: utf-8 -*-
"""Point lpmotortest data-page-links to our real pages (depth-aware)."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
mapping = json.loads(Path("url_mapping.json").read_text(encoding="utf-8"))

TARGETS = {
    "nashi-klienti": "o-kompanii/klienty",
    "otzivi": "o-kompanii/blagodarstvennye-pisma",
    "sozdanie-saitov-v-Petropavlovske": "web-studiya/sozdanie-saitov",
    "sozdanie-saitov-v-astane": "web-studiya/sozdanie-saitov",
    "sozdanie-saitov-v-karagande": "web-studiya/sozdanie-saitov",
}

RX = re.compile(r'data-page-link="(?:\.\./)*assets/s239948\.lpmotortest\.com/([\w-]+)/index\.html/index\.html"')

tot = 0
for beaut in mapping.values():
    p = ROOT / beaut / "index.html"
    t = p.read_text(encoding="utf-8")
    prefix = "../" * (beaut.count("/") + 1)

    def repl(m):
        global tot
        target = TARGETS.get(m.group(1))
        if not target:
            return m.group(0)
        tot += 1
        return f'data-page-link="{prefix}{target}"'

    t2 = RX.sub(repl, t)
    if t2 != t:
        p.write_text(t2, encoding="utf-8")
print("rewired lpmotortest links:", tot)
