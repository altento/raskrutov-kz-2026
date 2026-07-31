# -*- coding: utf-8 -*-
"""Rewrite Mottor asset urls in extracted CSS so they resolve from assets/css/."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CSS_DIR = Path("site_mirror/assets/css")
FILES = [
    "home-all-blocks.css",
    "home-popup-2782231.css",
    "home-popup-2773676.css",
]

# url(assets/...) or url('assets/...') or url("assets/...") → url(../...)
PAT = re.compile(
    r"""url\(\s*(['"]?)assets/""",
    re.I,
)


def fix(text: str) -> tuple[str, int]:
    n = 0

    def repl(m: re.Match) -> str:
        nonlocal n
        n += 1
        q = m.group(1) or ""
        return f"url({q}../"

    return PAT.sub(repl, text), n


for name in FILES:
    path = CSS_DIR / name
    if not path.exists():
        print("missing", name)
        continue
    raw = path.read_text(encoding="utf-8")
    fixed, n = fix(raw)
    path.write_text(fixed, encoding="utf-8")
    # sanity: remaining bad urls
    bad = len(re.findall(r"url\(\s*['\"]?assets/", fixed, flags=re.I))
    print(f"{name}: rewrote {n}, remaining assets/ urls: {bad}")

# verify a mask path resolves on disk
sample = CSS_DIR / "home-all-blocks.css"
t = sample.read_text(encoding="utf-8")
m = re.search(r"mask-image:\s*url\(([^)]+)\)", t)
if m:
    u = m.group(1).strip("'\"")
    print("sample mask url:", u)
    disk = (CSS_DIR / u).resolve()
    print("exists", disk.exists(), disk)
