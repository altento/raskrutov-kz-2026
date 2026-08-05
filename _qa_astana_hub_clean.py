# -*- coding: utf-8 -*-
from pathlib import Path
import re
import json

p = Path("site_mirror/web-studiya/astana/index-clean.html")
t = p.read_text(encoding="utf-8")

h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S)
titles = re.findall(r"<title>(.*?)</title>", t, re.S)
canons = re.findall(r'rel="canonical" href="([^"]+)"', t)
desc = re.findall(r'name="description" content="([^"]+)"', t)
links = sorted(set(re.findall(r'href="(/[^"#?]*)"', t)))
service_paths = [
    "/web-studiya/",
    "/web-studiya/sozdanie-saitov/",
    "/web-studiya/dizayn/",
    "/web-studiya/seo-prodvizhenie/",
    "/web-studiya/aeo-prodvizhenie/",
    "/web-studiya/kontekstnaya-reklama/",
    "/web-studiya/lidogeneratsiya/",
    "/web-studiya/podderzhka-saytov/",
    "/web-studiya/digital-konsalting/",
    "/keysy/",
]
missing = []
for sp in service_paths:
    rel = Path("site_mirror") / sp.strip("/") / "index.html"
    if not rel.is_file():
        missing.append(sp)

out = {
    "bytes": p.stat().st_size,
    "h1_count": len(h1s),
    "h1": h1s,
    "title": titles[0] if titles else None,
    "description": desc[0] if desc else None,
    "canonical": canons[0] if canons else None,
    "forms": t.count("data-lead-form"),
    "faq_details": t.count("<details>"),
    "has_public_bundle": "public.bundle" in t,
    "has_lpmotor": "lpmotor" in t.lower(),
    "has_rk_hub": "rk-hub-city" in t,
    "asset_depth_ok": "../../assets/" in t and "../assets/" not in t.replace("../../assets/", ""),
    "tel": "tel:+77000216900" in t,
    "wa": "wa.me/77000216900" in t,
    "jsonld_types": sorted(set(re.findall(r'"@type":\s*"([^"]+)"', t))),
    "internal_links_sample": links[:40],
    "service_paths_missing_on_disk": missing,
    "astana_office_claim": bool(re.search(r"офис.{0,40}Астан", t, re.I)),
}
print(json.dumps(out, ensure_ascii=False, indent=2))
