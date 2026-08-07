#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix mobile H1 on hub/seo geo pages: show city H1, hide Mottor duplicate."""
from __future__ import annotations

from pathlib import Path

ROOT = Path("site_mirror")
MARKER = 'data-rk-mobile-h1-fix="1"'
STYLE = (
    f'<style {MARKER}>'
    "@media (max-width:500px){"
    '.blk.blk_text[data-id="b-aa35398c497a44568f98430c09d8d76c"] '
    "h1.blk-data.blk-data--pc{"
    "display:block!important;"
    "font-size:20px!important;"
    "line-height:140%!important"
    "}"
    '.blk.blk_text[data-id="b-aa35398c497a44568f98430c09d8d76c"] '
    ".blk-data.blk-data--mobile370.heading--rank-1{"
    "display:none!important"
    "}"
    "}"
    "</style>"
)
TITLE_BLOCK = "aa35398c497a44568f98430c09d8d76c"


def city_pages() -> list[Path]:
    pages: list[Path] = []
    hub = ROOT / "web-studiya"
    for d in sorted(hub.iterdir()):
        if not d.is_dir():
            continue
        # skip service dirs
        if d.name in {
            "sozdanie-saitov",
            "seo-prodvizhenie",
            "dizayn",
            "kontekstnaya-reklama",
            "lidogeneratsiya",
            "podderzhka-saytov",
            "digital-konsalting",
            "aeo-prodvizhenie",
        }:
            continue
        idx = d / "index.html"
        if idx.exists():
            pages.append(idx)
    seo = hub / "seo-prodvizhenie"
    for d in sorted(seo.iterdir()):
        if d.is_dir() and (d / "index.html").exists():
            pages.append(d / "index.html")
    return pages


def patch(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    if TITLE_BLOCK not in html:
        return "skip-no-block"
    if MARKER in html:
        # refresh style content
        import re

        html2, n = re.subn(
            rf"<style {MARKER}>.*?</style>",
            STYLE,
            html,
            count=1,
            flags=re.S,
        )
        if n:
            path.write_text(html2, encoding="utf-8")
            return "updated"
        return "present"
    # insert after green-zone style if present, else before </head>
    needle = 'data-green-zone="1"'
    if needle in html:
        i = html.find(needle)
        end = html.find("</style>", i)
        if end == -1:
            return "fail-green"
        end += len("</style>")
        html = html[:end] + STYLE + html[end:]
    else:
        html = html.replace("</head>", STYLE + "</head>", 1)
    path.write_text(html, encoding="utf-8")
    return "patched"


def main():
    pages = city_pages()
    stats: dict[str, int] = {}
    for p in pages:
        r = patch(p)
        stats[r] = stats.get(r, 0) + 1
        print(f"{r}\t{p.as_posix()}")
    print("TOTAL", len(pages), stats)


if __name__ == "__main__":
    main()
