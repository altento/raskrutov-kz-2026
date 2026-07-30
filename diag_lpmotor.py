# -*- coding: utf-8 -*-
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
mapping = json.loads(Path("url_mapping.json").read_text(encoding="utf-8"))

vals = {}
for b in mapping.values():
    t = (ROOT / b / "index.html").read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'data-page-link="(?:\.\./)*assets/s239948\.lpmotortest\.com/([^"]+)"', t):
        vals.setdefault(m.group(1), set()).add(b)

print("distinct lpmotortest dpl targets:", len(vals))
for v, pages in sorted(vals.items()):
    local = ROOT / "assets/s239948.lpmotortest.com" / v
    print(f"{len(pages):3d}p  {v[:80]:82s} local={'Y' if local.exists() else 'N'}")

# also href (not only dpl)?
cnt_href = 0
for b in mapping.values():
    t = (ROOT / b / "index.html").read_text(encoding="utf-8", errors="ignore")
    cnt_href += len(re.findall(r'href="(?:\.\./)*assets/s239948\.lpmotortest\.com/', t))
print("href lpmotortest count:", cnt_href)
