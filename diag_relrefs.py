# -*- coding: utf-8 -*-
"""Inventory of all relative ref prefixes on pages/*.html before restructure."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")

forms = {}
for p in sorted((ROOT / "pages").glob("*.html")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    # all quoted strings starting with ../ or containing .html
    for m in re.finditer(r'"((?:\.\./)+[^"]{0,80})"', t):
        v = m.group(1)
        key = re.sub(r'[\w.-]+(?=/)', "X", v)[:40]
        if not any(s in v for s in ["assets/", "index.html"]):
            forms.setdefault(v[:60], 0)
            forms[v[:60]] += 1

print("non-assets non-index ../ refs:")
for k, v in sorted(forms.items()):
    print(f"  x{v:4d}  {k}")

# favicon refs
t = (ROOT / "pages/faq.html").read_text(encoding="utf-8")
for m in re.finditer(r'<link[^>]*rel="icon"[^>]*>', t):
    print("ICON:", m.group(0))
# check root files present
print("root files:", [f.name for f in ROOT.iterdir() if f.is_file()])
