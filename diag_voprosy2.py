# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

html = Path("site_mirror/index.html").read_text(encoding="utf-8")

for pos in [1246039, 1289622]:
    print("=" * 20, "pos", pos)
    ctx = html[pos - 1500:pos + 400]
    # print only tags + text compactly
    seg = re.sub(r"\s+", " ", ctx)
    # show around the Вопросы word
    idx = seg.find("Вопросы")
    print(seg[max(0, idx - 1200):idx + 300])
    print()
