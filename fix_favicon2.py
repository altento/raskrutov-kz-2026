#!/usr/bin/env python3
"""Favicon fix:
1. Generate a real multi-size favicon.ico at site root (from favicon__q_1.png)
2. Normalize all icon links: rel="shortcut icon" -> rel="icon"
3. Add /favicon.ico as an additional fallback link where missing
"""
import re
from pathlib import Path
from PIL import Image

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
SRC = M / "assets" / "m-files.cdn1.cc" / "lpfile" / "favicon" / "favicon__q_1.png"
ICO = M / "favicon.ico"

with Image.open(SRC) as im:
    im = im.convert("RGBA")
    im.save(ICO, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
print(f"favicon.ico written: {ICO.stat().st_size} bytes")

rel_fixed = ico_added = files = 0
for f in M.rglob("*.html"):
    if "assets" in f.relative_to(M).parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    orig = html

    new, n = re.subn(r'rel="shortcut icon"', 'rel="icon"', html)
    rel_fixed += n
    html = new

    rel = f.relative_to(M)
    prefix = "../" if len(rel.parts) > 1 else ""
    ico_href = f"{prefix}favicon.ico"
    if 'rel="icon"' in html and "favicon.ico" not in html:
        m = re.search(r'<link[^>]*rel="icon"[^>]*/?>', html)
        if m:
            html = html[: m.end()] + f'<link href="{ico_href}" sizes="16x16 32x32 48x48" rel="icon" type="image/x-icon"/>' + html[m.end():]
            ico_added += 1

    if html != orig:
        for attempt in range(5):
            try:
                f.write_text(html, encoding="utf-8")
                files += 1
                break
            except OSError:
                import time
                time.sleep(1.5)

print(f"files changed: {files}, rel normalized: {rel_fixed}, ico fallback links: {ico_added}")
