#!/usr/bin/env python3
"""Sample alt texts from a page to verify add_alts.py output."""
import re
from pathlib import Path

h = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\pages\keysy.html").read_text(
    encoding="utf-8"
)
alts = re.findall(r'alt="([^"]{4,90})"', h)
print(f"non-trivial alts: {len(alts)}")
for a in alts[2:14]:
    print("  ", a)
