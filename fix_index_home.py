#!/usr/bin/env python3
"""Fix homepage layout regressions: asset paths, duplicate attrs, broken img src."""
import re
from pathlib import Path

MIRROR = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
INDEX = MIRROR / "index.html"
ORIG = MIRROR / "assets" / "raskrutov.kz" / "index.html"


def dedupe_data_original_url(html: str) -> tuple[str, int]:
    n = 0

    def fix_tag(m: re.Match) -> str:
        nonlocal n
        tag = m.group(0)
        if tag.count("data-original-url=") <= 1:
            return tag
        urls = re.findall(r'data-original-url="([^"]*)"', tag)
        if not urls:
            return tag
        best = max(urls, key=len)
        tag = re.sub(r'\s*data-original-url="[^"]*"', "", tag)
        tag = tag.replace(">", f' data-original-url="{best}">', 1)
        n += 1
        return tag

    return re.sub(r"<[^>]+\sdata-original-url=\"[^\"]*\"\sdata-original-url=\"[^\"]*\"[^>]*>", fix_tag, html), n


def fix_asset_paths(html: str) -> tuple[str, int]:
    n = html.count("assets/assets/")
    html = html.replace("assets/assets/", "assets/")
    # broken favicon from bad rewrite
    html = html.replace(
        'href="assets/index.html/index.htmlfavicon__q_1.png"',
        'href="assets/m-files.cdn1.cc/lpfile/favicon/favicon__q_1.png"',
    )
    # common broken pattern if still present
    html = re.sub(
        r'href="assets/index\.html/index\.htmlfavicon[^"]*"',
        'href="assets/m-files.cdn1.cc/lpfile/favicon/favicon__q_1.png"',
        html,
    )
    return html, n


def restore_broken_img_src(html: str, orig_html: str) -> tuple[str, int]:
    """Restore img src truncated to /f.png by copying from original mirror."""
    n = 0
    broken = list(re.finditer(r'src="assets/m-files\.cdn1\.cc/[^"]+/f\.png"', html))
    if not broken:
        return html, 0
    orig_srcs = re.findall(r'src="(\.\./m-files\.cdn1\.cc/[^"]+)"', orig_html)
    orig_srcs += re.findall(r"src='(\.\./m-files\.cdn1\.cc/[^']+)'", orig_html)
    # map by lpfile hash path segment
    orig_by_tail = {}
    for src in orig_srcs:
        key = src.split("lpfile/")[-1] if "lpfile/" in src else src
        orig_by_tail[key.split("/-/")[0]] = src

    def repl(m: re.Match) -> str:
        nonlocal n
        bad = m.group(0)
        inner = bad[5:-1]
        if "lpfile/" not in inner:
            return bad
        key = inner.split("lpfile/")[-1].split("/-/")[0]
        orig = orig_by_tail.get(key)
        if not orig:
            return bad
        fixed = orig.replace("../m-files.cdn1.cc/", "assets/m-files.cdn1.cc/")
        n += 1
        return f'src="{fixed}"'

    html = re.sub(r'src="assets/m-files\.cdn1\.cc/[^"]+/f\.png"', repl, html)
    return html, n


def fix_broken_list_nesting(html: str) -> tuple[str, int]:
    """Remove accidental quadruple <li> wrappers from link wiring."""
    n = 0
    while "<li><li><li><li><a class=\"home-sub-link\"" in html:
        html = html.replace(
            "<li><li><li><li><a class=\"home-sub-link\"",
            "<li><a class=\"home-sub-link\"",
            1,
        )
        n += 1
    while "</a></li></li></li></li>" in html:
        html = html.replace("</a></li></li></li></li>", "</a></li>", 1)
        n += 1
    return html, n


def fix_email(html: str) -> tuple[str, int]:
    n = 0
    if "info@index.html" in html:
        html = html.replace("info@index.html", "info@raskrutov.kz")
        n += 1
    if 'href="mailto:info@index.html"' in html:
        html = html.replace('href="mailto:info@index.html"', 'href="mailto:info@raskrutov.kz"')
        n += 1
    return html, n


def main():
    html = INDEX.read_text(encoding="utf-8")
    orig = ORIG.read_text(encoding="utf-8") if ORIG.exists() else ""

    html, n1 = fix_asset_paths(html)
    html, n2 = dedupe_data_original_url(html)
    html, n3 = restore_broken_img_src(html, orig) if orig else (html, 0)
    html, n4 = fix_broken_list_nesting(html)
    html, n5 = fix_email(html)

    INDEX.write_text(html, encoding="utf-8")
    print(f"Fixed asset double-prefix: {n1}")
    print(f"Deduped data-original-url tags: {n2}")
    print(f"Restored broken img src: {n3}")
    print(f"Fixed broken list nesting: {n4}")
    print(f"Fixed email: {n5}")
    print(f"Remaining nested li: {html.count('<li><li><li><li>')}")


if __name__ == "__main__":
    main()
