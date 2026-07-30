# -*- coding: utf-8 -*-
"""List distinct residual mangled values containing assets+host mixes."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
mapping = json.loads(Path("url_mapping.json").read_text(encoding="utf-8"))

PAGES = [ROOT / "index.html"] + [ROOT / b / "index.html" for b in mapping.values()]
vals = {}
for p in PAGES:
    t = p.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'"((?:\.\./)*assets/[^"]*(?:https?://|www\.|t\.me|instagram|youtube|whatsapp|tiktok)[^"]*)"', t):
        v = m.group(1)
        norm = re.sub(r'^(\.\./)+', '../', v)
        vals.setdefault(norm, 0)
        vals[norm] += 1

for v, n in sorted(vals.items(), key=lambda x: -x[1]):
    print(f"x{n:5d}  {v[:130]}")
