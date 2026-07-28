#!/usr/bin/env python3
import re
from pathlib import Path

html = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html").read_text(encoding="utf-8", errors="ignore")

# Extract all ms-active-string texts in order from studio section (between Raskrutov Studio and Raskrutov Academy)
start = html.find("Raskrutov Studio")
end = html.find("Raskrutov Academy", start)
section = html[start:end] if start != -1 and end != -1 else html

items = []
for m in re.finditer(
    r'(data-page-link="([^"]*)")?.*?ms-active-string[^>]*>(.*?)</span>',
    section,
    re.S,
):
    text = re.sub(r"\s+", " ", m.group(3)).strip()
    link = m.group(2) or ""
    if text and text != "⟶":
        items.append((text, link))

Path(r"C:\Users\user\Projects\раскрутов\site_mirror\studio_text_links.txt").write_text(
    "\n".join(f"{t}\t{l}" for t, l in items),
    encoding="utf-8",
)
print("items", len(items))
for t, l in items[:30]:
    print(repr(t), "->", l)
