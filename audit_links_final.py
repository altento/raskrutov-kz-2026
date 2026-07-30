# -*- coding: utf-8 -*-
"""Final link audit with correct relative resolution (pure posix)."""
import posixpath
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

real = set()
for f in ROOT.rglob("*"):
    if f.is_file():
        real.add(f.relative_to(ROOT).as_posix())

ATTR = re.compile(r'(?:href|src)="([^"#][^"]*)"')
problems = {}
checked = 0
for page in PAGES:
    html = page.read_text(encoding="utf-8")
    base = "pages" if page.parent != ROOT else ""
    for m in ATTR.finditer(html):
        url = m.group(1)
        if re.match(r'^(https?://|mailto:|tel:|javascript:|//|data:)', url):
            continue
        path = url.split("?")[0]
        if not path or path.startswith("#"):
            continue
        checked += 1
        resolved = posixpath.normpath(posixpath.join(base, path)) if base else posixpath.normpath(path)
        resolved = resolved.replace("\\", "/")
        if resolved not in real:
            problems.setdefault(page.name, set()).add(path[:120])

print("checked:", checked)
if problems:
    for name, items in problems.items():
        print(name)
        for i in sorted(items)[:8]:
            print("   -", i)
    print("pages with missing refs:", len(problems))
else:
    print("ALL internal href/src resolve to real files")
