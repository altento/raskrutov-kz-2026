# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

html = Path("site_mirror/index.html").read_text(encoding="utf-8")

print("count 'Вопросы':", html.count("Вопросы"))
for m in re.finditer("Вопросы", html):
    pos = m.start()
    ctx = html[max(0, pos - 800):pos + 200]
    # find nearest link-ish structures
    links = re.findall(r'href="([^"]*)"|data-page-link="([^"]*)"|data-original-url="([^"]*)"', ctx)
    links = [x for tup in links for x in tup if x]
    has_menu = "ms-menu" in ctx
    print(f"--- pos {pos} | menu_ctx={has_menu} | links={links[-4:] if links else 'NONE'}")
