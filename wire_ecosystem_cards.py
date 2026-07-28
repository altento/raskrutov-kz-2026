# -*- coding: utf-8 -*-
"""Wire ecosystem pillar cards and finish homepage links."""
import json
import re
from pathlib import Path

MIRROR = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
INDEX = MIRROR / "index.html"
BASE = "https://raskrutov.kz"

# block_id -> (local_page, url_path)
BLOCK_WIRE = {
    "6545927d594044008dc224b8adab87ef": ("pages/crm.html", "/crm"),
}

# Text near card -> url (for reachGoals image wrappers in ecosystem section)
TEXT_WIRE = {
    "CRM": "/crm",
    "CRM и автоматизация": "/crm",
    "Raskrutov CRM": "/crm",
    "Академия": "/akademiya",
    "Raskrutov Academy": "/akademiya",
    "R-Builder": "/r-builder",
    "Raskrutov Studio": "/web-studiya",
    "Студия": "/web-studiya",
    "Партнёры": "/partneram",
    "Партнёрам": "/partneram",
}


def url_to_local(url_path: str) -> str:
    if url_path == "/":
        return "index.html"
    if url_path == "/web-studiya/aeo-prodvizhenie":
        return "pages/web-studiya_aeo-geo-prodvizhenie.html"
    return f"pages/{url_path.strip('/').replace('/', '_')}.html"


def wire_block_by_id(html: str, block_id: str, local: str, url_path: str) -> tuple[str, int]:
    n = 0
    # image wrapper reachGoals -> linkRedirect
    old_onclick = f"msJsWrapper(event,'{block_id}','reachGoals')"
    new_onclick = f"msJsWrapper(event,'{block_id}','linkRedirect')"
    if old_onclick in html:
        html = html.replace(old_onclick, new_onclick)
        n += 1
    # set data-page-link on elements in block vicinity
    idx = html.find(f'id="{block_id}"')
    if idx < 0:
        idx = html.find(f"data-id=\"b-{block_id}\"")
    if idx >= 0:
        end = html.find("</div>", idx + 500)
        end = html.find("blk_box", idx + 200)
        if end < 0:
            end = idx + 4000
        chunk = html[idx:end]
        chunk2 = chunk
        chunk2 = re.sub(
            r'data-page-link=""',
            f'data-page-link="{local}" data-original-url="{BASE}{url_path}"',
            chunk2,
            count=2,
        )
        if chunk2 != chunk:
            html = html[:idx] + chunk2 + html[end:]
            n += 1
    return html, n


def wire_reach_goals_in_section(html: str, section_id: str) -> tuple[str, int]:
    n = 0
    start = html.find(section_id)
    if start < 0:
        return html, 0
    # section ends at next blk_section at same level - approximate
    end = html.find('blk_class="section"', start + 100)
    if end < 0:
        end = start + 80000
    section = html[start:end]

    for text, url_path in TEXT_WIRE.items():
        local = url_to_local(url_path)
        pos = section.find(text)
        if pos < 0:
            continue
        window = section[max(0, pos - 1500): pos + 2500]
        if f'data-page-link="{local}"' in window:
            continue
        # fix reachGoals in window
        new_window = window
        new_window = new_window.replace("'reachGoals')", "'linkRedirect')")
        new_window = re.sub(
            r'data-page-link=""',
            f'data-page-link="{local}" data-original-url="{BASE}{url_path}"',
            new_window,
            count=3,
        )
        if new_window != window:
            section = section[: max(0, pos - 1500)] + new_window + section[pos + 2500 - 1500:]
            n += 1

    if n:
        html = html[:start] + section + html[end:]
    return html, n


def add_crm_to_local_nav(html: str) -> tuple[str, bool]:
    marker = "<!-- LOCAL-SUBPAGE-LINKS -->"
    if marker in html:
        nav_chunk = html[html.find(marker) : html.find(marker) + 8000]
        if "pages/crm.html" in nav_chunk:
            return html, False
    else:
        return html, False
    insert = f'  <a href="pages/crm.html" data-original-url="{BASE}/crm"></a>\n'
    html = html.replace(marker + "\n", marker + "\n" + insert, 1)
    return html, True


def main():
    html = INDEX.read_text(encoding="utf-8")
    total = 0

    for block_id, (local, url_path) in BLOCK_WIRE.items():
        html, n = wire_block_by_id(html, block_id, local, url_path)
        total += n
        print(f"block {block_id}: {n} changes")

    html, n = wire_reach_goals_in_section(html, "9466bf80aa894ca9b20b37b4d9409cc1")
    total += n
    print(f"ecosystem section: {n} text-based wires")

    html, added = add_crm_to_local_nav(html)
    if added:
        total += 1
        print("added crm to LOCAL-SUBPAGE-LINKS")

    INDEX.write_text(html, encoding="utf-8")
    print(f"Total changes: {total}")


if __name__ == "__main__":
    main()
