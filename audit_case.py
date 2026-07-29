# -*- coding: utf-8 -*-
"""Check all internal hrefs/srcs for case mismatches against real files."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

# build case-sensitive map of real files (relative posix paths, lowercased -> real)
real = {}
for f in ROOT.rglob("*"):
    if f.is_file():
        rel = f.relative_to(ROOT).as_posix()
        real[rel.lower()] = rel

ATTR = re.compile(r'(?:href|src)="([^"#][^"]*)"')
bad = {}
checked = 0
for page in PAGES:
    html = page.read_text(encoding="utf-8")
    base = page.parent
    for m in ATTR.finditer(html):
        url = m.group(1)
        if url.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "//", "data:")):
            continue
        path = url.split("?")[0]
        if not path or path.startswith("#"):
            continue
        checked += 1
        # resolve relative
        parts = []
        skip = False
        for seg in (path.split("/")):
            if seg == ".":
                continue
            if seg == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(seg)
        if page.parent != ROOT:
            rel_parts = ["pages"] + parts if not parts or parts[0] != ".." else parts
        # simpler: resolve against page dir
        resolved = (page.parent / path).as_posix()
        # normalize ../ manually
        norm = []
        for seg in resolved.split("/"):
            if seg == "..":
                if norm:
                    norm.pop()
            elif seg != ".":
                norm.append(seg)
        norm = "/".join(norm)
        if norm.startswith("site_mirror/"):
            norm = norm[len("site_mirror/"):]
        low = norm.lower()
        if low in real:
            if real[low] != norm:
                bad.setdefault(page.name, []).append(f"case: {path} -> real {real[low]}")
        else:
            if not low.startswith(("yandex", "vk", "t.me", "wa.me")):
                bad.setdefault(page.name, []).append(f"MISSING: {path}")

print("checked refs:", checked)
if bad:
    for page, items in list(bad.items())[:30]:
        print(page)
        for i in items[:6]:
            print("   -", i[:140])
    print("pages with problems:", len(bad))
else:
    print("NO case problems or missing internal refs")
