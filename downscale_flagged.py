# -*- coding: utf-8 -*-
"""Downscale oversized images flagged by PSI 'Improve image delivery' to ~2x
of their display size. Files are located by unique hash substrings."""
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror/assets/m-files.cdn1.cc/lpfile")

# (unique substring in path, target max width)
TARGETS = [
    ("61be3ed1ac9f22c625dcd8063d66537b/-/crop/0x0x1570x634/-/resize/330", 660),
    ("8a9295d7d2c61d6ba474e83ff6e56aaf/-/crop/0x0x1316x925/-/resize/330", 660),
    ("10a6848446203749a81f7e7c2ad273e9/-/crop/0x0x1600x895/-/resize/330", 660),
    ("f__q_57244759.webp", 660),
    ("f__q_80095311.webp", 660),
    ("6dcfc118dca247f9f6123d191c12fc43__q_60876912.webp", 96),
    ("25804b0", 96),  # f__q_61408205.webp — Telegram icon
    ("81a3fe2ab76d8a7d4df2ea1900ce0265/-/crop/0x0x955x221/-/resize/211", 422),
]

done = 0
for key, maxw in TARGETS:
    hits = [p for p in ROOT.rglob("*.webp") if key.replace("/", "\\") in str(p) or key in str(p).replace("\\", "/")]
    if not hits:
        print(f"!! not found: {key}")
        continue
    for f in hits:
        im = Image.open(f)
        w, h = im.size
        if w <= maxw:
            print(f"== skip (already {w}px): {f.name}")
            continue
        nh = round(h * maxw / w)
        im2 = im.resize((maxw, nh), Image.LANCZOS)
        old = f.stat().st_size
        im2.save(f, "WEBP", quality=80, method=6)
        new = f.stat().st_size
        done += 1
        print(f"OK {w}x{h}->{maxw}x{nh}  {old//1024}KB->{new//1024}KB  {f.name}")

print("done:", done)
