#!/usr/bin/env python3
"""Check url() references in the CSS bundle - are they relative?"""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
css_dir = M / "assets/m-files.cdn1.cc/web/build/pages"
bundles = list(css_dir.glob("public.bundle*.css"))
print(f"bundle files: {[b.name for b in bundles]}")
css = bundles[0].read_text(encoding="utf-8", errors="ignore")
print(f"size: {len(css)} chars")

urls = re.findall(r"url\((['\"]?)([^)'\"]+)\1\)", css)
print(f"url() refs: {len(urls)}")
kinds = {}
for _, u in urls:
    if u.startswith("http") or u.startswith("//"):
        k = "absolute-url"
    elif u.startswith("/"):
        k = "absolute-path"
    elif u.startswith("data:"):
        k = "data-uri"
    else:
        k = "relative"
    kinds[k] = kinds.get(k, 0) + 1
print(f"kinds: {kinds}")
print("samples:")
for _, u in urls[:15]:
    print(f"  {u[:110]}")
