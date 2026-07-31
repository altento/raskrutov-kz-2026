# -*- coding: utf-8 -*-
from pathlib import Path
import re

html = Path("site_mirror/index.html").read_text(encoding="utf-8", errors="replace")
head_end = html.find("</head>")
head = html[: head_end + 7]
print("HEAD bytes", len(head.encode()))
print("BODY starts at", head_end)
print("hero section id pos", html.find('id="9466bf80aa894ca9b20b37b4d9409cc1"'))
print("first blk_section pos", html.find("blk_section"))

for pat in [
    "lead-forms",
    "breadcrumbs",
    "font-display",
    "application/ld+json",
    "wa.me",
    "WhatsApp",
    "ym(",
    "mc.yandex",
]:
    print(pat, html.count(pat))

print("blk_section", html.count("blk_section"))
print("msf-form", html.count("msf-form"))
print("data-lead-form", html.count("data-lead-form"))
print("Ключевые направления", html.count("Ключевые направления"))

# style tag sizes
sizes = []
for m in re.finditer(r"<style([^>]*)>(.*?)</style>", html, re.S | re.I):
    attrs, body = m.group(1), m.group(2)
    sid = re.search(r'id=["\']([^"\']+)', attrs)
    sizes.append((len(body.encode()), (sid.group(1) if sid else attrs.strip()[:40]), m.start()))
sizes.sort(reverse=True)
print("top style blocks:")
for sz, sid, pos in sizes[:12]:
    print(f"  {sz/1024:.1f} KiB @ {pos} id/attrs={sid!r}")

# media rules for hero image
for token in ["6eea3ed3", "__q_39174817", "27e940bf"]:
    print(token, "count", html.count(token))

# font-face display
ff = re.findall(r"@font-face\s*\{[^}]{0,400}\}", html, re.I)
print("@font-face in html", len(ff))
swap = sum(1 for x in ff if "font-display" in x.lower())
print("with font-display", swap)

# sample font-face
if ff:
    print("sample:", ff[0][:220].replace("\n", " "))

ht = Path("site_mirror/.htaccess").read_text(encoding="utf-8", errors="replace")
print("--- .htaccess excerpt ---")
print(ht[:1500])
