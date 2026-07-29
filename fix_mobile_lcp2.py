#!/usr/bin/env python3
"""Mobile LCP fix round 2:
1. Split hero preload into media-scoped variants (mobile gets base crop, desktop gets __q crop)
   -> previously mobile downloaded a ~300KB desktop variant it never displays, delaying the real hero
2. Add <link rel="preload" as="style"> for the CSS bundle -> CSS downloads in parallel with HTML
   instead of waiting for a second roundtrip after HTML parse.
Idempotent.
"""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

HERO_RE = re.compile(
    r'<link rel="preload" as="image" href="([^"]+)" fetchpriority="high"/>'
)
CSS_LINK_RE = re.compile(
    r'<link href="((?:\.\./)*assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.css)" rel="stylesheet"/>'
)

files_changed = 0
hero_split = 0
css_preloads = 0

for f in sorted(M.rglob("*.html")):
    rel = f.relative_to(M)
    if "assets" in rel.parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    orig = html

    # --- 1. media-scoped hero preloads
    if 'media="(max-width: 1000px)"' not in html:
        def split_hero(m):
            global hero_split
            href = m.group(1)
            if "__q_" not in href:
                return m.group(0)  # single variant, keep
            base = re.sub(r"__q_\d+", "", href)
            # only split if the base file actually exists
            full = (f.parent / href).resolve() if href.startswith("../") else (M / href)
            if not (full.parent / base.split("/")[-1]).exists():
                return m.group(0)
            hero_split += 1
            return (
                f'<link rel="preload" as="image" href="{href}" media="(min-width: 1001px)" fetchpriority="high"/>'
                f'<link rel="preload" as="image" href="{base}" media="(max-width: 1000px)" fetchpriority="high"/>'
            )
        html = HERO_RE.sub(split_hero, html, count=1)

    # --- 2. preload the CSS bundle
    if 'rel="preload" as="style"' not in html:
        def add_css_preload(m):
            global css_preloads
            css_preloads += 1
            return f'<link rel="preload" as="style" href="{m.group(1)}"/>' + m.group(0)
        html = CSS_LINK_RE.sub(add_css_preload, html, count=1)

    if html != orig:
        f.write_text(html, encoding="utf-8")
        files_changed += 1

print(f"files changed: {files_changed}")
print(f"hero preloads split (media-scoped): {hero_split}")
print(f"css preloads added: {css_preloads}")

# verify index
html = (M / "index.html").read_text(encoding="utf-8")
head_zone = html[:3000]
print("\nindex.html preload zone:")
for m in re.finditer(r'<link rel="preload"[^>]*>', head_zone):
    print(f"  {m.group(0)[:150]}")
