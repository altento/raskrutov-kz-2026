# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
pages = sorted((ROOT / "pages").glob("*.html"))
out = []
for p in pages:
    t = p.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'<link rel="canonical" href="([^"]+)"', t)
    out.append(f"{p.name}\t{m.group(1) if m else '???'}")
print("\n".join(out))
