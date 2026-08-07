# -*- coding: utf-8 -*-
"""Force homepage links to / and redirect /index.html -> /."""
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")

# href/data-page-link that mean "home" via index.html variants
HOME_RE = re.compile(
    r'\b(href|data-page-link)=("|\')((?:\.\./)*(?:index\.html)?|/index\.html)(\2)'
)
# only exact home targets: "", after strip of ../ is index.html or /index.html
# Better explicit patterns:
PATS = [
    (re.compile(r'\b(href|data-page-link)=("|\')index\.html(\2)'), r'\1=\2/\2'),
    (re.compile(r'\b(href|data-page-link)=("|\')/index\.html(\2)'), r'\1=\2/\2'),
    (re.compile(r'\b(href|data-page-link)=("|\')(?:\.\./)+index\.html(\2)'), r'\1=\2/\2'),
    (re.compile(r'\b(data-original-url)=("|\')https://raskrutov\.kz/index\.html(\2)'), r'\1=\2https://raskrutov.kz/\2'),
]

stats = {"files": 0, "repl": 0}
pages = [
    p
    for p in ROOT.rglob("*.html")
    if "assets" not in p.relative_to(ROOT).parts
]

for page in pages:
    html = page.read_text(encoding="utf-8", errors="ignore")
    orig = html
    ntot = 0
    for pat, repl in PATS:
        html, n = pat.subn(repl, html)
        ntot += n
    if html != orig:
        for _ in range(5):
            try:
                page.write_text(html, encoding="utf-8")
                break
            except OSError:
                time.sleep(1)
        stats["files"] += 1
        stats["repl"] += ntot

# .htaccess redirect
ht = ROOT / ".htaccess"
rule = "Redirect 301 /index.html /"
if ht.exists():
    t = ht.read_text(encoding="utf-8", errors="ignore")
    if "Redirect 301 /index.html" not in t:
        t = t.rstrip() + "\n\n# Prefer clean homepage URL\n" + rule + "\n"
        ht.write_text(t, encoding="utf-8")
        print("added htaccess rule")
    else:
        print("htaccess rule already present")
else:
    ht.write_text(rule + "\n", encoding="utf-8")
    print("created htaccess")

print(stats)

# verify leftover nav index.html
left = 0
for page in pages:
    t = page.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'(?:href|data-page-link)="([^"]*index\.html[^"]*)"', t):
        v = m.group(1)
        if "assets/" in v or "svgSprite" in v or "/index.html/" in v:
            continue
        if v in ("index.html", "/index.html") or re.fullmatch(r"(?:\.\./)*index\.html", v):
            left += 1
            print("LEFT", page, v)
print("leftover home index.html:", left)
