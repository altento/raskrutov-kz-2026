#!/usr/bin/env python3
"""Conservative SVG minify: strip comments + inter-tag whitespace."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

total_old = total_new = changed = errors = 0
for f in M.rglob("*.svg"):
    try:
        svg = f.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        errors += 1
        continue
    old = len(svg)
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.DOTALL)
    svg = re.sub(r">\s+<", "><", svg)
    svg = svg.strip()
    new = len(svg)
    if new < old * 0.98:
        for attempt in range(4):
            try:
                f.write_text(svg, encoding="utf-8")
                total_old += old
                total_new += new
                changed += 1
                break
            except OSError:
                import time
                time.sleep(1)

print(f"SVG minified: {changed} files, {total_old/1024:.0f} KB -> {total_new/1024:.0f} KB (errors: {errors})")
