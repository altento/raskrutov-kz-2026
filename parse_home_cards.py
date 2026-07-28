#!/usr/bin/env python3
import re
from pathlib import Path

html = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html").read_text(encoding="utf-8", errors="ignore")

# studio services section - find m-card blocks with numbers 01, 02...
cards = []
for m in re.finditer(r'm-card[^>]*>.*?(?=m-card[^>]*>|$)', html, re.S):
    block = m.group(0)
    if len(block) > 50000:
        continue
    if re.search(r'0[1-9]|Создание сайтов|SEO|AEO|Лендинг', block, re.I):
        title = "?"
        tm = re.search(r'ms-active-string[^>]*>([^<]{3,80})<', block)
        if tm:
            title = re.sub(r'\s+', ' ', tm.group(1)).strip()
        links = re.findall(r'data-page-link="([^"]*)"', block)
        texts = re.findall(r'ms-active-string[^>]*>([^<]+)<', block)
        texts = [re.sub(r'\s+', ' ', t).strip() for t in texts if t.strip() and t.strip() != '⟶']
        cards.append({"title_guess": title, "links": links, "texts": texts[:15], "len": len(block)})

out = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\home_cards.json")
import json
out.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"cards: {len(cards)}")
for c in cards:
    print(c["texts"][:6], "->", c["links"])
