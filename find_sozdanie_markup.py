#!/usr/bin/env python3
import re
from pathlib import Path

html = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html").read_text(encoding="utf-8", errors="ignore")
pos = html.find("Создание сайтов")
ctx = html[pos - 200 : pos + 200]
Path(r"C:\Users\user\Projects\раскрутов\site_mirror\sozdanie_raw.txt").write_text(ctx, encoding="utf-8")

# find all occurrences
for i, m in enumerate(re.finditer("Создание сайтов", html)):
    p = m.start()
    snippet = html[p - 100 : p + 150]
    tag = re.search(r"<[^>]{0,40}$", html[p - 100 : p])
    Path(r"C:\Users\user\Projects\раскрутов\site_mirror\sozdanie_occ.txt").write_text(
        f"occ {i} pos {p}\n{snippet}\n", encoding="utf-8"
    )

# List all strings containing Лендинг in homepage
for word in ["Лендинги", "Корпоративные", "многостранич", "Создание сайтов", "SEO-продвижение", "AEO"]:
    idx = html.find(word)
    if idx >= 0:
        sn = html[idx - 80 : idx + len(word) + 80]
        print("===", word, idx, "===")
        print(sn.replace("\n", " ")[:200])
