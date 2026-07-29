# -*- coding: utf-8 -*-
"""Site-wide structural audit: duplicate/missing fixed menus, duplicate static
menus, multiple h1, duplicated block IDs, missing favicon, double JSON-LD."""
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

MENU_IDS = {"c79b353f": "white-std", "92c58db8": "purple", "8ab6b296": "static-std"}

issues = {}
def add(page, kind, detail=""):
    issues.setdefault(page, []).append(f"{kind}: {detail}".rstrip(": "))

for page in PAGES:
    rel = page.relative_to(ROOT).as_posix()
    html = page.read_text(encoding="utf-8")

    # fixed menu sections
    fixed_menus = []
    static_menus = []
    for m in re.finditer(r'<div blk_class="section" class="([^"]*)"[^>]*?id="([a-f0-9]{8})', html):
        cls, sid = m.group(1), m.group(2)
        seg = html[m.end():m.end() + 4000]
        if "ms-menu__wrapper" not in seg:
            continue
        if "is_fixed" in cls:
            fixed_menus.append(sid)
        else:
            static_menus.append(sid)

    if len(fixed_menus) > 1:
        add(rel, "DOUBLE-FIXED-MENU", ",".join(fixed_menus))
    if len(fixed_menus) == 0:
        add(rel, "NO-FIXED-MENU")
    if len(static_menus) > 1:
        add(rel, "DOUBLE-STATIC-MENU", ",".join(static_menus))
    if len(static_menus) == 0:
        add(rel, "NO-STATIC-MENU")

    # h1 count (visible markup may legitimately have pc/mobile dupes -> flag only >2)
    h1s = len(re.findall(r"<h1[\s>]", html))
    if h1s == 0:
        add(rel, "NO-H1")
    elif h1s > 2:
        add(rel, f"H1x{h1s}")

    # duplicate block IDs (id="b-..." / section ids)
    ids = re.findall(r'\bid="([a-f0-9]{32})"', html)
    dup = [i for i, c in Counter(ids).items() if c > 1]
    if dup:
        add(rel, "DUP-BLOCK-ID", f"{len(dup)} dup ({dup[0][:8]}…)")

    # JSON-LD blocks
    ld = len(re.findall(r'application/ld\+json', html))
    if ld == 0:
        add(rel, "NO-JSONLD")
    elif ld > 1:
        add(rel, f"JSONLDx{ld}")

    # favicon
    if 'rel="icon"' not in html:
        add(rel, "NO-FAVICON")

    # title
    titles = len(re.findall(r"<title>", html))
    if titles != 1:
        add(rel, f"TITLE-x{titles}")

    # canonical absolute
    m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not m:
        add(rel, "NO-CANONICAL")
    elif not m.group(1).startswith("https://raskrutov.kz"):
        add(rel, "CANONICAL-NOT-ABS", m.group(1)[:50])

print("=== PAGES WITH ISSUES ===")
for page, probs in issues.items():
    print(page)
    for p in probs:
        print("   -", p)
print()
print(f"pages with issues: {len(issues)} / {len(PAGES)}")
