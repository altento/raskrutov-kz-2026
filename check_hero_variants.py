#!/usr/bin/env python3
"""Check hero image URL variants: do base (no __q_) versions exist?"""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

# all preloads currently in pages
pre_re = re.compile(r'<link rel="preload" as="image" href="([^"]+)"')
variants = {}
missing_base = 0
checked = 0
for f in sorted(M.rglob("*.html")):
    if "assets" in f.relative_to(M).parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    m = pre_re.search(html)
    if not m:
        continue
    href = m.group(1)
    tail = href.split("/")[-1]
    base = re.sub(r"__q_\d+", "", tail)
    # resolve href to file
    rel = href.replace("../assets/", "assets/").replace("assets/", "assets/", 1)
    if href.startswith("../"):
        full = (f.parent / href).resolve()
    else:
        full = M / href
    base_full = full.parent / base
    checked += 1
    if base != tail:
        exists_orig = full.exists()
        exists_base = base_full.exists()
        key = f"orig={exists_orig} base={exists_base}"
        variants[key] = variants.get(key, 0) + 1
        if not exists_base:
            missing_base += 1
            if missing_base <= 5:
                print(f"  base missing: {f.name} -> {base_full.relative_to(M) if base_full.is_absolute() else base_full}")
    else:
        variants["no-suffix-already"] = variants.get("no-suffix-already", 0) + 1

print(f"\npreloads checked: {checked}")
print(f"variant stats: {variants}")

# how is the hero referenced in @media? find occurrences in index.html
html = (M / "index.html").read_text(encoding="utf-8", errors="ignore")
for mm in re.finditer(r"6eea3ed3de3e5cbe118d06eb148fe963[^'\")\s]*", html):
    ctx = html[max(0, mm.start()-250): mm.start()]
    media = "@media" in ctx[-200:]
    print(f"\n  occurrence: {mm.group(0)[:60]} (near @media: {media})")
    print(f"  context: ...{re.sub(chr(92)+'s+', ' ', ctx[-120:])}")
