# -*- coding: utf-8 -*-
"""Sozdanie PSI pass 2: CLS dims, hero reserve, image URL downsize, fonts in critical."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("site_mirror")
CSS_DIR = ROOT / "assets" / "css"
HERO = "1928a98fbb6447c7bb1413d2b56c3267"
HOME_HERO_WRONG = "9466bf80aa894ca9b20b37b4d9409cc1"

CITIES = [
    "almaty", "astana", "shymkent", "aktau", "aktobe", "atyrau", "karaganda",
    "kokshetau", "kostanay", "kyzylorda", "pavlodar", "petropavlovsk", "semey",
    "taldykorgan", "taraz", "turkestan", "uralsk", "ust-kamenogorsk",
]

FONT_CRITICAL = """
/* above-fold fonts — keep in critical to cut CLS from late swap */
@font-face{font-family:"Montserrat";src:url("../m-files.cdn1.cc/web/user/fonts/montserrat/montserrat_bold.woff2") format("woff2"),url("../m-files.cdn1.cc/web/user/fonts/montserrat/montserrat_bold.woff") format("woff");font-weight:700;font-style:normal;font-display:swap;}
@font-face{font-family:"Montserrat Fallback";src:local("Arial"),local("Helvetica Neue"),local("Helvetica");size-adjust:107%;ascent-override:92%;descent-override:23%;line-gap-override:0%;}
@font-face{font-family:"Inter Fallback";src:local("Arial"),local("Helvetica Neue"),local("Helvetica");size-adjust:100%;ascent-override:90%;descent-override:22%;line-gap-override:0%;}
@font-face{font-family:"Open Sans Fallback";src:local("Arial"),local("Helvetica Neue"),local("Helvetica");size-adjust:104%;ascent-override:96%;descent-override:26%;line-gap-override:0%;}
"""

HERO_RESERVE = (
    f'<style data-sozdanie-hero-reserve="1">'
    f'#{HERO},[data-id="s-{HERO}"]{{min-height:520px;}}'
    f'#{HERO} .section_image_container,[data-id="s-{HERO}"] .section_image_container{{min-height:520px;}}'
    f'#{HERO} .blk_section_inner,[data-id="s-{HERO}"] .blk_section_inner{{min-height:480px;}}'
    f'@media (max-width:500px){{'
    f'#{HERO},[data-id="s-{HERO}"]{{min-height:640px;}}'
    f'#{HERO} .section_image_container,[data-id="s-{HERO}"] .section_image_container{{min-height:640px;}}'
    f'#{HERO} .blk_section_inner,[data-id="s-{HERO}"] .blk_section_inner{{min-height:600px;}}'
    f'}}'
    f"</style>"
)


def guess_dims(src: str) -> tuple[int, int] | None:
    """Infer display size from Mottor CDN transform path."""
    # .../-/resize/N/... or crop WxH
    m = re.search(r"/resize/(\d+)(?:/|$)", src)
    # Prefer the FIRST (logical) resize before scale/x3/1920 junk
    first = re.search(r"/-/resize/(\d+)/", src)
    crop = re.search(r"/crop/(?:\d+x\d+x)?(\d+)x(\d+)/", src)
    if first:
        w = int(first.group(1))
        if crop:
            cw, ch = int(crop.group(1)), int(crop.group(2))
            if cw > 0:
                h = max(1, round(w * ch / cw))
                return w, h
        # square-ish icons
        if w <= 80:
            return w, w
        if w <= 350:
            return w, round(w * 0.75)
        return w, round(w * 0.6)
    if src.endswith(".svg"):
        return 48, 48
    return None


def downsize_src(src: str) -> str:
    """Drop Mottor 'scale x3 then force 1920' tail when an earlier resize exists."""
    # .../-/resize/42/-/scale/x3/-/resize/1920/ → .../-/resize/42/
    src2 = re.sub(r"(/-/resize/\d+)/-/scale/x\d+/-/resize/1920/", r"\1/", src)
    # .../-/resize/42/-/resize/1920/ → .../-/resize/42/
    src2 = re.sub(r"(/-/resize/\d+)/-/resize/1920/", r"\1/", src2)
    return src2


def patch_img_tag(tag: str) -> str:
    sm = re.search(r'src="([^"]+)"', tag)
    if not sm:
        return tag
    src = sm.group(1)
    new_src = downsize_src(src)
    if new_src != src:
        tag = tag.replace(f'src="{src}"', f'src="{new_src}"', 1)
        src = new_src
    if "width=" in tag and "height=" in tag:
        return tag
    dims = guess_dims(src)
    if not dims:
        return tag
    w, h = dims
    # insert before closing
    if tag.endswith("/>"):
        return tag[:-2] + f' width="{w}" height="{h}" />'
    if tag.endswith(">"):
        return tag[:-1] + f' width="{w}" height="{h}">'
    return tag


def fix_green_zone(html: str) -> str:
    # Replace wrong homepage hero id in green-zone with sozdanie hero
    html = html.replace(HOME_HERO_WRONG, HERO)
    return html


def ensure_hero_reserve(html: str) -> str:
    html = re.sub(r'<style data-sozdanie-hero-reserve="1">.*?</style>', "", html, flags=re.S)
    html = html.replace("</head>", HERO_RESERVE + "</head>", 1)
    return html


def ensure_font_critical() -> None:
    path = CSS_DIR / "sozdanie-critical.v1.css"
    css = path.read_text(encoding="utf-8")
    if "Montserrat Fallback" in css:
        return
    # prepend after banner
    if css.startswith("/* sozdanie critical"):
        nl = css.find("\n")
        css = css[: nl + 1] + FONT_CRITICAL + css[nl + 1 :]
    else:
        css = FONT_CRITICAL + css
    path.write_text(css, encoding="utf-8")
    print("critical fonts injected", round(path.stat().st_size / 1024, 1), "KiB")


def optimize_rk_cities() -> None:
    try:
        from PIL import Image
    except ImportError:
        print("PIL missing, skip rk-cities compress")
        return
    d = ROOT / "assets" / "rk-cities"
    if not d.exists():
        return
    for p in d.glob("*.jpg"):
        img = Image.open(p).convert("RGB")
        w, h = img.size
        # city cards ~ display ~220px; keep 440 for 2x
        max_w = 440
        if w > max_w:
            nh = round(h * max_w / w)
            img = img.resize((max_w, nh), Image.Resampling.LANCZOS)
        before = p.stat().st_size
        img.save(p, "JPEG", quality=72, optimize=True, progressive=True)
        after = p.stat().st_size
        print(f"rk-city {p.name}: {before//1024}→{after//1024} KiB {img.size}")


def patch_page(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    html = fix_green_zone(html)
    html = ensure_hero_reserve(html)

    def repl_img(m: re.Match) -> str:
        return patch_img_tag(m.group(0))

    html2, n = re.subn(r"<img\b[^>]*>", repl_img, html, flags=re.I)
    html = html2

    # aspect-ratio for rk-cities photos already in CSS; bump if needed
    if "rk-cities__photo{aspect-ratio" in html or "rk-cities__photo{aspect-ratio" in html.replace(" ", ""):
        pass

    path.write_text(html, encoding="utf-8")
    print("patched", path.as_posix(), "imgs touched pass", n)


def bump_cities_css_in_pages() -> None:
    """Ensure city photo boxes have aspect-ratio reserved (CLS)."""
    # already in injected style data-rk-cities; verify
    p = ROOT / "web-studiya/sozdanie-saitov/index.html"
    t = p.read_text(encoding="utf-8")
    if "aspect-ratio:4/3" in t or "aspect-ratio: 4/3" in t:
        print("rk-cities aspect-ratio ok")
    else:
        print("WARN: rk-cities aspect-ratio missing in page")


def main() -> int:
    ensure_font_critical()
    optimize_rk_cities()
    pages = [ROOT / "web-studiya/sozdanie-saitov/index.html"] + [
        ROOT / "web-studiya/sozdanie-saitov" / c / "index.html" for c in CITIES
    ]
    for path in pages:
        if path.exists():
            patch_page(path)
    bump_cities_css_in_pages()

    # quick sanity
    t = pages[0].read_text(encoding="utf-8")
    imgs = re.findall(r"<img\b[^>]*>", t, re.I)
    missing = sum(1 for i in imgs if "width=" not in i or "height=" not in i)
    print("parent imgs", len(imgs), "still missing dims", missing)
    print("hero reserve", "min-height:640px" in t)
    print("wrong home hero id left", HOME_HERO_WRONG in t)
    print("resize/1920 left", t.count("/-/resize/1920/"))
    print("resize/720", t.count("/-/resize/720/"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
