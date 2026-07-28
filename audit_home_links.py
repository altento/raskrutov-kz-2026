#!/usr/bin/env python3
import re
from pathlib import Path

index = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html").read_text(encoding="utf-8", errors="ignore")
out = []
for match in re.finditer(r'data-page-link="([^"]+)"', index):
    chunk = index[max(0, match.start() - 400) : match.end() + 400]
    if any(token in chunk for token in ("Создание сайтов", "Лендинг", "SEO", "О нас", "Команда", "web-studiya", "sozdanie", "01", "02", "03")):
        label_match = re.search(r"ms-active-string[^>]*>(.*?)<", chunk, re.S)
        label = re.sub(r"\s+", " ", label_match.group(1)).strip() if label_match else "?"
        out.append(f"{match.group(1)}\t{label}")

Path(r"C:\Users\user\Projects\раскрутов\site_mirror\home_links_audit.txt").write_text("\n".join(out), encoding="utf-8")
