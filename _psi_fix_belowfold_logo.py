# -*- coding: utf-8 -*-
"""Restore lazy on below-fold logo variant (not header)."""
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
path = Path("site_mirror/index.html")
html = path.read_text(encoding="utf-8")
old = (
    'f__q_80191472.webp" title="" alt="Raskrutov - экосистема цифрового роста бизнеса (8)" '
    'loading="eager" decoding="async" width="422" height="98">'
)
new = (
    'f__q_80191472.webp" title="" alt="Raskrutov - экосистема цифрового роста бизнеса (8)" '
    'loading="lazy" decoding="async" width="422" height="98">'
)
if old in html:
    path.write_text(html.replace(old, new, 1), encoding="utf-8")
    print("restored lazy on below-fold logo")
else:
    print("pattern not found / already ok")
