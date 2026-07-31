# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
h = Path("site_mirror/index.html").read_text(encoding="utf-8")
print("FONTS")
for m in re.findall(r'<link rel="preload"[^>]+as="font"[^>]*>', h):
    print(m)
print("PHONE")
m = re.search(r'<img src="[^"]*27e940bf[^"]+"[^>]*>', h)
print(m.group(0) if m else None)
print("LOGOS")
for m in re.finditer(r'<img src="[^"]*81a3fe2[^"]+"[^>]*>', h):
    print(m.group(0)[:300])
print("LCP preload", "6eea3ed3de3e5cbe118d06eb148fe963.webp" in h and 'rel="preload" as="image"' in h)
