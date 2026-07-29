# -*- coding: utf-8 -*-
"""Fix 'Вопросы' menu item in the fixed header: it has an empty scrollTo('')
onclick instead of a link. Wrap it in an anchor to the FAQ page, mirroring the
sibling menu items' markup. Applied to all pages (fixed menu is shared)."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

PAT = re.compile(
    r"<div class=\"ms-menu__item ms-menu__item-7\" onclick=\"return msJsWrapper\(event,'([a-f0-9]+)','scrollTo\(\\'\\'\)'\);\">(\s*<span class=\"ms-active-string\">Вопросы</span>\s*)</div>"
)

total = 0
other_empty = {}
for page in PAGES:
    html = page.read_text(encoding="utf-8")
    rel = "pages/faq.html" if page.parent == ROOT else "faq.html"

    def repl(m):
        global total
        total += 1
        sec = m.group(1)
        span = m.group(2).strip()
        return (
            f'<a href="{rel}" title="" onclick="return msJsWrapper(event,\'{sec}\',\'hideMobileMenu()\');">'
            f' <div class="ms-menu__item ms-menu__item-7"> {span} </div> </a>'
        )

    html2, n = PAT.subn(repl, html)
    if n:
        page.write_text(html2, encoding="utf-8")

    # other empty scrollTo menu items anywhere?
    leftovers = len(re.findall(r"scrollTo\(\\'\\'\)", html2))
    if leftovers:
        other_empty[page.name] = leftovers

print("fixed 'Вопросы' items:", total)
print("pages with other empty scrollTo:", other_empty if other_empty else "none")
