#!/usr/bin/env python3
import re
from pathlib import Path

html = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html").read_text(encoding="utf-8", errors="ignore")

# Section with service cards - between "01" and "Raskrutov Academy" or similar
start = html.find('font-84"><span style="color: rgba(58,58,58,1);">Создание сайтов')
if start == -1:
    start = html.find("Создание сайтов") - 5000
end = html.find("Raskrutov Academy", start)
section = html[start:end] if end > start else html[start : start + 80000]

cards = []
for m in re.finditer(
    r'<h3 class="blk-data[^"]*"><span[^>]*>([^<]+)</span></h3>.*?<ul>(.*?)</ul>',
    section,
    re.S,
):
    title = m.group(1).strip()
    ul = m.group(2)
    items = re.findall(r"<li>([^<]+)</li>", ul)
    # find arrow link in following 2000 chars
    tail = section[m.end() : m.end() + 2500]
    arrow_links = re.findall(r'data-page-link="([^"]+)"', tail)
    cards.append({"title": title, "items": items, "arrow_link": arrow_links[0] if arrow_links else ""})

import json

Path(r"C:\Users\user\Projects\раскрутов\site_mirror\home_service_cards.json").write_text(
    json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8"
)
for c in cards:
    print(c["title"], "->", c["arrow_link"])
    print("  ", c["items"])
