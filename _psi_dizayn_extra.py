# -*- coding: utf-8 -*-
"""Move leftover dizayn <style> tags from HEAD into dizayn-extra.v1.css (deferred)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("site_mirror")
CSS_DIR = ROOT / "assets" / "css"
PARENT = ROOT / "web-studiya" / "dizayn" / "index.html"
CITIES = [
    "almaty", "astana", "shymkent", "aktau", "aktobe", "atyrau", "karaganda",
    "kokshetau", "kostanay", "kyzylorda", "pavlodar", "petropavlovsk", "semey",
    "taldykorgan", "taraz", "turkestan", "uralsk", "ust-kamenogorsk",
]

KEEP_MARKERS = (
    "data-green-zone",
    "data-lead-forms",
    "data-rk-breadcrumbs",
    "data-dizayn-hero-reserve",
    "data-rk-reduced-motion",
    "data-rk-cities",
    "data-rk-hub",
)


def normalize_css_urls(css: str) -> str:
    css = re.sub(r"url\((['\"]?)\.\./\.\./\.\./assets/", r"url(\1../", css)
    css = re.sub(r"url\((['\"]?)\.\./\.\./assets/", r"url(\1../", css)
    css = re.sub(r"url\((['\"]?)/assets/", r"url(\1../", css)
    return css


def extract_leftovers(html: str) -> tuple[str, str]:
    head_end = html.find("</head>")
    head, tail = html[:head_end], html[head_end:]
    keep: list[str] = []
    dump: list[str] = []
    for m in re.finditer(r"<style\b([^>]*)>(.*?)</style>", head, re.S | re.I):
        attrs, body, full = m.group(1), m.group(2), m.group(0)
        if any(k in attrs or k in full[:100] for k in KEEP_MARKERS):
            keep.append(full)
            continue
        dump.append(body)
    new_head = re.sub(r"<style\b[^>]*>.*?</style>", "", head, flags=re.S | re.I)
    for k in keep:
        if k not in new_head:
            new_head += k
    return new_head + tail, "\n".join(dump)


def page_depth(path: Path) -> int:
    return len(path.relative_to(ROOT).parts) - 1


def wire_extra(html: str, depth: int) -> str:
    prefix = "../" * depth + "assets/"
    html = re.sub(
        r'<link[^>]+href="[^"]*assets/css/dizayn-extra\.v1\.css"[^>]*>\s*',
        "",
        html,
    )
    html = re.sub(
        r'<noscript><link rel="stylesheet" href="[^"]*dizayn-extra\.v1\.css"></noscript>\s*',
        "",
        html,
    )
    tag = (
        f'<link rel="stylesheet" href="{prefix}css/dizayn-extra.v1.css" media="print" '
        f"onload=\"this.media='all'\">"
        f'<noscript><link rel="stylesheet" href="{prefix}css/dizayn-extra.v1.css"></noscript>'
    )
    # after deferred link if present
    if "dizayn-deferred.v1.css" in html:
        html = re.sub(
            r'(<link rel="stylesheet" href="[^"]*dizayn-deferred\.v1\.css"[^>]*>)',
            r"\1" + tag,
            html,
            count=1,
        )
    else:
        html = re.sub(r"(<head[^>]*>)", r"\1" + tag, html, count=1, flags=re.I)
    return html


def main() -> int:
    parent = PARENT.read_text(encoding="utf-8")
    _, dump = extract_leftovers(parent)
    dump = normalize_css_urls(dump)
    CSS_DIR.mkdir(parents=True, exist_ok=True)
    (CSS_DIR / "dizayn-extra.v1.css").write_text(
        "/* dizayn extra leftover head styles — deferred */\n" + dump, encoding="utf-8"
    )
    print(f"extra {len(dump.encode())/1024:.1f} KiB")

    pages = [PARENT] + [ROOT / "web-studiya" / "dizayn" / c / "index.html" for c in CITIES]
    for path in pages:
        html = path.read_text(encoding="utf-8")
        html, _ = extract_leftovers(html)
        html = wire_extra(html, page_depth(path))
        path.write_text(html, encoding="utf-8")
        head = html[: html.find("</head>")]
        print("OK", path.relative_to(ROOT).as_posix(), f"head={len(head.encode())/1024:.1f}KiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
