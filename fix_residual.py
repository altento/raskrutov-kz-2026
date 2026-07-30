# -*- coding: utf-8 -*-
"""Fix nested-garbage attribute values (social buttons, GTM noscript)."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
mapping = json.loads(Path("url_mapping.json").read_text(encoding="utf-8"))
PAGES = [ROOT / "index.html"] + [ROOT / b / "index.html" for b in mapping.values()]

RULES = [
    (re.compile(r'"(?:\.\./)*assets/www\.\.\./assets/www\.instagram\.com/[^"\s]*"'), '"https://www.instagram.com/raskrutov"'),
    (re.compile(r'"(?:\.\./)*assets/www\.instagram\.com/[^"\s]*"'), '"https://www.instagram.com/raskrutov"'),
    (re.compile(r'"(?:\.\./)*assets/https://t\.me/Raskrutov_web"'), '"https://t.me/Raskrutov_web"'),
    (re.compile(r'"(?:\.\./)*assets/https://www\.youtube\.com/@raskrutov-kz"'), '"https://www.youtube.com/@raskrutov-kz"'),
    (re.compile(r'"(?:\.\./)*assets/www\.googletagmanager\.com/ns__q_id_([\w-]+)\.html"'), r'"https://www.googletagmanager.com/ns.html?id=\1"'),
]

tot = [0] * len(RULES)
for p in PAGES:
    t = p.read_text(encoding="utf-8")
    for i, (rx, rep) in enumerate(RULES):
        t, n = rx.subn(rep, t)
        tot[i] += n
    p.write_text(t, encoding="utf-8")
print("fixed per rule:", tot, " total:", sum(tot))
