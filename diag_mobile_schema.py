#!/usr/bin/env python3
"""Diagnostics: font sizes, SVG sizes, HTML comment sizes, FAQ block structure."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

print("=== Fonts ===")
fonts = list(M.rglob("*.woff")) + list(M.rglob("*.woff2"))
total = 0
for f in sorted(fonts, key=lambda x: -x.stat().st_size):
    sz = f.stat().st_size
    total += sz
    print(f"  {sz/1024:8.1f} KB  {f.relative_to(M)}")
print(f"  TOTAL: {total/1024:.0f} KB in {len(fonts)} files")

print("\n=== SVG ===")
svgs = list(M.rglob("*.svg"))
total = sum(f.stat().st_size for f in svgs)
big = sorted(svgs, key=lambda x: -x.stat().st_size)[:8]
for f in big:
    print(f"  {f.stat().st_size/1024:8.1f} KB  {f.relative_to(M)}")
print(f"  TOTAL: {total/1024:.0f} KB in {len(svgs)} files")

print("\n=== HTML comments in served pages ===")
total = 0
for f in M.rglob("*.html"):
    if "assets" in f.relative_to(M).parts:
        continue
    h = f.read_text(encoding="utf-8", errors="ignore")
    n = sum(len(m.group(0)) for m in re.finditer(r"<!--.*?-->", h, re.DOTALL))
    total += n
print(f"  TOTAL comments: {total/1024:.0f} KB")

print("\n=== FAQ block structure in index.html ===")
h = (M / "index.html").read_text(encoding="utf-8", errors="ignore")
i = h.find("Сколько стоит создание сайта?")
print("context before question:")
print(re.sub(r"\s+", " ", h[max(0, i-700): i+200]))
