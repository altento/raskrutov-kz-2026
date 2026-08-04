# -*- coding: utf-8 -*-
"""Extract + split Mottor CSS for hub / seo / dizayn templates (sozdanie pattern).

Does NOT touch public.bundle.js (stays sync).
Does NOT commit/push.
Sozdanie already extracted — skipped.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("site_mirror")
CSS_DIR = ROOT / "assets" / "css"

CITIES = [
    "almaty", "astana", "shymkent", "aktau", "aktobe", "atyrau", "karaganda",
    "kokshetau", "kostanay", "kyzylorda", "pavlodar", "petropavlovsk", "semey",
    "taldykorgan", "taraz", "turkestan", "uralsk", "ust-kamenogorsk",
]

TEMPLATES = [
    {
        "name": "hub",
        "prefix": "hub",
        "parent": ROOT / "web-studiya" / "index.html",
        "geo_dir": ROOT / "web-studiya",
        "hero": "04835b64e87241ad93cd6eafc671ae39",
        "lcp_img": "00e5f3089b7608f6ea110e879c58caea.webp",
        "geo_is_direct_child": True,  # /web-studiya/{city}/
    },
    {
        "name": "seo",
        "prefix": "seo",
        "parent": ROOT / "web-studiya" / "seo-prodvizhenie" / "index.html",
        "geo_dir": ROOT / "web-studiya" / "seo-prodvizhenie",
        "hero": "04835b64e87241ad93cd6eafc671ae39",
        "lcp_img": "00e5f3089b7608f6ea110e879c58caea.webp",
        "geo_is_direct_child": False,
    },
    {
        "name": "dizayn",
        "prefix": "dizayn",
        "parent": ROOT / "web-studiya" / "dizayn" / "index.html",
        "geo_dir": ROOT / "web-studiya" / "dizayn",
        "hero": "e90637d851c04778850a4256afe81582",
        "lcp_img": None,  # may be CSS-only / different
        "geo_is_direct_child": False,
    },
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


def collect_critical_ids(html: str, hero: str) -> set[str]:
    ids: set[str] = {hero}
    m = re.search(rf'\bid="{hero}"', html)
    if not m:
        raise SystemExit(f"hero id missing: {hero}")
    rest = html[m.start() :]
    end = len(rest)
    for mm in re.finditer(
        r'(?:class="[^"]*blk_section[^"]*"[^>]*id="([0-9a-f]{32})"|id="([0-9a-f]{32})"[^>]*class="[^"]*blk_section)',
        rest,
    ):
        sid = mm.group(1) or mm.group(2)
        if sid != hero:
            end = mm.start()
            break
    chunk = rest[: max(end, 40000)]
    ids.update(re.findall(r'\bid="([0-9a-f]{32})"', chunk))

    menu_roots = []
    for mm in re.finditer(r'id="([0-9a-f]{32})"', html):
        window = html[mm.start() : mm.start() + 400]
        if re.search(r"ms-menu|menu-bar|is_fixed", window, re.I):
            menu_roots.append(mm.group(1))
    for mid in menu_roots[:8]:
        pos = html.find(f'id="{mid}"')
        if pos < 0:
            continue
        ids.update(re.findall(r'\bid="([0-9a-f]{32})"', html[pos : pos + 12000]))
    return ids


def rule_is_critical(rule: str, ids: set[str], hero: str) -> bool:
    if re.search(
        r"mockup|ms-menu|site_wrapper|blk_section_inner|is_fixed|section-image|section_image|menu-bar|@font-face",
        rule,
        re.I,
    ):
        return True
    if hero in rule:
        return True
    for i in ids:
        if i in rule:
            return True
        if len(i) == 32 and i[0].isdigit() and i[1:8] in rule:
            return True
    return False


def normalize_css_urls(css: str) -> str:
    css = re.sub(r"url\((['\"]?)\.\./\.\./\.\./assets/", r"url(\1../", css)
    css = re.sub(r"url\((['\"]?)\.\./\.\./assets/", r"url(\1../", css)
    css = re.sub(r"url\((['\"]?)/assets/", r"url(\1../", css)
    return css


def extract_style(html: str, style_id: str) -> str | None:
    m = re.search(rf'<style id="{re.escape(style_id)}">(.*?)</style>', html, re.S)
    return m.group(1) if m else None


def remove_style(html: str, style_id: str) -> str:
    return re.sub(
        rf'\s*<style id="{re.escape(style_id)}">.*?</style>',
        "",
        html,
        count=1,
        flags=re.S,
    )


def page_depth(path: Path) -> int:
    rel = path.relative_to(ROOT)
    return len(rel.parts) - 1


def asset_prefix(depth: int) -> str:
    return "../" * depth + "assets/"


def wire_page(html: str, *, depth: int, prefix: str, hero: str, lcp_img: str | None) -> str:
    ap = asset_prefix(depth)

    html = re.sub(
        rf'<link[^>]+href="[^"]*assets/css/{re.escape(prefix)}-[^"]+"[^>]*>\s*',
        "",
        html,
    )
    html = re.sub(
        rf'<noscript><link rel="stylesheet" href="[^"]*assets/css/{re.escape(prefix)}-[^"]+"></noscript>\s*',
        "",
        html,
    )

    # Trim font preloads (keep montserrat bold)
    html = re.sub(
        r'<link rel="preload" href="[^"]*/fonts/(?:inter|open_sans)/[^"]+"[^>]*>\s*',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'<link rel="preload" href="[^"]*/fonts/montserrat/montserrat_(?:normal|medium)\.woff[^"]*"[^>]*>\s*',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'<link rel="preload" as="style" href="[^"]*public\.bundle[^"]*\.css"[^>]*>\s*',
        "",
        html,
    )

    links = (
        f'<link rel="preload" as="style" href="{ap}css/{prefix}-critical.v1.css"/>'
        f'<link rel="preload" as="style" href="{ap}css/{prefix}-popup-menu.v1.css"/>'
        f'<link rel="stylesheet" href="{ap}css/{prefix}-popup-menu.v1.css"/>'
        f'<link rel="stylesheet" href="{ap}css/{prefix}-critical.v1.css"/>'
        f'<link rel="stylesheet" href="{ap}css/{prefix}-deferred.v1.css" media="print" onload="this.media=\'all\'">'
        f'<noscript><link rel="stylesheet" href="{ap}css/{prefix}-deferred.v1.css"></noscript>'
        f'<link rel="stylesheet" href="{ap}css/{prefix}-popup-other.v1.css" media="print" onload="this.media=\'all\'">'
        f'<noscript><link rel="stylesheet" href="{ap}css/{prefix}-popup-other.v1.css"></noscript>'
    )
    html = re.sub(r"(<head[^>]*>)", r"\1" + links, html, count=1, flags=re.I)

    mark = f"data-{prefix}-hero-reserve"
    if mark not in html:
        reserve = (
            f'<style {mark}="1">'
            f'#{hero} .section_image_container,[data-id="s-{hero}"] .section_image_container{{min-height:280px;}}'
            f'@media (max-width:500px){{#{hero} .section_image_container,[data-id="s-{hero}"] .section_image_container{{min-height:320px;}}}}'
            f"</style>"
        )
        html = html.replace("</head>", reserve + "</head>", 1)

    # prefers-reduced-motion once
    if "data-rk-reduced-motion" not in html:
        html = html.replace(
            "</head>",
            '<style data-rk-reduced-motion="1">@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms !important;animation-iteration-count:1 !important;transition-duration:.01ms !important;scroll-behavior:auto !important}}</style></head>',
            1,
        )

    if lcp_img:
        # ensure preload for LCP bg if missing
        if lcp_img not in html.split("</head>")[0] or "preload" not in html.split(lcp_img)[0][-120:]:
            # find existing relative path to this asset if any
            m = re.search(rf'(["\'])([^"\']*{re.escape(lcp_img)})\1', html)
            if m:
                href = m.group(2)
                if "preload" not in html.split("</head>")[0] or lcp_img not in re.findall(
                    r'rel=["\']preload["\'][^>]+href=["\']([^"\']+)', html.split("</head>")[0]
                ):
                    pre = f'<link rel="preload" as="image" href="{href}" fetchpriority="high"/>'
                    html = re.sub(r"(<head[^>]*>)", r"\1" + pre, html, count=1, flags=re.I)

    return html


def pages_for(tpl: dict) -> list[Path]:
    out = [tpl["parent"]]
    geo = tpl["geo_dir"]
    for c in CITIES:
        if tpl["geo_is_direct_child"]:
            # skip service dirs mistaken as cities
            if c in {
                "sozdanie-saitov",
                "seo-prodvizhenie",
                "dizayn",
                "aeo-prodvizhenie",
                "kontekstnaya-reklama",
                "lidogeneratsiya",
                "podderzhka-saytov",
                "digital-konsalting",
            }:
                continue
        out.append(geo / c / "index.html")
    return out


def process_template(tpl: dict) -> None:
    name = tpl["name"]
    prefix = tpl["prefix"]
    hero = tpl["hero"]
    parent = tpl["parent"]
    print(f"\n==== {name} ====")
    parent_html = parent.read_text(encoding="utf-8")

    # already extracted?
    if f"{prefix}-critical.v1.css" in parent_html and "all_blocks-style" not in parent_html:
        print("already extracted, skip extract — re-wire only if needed")
        return

    if "all_blocks-style" not in parent_html:
        print("NO all_blocks-style — skip", name)
        return

    ids = collect_critical_ids(parent_html, hero)
    print("critical ids", len(ids))

    all_blocks = extract_style(parent_html, "all_blocks-style")
    pop_menu = extract_style(parent_html, "sp-2782231__blocks-style")
    pop_other = extract_style(parent_html, "sp-2773676__blocks-style")
    if not all_blocks or not pop_menu or not pop_other:
        raise SystemExit(f"{name}: missing style blocks")

    all_blocks = normalize_css_urls(all_blocks)
    pop_menu = normalize_css_urls(pop_menu)
    pop_other = normalize_css_urls(pop_other)

    rules = split_rules(all_blocks)
    crit, rest = [], []
    for r in rules:
        (crit if rule_is_critical(r, ids, hero) else rest).append(r)
    crit_css = f"/* {prefix} critical v1 */\n" + "".join(crit)
    def_css = f"/* {prefix} deferred v1 */\n" + "".join(rest)

    CSS_DIR.mkdir(parents=True, exist_ok=True)
    (CSS_DIR / f"{prefix}-critical.v1.css").write_text(crit_css, encoding="utf-8")
    (CSS_DIR / f"{prefix}-deferred.v1.css").write_text(def_css, encoding="utf-8")
    (CSS_DIR / f"{prefix}-popup-menu.v1.css").write_text(
        f"/* {prefix} popup menu (mobile) — blocking */\n" + pop_menu, encoding="utf-8"
    )
    (CSS_DIR / f"{prefix}-popup-other.v1.css").write_text(
        f"/* {prefix} popup other — deferred */\n" + pop_other, encoding="utf-8"
    )
    print(
        f"critical {len(crit_css.encode())/1024:.1f} KiB / deferred {len(def_css.encode())/1024:.1f} KiB / "
        f"menu {len(pop_menu.encode())/1024:.1f} / other {len(pop_other.encode())/1024:.1f}"
    )

    for path in pages_for(tpl):
        if not path.exists():
            print("SKIP missing", path)
            continue
        html = path.read_text(encoding="utf-8")
        for sid in ("all_blocks-style", "sp-2782231__blocks-style", "sp-2773676__blocks-style"):
            html = remove_style(html, sid)
        depth = page_depth(path)
        html = wire_page(
            html,
            depth=depth,
            prefix=prefix,
            hero=hero,
            lcp_img=tpl.get("lcp_img"),
        )
        path.write_text(html, encoding="utf-8")
        head = html[: html.find("</head>")]
        print(
            "OK",
            path.relative_to(ROOT).as_posix(),
            f"head={len(head.encode())/1024:.1f}KiB",
            "depth",
            depth,
        )


def main() -> int:
    for tpl in TEMPLATES:
        process_template(tpl)
    print("\nDONE — visual QA required before deploy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
