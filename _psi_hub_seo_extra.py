# -*- coding: utf-8 -*-
"""Dump leftover HEAD <style> for hub + seo into *-extra.v1.css (deferred)."""
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

KEEP = (
    "data-green-zone",
    "data-lead-forms",
    "data-rk-breadcrumbs",
    "data-hub-hero-reserve",
    "data-seo-hero-reserve",
    "data-rk-reduced-motion",
    "data-rk-cities",
    "data-rk-hub",
)


def normalize(css: str) -> str:
    css = re.sub(r"url\((['\"]?)\.\./\.\./\.\./assets/", r"url(\1../", css)
    css = re.sub(r"url\((['\"]?)\.\./\.\./assets/", r"url(\1../", css)
    css = re.sub(r"url\((['\"]?)/assets/", r"url(\1../", css)
    return css


def extract(html: str) -> tuple[str, str]:
    he = html.find("</head>")
    head, tail = html[:he], html[he:]
    keep, dump = [], []
    for m in re.finditer(r"<style\b([^>]*)>(.*?)</style>", head, re.S | re.I):
        attrs, body, full = m.group(1), m.group(2), m.group(0)
        if any(k in attrs or k in full[:100] for k in KEEP):
            keep.append(full)
        else:
            dump.append(body)
    new_head = re.sub(r"<style\b[^>]*>.*?</style>", "", head, flags=re.S | re.I)
    for k in keep:
        if k not in new_head:
            new_head += k
    return new_head + tail, "\n".join(dump)


def depth(path: Path) -> int:
    return len(path.relative_to(ROOT).parts) - 1


def wire(html: str, prefix: str, d: int) -> str:
    ap = "../" * d + "assets/"
    html = re.sub(rf'<link[^>]+href="[^"]*{re.escape(prefix)}-extra\.v1\.css"[^>]*>\s*', "", html)
    html = re.sub(
        rf'<noscript><link rel="stylesheet" href="[^"]*{re.escape(prefix)}-extra\.v1\.css"></noscript>\s*',
        "",
        html,
    )
    tag = (
        f'<link rel="stylesheet" href="{ap}css/{prefix}-extra.v1.css" media="print" '
        f"onload=\"this.media='all'\">"
        f'<noscript><link rel="stylesheet" href="{ap}css/{prefix}-extra.v1.css"></noscript>'
    )
    if f"{prefix}-deferred.v1.css" in html:
        html = re.sub(
            rf'(<link rel="stylesheet" href="[^"]*{re.escape(prefix)}-deferred\.v1\.css"[^>]*>)',
            r"\1" + tag,
            html,
            count=1,
        )
    else:
        html = re.sub(r"(<head[^>]*>)", r"\1" + tag, html, count=1, flags=re.I)
    return html


def run(name: str, parent: Path, pages: list[Path]) -> None:
    html0 = parent.read_text(encoding="utf-8")
    _, dump = extract(html0)
    dump = normalize(dump)
    (CSS_DIR / f"{name}-extra.v1.css").write_text(
        f"/* {name} extra leftover head styles — deferred */\n" + dump, encoding="utf-8"
    )
    print(f"{name} extra {len(dump.encode())/1024:.1f} KiB")
    for path in pages:
        html = path.read_text(encoding="utf-8")
        html, _ = extract(html)
        html = wire(html, name, depth(path))
        path.write_text(html, encoding="utf-8")
        h = html[: html.find("</head>")]
        print("OK", path.relative_to(ROOT).as_posix(), f"head={len(h.encode())/1024:.1f}KiB")


def main() -> int:
    CSS_DIR.mkdir(parents=True, exist_ok=True)
    hub_parent = ROOT / "web-studiya" / "index.html"
    hub_pages = [hub_parent] + [ROOT / "web-studiya" / c / "index.html" for c in CITIES]
    run("hub", hub_parent, hub_pages)

    seo_parent = ROOT / "web-studiya" / "seo-prodvizhenie" / "index.html"
    seo_pages = [seo_parent] + [
        ROOT / "web-studiya" / "seo-prodvizhenie" / c / "index.html" for c in CITIES
    ]
    run("seo", seo_parent, seo_pages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
