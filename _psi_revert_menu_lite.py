# -*- coding: utf-8 -*-
"""Revert menu-lite: restore full blocking sozdanie-popup-menu.v1.css."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("site_mirror")
CITIES = [
    "almaty", "astana", "shymkent", "aktau", "aktobe", "atyrau", "karaganda",
    "kokshetau", "kostanay", "kyzylorda", "pavlodar", "petropavlovsk", "semey",
    "taldykorgan", "taraz", "turkestan", "uralsk", "ust-kamenogorsk",
]

pages = [ROOT / "web-studiya/sozdanie-saitov/index.html"] + [
    ROOT / "web-studiya/sozdanie-saitov" / c / "index.html" for c in CITIES
]

for p in pages:
    t = p.read_text(encoding="utf-8")
    t = t.replace("sozdanie-menu-lite.v1.css", "sozdanie-popup-menu.v1.css")
    t = re.sub(
        r'<link rel="stylesheet" href="[^"]*sozdanie-popup-menu-deferred\.v1\.css"[^>]*>\s*',
        "",
        t,
    )
    t = re.sub(
        r'<noscript><link rel="stylesheet" href="[^"]*sozdanie-popup-menu-deferred\.v1\.css"></noscript>\s*',
        "",
        t,
    )
    p.write_text(t, encoding="utf-8")
    print("reverted", p.parent.name if p.parent.name != "sozdanie-saitov" else "parent")

# sanity
t = pages[0].read_text(encoding="utf-8")
print("has popup-menu", "sozdanie-popup-menu.v1.css" in t)
print("has menu-lite", "sozdanie-menu-lite" in t)
print("has deferred-menu", "popup-menu-deferred" in t)
