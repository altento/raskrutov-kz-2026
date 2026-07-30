# -*- coding: utf-8 -*-
"""Full list of refs resolving to missing files, with context type."""
import json
import posixpath
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
mapping = json.loads(Path("url_mapping.json").read_text(encoding="utf-8"))

real_files = set()
for f in ROOT.rglob("*"):
    if f.is_file():
        real_files.add(f.relative_to(ROOT).as_posix())

PAGES = [(ROOT / "index.html", "")] + [(ROOT / b / "index.html", b) for b in mapping.values()]

def resolve(base, path):
    path = path.split("#")[0].split("?")[0].strip().strip("'\"")
    if re.match(r"^(https?://|mailto:|tel:|javascript:|//|data:|blob:)", path) or not path:
        return None
    r = posixpath.normpath(posixpath.join(base, path)) if base else posixpath.normpath(path)
    return r.replace("\\", "/")

missing = {}
for page, beaut in PAGES:
    html = page.read_text(encoding="utf-8")
    for m in re.finditer(r'(href|src|srcset)="([^"]+)"|url\(([^)]*)\)', html):
        kind = m.group(1) or "cssurl"
        raw = m.group(2) or m.group(3) or ""
        urls = [u.strip().split(" ")[0] for u in raw.split(",")] if kind == "srcset" else [raw]
        for u in urls:
            r = resolve(beaut, u)
            if r and r not in real_files and r != ".":
                key = (kind, r)
                missing.setdefault(key, set()).add(beaut or "(root)")

print("unique missing targets:", len(missing))
for (kind, r), pages in sorted(missing.items(), key=lambda x: -len(x[1])):
    print(f"{len(pages):3d}p  {kind:7s} {r[:130]}")
