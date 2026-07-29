#!/usr/bin/env python3
"""Inspect render-blocking tags in index.html and a sample page."""
import re
from pathlib import Path

for name in ["index.html", "pages/keysy.html"]:
    p = Path(r"C:\Users\user\Projects\раскрутов\site_mirror") / name
    html = p.read_text(encoding="utf-8", errors="ignore")
    print(f"===== {name} =====")
    for m in re.finditer(r"<script[^>]*\bsrc=\"[^\"]*\"[^>]*>", html):
        head = "HEAD" if m.start() < html.find("</head>") else "body"
        print(f"  [{head}] {m.group(0)[:150]}")
    for m in re.finditer(r'<link[^>]*rel="stylesheet"[^>]*>', html):
        print(f"  [css ] {m.group(0)[:150]}")
    for m in re.finditer(r'<link[^>]*rel="preload"[^>]*>', html):
        print(f"  [prel] {m.group(0)[:150]}")
