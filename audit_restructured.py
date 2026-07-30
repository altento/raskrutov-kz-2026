# -*- coding: utf-8 -*-
"""Post-restructure audit: every href/src/srcset/url()/data-page-link resolves."""
import json
import posixpath
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
mapping = json.loads(Path("url_mapping.json").read_text(encoding="utf-8"))

real_files = set()
real_dirs = set()
for f in ROOT.rglob("*"):
    rel = f.relative_to(ROOT).as_posix()
    if f.is_file():
        real_files.add(rel)
    else:
        real_dirs.add(rel)

PAGES = [(ROOT / "index.html", "")]
for name, beaut in mapping.items():
    PAGES.append((ROOT / beaut / "index.html", beaut))

def resolve(base_dir, path):
    path = path.split("#")[0].split("?")[0].strip().strip("'\"")
    if not path:
        return None
    if re.match(r"^(https?://|mailto:|tel:|javascript:|//|data:|blob:)", path):
        return None
    r = posixpath.normpath(posixpath.join(base_dir, path)) if base_dir else posixpath.normpath(path)
    r = r.replace("\\", "/")
    if r in (".", ""):
        return None  # site root — always valid
    return r

problems = {}
counts = {"href": 0, "src": 0, "srcset": 0, "cssurl": 0, "dpl": 0}
checked_pages = 0
for page, beaut in PAGES:
    if not page.exists():
        problems.setdefault(str(page), set()).add("MOVED FILE MISSING")
        continue
    checked_pages += 1
    html = page.read_text(encoding="utf-8")
    base = beaut  # directory of the page == its beautiful path (index.html inside)
    for m in re.finditer(r'(?:href|src)="([^"#][^"]*)"', html):
        counts["href"] += 1
        r = resolve(base, m.group(1))
        if r and r not in real_files and r not in real_dirs and (r + "/index.html") not in real_files:
            problems.setdefault(page.as_posix()[12:], set()).add("href/src: " + m.group(1)[:90])
    for m in re.finditer(r'srcset="([^"]+)"', html):
        for entry in m.group(1).split(","):
            url = entry.strip().split(" ")[0]
            if not url:
                continue
            counts["srcset"] += 1
            r = resolve(base, url)
            if r and r not in real_files:
                problems.setdefault(page.as_posix()[12:], set()).add("srcset: " + url[:90])
    for m in re.finditer(r'url\(([^)]*)\)', html):
        counts["cssurl"] += 1
        r = resolve(base, m.group(1))
        if r and r not in real_files:
            problems.setdefault(page.as_posix()[12:], set()).add("url(): " + m.group(1)[:70])
    for m in re.finditer(r'data-page-link="([^"]+)"', html):
        counts["dpl"] += 1
        r = resolve(base, m.group(1))
        if r and r not in real_files and r not in real_dirs and (r + "/index.html") not in real_files:
            problems.setdefault(page.as_posix()[12:], set()).add("dpl: " + m.group(1)[:90])
    # canonical intact + matches location
    cans = re.findall(r'<link rel="canonical" href="([^"]*)"', html)
    if beaut and (len(cans) != 1 or cans[0] != f"https://raskrutov.kz/{beaut}"):
        problems.setdefault(page.as_posix()[12:], set()).add("canonical: " + str(cans))
    # exactly one JSON-LD
    n_ld = html.count("application/ld+json")
    if n_ld != 1:
        problems.setdefault(page.as_posix()[12:], set()).add(f"jsonld blocks: {n_ld}")

print("pages checked:", checked_pages, " counts:", counts)
if problems:
    for name, items in list(problems.items())[:25]:
        print(name)
        for i in sorted(items)[:5]:
            print("   -", i)
    print("pages with problems:", len(problems))
else:
    print("ALL REFERENCES RESOLVE — 0 broken")

# stubs sanity
bad_stubs = 0
for name, beaut in mapping.items():
    stub = (ROOT / "pages" / name).read_text(encoding="utf-8")
    if "<!--redirect-stub-->" not in stub or f"url=../{beaut}" not in stub:
        bad_stubs += 1
        print("BAD STUB:", name)
print("bad stubs:", bad_stubs)
