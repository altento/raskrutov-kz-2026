# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
html = Path("site_mirror/index.html").read_text(encoding="utf-8")

# H1 class font-84
for cls in ["font-84", "font-montserrat", "Montserrat", "Inter", "Open Sans"]:
    print(cls, html.count(cls))

# find CSS rule for .font-84
for m in re.finditer(r"\.font-84\s*\{[^}]+\}", html):
    print("rule", m.group(0)[:300])
    break

# nearby hero text block fonts
i = html.find('id="9466bf80aa894ca9b20b37b4d9409cc1"')
chunk = html[i : i + 8000]
fonts = re.findall(r"font-family:\s*([^;\"']+)", chunk)
print("inline fonts in hero chunk", fonts[:20])
print("font- classes in hero", re.findall(r"font-\d+", chunk)[:20])

# where __q_39174817 is referenced
j = html.find("__q_39174817")
print("variant ctx:", html[max(0, j - 250) : j + 80])
