# -*- coding: utf-8 -*-
"""Fix structural errors found by audit_site.py:
A. Remove duplicate purple fixed menu (92c58db8) from partneram pages
B. Demote extra h1 -> h2 on stub pages (keep first)
C. kontakty.html: promote h2 'Контакты' -> h1
D. consent/regulation: add title, lang, favicon, canonical
E. Remove our duplicate data-schema JSON-LD where an original block exists
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
stats = {}

# ---------- A. remove purple menu section ----------
PURPLE_ID = "92c58db8"

def remove_section(html: str, sid_prefix: str):
    m = re.search(r'<div blk_class="section"[^>]*?id="' + sid_prefix, html)
    if not m:
        return html, False
    start = m.start()
    depth, i = 0, start
    while True:
        mo = re.compile(r"<div\b|</div>").search(html, i)
        if not mo:
            return html, False
        if mo.group(0) == "<div":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end = mo.end()
                # sanity: next meaningful tag must be section open or container close
                nxt = html[end:end + 200].lstrip()
                if not (nxt.startswith("<div") or nxt.startswith("</div>")):
                    return html, False
                return html[:start] + html[end:], True
        i = mo.end()

for p in sorted((ROOT / "pages").glob("partneram*.html")):
    html = p.read_text(encoding="utf-8")
    html2, ok = remove_section(html, PURPLE_ID)
    if ok:
        p.write_text(html2, encoding="utf-8")
        stats.setdefault("purple_menu_removed", []).append(p.name)
    else:
        stats.setdefault("purple_menu_FAILED", []).append(p.name)

# ---------- B. demote extra h1 ----------
for name in ["web-studiya_aeo-geo-prodvizhenie.html",
             "web-studiya_lidogeneratsiya.html",
             "web-studiya_podderzhka-saytov.html"]:
    p = ROOT / "pages" / name
    html = p.read_text(encoding="utf-8")
    hits = list(re.finditer(r"<h1\b[^>]*>.*?</h1>", html, re.S))
    if len(hits) <= 1:
        stats.setdefault("h1_skip", []).append(name)
        continue
    # replace from END to keep offsets valid; skip first occurrence
    for m in reversed(hits[1:]):
        seg = m.group(0)
        seg2 = re.sub(r"^<h1\b", "<h2", seg)
        seg2 = re.sub(r"</h1>$", "</h2>", seg2)
        html = html[:m.start()] + seg2 + html[m.end():]
    p.write_text(html, encoding="utf-8")
    stats.setdefault("h1_demoted", []).append(f"{name} ({len(hits)-1})")

# ---------- C. kontakty h2 -> h1 ----------
p = ROOT / "pages/kontakty.html"
html = p.read_text(encoding="utf-8")
m = re.search(r"<h2\b[^>]*>(?:(?!</h2>).)*?Контакты.*?</h2>", html, re.S)
if m and "<h1" not in html:
    seg = m.group(0)
    seg2 = re.sub(r"^<h2\b", "<h1", seg)
    seg2 = re.sub(r"</h2>$", "</h1>", seg2)
    html = html[:m.start()] + seg2 + html[m.end():]
    p.write_text(html, encoding="utf-8")
    stats["kontakty_h1"] = True

# ---------- D. consent/regulation head fixes ----------
# favicon template from a healthy page
donor = (ROOT / "pages/crm.html").read_text(encoding="utf-8")
fav_links = "\n".join(re.findall(r"<link[^>]*rel=\"icon\"[^>]*>", donor))

TITLES = {
    "consent.html": ("Согласие на обработку персональных данных — Raskrutov", "https://raskrutov.kz/consent"),
    "regulation.html": ("Положение об обработке персональных данных — Raskrutov", "https://raskrutov.kz/regulation"),
}
for fname, (title, canon) in TITLES.items():
    p = ROOT / "pages" / fname
    if not p.exists():
        continue
    html = p.read_text(encoding="utf-8")
    changed = False
    if "<html>" in html and "<html lang=" not in html:
        html = html.replace("<html>", '<html lang="ru">', 1)
        changed = True
    if "<title>" not in html:
        inject = f"<title>{title}</title>\n"
        inject += f'<link rel="canonical" href="{canon}"/>\n'
        if fav_links:
            inject += fav_links + "\n"
        html = html.replace('<meta name="robots" content="noindex"/>',
                            '<meta name="robots" content="noindex"/>\n' + inject, 1)
        if inject not in html:  # fallback: after <head>
            html = re.sub(r"<head>", "<head>\n" + inject, html, count=1)
        changed = True
    if changed:
        p.write_text(html, encoding="utf-8")
        stats.setdefault("legal_fixed", []).append(fname)

# ---------- E. dedupe JSON-LD ----------
PLAIN = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
MINE = re.compile(r'\s*<script type="application/ld\+json" data-schema="raskrutov">.*?</script>', re.S)

for p in [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html")):
    html = p.read_text(encoding="utf-8")
    plain_blocks = list(PLAIN.finditer(html))
    mine_blocks = list(MINE.finditer(html))
    if not (plain_blocks and mine_blocks):
        continue
    # plain block valid?
    try:
        data = json.loads(plain_blocks[0].group(1))
        ok = "@type" in json.dumps(data) or "@graph" in data
    except Exception:
        ok = False
    if ok:
        html2 = MINE.sub("", html, count=1)
        p.write_text(html2, encoding="utf-8")
        stats.setdefault("jsonld_deduped", []).append(p.name)
    else:
        stats.setdefault("jsonld_INVALID_plain", []).append(p.name)

for k, v in stats.items():
    if isinstance(v, list):
        print(f"{k}: {len(v)}")
        for item in v[:20]:
            print("   ", item)
    else:
        print(f"{k}: {v}")
