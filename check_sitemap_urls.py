#!/usr/bin/env python3
import csv
import json
import ssl
import urllib.request
from pathlib import Path

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

text = Path(r"c:\Users\user\Downloads\САЙТ RASKRUTOV.KZ  СТРАНИЦЫ И ХОД ВЫПОЛНЕНИЯ - Карта сайта.csv").read_text(encoding="utf-8-sig")
lines = [line for line in text.splitlines() if line.strip() and not line.startswith("ID,")]
rows = list(csv.reader(lines))
if rows and not rows[0][0].strip():
    rows[0][0] = "1"
rows = [row for row in rows if len(row) >= 5 and row[4].startswith("/")]

results = []
for row in rows:
    path = row[4]
    url = "https://raskrutov.kz" + path
    status = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20, context=CTX) as resp:
            status = resp.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except Exception:
        status = "ERR"
    results.append(
        {
            "id": row[0],
            "url": path,
            "title": row[3] if len(row) > 3 else "",
            "status": status,
            "plan_status": row[11] if len(row) > 11 else "",
        }
    )

available = [item for item in results if item["status"] == 200]
missing = [item for item in results if item["status"] != 200]

out = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\sitemap_availability.json")
out.write_text(json.dumps({"available": available, "missing": missing}, ensure_ascii=False, indent=2), encoding="utf-8")

print("Available:", len(available))
for item in available:
    print(" OK", item["url"], "-", item["title"])
print("\nMissing published pages:")
for item in missing:
    if item.get("plan_status") == "Опубликована":
        print(" ", item["status"], item["url"], "-", item["title"])
