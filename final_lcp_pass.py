#!/usr/bin/env python3
"""Final LCP pass: preload bundle JS (fetch starts immediately, defer execution
unchanged) and raise hero image preload priority via fetchpriority=high."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

BUNDLE_JS_RE = re.compile(
    r'<script src="((?:\.\./)*assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.js)"([^>]*?) defer></script>'
)
HERO_PRELOAD_RE = re.compile(r'<link rel="preload" as="image" href="([^"]+)"/?>')

js_pre = hero_prio = files = 0
for f in M.rglob("*.html"):
    if "assets" in f.relative_to(M).parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    orig = html

    mjs = BUNDLE_JS_RE.search(html)
    if mjs and f'rel="preload" as="script"' not in html:
        head_end = html.find("</head>")
        if head_end != -1:
            html = (
                html[:head_end]
                + f'<link rel="preload" as="script" href="{mjs.group(1)}"/>'
                + html[head_end:]
            )
            js_pre += 1

    def prio_repl(m: re.Match) -> str:
        global hero_prio
        if "fetchpriority" in m.group(0):
            return m.group(0)
        hero_prio += 1
        return f'<link rel="preload" as="image" href="{m.group(1)}" fetchpriority="high"/>'
    html = HERO_PRELOAD_RE.sub(prio_repl, html, count=1)

    if html != orig:
        f.write_text(html, encoding="utf-8")
        files += 1

print(f"files changed: {files}, js preloads: {js_pre}, hero fetchpriority: {hero_prio}")
