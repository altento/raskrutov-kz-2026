# -*- coding: utf-8 -*-
"""home-sub-link: inline (word-wrapping restored) + padding-only touch target."""
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
PAGES = [p for p in ROOT.rglob("*.html") if "assets" not in p.relative_to(ROOT).parts]

VARIANTS = [
    ".home-sub-link{display:inline-block;padding:8px 6px 8px 0;margin:-8px 0;}",
    ".home-sub-link{display:inline-block;padding:8px 6px 8px 0;line-height:1.7;}",
]
NEW = ".home-sub-link{padding:8px 6px 8px 0;}"

n = 0
for page in PAGES:
    html = page.read_text(encoding="utf-8", errors="ignore")
    orig = html
    for v in VARIANTS:
        html = html.replace(v, NEW)
    if html != orig:
        for attempt in range(5):
            try:
                page.write_text(html, encoding="utf-8")
                break
            except OSError:
                time.sleep(1.5)
        n += 1
print("files fixed:", n)
