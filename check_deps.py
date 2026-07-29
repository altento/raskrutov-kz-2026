#!/usr/bin/env python3
"""Check what follows the bundle script, inline style sizes, hero background."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
html = (M / "index.html").read_text(encoding="utf-8", errors="ignore")

# position of bundle script vs end of file
m = re.search(r'<script src="assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*"[^>]*></script>', html)
if m:
    tail = html[m.end():]
    print(f"script ends at {m.end()}, tail after it: {len(tail)} chars")
    print("tail preview:", re.sub(r"\s+", " ", tail[:400]))
    # any inline scripts after?
    print("inline <script> after bundle:", len(re.findall(r"<script(?![^>]*src)", tail)))

# inline style blocks
styles = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL)
total = sum(len(s) for s in styles)
print(f"\ninline <style> blocks: {len(styles)}, total {total/1024:.1f} KB")
for s in styles[:6]:
    print("  block preview:", re.sub(r"\s+", " ", s[:120]))

# hero background image (first m-block-wrapper style)
mm = re.search(r'm-block-wrapper[^>]*style="[^"]*url\(([^)]+)\)', html)
if not mm:
    mm = re.search(r'url\(([^)]*(?:webp|png|jpg)[^)]*)\)', html)
print("\nfirst bg url:", mm.group(1) if mm else "none")

# first few img tags with src
for im in re.finditer(r'<img[^>]*src="([^"]+)"', html):
    print("img:", im.group(1)[:100])
    if im.start() > 20000:
        break
