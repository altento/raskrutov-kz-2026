# -*- coding: utf-8 -*-
"""Split sozdanie-popup-menu into tiny blocking menu + deferred rest."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("site_mirror")
CSS_DIR = ROOT / "assets" / "css"
SRC = CSS_DIR / "sozdanie-popup-menu.v1.css"
CITIES = [
    "almaty", "astana", "shymkent", "aktau", "aktobe", "atyrau", "karaganda",
    "kokshetau", "kostanay", "kyzylorda", "pavlodar", "petropavlovsk", "semey",
    "taldykorgan", "taraz", "turkestan", "uralsk", "ust-kamenogorsk",
]

MENU_NEEDLES = (
    "ms-menu",
    "menu-bar",
    "menu_bar",
    "is_fixed",
    "burger",
    "hamburger",
    "site_wrapper",
    "blk_section_inner",
    "popup",  # careful - might pull everything
)


def split_rules(css: str) -> list[str]:
    rules: list[str] = []
    i, n = 0, len(css)
    while i < n:
        while i < n and css[i].isspace():
            i += 1
        if i >= n:
            break
        start = i
        while i < n and css[i] != "{":
            i += 1
        if i >= n:
            break
        depth = 0
        while i < n:
            if css[i] == "{":
                depth += 1
            elif css[i] == "}":
                depth -= 1
                if depth == 0:
                    i += 1
                    rules.append(css[start:i].strip())
                    break
            i += 1
    return rules


def is_menu_rule(rule: str) -> bool:
    # Prefer explicit menu shell; avoid dumping all popup content into blocking
    if re.search(r"ms-menu|menu-bar|menu_bar|hamburger|burger|is_fixed|nav-menu|m-menu", rule, re.I):
        return True
    return False


def main() -> int:
    css = SRC.read_text(encoding="utf-8")
    # strip banner
    body = re.sub(r"^/\*.*?\*/\s*", "", css, count=1, flags=re.S)
    rules = split_rules(body)
    menu, rest = [], []
    for r in rules:
        (menu if is_menu_rule(r) else rest).append(r)
    lite = "/* sozdanie menu lite — blocking */\n" + "".join(menu)
    heavy = "/* sozdanie popup menu heavy — deferred */\n" + "".join(rest)
    (CSS_DIR / "sozdanie-menu-lite.v1.css").write_text(lite, encoding="utf-8")
    (CSS_DIR / "sozdanie-popup-menu-deferred.v1.css").write_text(heavy, encoding="utf-8")
    print(f"rules {len(rules)} menu-lite {len(lite.encode())/1024:.1f} KiB deferred-popup {len(heavy.encode())/1024:.1f} KiB")

    pages = [ROOT / "web-studiya/sozdanie-saitov/index.html"] + [
        ROOT / "web-studiya/sozdanie-saitov" / c / "index.html" for c in CITIES
    ]
    for path in pages:
        html = path.read_text(encoding="utf-8")
        depth = len(path.relative_to(ROOT).parts) - 1
        prefix = "../" * depth + "assets/css/"
        # replace blocking popup-menu with lite; defer heavy (+ keep old file unused)
        html = html.replace(
            f'{prefix}sozdanie-popup-menu.v1.css',
            f'{prefix}sozdanie-menu-lite.v1.css',
        )
        # ensure deferred heavy linked
        if "sozdanie-popup-menu-deferred.v1.css" not in html:
            inject = (
                f'<link rel="stylesheet" href="{prefix}sozdanie-popup-menu-deferred.v1.css" media="print" onload="this.media=\'all\'">'
                f'<noscript><link rel="stylesheet" href="{prefix}sozdanie-popup-menu-deferred.v1.css"></noscript>'
            )
            html = html.replace(
                f'sozdanie-extra.v1.css"></noscript>',
                f'sozdanie-extra.v1.css"></noscript>{inject}',
                1,
            )
            if "sozdanie-popup-menu-deferred.v1.css" not in html:
                html = html.replace("</head>", inject + "</head>", 1)
        # drop preload of old fat popup-menu if still present as preload of lite ok
        path.write_text(html, encoding="utf-8")
        print("wired", path.parent.name if path.parent.name != "sozdanie-saitov" else "parent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
