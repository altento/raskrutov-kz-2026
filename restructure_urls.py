# -*- coding: utf-8 -*-
"""URL restructure: pages/X.html -> <canonical path>/index.html with full ref rewrite.

- Asset refs: normalized to ("../" x depth) + "assets/..."
- Inter-page refs: relative beautiful paths (no .html, no trailing slash)
- data-page-link: page-relative (window.open resolves vs document base) = same as href
- Old pages/X.html -> redirect stubs (GH Pages); .htaccess 301 for Apache (ps.kz)
- sitemap.xml + robots.txt generated
Idempotent: stubs and already-moved files are skipped.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
DRY = "--apply" not in sys.argv

mapping = json.loads(Path("url_mapping.json").read_text(encoding="utf-8"))
assert len(mapping) == 74

STUB_MARK = "<!--redirect-stub-->"
HT_MARK = "# 301: legacy /pages/*.html -> pretty URLs"

stats = {"moved": 0, "assets": 0, "favicon": 0, "page_links": 0, "root_links": 0, "index_page_links": 0, "stubs": 0, "skipped": 0}

def depth_prefix(beaut):
    return "../" * (beaut.count("/") + 1)

ASSET_DBL = re.compile(r"(?<!\.)\.\./assets/\.\./assets/")
ASSET_SGL = re.compile(r"(?<!\.)\.\./assets/")
FAVICON = re.compile(r"(?<!\.)\.\./favicon\.ico")
PAGE_REF = re.compile(r"([\"'])((?:\.\./)?(?:pages/)?)([\w.-]+\.html)(#[^\"']*)?\1")

def rewrite_page(html, beaut):
    prefix = depth_prefix(beaut)
    html, n = ASSET_DBL.subn(prefix + "assets/", html)
    stats["assets"] += n
    html, n = ASSET_SGL.subn(prefix + "assets/", html)
    stats["assets"] += n
    html, n = FAVICON.subn(prefix + "favicon.ico", html)
    stats["favicon"] += n

    def repl(m):
        q, pre, base, frag = m.group(1), m.group(2), m.group(3), m.group(4) or ""
        if base in mapping:
            stats["page_links"] += 1
            return f"{q}{prefix}{mapping[base]}{frag}{q}"
        if base == "index.html" and pre == "../":
            stats["root_links"] += 1
            return f"{q}{prefix}{q}"
        return m.group(0)
    html = PAGE_REF.sub(repl, html)
    return html

STUB = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
{mark}
<meta http-equiv="refresh" content="0; url=../{beaut}">
<link rel="canonical" href="https://raskrutov.kz/{beaut}">
<title>{beaut} — Raskrutov</title>
</head>
<body>
<p>Страница переехала: <a href="../{beaut}">https://raskrutov.kz/{beaut}</a></p>
</body>
</html>
"""

moved = []
for name, beaut in sorted(mapping.items()):
    old = ROOT / "pages" / name
    new = ROOT / beaut / "index.html"
    cur = old.read_text(encoding="utf-8")
    if STUB_MARK in cur:
        stats["skipped"] += 1
        continue
    html = rewrite_page(cur, beaut)
    if not DRY:
        new.parent.mkdir(parents=True, exist_ok=True)
        new.write_text(html, encoding="utf-8")
        old.write_text(STUB.format(mark=STUB_MARK, beaut=beaut), encoding="utf-8")
    stats["moved"] += 1
    stats["stubs"] += 1
    moved.append((name, beaut))

# index.html: "pages/X.html" -> beautiful (root-relative form)
idx = ROOT / "index.html"
html = idx.read_text(encoding="utf-8")
def idx_repl(m):
    q, pre, base, frag = m.group(1), m.group(2), m.group(3), m.group(4) or ""
    if pre == "pages/" and base in mapping:
        stats["index_page_links"] += 1
        return f"{q}{mapping[base]}{frag}{q}"
    return m.group(0)
html = PAGE_REF.sub(idx_repl, html)
if not DRY:
    idx.write_text(html, encoding="utf-8")

# .htaccess redirects
ht = ROOT / ".htaccess"
ht_text = ht.read_text(encoding="utf-8")
if HT_MARK not in ht_text:
    rules = [HT_MARK, "<IfModule mod_alias.c>"]
    for name, beaut in sorted(mapping.items()):
        rules.append(f"Redirect 301 /pages/{name} /{beaut}")
    rules.append("</IfModule>\n")
    if not DRY:
        ht.write_text("\n".join(rules) + "\n" + ht_text, encoding="utf-8")
    ht_added = True
else:
    ht_added = False

# sitemap.xml + robots.txt
urls = ["https://raskrutov.kz/"] + [f"https://raskrutov.kz/{b}" for _, b in sorted(mapping.items(), key=lambda kv: kv[1])]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sitemap += "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
sitemap += "\n</urlset>\n"
robots = "User-agent: *\nAllow: /\n\nSitemap: https://raskrutov.kz/sitemap.xml\n"
if not DRY:
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")

print("DRY-RUN" if DRY else "APPLIED")
print("stats:", stats)
print("htaccess redirects added:", ht_added or HT_MARK in ht_text)
print("sample moves:")
for name, beaut in moved[:6]:
    print(f"  pages/{name} -> /{beaut}/index.html")
