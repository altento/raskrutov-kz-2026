#!/usr/bin/env python3
"""Correct hero preloads: keep ONLY the base-variant preload (true LCP image at all widths),
drop the desktop __q preload (it's a decorative backdrop discovered early via inline CSS anyway).
"""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

SPLIT_RE = re.compile(
    r'<link rel="preload" as="image" href="([^"]+__q_\d+\.webp)" media="\(min-width: 1001px\)" fetchpriority="high"/>'
    r'<link rel="preload" as="image" href="([^"]+\.webp)" media="\(max-width: 1000px\)" fetchpriority="high"/>'
)

files_changed = 0
collapsed = 0
for f in sorted(M.rglob("*.html")):
    rel = f.relative_to(M)
    if "assets" in rel.parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    orig = html
    def collapse(m):
        global collapsed
        collapsed += 1
        return f'<link rel="preload" as="image" href="{m.group(2)}" fetchpriority="high"/>'
    html = SPLIT_RE.sub(collapse, html, count=1)
    if html != orig:
        f.write_text(html, encoding="utf-8")
        files_changed += 1

print(f"files changed: {files_changed}, preloads collapsed to base variant: {collapsed}")

html = (M / "index.html").read_text(encoding="utf-8")
for m in re.finditer(r'<link rel="preload"[^>]*>', html[:4000]):
    print(f"  {m.group(0)[:140]}")
