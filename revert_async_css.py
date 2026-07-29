#!/usr/bin/env python3
"""Revert async CSS back to blocking stylesheet (async caused CLS=1 on mobile)."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

ASYNC_RE = re.compile(
    r'<link href="((?:\.\./)*assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.css)" '
    r'rel="preload" as="style" onload="this\.onload=null;this\.rel=\'stylesheet\'"/?>(?:\s*'
    r"<noscript><link [^>]*></noscript>)?"
)

changed = 0
for f in M.rglob("*.html"):
    if "assets" in f.relative_to(M).parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    new = ASYNC_RE.sub(lambda m: f'<link href="{m.group(1)}" rel="stylesheet"/>', html)
    if new != html:
        f.write_text(new, encoding="utf-8")
        changed += 1

print(f"Reverted async CSS on {changed} pages")
