#!/usr/bin/env python3
"""Find all http URLs containing '..' and print with file names."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
pat = re.compile(r"https?://[^\s\"'<>]*\.\.[^\s\"'<>]*")
seen: set[str] = set()
for f in M.rglob("*.html"):
    if "assets" in f.relative_to(M).parts:
        continue
    h = f.read_text(encoding="utf-8", errors="ignore")
    for m in pat.findall(h):
        key = m
        if key not in seen:
            seen.add(key)
            print(f"{f.relative_to(M)}: {m[:120]}")
