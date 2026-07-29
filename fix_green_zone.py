# -*- coding: utf-8 -*-
"""Green-zone fixes: canonical absolute, empty anchors, role=main, href-less
anchors, home-sub-link touch targets, contrast colors, sr-only H2 (mobile)."""
import re
import sys
from pathlib import Path

io_enc = "utf-8"
sys.stdout.reconfigure(encoding=io_enc, errors="replace")

ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

PROD = "https://raskrutov.kz"

def page_url(p: Path) -> str:
    if p.name == "index.html" and p.parent == ROOT:
        return PROD + "/"
    stem = p.stem  # e.g. web-studiya_sozdanie-saitov_landing
    return PROD + "/" + stem.replace("_", "/")

def color_lum(bg: str):
    """Return relative luminance of a css color string, or None."""
    bg = bg.strip()
    m = re.match(r"#([0-9a-fA-F]{3,8})$", bg)
    if m:
        h = m.group(1)
        if len(h) == 3:
            r, g, b = (int(c * 2, 16) for c in h)
        elif len(h) >= 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        else:
            return None
    else:
        m = re.match(r"rgba?\(([^)]+)\)", bg)
        if not m:
            return None
        parts = [x.strip() for x in m.group(1).split(",")]
        try:
            r, g, b = (float(parts[0]), float(parts[1]), float(parts[2]))
        except (ValueError, IndexError):
            return None
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def ctx_is_dark(html: str, pos: int) -> bool:
    """Heuristic: nearest background in preceding context is dark."""
    ctx = html[max(0, pos - 700):pos]
    bgs = re.findall(r"background(?:-color)?\s*:\s*([^;}]+)", ctx)
    for bg in reversed(bgs):
        bg = bg.strip()
        if "url(" in bg or "gradient" in bg:
            continue
        lum = color_lum(bg)
        if lum is None:
            continue
        return lum < 0.35
    return False  # default: site is white-themed

stats = {}

for page in PAGES:
    html = page.read_text(encoding="utf-8")
    orig = html
    rel = page.relative_to(ROOT).as_posix()

    # A. canonical -> absolute
    new_can = f'<link rel="canonical" href="{page_url(page)}"/>'
    html2, n = re.subn(r'<link rel="canonical" href="[^"]*"\s*/?>', new_can, html, count=1)
    if n:
        stats["canonical"] = stats.get("canonical", 0) + 1
        html = html2

    # B. empty anchors with data-original-url -> aria-hidden
    html2, n = re.subn(
        r'<a href="([^"]*)" data-original-url="([^"]*)"></a>',
        r'<a href="\1" data-original-url="\2" aria-hidden="true" tabindex="-1"></a>',
        html,
    )
    if n:
        stats["empty_anchors"] = stats.get("empty_anchors", 0) + n
        html = html2

    # C. role=main on sections_list
    if 'id="sections_list"' in html and 'id="sections_list" role=' not in html:
        html = html.replace('<div id="sections_list">', '<div id="sections_list" role="main">', 1)
        stats["role_main"] = stats.get("role_main", 0) + 1

    # D. href-less anchors -> role=button
    html2, n = re.subn(r'<a class="wind-close">', '<a class="wind-close" role="button" tabindex="0" aria-label="Закрыть">', html)
    if n:
        stats["wind_close"] = stats.get("wind_close", 0) + n
        html = html2
    html2, n = re.subn(
        r'<a class="wind-btn-apply w10 no_sel" ondragstart="return false;">',
        '<a class="wind-btn-apply w10 no_sel" role="button" tabindex="0" aria-label="Применить" ondragstart="return false;">',
        html,
    )
    if n:
        stats["wind_apply"] = stats.get("wind_apply", 0) + n
        html = html2

    # E. home-sub-link touch-target CSS
    if "home-sub-link" in html and "data-green-zone" not in html:
        css = ("<style data-green-zone=\"1\">"
               ".home-sub-link{display:inline-block;padding:8px 6px 8px 0;line-height:1.7;}"
               "</style>")
        html = html.replace("</head>", css + "\n</head>", 1)
        stats["sublink_css"] = stats.get("sublink_css", 0) + 1

    # F. contrast colors (light contexts only)
    out = []
    last = 0
    changed_p = changed_g = 0
    for m in re.finditer(r"rgba\(152,103,243,1\)|rgb\(21, 210, 13\)", html):
        out.append(html[last:m.start()])
        tok = m.group(0)
        if ctx_is_dark(html, m.start()):
            out.append(tok)
        else:
            if tok.startswith("rgba(152"):
                out.append("rgba(127,63,242,1)")
                changed_p += 1
            else:
                out.append("rgb(14, 122, 9)")
                changed_g += 1
        last = m.end()
    out.append(html[last:])
    html = "".join(out)
    stats["purple_fixed"] = stats.get("purple_fixed", 0) + changed_p
    stats["green_fixed"] = stats.get("green_fixed", 0) + changed_g

    # F2. button color (m-button-h8mLz9T blue on white)
    html2, n = re.subn(r"(\.m-button-h8mLz9T \{ cursor: pointer; color: )#24A0FF", r"\g<1>#006FDC", html)
    if n:
        stats["btn_blue"] = stats.get("btn_blue", 0) + n
        html = html2
    html2, n = re.subn(r"\.m-button-h8mLz9T:hover \{ color: #9867F3; \}", ".m-button-h8mLz9T:hover { color: #7F3FF2; }", html)
    if n:
        stats["btn_hover"] = stats.get("btn_hover", 0) + n
        html = html2
    html2, n = re.subn(r"(\.m-button-h8mLz9T:hover \.m-button__img-h8mLz9T \{ background: )#9867F3", r"\g<1>#7F3FF2", html)
    if n:
        stats["btn_img_hover"] = stats.get("btn_img_hover", 0) + n
        html = html2

    # G. sr-only H2 before mobile hero H3s (homepage-like pages only)
    if "экосистема цифрового роста" in html and 'data-sr-h2="1"' not in html:
        m = re.search(r'<h3 class="blk-data clearfix font-84">\s*<[^>]*>?\s*Сайты', html)
        if not m:
            m = re.search(r'<h3 class="blk-data clearfix font-84">(?:(?!</h3>).){0,200}?Сайты', html, re.S)
        if m:
            sr = ('<h2 data-sr-h2="1" style="position:absolute!important;width:1px;height:1px;'
                  'padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">'
                  'Ключевые направления и продукты</h2>')
            html = html[:m.start()] + sr + html[m.start():]
            stats["sr_h2"] = stats.get("sr_h2", 0) + 1

    if html != orig:
        page.write_text(html, encoding="utf-8")

print("stats:", stats)
print("pages scanned:", len(PAGES))
