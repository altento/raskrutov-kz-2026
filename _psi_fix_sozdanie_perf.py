# -*- coding: utf-8 -*-
"""Fix sozdanie perf pass: LCP preload, video lazy, tighter critical CSS, dump leftover styles."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("site_mirror")
CSS_DIR = ROOT / "assets" / "css"
HERO = "1928a98fbb6447c7bb1413d2b56c3267"
HERO_BG = "00e5f3089b7608f6ea110e879c58caea.webp"
OLD_PRELOAD = "a48f76b29b68f1c814592122216e6e86.webp"

CITIES = [
    "almaty", "astana", "shymkent", "aktau", "aktobe", "atyrau", "karaganda",
    "kokshetau", "kostanay", "kyzylorda", "pavlodar", "petropavlovsk", "semey",
    "taldykorgan", "taraz", "turkestan", "uralsk", "ust-kamenogorsk",
]


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


def collect_critical_ids(html: str) -> set[str]:
    ids = {HERO}
    m = re.search(rf'\bid="{HERO}"', html)
    if not m:
        raise SystemExit("hero missing")
    rest = html[m.start() :]
    # end at next blk_section
    end = len(rest)
    for mm in re.finditer(
        r'(?:class="[^"]*blk_section[^"]*"[^>]*id="([0-9a-f]{32})"|id="([0-9a-f]{32})"[^>]*class="[^"]*blk_section)',
        rest,
    ):
        sid = mm.group(1) or mm.group(2)
        if sid != HERO:
            end = mm.start()
            break
    chunk = rest[:end]
    ids.update(re.findall(r'\bid="([0-9a-f]{32})"', chunk))

    # menus only: look for ms-menu / menu-bar containers, take nearby ids (8k window once each)
    menu_roots = []
    for mm in re.finditer(r'id="([0-9a-f]{32})"', html):
        window = html[mm.start() : mm.start() + 400]
        if re.search(r"ms-menu|menu-bar|is_fixed", window, re.I):
            menu_roots.append(mm.group(1))
    for mid in menu_roots[:6]:
        pos = html.find(f'id="{mid}"')
        if pos < 0:
            continue
        ids.update(re.findall(r'\bid="([0-9a-f]{32})"', html[pos : pos + 12000]))
    return ids


def rule_is_critical(rule: str, ids: set[str]) -> bool:
    if re.search(r"mockup|ms-menu|site_wrapper|blk_section_inner|is_fixed|section-image|section_image|menu-bar", rule, re.I):
        return True
    if HERO in rule:
        return True
    for i in ids:
        if i in rule:
            return True
        if len(i) == 32 and i[0].isdigit() and i[1:8] in rule:
            return True
    return False


def resplit_css(html: str) -> None:
    crit = (CSS_DIR / "sozdanie-critical.v1.css").read_text(encoding="utf-8")
    deferred = (CSS_DIR / "sozdanie-deferred.v1.css").read_text(encoding="utf-8")
    combined = re.sub(r"/\* sozdanie (critical|deferred) v1 \*/\s*", "", crit + deferred)
    ids = collect_critical_ids(html)
    print("tight critical ids", len(ids))
    rules = split_rules(combined)
    c, d = [], []
    for r in rules:
        (c if rule_is_critical(r, ids) else d).append(r)
    crit_css = "/* sozdanie critical v1 */\n" + "".join(c)
    def_css = "/* sozdanie deferred v1 */\n" + "".join(d)
    (CSS_DIR / "sozdanie-critical.v1.css").write_text(crit_css, encoding="utf-8")
    (CSS_DIR / "sozdanie-deferred.v1.css").write_text(def_css, encoding="utf-8")
    print(f"re-split critical {len(crit_css.encode())/1024:.1f} KiB deferred {len(def_css.encode())/1024:.1f} KiB")


def fix_video_scripts(html: str) -> str:
    # Remove broken half-transforms
    html = html.replace(' type="text/plain" data-rk-video-src-hold', "")
    html = re.sub(r"\s*data-rk-video-src-hold", "", html)

    def hold(m: re.Match) -> str:
        tag = m.group(0)
        if "data-rk-video-src=" in tag:
            return tag
        sm = re.search(r"""\ssrc=(['"])([^'"]+)\1""", tag)
        if not sm:
            return tag
        src = sm.group(2)
        # Mottor sometimes prefixes absolute URLs with ../../assets/
        if "assets/https://" in src:
            src = src.split("assets/", 1)[1]
        if not any(k in src for k in ("youtube", "vimeo", "kinescope", "vk.com/js", "player.")):
            return tag
        tag2 = re.sub(r"""\ssrc=(['"])([^'"]+)\1""", f' data-rk-video-src="{src}"', tag, count=1)
        if "type=" not in tag2:
            tag2 = tag2.replace("<script", '<script type="text/plain"', 1)
        else:
            tag2 = re.sub(r"""type=(['"])[^'"]*\1""", 'type="text/plain"', tag2, count=1)
        return tag2

    html = re.sub(r"<script\b[^>]*>", hold, html, flags=re.I)
    return html


def extract_leftover_head_styles(html: str, depth: int) -> tuple[str, str]:
    """Move non-critical leftover <style> from head into deferred extra CSS (shared file once)."""
    head_end = html.find("</head>")
    head = html[:head_end]
    rest = html[head_end:]
    keep: list[str] = []
    dump: list[str] = []
    for m in re.finditer(r"<style\b([^>]*)>(.*?)</style>", head, re.S | re.I):
        attrs, body = m.group(1), m.group(2)
        full = m.group(0)
        # keep: green-zone, lead-forms, breadcrumbs, hero-reserve, schema-adjacent tiny
        if any(
            k in attrs or k in full[:80]
            for k in (
                "data-green-zone",
                "data-lead-forms",
                "data-rk-breadcrumbs",
                "data-sozdanie-hero-reserve",
                "data-critical",
                "rk-cities",
            )
        ):
            keep.append(full)
            continue
        # keep font-face Montserrat only? dump all font-faces to deferred (preload bold remains)
        dump.append(body)
    # rebuild head without dumped styles
    new_head = re.sub(r"<style\b[^>]*>.*?</style>", "", head, flags=re.S | re.I)
    # re-append keep styles before </head> is in rest; insert keep before rest
    # Actually we stripped ALL styles including keep — put keep back
    new_head = new_head  # styles removed
    # Ensure keep styles are present
    for k in keep:
        if k not in new_head:
            new_head += k
    return new_head + rest, "\n".join(dump)


def fix_lcp_preload(html: str, depth: int) -> str:
    prefix = "../" * depth + "assets/"
    new_href = f"{prefix}m-files.cdn1.cc/lpfile/0/0/e/{HERO_BG}"
    # replace old wrong preload
    html = re.sub(
        rf'<link rel="preload" as="image" href="[^"]*{re.escape(OLD_PRELOAD)}"[^>]*/?>',
        f'<link rel="preload" as="image" href="{new_href}" fetchpriority="high"/>',
        html,
        count=1,
    )
    # if hero bg preload missing, inject near head
    if HERO_BG not in html.split("</head>")[0]:
        html = re.sub(
            r"(<head[^>]*>)",
            rf'\1<link rel="preload" as="image" href="{new_href}" fetchpriority="high"/>',
            html,
            count=1,
            flags=re.I,
        )
    return html


def page_depth(path: Path) -> int:
    return len(path.relative_to(ROOT).parts) - 1


def main() -> int:
    parent = ROOT / "web-studiya/sozdanie-saitov/index.html"
    parent_html = parent.read_text(encoding="utf-8")
    resplit_css(parent_html)

    # Build leftover styles dump from parent once
    pages = [parent] + [
        ROOT / "web-studiya/sozdanie-saitov" / c / "index.html" for c in CITIES
    ]

    leftover_css = None
    for path in pages:
        html = path.read_text(encoding="utf-8")
        depth = page_depth(path)
        html = fix_video_scripts(html)
        html = fix_lcp_preload(html, depth)

        html2, dump = extract_leftover_head_styles(html, depth)
        if leftover_css is None:
            # normalize urls in dump for assets/css
            dump_n = dump
            dump_n = re.sub(r"url\((['\"]?)\.\./\.\./\.\./assets/", r"url(\1../", dump_n)
            dump_n = re.sub(r"url\((['\"]?)\.\./\.\./assets/", r"url(\1../", dump_n)
            leftover_css = "/* sozdanie leftover head styles — deferred */\n" + dump_n
            (CSS_DIR / "sozdanie-extra.v1.css").write_text(leftover_css, encoding="utf-8")
            print(f"extra styles {len(leftover_css.encode())/1024:.1f} KiB")
        html = html2

        # wire extra deferred css if missing
        prefix = "../" * depth + "assets/"
        extra_link = (
            f'<link rel="stylesheet" href="{prefix}css/sozdanie-extra.v1.css" media="print" '
            f'onload="this.media=\'all\'">'
            f'<noscript><link rel="stylesheet" href="{prefix}css/sozdanie-extra.v1.css"></noscript>'
        )
        if "sozdanie-extra.v1.css" not in html:
            # after deferred blocks link
            html = html.replace(
                f'sozdanie-popup-other.v1.css"></noscript>',
                f'sozdanie-popup-other.v1.css"></noscript>{extra_link}',
                1,
            )
            if "sozdanie-extra.v1.css" not in html:
                html = html.replace("</head>", extra_link + "</head>", 1)

        path.write_text(html, encoding="utf-8")
        head = html[: html.find("</head>")]
        print("fixed", path.parent.name if path.parent.name != "sozdanie-saitov" else "parent", f"head={len(head.encode())/1024:.1f}KiB")

    # sanity video on parent
    p = parent.read_text(encoding="utf-8")
    for m in re.finditer(r"<script[^>]*(youtube|vk\.com)[^>]*>", p, re.I):
        print("VID", m.group(0)[:180])
    print("hero preload ok", HERO_BG in p.split("</head>")[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
