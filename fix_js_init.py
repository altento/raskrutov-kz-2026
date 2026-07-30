# -*- coding: utf-8 -*-
"""Rollback the JS-breaking perf pass:
1. remove `defer` from public.bundle script tag (restore sync execution order:
   bundle BEFORE inline block-registration scripts, as the builder requires)
2. unwrap our DOMContentLoaded wrappers around inline scripts
3. fix .home-sub-link touch-target CSS: negative vertical margins cancel the
   baseline shift (text vs bullet dots) while keeping the 24px touch area
"""
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
PAGES = [p for p in ROOT.rglob("*.html") if "assets" not in p.relative_to(ROOT).parts]

DEFER_RE = re.compile(
    r'(<script src="(?:\.\./)*assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.js"[^>]*?) defer(></script>)'
)
WRAP_RE = re.compile(
    r"<script type=\"text/javascript\">document\.addEventListener\('DOMContentLoaded',function\(\)\{(.*?)\}\);</script>",
    re.DOTALL,
)
OLD_CSS = ".home-sub-link{display:inline-block;padding:8px 6px 8px 0;line-height:1.7;}"
NEW_CSS = ".home-sub-link{display:inline-block;padding:8px 6px 8px 0;margin:-8px 0;}"

stats = {"defer_removed": 0, "unwrapped": 0, "css_fixed": 0, "files": 0}

for page in PAGES:
    html = page.read_text(encoding="utf-8", errors="ignore")
    orig = html

    html, n = DEFER_RE.subn(r"\1\2", html)
    stats["defer_removed"] += n

    html, n = WRAP_RE.subn(lambda m: '<script type="text/javascript">' + m.group(1) + "</script>", html)
    stats["unwrapped"] += n

    if OLD_CSS in html:
        html = html.replace(OLD_CSS, NEW_CSS)
        stats["css_fixed"] += 1

    if html != orig:
        for attempt in range(5):
            try:
                page.write_text(html, encoding="utf-8")
                break
            except OSError:
                time.sleep(1.5)
        stats["files"] += 1

print(stats)
