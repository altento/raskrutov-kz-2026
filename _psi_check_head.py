# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
h = Path("site_mirror/index.html").read_text(encoding="utf-8")
head = h[: h.find("</head>")]
print(head[:3000])
print("\n---TAIL HEAD---\n")
print(head[-1200:])
print("\nbundle js defer?", 'public.bundle__q_v_1784122069.js" defer' in h)
print("popup css", "home-popup-2782231.css" in h)
print("mobile hero preload", "hero-home-mobile.webp" in head)
print("all blocks link", 'href="assets/css/home-all-blocks.css"' in head)
