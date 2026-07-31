# -*- coding: utf-8 -*-
"""Low-risk homepage LCP helpers. Does not touch Mottor public.bundle."""
from pathlib import Path
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = Path("site_mirror/index.html")
html = path.read_text(encoding="utf-8")
orig = html

# 1) Drop non-critical font preloads (hero H1 uses Montserrat 700).
# Keep Montserrat; remove Inter + Open Sans preloads that compete with LCP image.
drop_fonts = [
    '<link rel="preload" href="assets/m-files.cdn1.cc/web/user/fonts/inter/inter_normal.woff" as="font" type="font/woff" crossorigin>\n',
    '<link rel="preload" href="assets/m-files.cdn1.cc/web/user/fonts/inter/inter_bold.woff" as="font" type="font/woff" crossorigin>\n',
    '<link rel="preload" href="assets/m-files.cdn1.cc/web/user/fonts/open_sans/open_sans_normal.woff" as="font" type="font/woff" crossorigin>\n',
]
removed = 0
for tag in drop_fonts:
    if tag in html:
        html = html.replace(tag, "", 1)
        removed += 1
    else:
        alt = tag.rstrip("\n")
        if alt in html:
            html = html.replace(alt, "", 1)
            removed += 1
print("removed font preloads:", removed)

# 2) Hero phone mockup (above-fold, NOT LCP): eager + dims, no fetchpriority=high
phone_old = (
    '<img src="assets/m-files.cdn1.cc/lpfile/2/7/e/27e940bfca13c46588cbb867b1d4c3d6/'
    '-/resize/1000/f__q_80115761.webp" title="/" alt="/" loading="lazy" decoding="async">'
)
phone_new = (
    '<img src="assets/m-files.cdn1.cc/lpfile/2/7/e/27e940bfca13c46588cbb867b1d4c3d6/'
    '-/resize/1000/f__q_80115761.webp" title="/" alt="/" width="294" height="643" '
    'loading="eager" decoding="async">'
)
if phone_old in html:
    html = html.replace(phone_old, phone_new, 1)
    print("phone attrs: updated")
else:
    # already patched or slightly different
    m = re.search(
        r'<img src="assets/m-files\.cdn1\.cc/lpfile/2/7/e/27e940bf[^"]+"[^>]*>',
        html,
    )
    print("phone attrs: exact match missing; found=", bool(m), m.group(0)[:180] if m else "")

# 3) Header logos (two menu copies): remove lazy, set dims if missing
logo_re = re.compile(
    r'(<img src="assets/m-files\.cdn1\.cc/lpfile/8/1/a/81a3fe2ab76d8a7d4df2ea1900ce0265/'
    r'[^"]+"[^>]*?)(loading="lazy"\s*)?([^>]*>)'
)

def fix_logo(m: re.Match) -> str:
    start, lazy, end = m.group(1), m.group(2) or "", m.group(3)
    tag = start + end
    if 'loading="' not in tag:
        tag = tag[:-1] + ' loading="eager" decoding="async">'
    else:
        tag = tag.replace('loading="lazy"', 'loading="eager"')
    if "width=" not in tag:
        tag = tag[:-1] + ' width="422" height="98">'
    return tag

html2, nlogo = logo_re.subn(fix_logo, html)
print("logo tags touched:", nlogo)
html = html2

# 4) Confirm LCP preload still present once
preload_lcp = (
    '<link rel="preload" as="image" '
    'href="assets/m-files.cdn1.cc/lpfile/6/e/e/6eea3ed3de3e5cbe118d06eb148fe963.webp" '
    'fetchpriority="high"/>'
)
print("lcp preload present:", preload_lcp in html)
print("remaining font preloads:", html.count('as="font"'))

if html == orig:
    print("NO CHANGES")
else:
    path.write_text(html, encoding="utf-8")
    print("wrote", path, "delta bytes", len(html) - len(orig))
