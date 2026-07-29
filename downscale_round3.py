# -*- coding: utf-8 -*-
"""Downscale the second wave of flagged variants (desktop-display images that
also download on mobile) to ~2x of their display width."""
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror/assets/m-files.cdn1.cc/lpfile")

TARGETS = [
    # displayed 527 wide on desktop
    ("61be3ed1ac9f22c625dcd8063d66537b/-/crop/25x0x1365x634/-/resize/527", 1054),
    # displayed 348 wide on desktop
    ("8a9295d7d2c61d6ba474e83ff6e56aaf/-/crop/0x0x1316x929/-/resize/348", 696),
    # displayed 439 wide on desktop
    ("10a6848446203749a81f7e7c2ad273e9/-/crop/0x0x1600x896/-/resize/439", 878),
]

done = 0
for key, maxw in TARGETS:
    hits = [p for p in ROOT.rglob("*.webp") if key in str(p).replace("\\", "/")]
    if not hits:
        print(f"!! not found: {key}")
        continue
    for f in hits:
        im = Image.open(f)
        w, h = im.size
        if w <= maxw:
            print(f"== skip ({w}px): {f.name}")
            continue
        nh = round(h * maxw / w)
        im2 = im.resize((maxw, nh), Image.LANCZOS)
        old = f.stat().st_size
        im2.save(f, "WEBP", quality=78, method=6)
        new = f.stat().st_size
        done += 1
        print(f"OK {w}x{h}->{maxw}x{nh}  {old//1024}KB->{new//1024}KB  {f.name}")

print("done:", done)
