# -*- coding: utf-8 -*-
"""Extended audit: data-page-link, srcset entries, url() in styles and inline CSS."""
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

def resolve(base, path):
    path = path.split("?")[0].split("#")[0].strip().strip("'\"")
    if not path:
        return None
    if re.match(r"^(https?://|mailto:|tel:|javascript:|//|data:|blob:)", path):
        return None
    r = posixpath.normpath(posixpath.join(base, path)) if base else posixpath.normpath(path)
    return r.replace("\\", "/")

problems = {}
counts = {"dpl": 0, "srcset": 0, "cssurl": 0}
for page in PAGES:
    html = page.read_text(encoding="utf-8")
    base = "pages" if page.parent != ROOT else ""
    # data-page-link
    for m in re.finditer(r'data-page-link="([^"]+)"', html):
        counts["dpl"] += 1
        r = resolve(base, m.group(1))
        if r and r not in real:
            problems.setdefault(page.name, set()).add("dpl: " + m.group(1)[:90])
    # srcset
    for m in re.finditer(r'srcset="([^"]+)"', html):
        for entry in m.group(1).split(","):
            url = entry.strip().split(" ")[0]
            if not url:
                continue
            counts["srcset"] += 1
            r = resolve(base, url)
            if r and r not in real:
                problems.setdefault(page.name, set()).add("srcset: " + url[:90])
    # url() in style attributes and <style> blocks (exclude data:)
    for m in re.finditer(r'url\(([^)]*)\)', html):
        counts["cssurl"] += 1
        u = m.group(1).strip().strip("'\"")
        r = resolve(base, u)
        if r and r not in real:
            problems.setdefault(page.name, set()).add("url(): " + u[:90])

print("counts:", counts)
if problems:
    for name, items in list(problems.items())[:25]:
        print(name)
        for i in sorted(items)[:6]:
            print("   -", i)
    print("pages with problems:", len(problems))
else:
    print("ALL dpl/srcset/url() resolve OK")
