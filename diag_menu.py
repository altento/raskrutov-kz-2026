# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t = Path("site_mirror/index.html").read_text(encoding="utf-8")

# find a mega-menu item markup (Лендинги as menu entry, not block title)
i = t.find('data-page-link="pages/web-studiya_sozdanie-saitov_landing.html"')
print("FOUND at:", i)
print(t[max(0, i - 600):i + 250].replace("\n", " ")[:850])
print()
print("=== how many anchors vs bare divs carry data-page-link ===")
anchors = len(re.findall(r"<a\b[^>]*data-page-link", t))
divs = len(re.findall(r"<(?:div|li|span|td)\b[^>]*data-page-link", t))
print("anchors:", anchors, "non-anchor elements:", divs)

# check whether any script references data-page-link handling
for m in re.finditer(r"page-link", t):
    s = t.rfind("<script", 0, m.start())
    e = t.find("</script>", m.start())
    if s >= 0 and e > m.start():
        seg = t[s:e]
        if "querySelector" in seg or "addEventListener" in seg or "onclick" in seg:
            print("SCRIPT HANDLER FOUND:", seg[:400])
            break
else:
    print("no inline JS handler for data-page-link found")
