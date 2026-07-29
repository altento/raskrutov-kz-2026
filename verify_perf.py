#!/usr/bin/env python3
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
html = (M / "index.html").read_text(encoding="utf-8", errors="ignore")
print("index.html size now:", (M / "index.html").stat().st_size, "bytes")

ff = re.findall(r"@font-face\s*\{[^}]*\}", html)
print(f"@font-face in index.html: {len(ff)}")
with_swap = sum(1 for b in ff if "font-display" in b)
print(f"  with font-display: {with_swap}")
if ff:
    print("  sample:", ff[0][:200])

# sanity: defer + preload + noscript present
print("defer on bundle:", 'public.bundle' in html and ' defer></script>' in html)
print("async css:", 'rel="preload" as="style"' in html)
print("noscript fallback:", "<noscript><link" in html)
print("hero preload:", re.search(r'<link rel="preload" as="image" href="([^"]+)"', html).group(1))
# inline scripts wrapped?
tail = html[html.find(" defer></script>"):]
print("wrapped DOMContentLoaded count:", tail.count("DOMContentLoaded"))
print("unwrapped inline scripts after bundle:", len(re.findall(r'<script type="text/javascript">(?!document\.addEventListener)', tail)))
