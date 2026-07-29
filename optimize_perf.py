#!/usr/bin/env python3
"""Performance optimization pass for the mirrored site.

Per served HTML page (outside assets/):
1. defer the public.bundle JS
2. wrap inline scripts AFTER the bundle in DOMContentLoaded (they call FE.* which
   becomes available only after deferred bundle executes)
3. async-load the public.bundle CSS via preload-swap (+ noscript fallback)
4. add font-display:swap to inline @font-face rules missing it
5. preload the first image url() found in the document (hero/LCP candidate)
6. conservatively minify inline <style> blocks (comments + whitespace)

Global:
7. font-display:swap in assets/*.css files
"""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

BUNDLE_JS_RE = re.compile(
    r'<script src="((?:\.\./)*assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.js)"([^>]*)></script>'
)
BUNDLE_CSS_RE = re.compile(
    r'<link href="((?:\.\./)*assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.css)" rel="stylesheet"\s*/?>'
)
INLINE_SCRIPT_RE = re.compile(
    r'<script type="text/javascript">(.*?)</script>', re.DOTALL
)
STYLE_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.DOTALL)
FONT_FACE_RE = re.compile(r"@font-face\s*\{")
IMG_URL_RE = re.compile(
    r"url\(['\"]?((?:\.\./)*assets/[^)'\"]+\.(?:webp|png|jpg|jpeg))['\"]?\)",
    re.IGNORECASE,
)

stats = {"defer": 0, "wrap": 0, "asynccss": 0, "fontface": 0, "preload": 0, "minify_kb": 0.0, "files": 0}


def minify_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    css = re.sub(r"[ \t]+", " ", css)
    css = re.sub(r"\s*\n\s*", "", css)
    return css.strip()


def add_font_display(html: str) -> tuple[str, int]:
    """Insert font-display:swap right after @font-face { if missing in that block."""
    n = 0
    out = []
    pos = 0
    for m in FONT_FACE_RE.finditer(html):
        close = html.find("}", m.end())
        if close == -1:
            continue
        block = html[m.end():close]
        if "font-display" not in block:
            out.append(html[pos:m.end()])
            out.append("font-display:swap;")
            pos = m.end()
            n += 1
    if not n:
        return html, 0
    out.append(html[pos:])
    return "".join(out), n


def process_page(path: Path) -> None:
    html = path.read_text(encoding="utf-8", errors="ignore")
    orig = html

    # 1. defer bundle js (only if not already deferred)
    def defer_repl(m: re.Match) -> str:
        if "defer" in m.group(2):
            return m.group(0)
        stats["defer"] += 1
        return f'<script src="{m.group(1)}"{m.group(2)} defer></script>'
    html = BUNDLE_JS_RE.sub(defer_repl, html)

    # 2. wrap inline scripts that appear AFTER the bundle script tag
    bundle_m = BUNDLE_JS_RE.search(html)
    if bundle_m:
        cut = bundle_m.end()
        head_part, tail_part = html[:cut], html[cut:]

        def wrap_repl(m: re.Match) -> str:
            body = m.group(1)
            if not body.strip() or "DOMContentLoaded" in body[:80]:
                return m.group(0)
            stats["wrap"] += 1
            return (
                '<script type="text/javascript">'
                "document.addEventListener('DOMContentLoaded',function(){"
                + body
                + "});</script>"
            )
        tail_part = INLINE_SCRIPT_RE.sub(wrap_repl, tail_part)
        html = head_part + tail_part

    # 3. async css
    def asynccss_repl(m: re.Match) -> str:
        stats["asynccss"] += 1
        href = m.group(1)
        return (
            f'<link href="{href}" rel="preload" as="style" '
            f"onload=\"this.onload=null;this.rel='stylesheet'\"/>"
            f'<noscript><link href="{href}" rel="stylesheet"/></noscript>'
        )
    html = BUNDLE_CSS_RE.sub(asynccss_repl, html)

    # 4. font-display swap in inline styles
    html, nfd = add_font_display(html)
    stats["fontface"] += nfd

    # 5. preload first image url()
    if 'rel="preload" as="image"' not in html:
        mimg = IMG_URL_RE.search(html)
        if mimg:
            head_end = html.find("</head>")
            if head_end != -1:
                html = (
                    html[:head_end]
                    + f'<link rel="preload" as="image" href="{mimg.group(1)}"/>'
                    + html[head_end:]
                )
                stats["preload"] += 1

    # 6. minify inline style blocks
    def minify_repl(m: re.Match) -> str:
        body = m.group(1)
        mini = minify_css(body)
        stats["minify_kb"] += (len(body) - len(mini)) / 1024
        return m.group(0).replace(body, mini, 1)
    html = STYLE_RE.sub(minify_repl, html)

    if html != orig:
        path.write_text(html, encoding="utf-8")
        stats["files"] += 1


def main() -> None:
    for f in M.rglob("*.html"):
        if "assets" in f.relative_to(M).parts:
            continue
        process_page(f)

    # 7. font-display in asset css files
    css_files = 0
    for f in M.rglob("*.css"):
        css = f.read_text(encoding="utf-8", errors="ignore")
        new, n = add_font_display(css)
        if new != css:
            f.write_text(new, encoding="utf-8")
            css_files += 1
            stats["fontface"] += n

    print(f"HTML files changed: {stats['files']}")
    print(f"bundle defer added: {stats['defer']}")
    print(f"inline scripts wrapped: {stats['wrap']}")
    print(f"css async'd: {stats['asynccss']}")
    print(f"@font-face swap added: {stats['fontface']} (css files changed: {css_files})")
    print(f"hero preloads added: {stats['preload']}")
    print(f"inline css minified savings: {stats['minify_kb']:.0f} KB total")


if __name__ == "__main__":
    main()
