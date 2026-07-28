#!/usr/bin/env python3
import csv
import re
from pathlib import Path

INDEX = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html")
SITEMAP = Path(r"C:\Users\user\Downloads\САЙТ RASKRUTOV.KZ  СТРАНИЦЫ И ХОД ВЫПОЛНЕНИЯ - Карта сайта.csv")
OUT = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\studio_links_report.txt")

html = INDEX.read_text(encoding="utf-8", errors="ignore")
lines = []

for token in ["Создание сайтов", "Лендинги", "Корпоративные", "многостранич", "SEO-продвижение", "AEO", "О нас", "Команда"]:
    pos = 0
    while True:
        pos = html.find(token, pos)
        if pos == -1:
            break
        chunk = html[max(0, pos - 1500) : pos + 1500]
        links = re.findall(r'data-page-link="([^"]*)"', chunk)
        labels = re.findall(r"ms-active-string[^>]*>(.*?)<", chunk, re.S)
        labels = [re.sub(r"\s+", " ", x).strip() for x in labels]
        lines.append(f"\n=== {token} @ {pos} ===")
        lines.append(f"  data-page-link nearby: {links}")
        lines.append(f"  labels nearby: {labels[:8]}")
        pos += len(token)

lines.append("\n=== ALL homepage data-page-link with labels ===")
for match in re.finditer(r'data-page-link="([^"]+)"', html):
    start = max(0, match.start() - 400)
    end = min(len(html), match.end() + 400)
    chunk = html[start:end]
    label = "?"
    m = re.search(r"ms-active-string[^>]*>(.*?)<", chunk, re.S)
    if m:
        label = re.sub(r"\s+", " ", m.group(1)).strip()
    if "web-studiya" in match.group(1) or "o-kompanii" in match.group(1) or label not in ("?", "⟶"):
        lines.append(f"{match.group(1)}\t{label}")

lines.append("\n=== Sitemap URLs (web-studiya + o-kompanii subpaths) ===")
with SITEMAP.open(encoding="utf-8-sig", newline="") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        url = (row.get("URL") or row.get("url") or "").strip()
        status = (row.get("Статус") or row.get("Status") or "").strip()
        if not url:
            continue
        if "/web-studiya/" in url or "/o-kompanii/" in url:
            lines.append(f"{status}\t{url}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("Wrote", OUT)
