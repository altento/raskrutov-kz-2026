#!/usr/bin/env python3
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
for name in ["pages/keysy.html", "index.html"]:
    h = (M / name).read_text(encoding="utf-8", errors="ignore")
    print(f"===== {name} =====")
    for i in re.findall(r"<link[^>]*rel=\"icon\"[^>]*>", h):
        print(" ", i[:140])
    # sample a few newly filled alts
    alts = re.findall(r'<img[^>]*alt="([^"]{10,})"', h)
    print("  sample alts:", alts[:4])
print("favicon.ico exists:", (M / "favicon.ico").exists())
