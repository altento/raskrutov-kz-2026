#!/usr/bin/env python3
"""Validate all injected JSON-LD blocks: JSON parse, node types, FAQ counts."""
import json
import re
from collections import Counter
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
BLOCK_RE = re.compile(r'<script type="application/ld\+json" data-schema="raskrutov">\s*(.*?)\s*</script>', re.DOTALL)

bad = []
types_counter: Counter = Counter()
faq_total = 0
pages = 0

for f in sorted(M.rglob("*.html")):
    if "assets" in f.relative_to(M).parts:
        continue
    pages += 1
    html = f.read_text(encoding="utf-8", errors="ignore")
    blocks = BLOCK_RE.findall(html)
    if len(blocks) != 1:
        bad.append(f"{f.name}: {len(blocks)} blocks")
        continue
    try:
        data = json.loads(blocks[0])
    except json.JSONDecodeError as e:
        bad.append(f"{f.name}: JSON error {e}")
        continue
    for n in data["@graph"]:
        types_counter[n["@type"]] += 1
        if n["@type"] == "FAQPage":
            faq_total += len(n["mainEntity"])

print(f"pages: {pages}, invalid: {len(bad)}")
for b in bad[:10]:
    print(" ", b)
print(f"\nnode types across site: {dict(types_counter)}")
print(f"total FAQ questions marked: {faq_total}")

# spot check: breadcrumb chain of a deep page + a service page graph
deep = M / "pages" / "web-studiya_sozdanie-saitov_landing.html"
data = json.loads(BLOCK_RE.findall(deep.read_text(encoding="utf-8"))[0])
print(f"\n{deep.name} graph: {[n['@type'] for n in data['@graph']]}")
bc = next(n for n in data["@graph"] if n["@type"] == "BreadcrumbList")
print("breadcrumbs:")
for it in bc["itemListElement"]:
    print(f"  {it['position']}. {it['name']} -> {it['item']}")
svc = next((n for n in data["@graph"] if n["@type"] == "Service"), None)
if svc:
    print("service:", svc["name"][:80])

faq_page = M / "pages" / "faq_seo.html"
data = json.loads(BLOCK_RE.findall(faq_page.read_text(encoding="utf-8"))[0])
faq = next((n for n in data["@graph"] if n["@type"] == "FAQPage"), None)
if faq:
    print(f"\nfaq_seo.html questions: {len(faq['mainEntity'])}")
    for q in faq["mainEntity"][:3]:
        print("  Q:", q["name"][:90])
        print("  A:", q["acceptedAnswer"]["text"][:110])
