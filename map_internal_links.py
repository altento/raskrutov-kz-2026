#!/usr/bin/env python3
import re
from pathlib import Path
from collections import defaultdict

MIRROR = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
by_file = {}
all_links = defaultdict(set)

for html_path in [MIRROR / "index.html", *sorted((MIRROR / "pages").glob("*.html"))]:
    rel = html_path.relative_to(MIRROR).as_posix()
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    links = sorted(set(re.findall(r'data-page-link="([^"]+)"', text)))
    links = [l for l in links if l and not l.startswith(("tel:", "http", "assets/"))]
    by_file[rel] = links
    for l in links:
        all_links[l].add(rel)

lines = ["=== Unique internal data-page-link targets ==="]
for link in sorted(all_links):
    if any(x in link for x in [".html", "pages/"]) or link.startswith("../"):
        lines.append(f"  {link} <- {sorted(all_links[link])}")

lines += ["\n=== Per page (non-nav only) ==="]
nav_only = {"../index.html", "index.html", "web-studiya.html", "r-builder.html", "akademiya.html", "partneram.html", "o-kompanii.html", "keysy.html", "kontakty.html", "pages/web-studiya.html", "pages/r-builder.html", "pages/akademiya.html", "pages/partneram.html", "pages/o-kompanii.html", "pages/keysy.html", "pages/kontakty.html", "pages/faq.html"}
for rel, links in by_file.items():
    extra = [l for l in links if l not in nav_only and l != f"pages/{Path(rel).name}"]
    if extra:
        lines.append(f"{rel}: {extra}")

Path(MIRROR / "internal_links_map.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[:80]))
