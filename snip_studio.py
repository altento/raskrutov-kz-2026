#!/usr/bin/env python3
import re
from pathlib import Path

html = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html").read_text(encoding="utf-8", errors="ignore")
start = html.find("Создание сайтов") - 500
end = html.find("SEO-продвижение", start) + 2000
chunk = html[start:end]
# find linkRedirect blocks
blocks = list(re.finditer(r'<div class="m-button-wrapper[^"]*"[^>]*act="linkRedirect"[^>]*data-page-link="([^"]*)"[^>]*>', chunk))
Path(r"C:\Users\user\Projects\раскрутов\site_mirror\studio_section_snip.txt").write_text(
    f"Found {len(blocks)} linkRedirect in studio section\n\n" +
    "\n---\n".join(f"link={m.group(1)}\n{chunk[m.start():m.start()+800]}" for m in blocks[:10]),
    encoding="utf-8",
)
# Also find text-only items (Лендинги etc)
for word in ["Создание сайтов", "Лендинги", "Корпоративные", "Многостранич", "SEO-продвижение", "AEO-продвижение", "О нас", "Команда"]:
    for m in re.finditer(re.escape(word), chunk, re.I):
        ctx = chunk[max(0,m.start()-300):m.end()+300]
        has_link = "data-page-link" in ctx
        has_redirect = "linkRedirect" in ctx
        print(word, "link=", has_link, "redirect=", has_redirect)
