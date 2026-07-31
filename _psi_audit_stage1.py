#!/usr/bin/env python3
"""Stage 1 PageSpeed audit for homepage — read-only."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
HOME = ROOT / "site_mirror" / "index.html"
html = HOME.read_text(encoding="utf-8", errors="replace")
print("=== FILE ===")
print("path", HOME)
print("bytes", HOME.stat().st_size, "chars", len(html))

print("\n=== HEAD / CRITICAL RESOURCES ===")
head = html.split("</head>", 1)[0] if "</head>" in html else html[:50000]
preloads = re.findall(r'<link[^>]+rel=["\']preload["\'][^>]*>', head, re.I)
print("preloads", len(preloads))
for p in preloads:
    print(" ", re.sub(r"\s+", " ", p)[:220])
stylesheets = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', html, re.I)
print("stylesheets", len(stylesheets))
for s in stylesheets:
    print(" ", re.sub(r"\s+", " ", s)[:220])
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>', html, re.I)
print("script srcs:")
for s in scripts:
    print(" ", s)
inline_styles = len(re.findall(r"<style\b", html, re.I))
inline_scripts = len(re.findall(r"<script\b(?![^>]*\bsrc=)", html, re.I))
print("inline style tags", inline_styles, "inline scripts(no src)", inline_scripts)

print("\n=== HERO / SECTION IMAGE ===")
# Mottor section-image backgrounds
for m in re.finditer(
    r'id="(section_image_[a-f0-9]+)"[^>]*style="([^"]*)"',
    html,
    re.I,
):
    sid, style = m.group(1), m.group(2)
    if "background" in style or "url(" in style:
        print(sid, style[:240])

# first section with section_image_container
idx = html.find('class="section_image_container"')
print("first section_image_container at", idx)
if idx > 0:
    chunk = html[max(0, idx - 400) : idx + 800]
    print("context:", re.sub(r"\s+", " ", chunk)[:500])

# hero section id from prior work
HERO = "9466bf80aa894ca9b20b37b4d9409cc1"
print("\nhero section present", HERO in html)
# background urls near hero
hero_pos = html.find(HERO)
if hero_pos >= 0:
    region = html[hero_pos : hero_pos + 15000]
    urls = re.findall(r"url\(([^)]+)\)", region)
    print("urls near hero section (first 15):")
    for u in urls[:15]:
        print(" ", u[:160])
    imgs = re.findall(r"<img\b[^>]*>", region, re.I)
    print("img tags in hero region", len(imgs))
    for im in imgs[:8]:
        print(" ", re.sub(r"\s+", " ", im)[:220])

print("\n=== IMAGE 27e940bf (PSI flagged) ===")
flag = "27e940bfca13c46588cbb867b1d4c3d6"
pos = 0
n = 0
while True:
    i = html.find(flag, pos)
    if i < 0:
        break
    n += 1
    start = html.rfind("<", 0, i)
    end = html.find(">", i)
    tag = html[start : end + 1] if start >= 0 and end > start else ""
    # surrounding section id
    sec = html.rfind('data-id="s-', 0, i)
    sec_id = html[sec : sec + 50] if sec >= 0 else "?"
    print(f"occurrence {n} at {i}")
    print("  tag", re.sub(r"\s+", " ", tag)[:260])
    print("  near", re.sub(r"\s+", " ", sec_id))
    # estimate position in document %
    print("  doc%", round(100 * i / len(html), 1))
    pos = i + len(flag)
print("total occurrences", n)

print("\n=== PRELOADED HERO IMAGE 6eea3ed3 ===")
print("6eea3ed3 present", "6eea3ed3de3e5cbe118d06eb148fe963" in html)
print("preload 6eea", '6eea3ed3de3e5cbe118d06eb148fe963.webp"' in html or "6eea3ed3de3e5cbe118d06eb148fe963.webp" in html)

print("\n=== FONT PRELOADS ===")
for p in preloads:
    if "font" in p.lower() or "woff" in p.lower():
        print(" ", re.sub(r"\s+", " ", p)[:200])

print("\n=== HIDDEN / DUPLICATE SIGNALS ===")
print("display:none count", len(re.findall(r"display\s*:\s*none", html, re.I)))
print("is_hidden", html.count('"is_hidden":1'))
print("aria-hidden=true", html.count('aria-hidden="true"'))
print("hidden attr", len(re.findall(r"\shidden\b", html)))
print("section count", len(re.findall(r'class="[^"]*blk_section', html)))
print("h1 count", len(re.findall(r"<h1\b", html, re.I)))
print("form count", len(re.findall(r"<form\b", html, re.I)))
print("data-lead-form", html.count("data-lead-form"))
print("msf-form", html.count("msf-form"))
print("popup/wind", html.count("wind_container"), html.count("section_popup"))

# adapter hidden blocks
hidden = re.findall(r'"([a-f0-9]{32})"\s*:\s*\{\s*"is_hidden"\s*:\s*1', html)
print("adapter is_hidden ids", len(set(hidden)))

print("\n=== THIRD PARTY ===")
for host in [
    "googletagmanager",
    "google-analytics",
    "yandex",
    "vk.com",
    "kinescope",
    "vimeo",
    "youtube",
    "whatsapp",
    "supabase",
]:
    print(host, html.lower().count(host))

print("\n=== IMG LAZY ABOVE-FOLD CANDIDATES (first 80k) ===")
chunk = html[:80000]
for im in re.findall(r"<img\b[^>]*>", chunk, re.I)[:20]:
    lazy = "lazy" in im
    eager = "eager" in im
    fp = "fetchpriority" in im.lower()
    src_m = re.search(r'src=["\']([^"\']+)["\']', im)
    src = src_m.group(1) if src_m else "?"
    wh = re.search(r'width=["\'](\d+)["\'][^>]*height=["\'](\d+)["\']', im)
    print(
        f" lazy={lazy} eager={eager} fp={fp} wh={wh.groups() if wh else None} src={src[-90:]}"
    )
