#!/usr/bin/env python3
"""Safe mobile PageSpeed wins without breaking Mottor public.bundle JS sync load.

- Inline tiny lead-forms.css + breadcrumbs.css (kill 2 render-blocking requests)
- Fix logo width/height 10x10 → real aspect
- Larger .home-sub-link padding for touch targets (no inline-block)
- Reserve min-height on homepage hero image container (CLS)
"""
from __future__ import annotations

import re
from pathlib import Path

MIRROR = Path(__file__).resolve().parent / "site_mirror"
LEAD_CSS = (MIRROR / "assets/css/lead-forms.css").read_text(encoding="utf-8")
CRUMB_CSS = (MIRROR / "assets/css/breadcrumbs.css").read_text(encoding="utf-8")

LEAD_LINK_RE = re.compile(
    r'<link\s+rel=["\']stylesheet["\']\s+href=["\'][^"\']*assets/css/lead-forms\.css["\'][^>]*/?>',
    re.I,
)
CRUMB_LINK_RE = re.compile(
    r'<link\s+rel=["\']stylesheet["\']\s+href=["\'][^"\']*assets/css/breadcrumbs\.css["\'][^>]*/?>',
    re.I,
)
INLINE_LEAD_RE = re.compile(
    r'<style\s+data-lead-forms-inline=["\']1["\']\s*>.*?</style>',
    re.I | re.S,
)
INLINE_CRUMB_RE = re.compile(
    r'<style\s+data-rk-breadcrumbs-inline=["\']1["\']\s*>.*?</style>',
    re.I | re.S,
)
GREEN_STYLE_RE = re.compile(
    r'<style\s+data-green-zone=["\']1["\']\s*>.*?</style>',
    re.I | re.S,
)
LOGO_IMG_RE = re.compile(
    r'(<img\b[^>]*src=["\'][^"\']*81a3fe2ab76d8a7d4df2ea1900ce0265[^"\']*["\'][^>]*)(>)',
    re.I,
)
HERO_SECTION = "9466bf80aa894ca9b20b37b4d9409cc1"


def minify_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    return css.strip()


def inline_css(html: str) -> tuple[str, int]:
    n = 0
    lead = minify_css(LEAD_CSS)
    crumb = minify_css(CRUMB_CSS)

    if LEAD_LINK_RE.search(html):
        html = LEAD_LINK_RE.sub("", html, count=1)
        n += 1
    if CRUMB_LINK_RE.search(html):
        html = CRUMB_LINK_RE.sub("", html, count=1)
        n += 1

    html = INLINE_LEAD_RE.sub("", html)
    html = INLINE_CRUMB_RE.sub("", html)

    inject = (
        f'<style data-lead-forms-inline="1">{lead}</style>'
        f'<style data-rk-breadcrumbs-inline="1">{crumb}</style>'
    )
    if "</head>" in html:
        html = html.replace("</head>", inject + "\n</head>", 1)
        n += 1
    return html, n


def fix_green_zone_style(html: str) -> tuple[str, int]:
    # Larger touch padding; still no inline-block (breaks list wrap)
    style = (
        '<style data-green-zone="1">'
        ".home-sub-link{padding:12px 10px 12px 0;min-height:44px;box-sizing:border-box;}"
        # CLS: reserve space for homepage hero image plane on mobile
        f"#{HERO_SECTION} .section_image_container,"
        f'[data-id="s-{HERO_SECTION}"] .section_image_container{{min-height:280px;}}'
        f"@media (max-width:500px){{"
        f"#{HERO_SECTION} .section_image_container,"
        f'[data-id="s-{HERO_SECTION}"] .section_image_container{{min-height:320px;}}'
        f"}}"
        "</style>"
    )
    if GREEN_STYLE_RE.search(html):
        html2, n = GREEN_STYLE_RE.subn(style, html, count=1)
        return html2, n
    if "</head>" in html:
        return html.replace("</head>", style + "\n</head>", 1), 1
    return html, 0


def fix_logo_dims(html: str) -> tuple[str, int]:
    n = 0

    def repl(m: re.Match) -> str:
        nonlocal n
        tag = m.group(1)
        # logo crop is ~955x221 → display ~211x49; use intrinsic aspect 422x98 ≈ 4.31
        if re.search(r'\bwidth=["\']10["\']', tag) or re.search(r'\bheight=["\']10["\']', tag):
            tag = re.sub(r'\swidth=["\'][^"\']*["\']', "", tag)
            tag = re.sub(r'\sheight=["\'][^"\']*["\']', "", tag)
            tag += ' width="422" height="98"'
            n += 1
        elif "width=" not in tag:
            tag += ' width="422" height="98"'
            n += 1
        return tag + m.group(2)

    html = LOGO_IMG_RE.sub(repl, html)
    return html, n


def process(path: Path) -> dict:
    html = path.read_text(encoding="utf-8", errors="replace")
    stats = {"file": path.relative_to(MIRROR).as_posix(), "css": 0, "green": 0, "logo": 0}
    html, stats["css"] = inline_css(html)
    html, stats["green"] = fix_green_zone_style(html)
    html, stats["logo"] = fix_logo_dims(html)
    path.write_text(html, encoding="utf-8", newline="\n")
    return stats


def main() -> None:
    # Homepage first (PageSpeed target), then all HTML outside assets/pages
    targets = [MIRROR / "index.html"]
    for p in sorted(MIRROR.rglob("*.html")):
        if p == targets[0]:
            continue
        rel = p.relative_to(MIRROR)
        if "assets" in rel.parts or rel.parts[0] == "pages":
            continue
        targets.append(p)

    changed = 0
    for p in targets:
        s = process(p)
        if s["css"] or s["green"] or s["logo"]:
            changed += 1
            if s["file"] == "index.html" or changed <= 5:
                print(s)
    print(f"done pages_touched={changed}/{len(targets)}")


if __name__ == "__main__":
    main()
