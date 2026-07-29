#!/usr/bin/env python3
"""Fix broken favicon references: copy real file to expected path, normalize hrefs."""
import shutil
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
SRC = M / "assets" / "raskrutov.kz" / "favicon__q_1.png"
DST = M / "assets" / "m-files.cdn1.cc" / "lpfile" / "favicon" / "favicon__q_1.png"

DST.parent.mkdir(parents=True, exist_ok=True)
if SRC.exists() and not DST.exists():
    shutil.copy2(SRC, DST)
    print("favicon copied")
else:
    print("copy skipped (src missing or dst exists)")

GOOD_TAIL = "m-files.cdn1.cc/lpfile/favicon/favicon__q_1.png"
BAD_PATTERNS = [
    "../assets/../assets/../index.html/index.htmlfavicon__q_1.png",
    "assets/assets/index.html/index.htmlfavicon__q_1.png",
    "assets/index.html/index.htmlfavicon__q_1.png",
    "../index.html/index.htmlfavicon__q_1.png",
]
fixed = 0
for f in M.rglob("*.html"):
    if "assets" in f.relative_to(M).parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    orig = html
    rel_prefix = "../assets/" if f.parent.name == "pages" else "assets/"
    for bad in BAD_PATTERNS:
        if bad in html:
            html = html.replace(bad, rel_prefix + GOOD_TAIL)
    if html != orig:
        f.write_text(html, encoding="utf-8")
        fixed += 1
print(f"html files fixed: {fixed}")
