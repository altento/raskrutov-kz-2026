# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
html = Path("site_mirror/index.html").read_text(encoding="utf-8")

print("=== STYLE TAGS ===")
for m in re.finditer(r"<style([^>]*)>(.*?)</style>", html, re.S | re.I):
    attrs, body = m.group(1), m.group(2)
    sid = re.search(r'\bid=["\']([^"\']+)', attrs)
    data = re.search(r"\bdata-[\w-]+=", attrs)
    label = sid.group(1) if sid else (attrs.strip()[:60] or "(no id)")
    print(f"{len(body)/1024:8.1f} KiB  @{m.start():8d}  {label}")

print("\n=== SCRIPT SRC ===")
for m in re.finditer(r'<script[^>]+src=["\']([^"\']+)', html, re.I):
    print(m.group(1)[:120], "defer" if "defer" in m.group(0) else "", "async" if "async" in m.group(0) else "")

print("\n=== SECTION IDS / H2 near sections ===")
# section blocks with ids
secs = list(re.finditer(
    r'<div[^>]*blk_class="section"[^>]*id="([0-9a-f]{32})"[^>]*>',
    html,
    re.I,
))
print("section count", len(secs))
for m in secs[:40]:
    chunk = html[m.start() : m.start() + 2500]
    h = re.search(r"<h[12][^>]*>(.*?)</h[12]>", chunk, re.S | re.I)
    title = re.sub(r"<[^>]+>", "", h.group(1)).strip()[:80] if h else "(no h1/h2 in first 2.5k)"
    print(f"{m.group(1)[:8]}… @{m.start()}  {title}")

print("\n=== IMG loading stats ===")
lazy = len(re.findall(r'loading="lazy"', html))
eager = len(re.findall(r'loading="eager"', html))
imgs = len(re.findall(r"<img\b", html, re.I))
print("img", imgs, "lazy", lazy, "eager", eager)

# phone / belowfold logo
print("belowfold logo eager?", 'f__q_80191472.webp" title="" alt="Raskrutov' in html and 'loading="eager"' in html[html.find("f__q_80191472") : html.find("f__q_80191472") + 300])
