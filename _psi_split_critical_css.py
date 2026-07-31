# -*- coding: utf-8 -*-
"""Split home-all-blocks into critical (above-fold) + deferred rest.

Critical = hero section subtree IDs + menus + mockups + all matching @media rules.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("site_mirror")
CSS_DIR = ROOT / "assets" / "css"
HTML = ROOT / "index.html"
SRC = CSS_DIR / "home-all-blocks.v2.css"

HERO = "9466bf80aa894ca9b20b37b4d9409cc1"
MENU_DESK = "c79b353fa8844473a07a1c2ced4acba2"
MENU_MOB = "8ab6b296523d428eb73b4f55d760af8a"
NEXT_AFTER_HERO = "2d69865c"  # key directions


def collect_hero_ids(html: str) -> set[str]:
    h0 = html.find(f'id="{HERO}"')
    h1 = html.find(f'id="{NEXT_AFTER_HERO}')
    if h0 < 0:
        raise SystemExit("hero missing")
    chunk = html[h0 : h1 if h1 > h0 else h0 + 80000]
    ids = set(re.findall(r'\bid="([0-9a-f]{32})"', chunk))
    ids.add(HERO)
    ids.add(MENU_DESK)
    ids.add(MENU_MOB)
    # also menus themselves may be outside hero chunk
    for mid in (MENU_DESK, MENU_MOB):
        m = re.search(rf'id="{mid}"', html)
        if m:
            ids.update(re.findall(r'\bid="([0-9a-f]{32})"', html[m.start() : m.start() + 20000]))
    return ids


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


def rule_is_critical(rule: str, ids: set[str]) -> bool:
    # always keep mockup system + menu shell + layout
    if re.search(r"mockup|ms-menu|site_wrapper|blk_section_inner|is_fixed|section-image|section_image", rule, re.I):
        return True
    for i in ids:
        if i in rule:
            return True
        # escaped leading digit form #\30 xxx
        if len(i) == 32 and i[0].isdigit():
            esc = r"\3" + i[0] + " " + i[1:]
            if esc in rule or ("\\" + i[0] in rule and i[1:8] in rule):
                return True
    return False


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    ids = collect_hero_ids(html)
    print("critical ids", len(ids))

    css = SRC.read_text(encoding="utf-8")
    rules = split_rules(css)
    crit, rest = [], []
    for r in rules:
        (crit if rule_is_critical(r, ids) else rest).append(r)

    crit_css = "".join(crit)
    rest_css = "".join(rest)
    crit_path = CSS_DIR / "home-critical.v3.css"
    rest_path = CSS_DIR / "home-deferred.v3.css"
    crit_path.write_text(crit_css, encoding="utf-8")
    rest_path.write_text(rest_css, encoding="utf-8")
    print(f"rules total={len(rules)} critical={len(crit)} deferred={len(rest)}")
    print(f"critical {len(crit_css)/1024:.1f} KiB")
    print(f"deferred {len(rest_css)/1024:.1f} KiB")

    # Ensure HTML wiring (idempotent)
    # Remove old all-blocks
    html = re.sub(
        r'<link rel="preload" as="style" href="assets/css/home-all-blocks[^"]*"\s*/?>\s*',
        "",
        html,
    )
    html = re.sub(
        r'<link rel="stylesheet" href="assets/css/home-all-blocks[^"]*"\s*/?>\s*',
        "",
        html,
    )
    # Reset v3 link injections then re-add
    html = re.sub(
        r'<link rel="preload" as="style" href="assets/css/home-critical\.v3\.css"\s*/?>\s*',
        "",
        html,
    )
    html = re.sub(
        r'<link rel="stylesheet" href="assets/css/home-critical\.v3\.css"\s*/?>\s*',
        "",
        html,
    )
    # Remove any previous deferred wiring (preload OR media=print)
    html = re.sub(
        r'<link rel="preload" href="assets/css/home-deferred\.v3\.css" as="style" onload="this\.onload=null;this\.rel=\'stylesheet\'">\s*'
        r'<noscript><link rel="stylesheet" href="assets/css/home-deferred\.v3\.css"></noscript>\s*',
        "",
        html,
    )
    html = re.sub(
        r'<link rel="stylesheet" href="assets/css/home-deferred\.v3\.css" media="print" onload="this\.media=\'all\'">\s*'
        r'<noscript><link rel="stylesheet" href="assets/css/home-deferred\.v3\.css"></noscript>\s*',
        "",
        html,
    )

    html = re.sub(
        r"(<head[^>]*>)",
        r'\1<link rel="preload" as="style" href="assets/css/home-critical.v3.css"/>',
        html,
        count=1,
    )
    # media=print: fetch at low priority so it does NOT steal LCP bandwidth
    # (unlike rel=preload as=style which is high priority).
    inject = (
        '<link rel="stylesheet" href="assets/css/home-critical.v3.css"/>'
        '<link rel="stylesheet" href="assets/css/home-deferred.v3.css" media="print" '
        'onload="this.media=\'all\'">'
        '<noscript><link rel="stylesheet" href="assets/css/home-deferred.v3.css"></noscript>\n'
    )
    html = html.replace("</head>", inject + "</head>", 1)

    # Drop normal font preload if still present
    html = re.sub(
        r'<link rel="preload" href="assets/m-files\.cdn1\.cc/web/user/fonts/montserrat/montserrat_normal\.woff"[^>]*>\s*',
        "",
        html,
        count=1,
    )

    tmp = HTML.with_suffix(".html.tmp")
    tmp.write_bytes(html.encode("utf-8"))
    tmp.replace(HTML)
    print("ok")


if __name__ == "__main__":
    main()
