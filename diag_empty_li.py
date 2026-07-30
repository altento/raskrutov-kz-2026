# -*- coding: utf-8 -*-
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def git_show(rev):
    return subprocess.run(["git", "show", rev], capture_output=True).stdout.decode("utf-8", errors="replace")

orig = git_show("b7ffe07:site_mirror/pages/web-studiya.html")
cur = Path("site_mirror/web-studiya/index.html").read_text(encoding="utf-8")

for label, t in [("ORIG", orig), ("CUR", cur)]:
    i = t.find("Брендбук")
    seg = t[i:i + 1200]
    print(f"===== {label}: between Брендбук and Логотип")
    j = seg.find("Логотип")
    print(" ".join(seg[:j + 60].split())[:900])
    print()
