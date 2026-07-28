#!/usr/bin/env python3
import re
from pathlib import Path

html = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html").read_text(encoding="utf-8", errors="ignore")
pos = html.find("Создание сайтов")
section = html[pos - 8000 : pos + 25000]

# Extract structured info: each blk_text or ms-active-string with nearby linkRedirect
entries = []
for m in re.finditer(r"ms-active-string[^>]*>(.*?)</span>", section, re.S):
    text = re.sub(r"\s+", " ", m.group(1)).strip()
    if not text or text == "⟶":
        continue
    ctx = section[max(0, m.start() - 1200) : m.end() + 400]
    links = re.findall(r'data-page-link="([^"]*)"', ctx)
    redirects = "linkRedirect" in ctx
    onclick_img = "linkRedirect" in ctx and "m-image__wrapper" in ctx
    entries.append(
        {
            "text": text,
            "links": links[-3:] if links else [],
            "has_redirect": redirects,
            "onclick_image": onclick_img,
        }
    )

out = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\sozdanie_block_entries.json")
import json

out.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), "entries")
for e in entries:
    print(e["text"][:60], "| links:", e["links"], "| redirect:", e["has_redirect"])
