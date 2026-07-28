#!/usr/bin/env python3
import re
from pathlib import Path

html = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html").read_text(encoding="utf-8", errors="ignore")
for token in ["Лендинги", "Создание сайтов", "Корпоративные", "многостранич", "SEO-продвижение", "О нас", "Команда"]:
    idx = 0
    hits = []
    while True:
        pos = html.find(token, idx)
        if pos == -1:
            break
        chunk = html[max(0, pos - 300) : pos + 500]
        links = re.findall(r'data-page-link="([^"]*)"', chunk)
        hrefs = re.findall(r'href="([^"]*)"', chunk)
        hits.append((pos, links, hrefs))
        idx = pos + len(token)
    Path(r"C:\Users\user\Projects\раскрутов\site_mirror\token_hits.txt").open("a", encoding="utf-8").write(
        f"\n=== {token} ({len(hits)}) ===\n"
    )
    for pos, links, hrefs in hits[:5]:
        Path(r"C:\Users\user\Projects\раскрутов\site_mirror\token_hits.txt").open("a", encoding="utf-8").write(
            f"pos={pos} links={links} hrefs={hrefs}\n"
        )
