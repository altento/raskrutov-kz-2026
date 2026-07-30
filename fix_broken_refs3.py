# -*- coding: utf-8 -*-
"""Final reference fix pass:
1. exact social/messenger mangled values -> correct external URLs
2. external hosts trapped under assets/<host>/ -> https://<host>/
3. trailing garbage on rewritten externals (/index.html repeats, .js.js)
4. quoted 'index.html/index.html<word>' garbage -> https://raskrutov.kz/
5. pages-dir files: bare assets/m-files.cdn1.cc -> ../assets/m-files.cdn1.cc
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

EXACT = {
    "assets/www.instagram.com/index.html": "https://www.instagram.com/raskrutov",
    "assets/assets/www.instagram.com/index.html": "https://www.instagram.com/raskrutov",
}
HOSTS = ["www.youtube.com", "img.youtube.com", "t.me", "player.kinescope.io", "player.vimeo.com"]
TRAIL = re.compile(r'(https://(?:www\.youtube\.com|img\.youtube\.com|t\.me|player\.kinescope\.io|player\.vimeo\.com)/[^"\'\s]*?)(?:(?:/index\.html)+|\.js\.js)(["\'\s])')
GARBAGE_Q = re.compile(r'"(?:\.\./)*(?:assets/)+(?:\.\./)*index\.html/index\.html[\w/.-]*"')
BARE_MF = re.compile(r'(?<![\w./-])assets/m-files\.cdn1\.cc')

stats = dict(exact=0, hosts=0, trail=0, garbage=0, mf=0)
for page in PAGES:
    html = page.read_text(encoding="utf-8")
    for bad, good in sorted(EXACT.items(), key=lambda kv: -len(kv[0])):
        stats["exact"] += html.count(bad)
        html = html.replace(bad, good)
    for h in HOSTS:
        pat = "assets/" + h + "/"
        stats["hosts"] += html.count(pat)
        html = html.replace(pat, "https://" + h + "/")
    html, n = TRAIL.subn(r"\1\2", html)
    stats["trail"] += n
    html, n = GARBAGE_Q.subn('"https://raskrutov.kz/"', html)
    stats["garbage"] += n
    if page.parent != ROOT:
        html, n = BARE_MF.subn("../assets/m-files.cdn1.cc", html)
        stats["mf"] += n
    page.write_text(html, encoding="utf-8")

print("stats:", stats)
