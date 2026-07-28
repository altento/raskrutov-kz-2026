#!/usr/bin/env python3
import re
import ssl
import urllib.request
from urllib.error import HTTPError, URLError

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

BASE = "https://raskrutov.kz"
PATHS = [
    "/web-studiya/sozdanie-saitov/landing",
    "/web-studiya/sozdanie-saitov/mnogostranichnye-sayty",
    "/web-studiya/sozdanie-saitov/korporativnyy-sayt",
    "/web-studiya/sozdanie-saitov/internet-magazin",
    "/web-studiya/seo-prodvizhenie",
    "/web-studiya/seo-prodvizhenie/google",
    "/web-studiya/seo-prodvizhenie/yandex",
    "/web-studiya/aeo-prodvizhenie",
    "/o-kompanii/o-nas",
    "/o-kompanii/komanda",
    "/web-studiya/dizayn/neyming",
    "/partneram/franshiza",
    "/r-builder/chto-takoe-r-builder",
    "/crm",
    "/web-studiya/sozdanie-saitov",
]

results = []
for path in PATHS:
    url = BASE + path
    row = {"path": path, "status": None, "title": "", "error": ""}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
            raw = resp.read(200000).decode("utf-8", "ignore")
            row["status"] = resp.status
            m = re.search(r"<title>(.*?)</title>", raw, re.I | re.S)
            if m:
                row["title"] = re.sub(r"\s+", " ", m.group(1)).strip()[:100]
    except HTTPError as exc:
        row["status"] = exc.code
        row["error"] = str(exc)
    except URLError as exc:
        row["error"] = str(exc.reason)
    except Exception as exc:
        row["error"] = str(exc)
    results.append(row)

for row in results:
    if row["status"] == 200:
        print(f"OK   {row['path']} | {row['title']}")
    elif row["status"]:
        print(f"HTTP {row['status']} {row['path']}")
    else:
        print(f"FAIL {row['path']} | {row['error']}")
