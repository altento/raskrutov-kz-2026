#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

SITEMAP = Path(r"c:\Users\user\Downloads\САЙТ RASKRUTOV.KZ  СТРАНИЦЫ И ХОД ВЫПОЛНЕНИЯ - Карта сайта.csv")
SEMANTICS = Path(r"c:\Users\user\Downloads\semantika_franshiza_raskrutov_kazakhstan.csv")

text = SITEMAP.read_text(encoding="utf-8-sig")
lines = [line for line in text.splitlines() if line.strip() and not line.startswith("ID,")]
rows = list(csv.reader(lines))
if rows and not rows[0][0].strip():
    rows[0][0] = "1"
rows = [row for row in rows if len(row) >= 5 and row[4].startswith("/")]

mirrored_urls = {
    "/",
    "/web-studiya",
    "/web-studiya/sozdanie-saitov",
    "/web-studiya/dizayn",
    "/web-studiya/aeo-prodvizhenie",
    "/web-studiya/kontekstnaya-reklama",
    "/web-studiya/lidogeneratsiya",
    "/web-studiya/podderzhka-saytov",
    "/web-studiya/digital-konsalting",
    "/akademiya",
    "/r-builder",
    "/partneram",
    "/keysy",
    "/keysy/sayty",
    "/keysy/prodvizhenie",
    "/faq",
    "/o-kompanii",
    "/kontakty",
}

print("SITEMAP pages:", len(rows))
print("Status:", dict(Counter(row[11] for row in rows if len(row) > 11)))
print("Stage:", dict(Counter(row[12] for row in rows if len(row) > 12)))
print("Priority:", dict(Counter(row[6] for row in rows if len(row) > 6)))

in_mirror = sum(1 for row in rows if row[4] in mirrored_urls)
print("Mirrored overlap:", in_mirror, "/", len(rows))

print("\nPublished but missing in mirror:")
for row in rows:
    if len(row) > 11 and row[11] == "Опубликована" and row[4] not in mirrored_urls:
        print(" ", row[4], "-", row[3])

print("\nPlanned P0/P1 missing:")
for row in rows:
    if (
        len(row) > 11
        and row[11] == "Запланировано"
        and row[6] in {"P0", "P1"}
        and row[4] not in mirrored_urls
    ):
        print(" ", row[6], row[4], "-", row[3])

with SEMANTICS.open(encoding="utf-8-sig", newline="") as handle:
    sem_rows = list(csv.reader(handle, delimiter=";"))

header = sem_rows[0]
data = sem_rows[1:]
print("\nSEMANTICS rows:", len(data))
print("Columns:", header)
print("Sources:", dict(Counter(row[2] for row in data if len(row) > 2)))
print("Geo regions:", len(set(row[1] for row in data if len(row) > 1)))
print("Franchise keywords:", sum(1 for row in data if "франшиз" in row[0].lower()))
print("Raskrutov brand keywords:", sum(1 for row in data if "raskrutov" in row[0].lower()))
