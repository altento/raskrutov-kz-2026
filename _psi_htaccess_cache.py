# -*- coding: utf-8 -*-
"""Add Cache-Control for versioned static assets; keep HTML non-immutable."""
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
path = Path("site_mirror/.htaccess")
text = path.read_text(encoding="utf-8")
marker = "# Cache-Control for hashed/static assets (PSI / repeat views)"
block = f"""
{marker}
<IfModule mod_headers.c>
  <FilesMatch "\\.(css|js|mjs|webp|png|jpe?g|gif|svg|woff2?|ttf|ico)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  <FilesMatch "\\.(html|htm)$">
    Header set Cache-Control "public, max-age=0, must-revalidate"
  </FilesMatch>
</IfModule>
"""
if marker in text:
    print("Cache-Control block already present")
else:
    # insert after mod_expires block if present, else append
    anchor = "</IfModule>\n\n# Compression for text resources"
    if anchor in text:
        text = text.replace(anchor, "</IfModule>\n" + block + "\n# Compression for text resources", 1)
    else:
        text = text.rstrip() + "\n" + block
    path.write_text(text, encoding="utf-8")
    print("added Cache-Control block to .htaccess")
