# -*- coding: utf-8 -*-
"""Homepage performance pass (approved):

1. Move LCP/font/CSS preloads to the top of <head> (before megabyte of CSS).
2. Externalize #all_blocks-style and popup style blocks.
3. Defer popup CSS (media=print onload).
4. Async-load public.bundle.css with noscript fallback (JS bundle stays sync).
5. Keep a small critical CSS stub for layout + hero reservation.
6. Mobile hero webp + media preload / CSS override.
7. Trim Montserrat preloads to normal+bold (drop medium).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "site_mirror"
HTML_PATH = MIRROR / "index.html"
CSS_DIR = MIRROR / "assets" / "css"
HERO_ID = "9466bf80aa894ca9b20b37b4d9409cc1"
HERO_BASE = "assets/m-files.cdn1.cc/lpfile/6/e/e/6eea3ed3de3e5cbe118d06eb148fe963.webp"
HERO_MOBILE_REL = "assets/css/hero-home-mobile.webp"
BUNDLE_CSS = "assets/m-files.cdn1.cc/web/build/pages/public.bundle__q_v_1784122059.css"
BUNDLE_JS = "assets/m-files.cdn1.cc/web/build/pages/public.bundle__q_v_1784122069.js"

STYLE_RE = re.compile(r"<style([^>]*)>(.*?)</style>", re.S | re.I)


def minify_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"[ \t]+", " ", css)
    css = re.sub(r"\s*\n\s*", "", css)
    return css.strip()


def extract_style_by_id(html: str, style_id: str) -> tuple[str, str | None]:
    """Remove <style id=...> and return (html, css_body|None)."""
    pat = re.compile(
        rf'<style([^>]*\bid=["\']{re.escape(style_id)}["\'][^>]*)>(.*?)</style>',
        re.S | re.I,
    )
    m = pat.search(html)
    if not m:
        return html, None
    return html[: m.start()] + html[m.end() :], m.group(2)


def make_mobile_hero() -> Path | None:
    src = MIRROR / HERO_BASE.replace("/", "\\") if False else MIRROR / Path(HERO_BASE)
    if not src.exists():
        print("hero source missing", src)
        return None
    try:
        from PIL import Image
    except ImportError:
        print("PIL missing, skip mobile hero")
        return None
    out = MIRROR / Path(HERO_MOBILE_REL)
    out.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    # Mobile cover ~390 CSS px * 2.5 DPR ≈ 975; use 1100 wide
    w = 1100
    h = max(1, round(im.height * (w / im.width)))
    im = im.resize((w, h), Image.Resampling.LANCZOS)
    im.save(out, "WEBP", quality=78, method=6)
    print(f"mobile hero {out.relative_to(MIRROR)} {out.stat().st_size/1024:.1f} KiB {im.size}")
    return out


def critical_css_stub() -> str:
    return minify_css(
        f"""
        body,#site_wrapper1{{min-width:1400px;}}
        .blk_section_inner{{width:1400px;}}
        @media (max-width:500px){{
          body,#site_wrapper1{{min-width:370px;}}
          .blk_section_inner{{width:370px;}}
          .section_popup_wnd{{width:300px!important;}}
          .blk-section--ms-popup{{max-width:300px}}
        }}
        #{HERO_ID} .section_image_container,
        [data-id="s-{HERO_ID}"] .section_image_container{{min-height:280px;}}
        @media (max-width:500px){{
          #{HERO_ID} .section_image_container,
          [data-id="s-{HERO_ID}"] .section_image_container{{min-height:320px;}}
          #section_image_{HERO_ID}.section-image{{
            background-image:url('{HERO_MOBILE_REL}')!important;
          }}
        }}
        .home-sub-link{{padding:12px 10px 12px 0;min-height:44px;box-sizing:border-box;}}
        """
    )


def early_head_block() -> str:
    """High-priority resource hints immediately after <head>."""
    return (
        f'<link rel="preload" as="image" href="{HERO_MOBILE_REL}" '
        f'media="(max-width: 500px)" fetchpriority="high"/>'
        f'<link rel="preload" as="image" href="{HERO_BASE}" '
        f'media="(min-width: 501px)" fetchpriority="high"/>'
        f'<link rel="preload" as="style" href="{BUNDLE_CSS}"/>'
        f'<link rel="preload" as="style" href="assets/css/home-all-blocks.css"/>'
        f'<link rel="preload" href="assets/m-files.cdn1.cc/web/user/fonts/montserrat/montserrat_bold.woff" '
        f'as="font" type="font/woff" crossorigin>'
        f'<link rel="preload" href="assets/m-files.cdn1.cc/web/user/fonts/montserrat/montserrat_normal.woff" '
        f'as="font" type="font/woff" crossorigin>'
    )


def async_css_link(href: str) -> str:
    return (
        f'<link rel="preload" href="{href}" as="style" '
        f'onload="this.onload=null;this.rel=\'stylesheet\'">'
        f'<noscript><link rel="stylesheet" href="{href}"></noscript>'
    )


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    orig_len = len(html)
    CSS_DIR.mkdir(parents=True, exist_ok=True)

    make_mobile_hero()

    # --- extract heavy style blocks ---
    extracted = {}
    for sid, fname in [
        ("all_blocks-style", "home-all-blocks.css"),
        ("sp-2782231__blocks-style", "home-popup-2782231.css"),
        ("sp-2773676__blocks-style", "home-popup-2773676.css"),
    ]:
        html, css = extract_style_by_id(html, sid)
        if css is None:
            print("WARN missing style", sid)
            continue
        css_m = minify_css(css)
        out = CSS_DIR / fname
        out.write_text(css_m, encoding="utf-8")
        extracted[sid] = fname
        print(f"wrote assets/css/{fname} {len(css_m)/1024:.1f} KiB (was {len(css)/1024:.1f})")

    # Remove old LCP/font/bundle preloads we will re-inject early
    html = re.sub(
        r'<link rel="preload" as="image" href="assets/m-files\.cdn1\.cc/lpfile/6/e/e/6eea3ed3[^"]*"\s*fetchpriority="high"\s*/?>\s*',
        "",
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="preload" as="style" href="assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.css"\s*/?>\s*',
        "",
        html,
        count=1,
    )
    for font in ("montserrat_normal", "montserrat_medium", "montserrat_bold", "inter_normal", "inter_bold", "open_sans_normal"):
        html = re.sub(
            rf'<link rel="preload" href="assets/m-files\.cdn1\.cc/web/user/fonts/[^"]*{font}\.woff" as="font" type="font/woff" crossorigin>\s*',
            "",
            html,
            count=1,
        )

    # Keep public.bundle.css BLOCKING. Async caused Mottor --height race on mobile menu.
    bundle_link_re = re.compile(
        r'<link href="(assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.css)" rel="stylesheet"\s*/?>',
        re.I,
    )
    if bundle_link_re.search(html):
        print("bundle CSS stays blocking stylesheet")
    else:
        # Undo accidental async swap if present
        async_pat = re.compile(
            r'<link rel="preload" href="(assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.css)" as="style" '
            r'onload="this\.onload=null;this\.rel=\'stylesheet\'">\s*'
            r'<noscript><link rel="stylesheet" href="\1"></noscript>',
            re.I,
        )
        if async_pat.search(html):
            html = async_pat.sub(r'<link href="\1" rel="stylesheet"/>', html, count=1)
            print("bundle CSS restored to blocking")
        else:
            print("WARN bundle css link not found")

    # Update / replace green-zone style with critical stub (includes mobile hero)
    green = f'<style data-green-zone="1" data-critical="1">{critical_css_stub()}</style>'
    green_re = re.compile(r'<style\s+data-green-zone=["\']1["\'][^>]*>.*?</style>', re.S | re.I)
    if green_re.search(html):
        html = green_re.sub(green, html, count=1)
    else:
        html = html.replace("</head>", green + "</head>", 1)

    # Remove duplicate min-width style that sat next to bundle (now in critical stub)
    html = re.sub(
        r"<style>body,#site_wrapper1\{min-width:1400px;\}.*?</style>",
        "",
        html,
        count=1,
        flags=re.S,
    )

    # Inject early preloads right after <head...>
    head_m = re.search(r"<head[^>]*>", html, re.I)
    if not head_m:
        raise SystemExit("no head")
    insert_at = head_m.end()
    html = html[:insert_at] + early_head_block() + html[insert_at:]

    # Inject all_blocks as render-blocking link just before </head>
    # (external file: smaller HTML stream; still needed for layout of rest of page)
    all_blocks_link = '<link rel="stylesheet" href="assets/css/home-all-blocks.css"/>'
    if "home-all-blocks.css" in extracted.values() or (CSS_DIR / "home-all-blocks.css").exists():
        # Avoid duplicate if re-run
        html = re.sub(
            r'<link rel="stylesheet" href="assets/css/home-all-blocks\.css"\s*/?>\s*',
            "",
            html,
        )
        html = html.replace("</head>", all_blocks_link + "\n</head>", 1)
        print("all_blocks -> external blocking stylesheet")

    # sp-2782231 includes mobile menu critical rules — BLOCKING in head.
    # sp-2773676 is true popup styles — defer at </body>.
    menu_css = "assets/css/home-popup-2782231.css"
    popup_css = "assets/css/home-popup-2773676.css"
    html = re.sub(
        r'<link rel="stylesheet" href="assets/css/home-popup-[^"]+"[^>]*>\s*'
        r'(?:<noscript><link rel="stylesheet" href="assets/css/home-popup-[^"]+"></noscript>\s*)?',
        "",
        html,
    )
    if (CSS_DIR / "home-popup-2782231.css").exists():
        html = html.replace("</head>", f'<link rel="stylesheet" href="{menu_css}"/>\n</head>', 1)
        print("menu CSS (2782231) blocking in head")
    if (CSS_DIR / "home-popup-2773676.css").exists():
        defer = (
            f'<link rel="stylesheet" href="{popup_css}" media="print" '
            f'onload="this.media=\'all\'">'
            f'<noscript><link rel="stylesheet" href="{popup_css}"></noscript>\n'
        )
        if "</body>" in html:
            html = html.replace("</body>", defer + "</body>", 1)
        else:
            html += defer
        print("true popup CSS deferred at </body>")

    # Ensure public.bundle JS has NO defer/async
    html = re.sub(
        rf'(<script src="{re.escape(BUNDLE_JS)}")\s+defer(\s*)>',
        r"\1>",
        html,
    )
    html = re.sub(
        rf'(<script src="{re.escape(BUNDLE_JS)}")\s+async(\s*)>',
        r"\1>",
        html,
    )

    # Ensure hero section still uses base webp in inline style (desktop)
    if HERO_BASE not in html:
        print("WARN hero base url missing from html")

    # Windows sometimes rejects write_text on huge Mottor HTML; use bytes + replace.
    tmp = HTML_PATH.with_suffix(".html.tmp")
    data = html.encode("utf-8")
    tmp.write_bytes(data)
    tmp.replace(HTML_PATH)
    print(f"index.html {orig_len/1024:.0f} -> {len(html)/1024:.0f} KiB (delta {(len(html)-orig_len)/1024:.0f} KiB)")
    head_end = html.find("</head>")
    print("HEAD approx", (head_end / 1024 if head_end != -1 else -1), "KiB")


if __name__ == "__main__":
    main()
