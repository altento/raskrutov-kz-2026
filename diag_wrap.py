# -*- coding: utf-8 -*-
"""Check which inline scripts referencing builder globals are NOT wrapped in DOMContentLoaded."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GLOBALS = ["MsJsPublishedManager", "adapterManager", "FE.", "yandexMaps", "MsVueTemplate"]

def analyze(path):
    t = Path(path).read_text(encoding="utf-8")
    scripts = []
    for m in re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", t, re.S):
        body = m.group(1)
        if not body.strip():
            continue
        wrapped = bool(re.match(r"\s*document\.addEventListener\('DOMContentLoaded'", body))
        used = [g for g in GLOBALS if g in body]
        scripts.append((wrapped, used, " ".join(body.split())[:90]))
    return scripts

for f in ["site_mirror/web-studiya/index.html", "site_mirror/index.html"]:
    print("=====", f)
    for wrapped, used, head in analyze(f):
        if used and not wrapped:
            print(f"  UNWRAPPED uses {used}: {head}")
    n_wrapped = sum(1 for w, u, h in analyze(f) if w)
    n_unwrapped_users = sum(1 for w, u, h in analyze(f) if u and not w)
    print(f"  wrapped: {n_wrapped}, unwrapped-with-globals: {n_unwrapped_users}")
    print()
