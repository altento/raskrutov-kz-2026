# -*- coding: utf-8 -*-
"""Conservative HTML minification: strip HTML comments outside
script/style/pre/textarea and collapse runs of blank lines."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

PROTECT = re.compile(r"<(script|style|pre|textarea)\b.*?</\1>", re.S | re.I)
COMMENT = re.compile(r"<!--(?!\[if).*?-->", re.S)
BLANKS = re.compile(r"\n[ \t]*\n([ \t]*\n)+")

total_saved = 0
changed = 0
for page in PAGES:
    html = page.read_text(encoding="utf-8")
    orig_len = len(html)

    protected = []
    def stash(m):
        protected.append(m.group(0))
        return f"\x00PROT{len(protected)-1}\x00"

    work = PROTECT.sub(stash, html)
    work = COMMENT.sub("", work)
    work = BLANKS.sub("\n\n", work)

    def unstash(m):
        return protected[int(m.group(1))]

    work = re.sub(r"\x00PROT(\d+)\x00", unstash, work)

    if work != html:
        import time
        for attempt in range(6):
            try:
                page.write_text(work, encoding="utf-8")
                break
            except OSError:
                time.sleep(1.5)
        else:
            print(f"SKIP (locked): {page}")
            continue
        saved = orig_len - len(work)
        total_saved += saved
        changed += 1

print(f"changed {changed} pages, saved {total_saved/1024:.0f} KB raw")
