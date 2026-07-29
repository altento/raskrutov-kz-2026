#!/usr/bin/env python3
"""Show any tiktok mentions in original mirrored pages with context."""
import re
from pathlib import Path

D = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\assets\raskrutov.kz")
pat = re.compile(r".{0,60}tiktok.{0,80}", re.IGNORECASE)
seen: set[str] = set()
for f in D.rglob("*.html"):
    h = f.read_text(encoding="utf-8", errors="ignore")
    for m in pat.findall(h):
        s = m.replace("\n", " ")
        if s not in seen:
            seen.add(s)
            print(f"{f.name}: {s}")
