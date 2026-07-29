# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")

for fname in ["pages/web-studiya_sozdanie-saitov.html", "pages/faq.html", "pages/kontakty.html"]:
    t = (ROOT / fname).read_text(encoding="utf-8")
    print("=====", fname)
    for m in re.finditer(r".{100}index\.htmlindex\.html.{60}", t, re.S):
        ctx = " ".join(m.group(0).split())
        print("  ...", ctx[:230])
    print()
