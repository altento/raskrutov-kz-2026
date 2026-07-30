#!/usr/bin/env python3
"""Import freshly mirrored Mottor service pages into pretty URL dirs."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "site_mirror"
PAGES = MIRROR / "pages"

IMPORTS = {
    "web-studiya_sozdanie-saitov_landing.html": "/web-studiya/sozdanie-saitov/landing/",
    "web-studiya_sozdanie-saitov_internet-magazin.html": "/web-studiya/sozdanie-saitov/internet-magazin/",
    "web-studiya_sozdanie-saitov_korporativnyy-sayt.html": "/web-studiya/sozdanie-saitov/korporativnyy-sayt/",
}

# Known good sprite used across production pages (if present)
SPRITE_CANDIDATES = [
    MIRROR / "assets/m-files.cdn1.cc/web/mottor-frontend/svg/sprite__q_v_20260618.svg",
    MIRROR / "assets/m-files.cdn1.cc/web/mottor-frontend/svg/sprite.svg",
]


def depth_of(pretty: str) -> int:
    return len([p for p in pretty.strip("/").split("/") if p])


def asset_prefix(depth: int) -> str:
    return "../" * depth + "assets/"


def rewrite_raskrutov_assets(html: str) -> str:
    """../assets/raskrutov.kz/foo/index.html → /foo/"""

    def repl(m: re.Match) -> str:
        path = m.group(1)
        path = path.replace("/index.html", "/").replace("index.html", "")
        if not path.startswith("/"):
            path = "/" + path
        if path != "/" and not path.endswith("/"):
            path += "/"
        return path

    html = re.sub(
        r"(?:\.\./)+assets/raskrutov\.kz(/[^\"'\s]*)",
        repl,
        html,
    )
    html = re.sub(
        r"https?://(?:www\.)?raskrutov\.kz(/[^\"'\s]*)",
        lambda m: (m.group(1) if m.group(1).endswith("/") or m.group(1) == "/" else m.group(1) + "/")
        if not m.group(1).endswith((".png", ".jpg", ".webp", ".ico", ".svg", ".js", ".css"))
        else m.group(0),
        html,
    )
    return html


def rewrite_social(html: str) -> str:
    reps = [
        (
            r"(?:\.\./)+assets/api\.whatsapp\.com/send/index__q_phone_77000216900\.html",
            "https://wa.me/77000216900",
        ),
        (r"(?:\.\./)+assets/www\.instagram\.com/raskrutov\.kz/?", "https://www.instagram.com/raskrutov.kz/"),
        (r"(?:\.\./)+assets/www\.youtube\.com/@raskrutov-kz(?:/index\.html)?/?", "https://www.youtube.com/@raskrutov-kz"),
        (r"(?:\.\./)+assets/t\.me/Raskrutov_web(?:/index\.html)?/?", "https://t.me/Raskrutov_web"),
        (r"https://m65176a2c628d6\.lpmotortest\.com/", "https://raskrutov.kz/"),
        (r"//m65176a2c628d6\.lpmotortest\.com/", "https://raskrutov.kz/"),
    ]
    for pat, repl in reps:
        html = re.sub(pat, repl, html)
    return html


def rewrite_assets_prefix(html: str, depth: int) -> str:
    pref = asset_prefix(depth)
    # From pages/ mirror: ../assets/ → depth-relative
    html = html.replace("../assets/", pref)
    # Also absolute /assets/ → depth-relative for consistency with siblings
    html = re.sub(r'(["\'(=])/assets/', rf"\1{pref}", html)
    return html


def fix_sprite(html: str, depth: int) -> str:
    pref = asset_prefix(depth)
    for cand in SPRITE_CANDIDATES:
        if cand.exists():
            rel = pref + cand.relative_to(MIRROR / "assets").as_posix()
            html = re.sub(
                r"window\.svgSpritePath\s*=\s*['\"][^'\"]*['\"]",
                f"window.svgSpritePath='{rel}'",
                html,
                count=1,
            )
            break
    # Drop motortest host asset refs that failed / are wrong host folder
    html = html.replace(
        f"{pref}m65176a2c628d6.lpmotortest.com/",
        pref + "m-files.cdn1.cc/",
    )
    return html


def ensure_target_blank(html: str) -> str:
    def add_rel(m: re.Match) -> str:
        tag = m.group(0)
        if "rel=" in tag:
            return tag
        return tag[:-1] + ' rel="noopener noreferrer">'

    html = re.sub(
        r'<a\s+[^>]*href="https?://(?:wa\.me|www\.instagram\.com|www\.youtube\.com|t\.me)[^"]*"[^>]*>',
        add_rel,
        html,
        flags=re.I,
    )
    return html


def write_redirect_stub(src_name: str, pretty: str) -> None:
    target = pretty if pretty.endswith("/") else pretty + "/"
    canon = "https://raskrutov.kz" + pretty.rstrip("/")
    stub = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<meta http-equiv="refresh" content="0;url={target}"/>
<link rel="canonical" href="{canon}"/>
<title>Redirect</title>
</head>
<body>
<p>Страница переехала: <a href="{target}">{canon}</a></p>
</body>
</html>
"""
    (PAGES / src_name).write_text(stub, encoding="utf-8")


def process_one(src_name: str, pretty: str) -> Path:
    src = PAGES / src_name
    if not src.exists():
        raise FileNotFoundError(src)
    raw = src.read_text(encoding="utf-8", errors="replace")
    # Backup full mirrored source before stub overwrite
    bak = PAGES / (src_name + ".motortest.bak")
    if not bak.exists():
        shutil.copy2(src, bak)

    depth = depth_of(pretty)
    html = raw
    html = rewrite_raskrutov_assets(html)
    html = rewrite_social(html)
    html = rewrite_assets_prefix(html, depth)
    html = fix_sprite(html, depth)
    html = ensure_target_blank(html)

    # Force single clean canonical (fix_all_links will refine)
    canon = "https://raskrutov.kz" + pretty.rstrip("/")
    html = re.sub(
        r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\']\s*/?>',
        f'<link rel="canonical" href="{canon}"/>',
        html,
        flags=re.I,
    )
    # og:url
    html = re.sub(
        r'(property=["\']og:url["\']\s+content=["\'])[^"\']*(["\'])',
        rf"\g<1>{canon}\2",
        html,
        flags=re.I,
    )

    out = MIRROR / pretty.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    write_redirect_stub(src_name, pretty)
    return out


def main() -> None:
    for src_name, pretty in IMPORTS.items():
        out = process_one(src_name, pretty)
        text = out.read_text(encoding="utf-8", errors="replace")
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
        h1t = re.sub(r"<[^>]+>", "", h1.group(1)).strip()[:70] if h1 else "?"
        print(f"OK {out.relative_to(MIRROR)}  size={out.stat().st_size}  H1={h1t!r}")
        print(f"   assets prefix sample: {asset_prefix(depth_of(pretty))}")
        print(f"   lpmotortest left: {text.count('lpmotortest')}")
        print(f"   broken raskrutov.kz assets: {text.count('assets/raskrutov.kz')}")


if __name__ == "__main__":
    main()
