#!/usr/bin/env python3
import re
import ssl
import urllib.request
from pathlib import Path

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

html = urllib.request.urlopen(
    urllib.request.Request("https://raskrutov.kz/", headers={"User-Agent": "Mozilla/5.0"}),
    context=CTX,
    timeout=30,
).read().decode("utf-8", "ignore")

links = sorted(set(re.findall(r'(?:href|data-page-link)="([^"]+)"', html, re.I)))
print("Live homepage relevant links:")
for link in links:
    if any(token in link for token in ("web-studiya", "landing", "sozdanie", "seo", "o-kompanii", "komanda", "crm")):
        print(" ", link)

index = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html").read_text(encoding="utf-8", errors="ignore")
print("\nLocal homepage relevant data-page-link:")
for match in re.finditer(r'data-page-link="([^"]+)"', index):
    chunk = index[max(0, match.start() - 250) : match.end() + 250]
    if any(token in chunk for token in ("Создание сайтов", "Лендинг", "SEO", "О нас", "Команда", "web-studiya", "sozdanie")):
        label = "?"
        label_match = re.search(r"ms-active-string[^>]*>(.*?)<", chunk, re.S)
        if label_match:
            label = re.sub(r"\s+", " ", label_match.group(1)).strip()[:80]
        print(f"  {match.group(1)} <= {label}")
