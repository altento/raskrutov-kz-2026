#!/usr/bin/env python3
"""Inventory images in site_mirror: formats, sizes, img tags without alt."""
import re
from collections import Counter
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif", ".ico", ".bmp"}

ext_count: Counter = Counter()
ext_size: Counter = Counter()
biggest: list[tuple[int, str]] = []
total = 0
for f in M.rglob("*"):
    if not f.is_file():
        continue
    ext = f.suffix.lower()
    if ext not in IMG_EXT:
        continue
    sz = f.stat().st_size
    ext_count[ext] += 1
    ext_size[ext] += sz
    total += sz
    biggest.append((sz, f.relative_to(M).as_posix()))

print("=== Image files by extension ===")
for ext, n in ext_count.most_common():
    print(f"{ext:8s} {n:5d} files  {ext_size[ext]/1024/1024:8.1f} MB")
print(f"TOTAL: {sum(ext_count.values())} files, {total/1024/1024:.1f} MB")

print("\n=== 15 biggest files ===")
for sz, p in sorted(biggest, reverse=True)[:15]:
    print(f"{sz/1024/1024:7.2f} MB  {p}")

# img tags without alt in served pages
no_alt = with_alt = empty_alt = 0
img_re = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
for f in M.rglob("*.html"):
    if "assets" in f.relative_to(M).parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    for tag in img_re.findall(html):
        m = re.search(r'\balt\s*=\s*"([^"]*)"', tag, re.IGNORECASE)
        if m is None:
            no_alt += 1
        elif m.group(1).strip() == "":
            empty_alt += 1
        else:
            with_alt += 1
print("\n=== <img> tags in served pages ===")
print(f"with alt: {with_alt}, empty alt: {empty_alt}, missing alt: {no_alt}")
