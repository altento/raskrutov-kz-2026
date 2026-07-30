# -*- coding: utf-8 -*-
"""Extract linkRedirect / removeUrlModifiers implementations and compare orig vs current."""
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
    print(f"===== {label}: linkRedirect definition")
    for m in re.finditer(r"linkRedirect\s*:\s*function[^{]*\{", t):
        # capture balanced braces
        i = m.end() - 1
        depth = 0
        j = i
        while j < len(t):
            if t[j] == "{":
                depth += 1
            elif t[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = t[m.start():j + 1]
        print(body[:1200])
        print("---")
    print(f"===== {label}: removeUrlModifiers")
    for m in re.finditer(r"removeUrlModifiers\s*:\s*function[^{]*\{", t):
        i = m.end() - 1
        depth = 0
        j = i
        while j < len(t):
            if t[j] == "{":
                depth += 1
            elif t[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        print(t[m.start():j + 1][:800])
        print("---")
    print()
