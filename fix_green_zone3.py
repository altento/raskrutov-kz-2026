# -*- coding: utf-8 -*-
"""Round 3: lazy-load ALL remaining eager <img> (hidden breakpoint variants
download eagerly otherwise — PSI mobile flagged 350KB waste), plus keep hero
div-background preload untouched (LCP element is not an <img>)."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

IMG = re.compile(r"<img\b[^>]*>")

stats = {"lazy_added": 0, "already": 0}
for page in PAGES:
    html = page.read_text(encoding="utf-8")
    orig = html

    def fix(m):
        tag = m.group(0)
        if "loading=" in tag:
            stats["already"] += 1
            return tag
        stats["lazy_added"] += 1
        if tag.endswith("/>"):
            return tag[:-2] + ' loading="lazy" decoding="async"/>'
        return tag[:-1] + ' loading="lazy" decoding="async">'

    html = IMG.sub(fix, html)
    if html != orig:
        page.write_text(html, encoding="utf-8")

print("stats:", stats)
