# -*- coding: utf-8 -*-
"""Bust immutable cache on extracted Mottor CSS by renaming to .v2.css."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("site_mirror")
CSS = ROOT / "assets" / "css"
HTML = ROOT / "index.html"

renames = {
    "home-all-blocks.css": "home-all-blocks.v2.css",
    "home-popup-2782231.css": "home-popup-2782231.v2.css",
    "home-popup-2773676.css": "home-popup-2773676.v2.css",
}

for old, new in renames.items():
    src, dst = CSS / old, CSS / new
    if not src.exists() and dst.exists():
        print("already", new)
        continue
    if not src.exists():
        raise SystemExit(f"missing {src}")
    shutil.copy2(src, dst)
    print("copied", old, "->", new)

html = HTML.read_text(encoding="utf-8")
for old, new in renames.items():
    if old not in html and new in html:
        continue
    n = html.count(old)
    html = html.replace(old, new)
    print(f"html replace {old}: {n}")

tmp = HTML.with_suffix(".html.tmp")
tmp.write_bytes(html.encode("utf-8"))
tmp.replace(HTML)

# Soften Cache-Control: immutable only for hashed Mottor paths / woff with hash-like names
ht = (ROOT / ".htaccess").read_text(encoding="utf-8")
marker = "# Cache-Control for hashed/static assets (PSI / repeat views)"
new_block = """# Cache-Control for hashed/static assets (PSI / repeat views)
<IfModule mod_headers.c>
  # Versioned Mottor bundles & hashed lpfile paths — long cache
  <FilesMatch "(__q_v_|/-/|lpfile/).+\\.(css|js|webp|png|jpe?g|svg|woff2?)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  # Site-owned CSS/JS without content-hash in filename — short cache so hotfixes propagate
  <FilesMatch "^(home-|lead-forms|breadcrumbs|hero-).+\\.(css|js|webp)$">
    Header set Cache-Control "public, max-age=3600, must-revalidate"
  </FilesMatch>
  <FilesMatch "\\.(html|htm)$">
    Header set Cache-Control "public, max-age=0, must-revalidate"
  </FilesMatch>
</IfModule>
"""
if marker in ht:
    # replace from marker through next blank-line-terminated IfModule roughly
    start = ht.find(marker)
    end = ht.find("# Compression for text resources", start)
    if end == -1:
        end = ht.find("Redirect 301 /web-studiya/aeo", start)
    if end != -1:
        ht = ht[:start] + new_block + "\n" + ht[end:]
        (ROOT / ".htaccess").write_text(ht, encoding="utf-8")
        print("updated .htaccess cache rules")
    else:
        print("WARN could not locate htaccess end anchor")
else:
    print("WARN cache marker missing")

print("done")
