#!/usr/bin/env python3
"""Diagnose remaining images without alt + favicon link state across all pages."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)

pages_total = 0
no_alt: dict[str, list[str]] = {}
favicon_variants: dict[str, int] = {}
favicon_file = M / "assets" / "m-files.cdn1.cc" / "lpfile" / "favicon" / "favicon__q_1.png"
print(f"favicon file exists: {favicon_file.exists()}")
if favicon_file.exists():
    print(f"  size: {favicon_file.stat().st_size} bytes")

for f in sorted(M.rglob("*.html")):
    rel = f.relative_to(M).as_posix()
    if "assets" in f.relative_to(M).parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    pages_total += 1

    for m in IMG_RE.finditer(html):
        tag = m.group(0)
        ma = re.search(r'\balt\s*=\s*"([^"]*)"', tag, re.IGNORECASE)
        if ma is None or ma.group(1).strip() == "":
            src_m = re.search(r'\bsrc\s*=\s*"([^"]*)"', tag, re.IGNORECASE)
            src = src_m.group(1) if src_m else "?"
            no_alt.setdefault(rel, []).append(src.split("/")[-1][:60])

    for m in re.finditer(r'<link[^>]*rel="(?:shortcut )?icon"[^>]*>', html):
        favicon_variants[m.group(0)[:110]] = favicon_variants.get(m.group(0)[:110], 0) + 1
    for m in re.finditer(r'<link[^>]*href="([^"]*favicon[^"]*)"[^>]*>', html):
        key = f"{rel}: {m.group(1)[:80]}"
        favicon_variants[key] = favicon_variants.get(key, 0) + 1

print(f"\npages scanned: {pages_total}")
print(f"pages with imgs missing alt: {len(no_alt)}")
total_missing = sum(len(v) for v in no_alt.values())
print(f"total imgs missing alt: {total_missing}")
for rel, srcs in list(no_alt.items())[:12]:
    print(f"  {rel}: {len(srcs)} -> {srcs[:4]}")

print(f"\nfavicon link variants ({len(favicon_variants)}):")
for k, c in sorted(favicon_variants.items())[:20]:
    print(f"  [{c}x] {k}")
