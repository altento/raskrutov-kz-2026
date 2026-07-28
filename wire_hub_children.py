#!/usr/bin/env python3
"""Inject child-page links into hub pages from sitemap."""
import csv
import re
from collections import defaultdict
from pathlib import Path

MIRROR = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
PAGES = MIRROR / "pages"
CSV_PATH = Path(
    r"C:\Users\user\Downloads\САЙТ RASKRUTOV.KZ  СТРАНИЦЫ И ХОД ВЫПОЛНЕНИЯ - Карта сайта.csv"
)
BASE = "https://raskrutov.kz"
MARKER = "<!-- HUB-CHILD-LINKS -->"

ALIASES = {"/web-studiya/aeo-prodvizhenie": "web-studiya_aeo-geo-prodvizhenie.html"}


def load_sitemap():
    text = CSV_PATH.read_text(encoding="utf-8-sig")
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("ID,")]
    rows = list(csv.reader(lines))
    if rows and not rows[0][0].strip():
        rows[0][0] = "1"
    out = []
    for row in rows:
        if len(row) < 5 or not row[4].startswith("/"):
            continue
        out.append({"url": row[4].strip(), "title": row[3].strip()})
    return out


def url_to_local(url_path: str) -> str:
    if url_path == "/":
        return "index.html"
    if url_path in ALIASES:
        return f"pages/{ALIASES[url_path]}"
    return f"pages/{url_path.strip('/').replace('/', '_')}.html"


def parent_url(url_path: str) -> str | None:
    parts = url_path.strip("/").split("/")
    if len(parts) <= 1:
        return None
    return "/" + "/".join(parts[:-1])


def rel_link(from_rel: str, to_rel: str) -> str:
    import posixpath
    from_p = MIRROR / from_rel
    to_p = MIRROR / to_rel
    return posixpath.relpath(to_p.as_posix(), start=from_p.parent.as_posix())


def main():
    items = load_sitemap()
    children: dict[str, list] = defaultdict(list)
    for item in items:
        p = parent_url(item["url"])
        if p:
            children[p].append(item)

    hubs_wired = 0
    links_added = 0
    for hub_url, kids in sorted(children.items()):
        hub_local = url_to_local(hub_url)
        hub_path = MIRROR / hub_local
        if not hub_path.exists():
            continue
        html = hub_path.read_text(encoding="utf-8", errors="ignore")
        if MARKER in html:
            html = re.sub(rf"{re.escape(MARKER)}.*?</nav>\s*", "", html, flags=re.S)

        block = f'{MARKER}\n<nav class="hub-child-links" aria-label="Подразделы" style="padding:12px;text-align:center">\n'
        for kid in kids:
            kid_local = url_to_local(kid["url"])
            if not (MIRROR / kid_local).exists():
                continue
            href = rel_link(hub_local, kid_local)
            full = BASE + kid["url"]
            block += (
                f'  <a class="home-sub-link" href="{href}" data-page-link="{href}" '
                f'data-original-url="{full}">{kid["title"]}</a>\n'
            )
            links_added += 1
        block += "</nav>\n"
        html = html.replace("</body>", block + "</body>", 1)
        hub_path.write_text(html, encoding="utf-8")
        hubs_wired += 1

    print(f"Hubs wired: {hubs_wired}, child links: {links_added}")


if __name__ == "__main__":
    main()
