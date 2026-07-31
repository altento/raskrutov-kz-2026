# -*- coding: utf-8 -*-
"""Safety: mobile menu section must not inherit desktop --height padding."""
from pathlib import Path
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
path = Path("site_mirror/index.html")
html = path.read_text(encoding="utf-8")
MENU_ID = "8ab6b296523d428eb73b4f55d760af8a"
# Mottor escapes leading digit in CSS as #\\38 ...
safe = (
    f"@media (max-width:500px){{"
    f"#{MENU_ID}.blk_section,"
    f".blk_section[data-id=\"s-{MENU_ID}\"]{{padding-top:100px!important;}}"
    f"}}"
)
green_re = re.compile(
    r'(<style\s+data-green-zone=["\']1["\'][^>]*>)(.*?)(</style>)',
    re.S | re.I,
)
m = green_re.search(html)
if not m:
    raise SystemExit("green zone style missing")
body = m.group(2)
if "padding-top:100px!important" in body:
    print("safety already present")
else:
    body2 = body.rstrip() + safe
    html = html[: m.start()] + m.group(1) + body2 + m.group(3) + html[m.end() :]
    tmp = path.with_suffix(".html.tmp")
    tmp.write_bytes(html.encode("utf-8"))
    tmp.replace(path)
    print("added mobile menu padding safety")
