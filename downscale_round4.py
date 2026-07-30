# -*- coding: utf-8 -*-
"""Round 4 downscale: PSI mobile flagged images (containers from PSI report)."""
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
A = "assets/m-files.cdn1.cc/lpfile"

# (relative path, target width or None for recompress-only, quality)
TARGETS = [
    # phone mockup 333x728 -> container 147x321 (2x = 294)
    (f"{A}/2/7/e/27e940bfca13c46588cbb867b1d4c3d6/-/resize/1000/f__q_80115761.webp", 294, 80),
    # case card 660x464 -> container 578x406
    (f"{A}/8/a/9/8a9295d7d2c61d6ba474e83ff6e56aaf/-/crop/0x0x1316x925/-/resize/330/-/scale/x3/-/resize/1920/f__q_43722790.webp", 600, 80),
    # design card 660x366 -> container 505x280
    (f"{A}/d/1/c/d1cbe283f2e7f3e691ab26abf773bc60/-/resize/1000/f__q_57244759.webp", 560, 80),
    # raki logo strip 422x98 -> compression only (already 2x of 211)
    (f"{A}/8/1/a/81a3fe2ab76d8a7d4df2ea1900ce0265/-/crop/0x0x955x221/-/resize/211/-/scale/x3/-/resize/1920/f.webp", None, 62),
    # case card 660x370 -> container 578x324
    (f"{A}/1/0/a/10a6848446203749a81f7e7c2ad273e9/-/crop/0x0x1600x895/-/resize/330/-/scale/x3/-/resize/1920/f__q_99007932.webp", 600, 80),
    # academy screenshot 660x492 -> container 578x431
    (f"{A}/4/9/a/49a2df89a8e1a9fb63b9cbaff20df7d1/-/crop/0x0x1448x1081/-/resize/330/-/scale/x3/-/resize/1920/f__q_80095311.webp", 600, 80),
    # banner 660x266 -> container 578x233
    (f"{A}/6/1/b/61be3ed1ac9f22c625dcd8063d66537b/-/crop/0x0x1570x634/-/resize/330/-/scale/x3/f__q_63750526.webp", 600, 80),
]

total_before = total_after = 0
for rel, maxw, q in TARGETS:
    f = ROOT / rel
    if not f.exists():
        print("MISSING:", rel)
        continue
    before = f.stat().st_size
    im = Image.open(f)
    im.load()
    if maxw and im.width > maxw:
        h = round(im.height * maxw / im.width)
        im = im.resize((maxw, h), Image.LANCZOS)
    im.save(f, "WEBP", quality=q, method=6)
    after = f.stat().st_size
    total_before += before
    total_after += after
    print(f"{im.size} {before//1024}KB -> {after//1024}KB  {f.name}")

print(f"TOTAL: {total_before//1024}KB -> {total_after//1024}KB (saved {(total_before-total_after)//1024}KB)")
