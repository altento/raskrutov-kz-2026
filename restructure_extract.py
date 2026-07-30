# -*- coding: utf-8 -*-
"""Extract canonical->beautiful path mapping for all pages. Validation only."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")

mapping = {}
for p in sorted((ROOT / "pages").glob("*.html")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'<link rel="canonical" href="https://raskrutov\.kz/([^"]*)"', t)
    if not m:
        print("NO CANONICAL:", p.name)
        continue
    path = m.group(1).strip("/")
    mapping[p.name] = path

print("pages mapped:", len(mapping))
dups = {}
for name, path in mapping.items():
    dups.setdefault(path, []).append(name)
for path, names in dups.items():
    if len(names) > 1:
        print("DUP PATH:", path, names)

# depth histogram
from collections import Counter
depths = Counter(p.count("/") + 1 if p else 0 for p in mapping.values())
print("depth histogram:", dict(depths))

# sample
for name in ["crm.html", "faq.html", "web-studiya_sozdanie-saitov_landing.html", "akademiya_obuchenie-seo-aeo.html", "consent.html", "regulation.html", "keysy.html", "kontakty.html"]:
    print(f"  {name:50s} -> /{mapping.get(name)}")

Path("url_mapping.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved url_mapping.json")
