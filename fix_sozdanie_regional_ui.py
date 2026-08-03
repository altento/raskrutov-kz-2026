# -*- coding: utf-8 -*-
"""Fix sozdanie-saitov donor + re-apply to all geo pages.

- Price card titles → links to real service pages; geo pages get «в Городе»
- Portfolio Drive mirrors → live client sites (or keysy fallback)
- Kazakhstan cities block → all 18 cities with photos + pretty links
- Harden mockup mask/img asset URLs to root-absolute /assets/
"""
from __future__ import annotations

import hashlib
import re
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "site_mirror"
DONOR = MIRROR / "web-studiya" / "sozdanie-saitov" / "index.html"
CITIES_DIR = MIRROR / "assets" / "rk-cities"

# Import city maps from generator
sys.path.insert(0, str(ROOT))
from generate_regional_sozdanie import (  # noqa: E402
    CITY_IN,
    CITY_SLUG,
    deepen_prefixes,
    load_final_meta,
    load_matrix_sozdanie,
    replace_seo,
)

PRICE_LINKS = [
    # (title_core_regex_or_exact, href, name_for_geo_insert_before_от)
    (
        "ЛЕНДИНГ-ПЕЙДЖ (LANDING PAGE)",
        "/web-studiya/sozdanie-saitov/landing/",
    ),
    (
        "САЙТ-КАТАЛОГ",
        "/web-studiya/sozdanie-saitov/mnogostranichnye-sayty/",
    ),
    (
        "МНОГОСТРАНИЧНЫЙ САЙТ",
        "/web-studiya/sozdanie-saitov/mnogostranichnye-sayty/",
    ),
    (
        "САЙТ ИНТЕРНЕТ-МАГАЗИН",
        "/web-studiya/sozdanie-saitov/internet-magazin/",
    ),
    (
        "КОРПОРАТИВНЫЙ САЙТ",
        "/web-studiya/sozdanie-saitov/korporativnyy-sayt/",
    ),
]

# Case gallery Drive → live sites
CASE_HREFS = {
    # Pilates — no stable own site; open keysy gallery
    "1bprdsc0cd6Kb5jMcg7ilTlqr2xUeznuO": "https://raskrutov.kz/keysy/sayty/",
    # ЧИОЧИОСАН
    "1a1qwQLvQmIzIDzliPkdh1-TJ-4Y9KuOZ": "https://chiochiosan-astana.kz/",
    # KESLER CAR
    "12v5RLgjD-CGzttrt50JqVUilI6IRTD1C": "https://kesler.kz/",
}

# Eurasia wrongly reused Pilates drive id — fix by title context separately
EURASIA_URL = "https://sherdar.kz/"

# Existing Mottor city photo hashes (reuse where we have them)
EXISTING_CITY_IMGS = {
    "astana": "32e8eac576d37936896bba2a35b52bdc",
    "petropavlovsk": "c6937ec1201641a5666bc4606abdb165",
    "almaty": "05fba2f37e0d0ebf16bf74efc995e0b9",
    "karaganda": "4164fcbd8cd10da83d49ff55b12a2220",
    "shymkent": "d8eb27b3bca04551081de512908b16a5",
}

# Localizable city photos (Unsplash — downloaded once into assets/rk-cities/)
CITY_PHOTO_URLS = {
    "aktau": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=640&q=80",
    "aktobe": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=640&q=80",
    "atyrau": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=640&q=80",
    "kokshetau": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=640&q=80",
    "kostanay": "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?auto=format&fit=crop&w=640&q=80",
    "kyzylorda": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=640&q=80",
    "pavlodar": "https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=640&q=80",
    "semey": "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=640&q=80",
    "taldykorgan": "https://images.unsplash.com/photo-1444723121867-7a241dac7e20?auto=format&fit=crop&w=640&q=80",
    "taraz": "https://images.unsplash.com/photo-1555881400-74d7acaacd8b?auto=format&fit=crop&w=640&q=80",
    "turkestan": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=640&q=80",
    "uralsk": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=640&q=80",
    "ust-kamenogorsk": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?auto=format&fit=crop&w=640&q=80",
}

CITY_ORDER = [
    "Астана",
    "Алматы",
    "Шымкент",
    "Караганда",
    "Петропавловск",
    "Актобе",
    "Атырау",
    "Павлодар",
    "Усть-Каменогорск",
    "Семей",
    "Костанай",
    "Кызылорда",
    "Уральск",
    "Тараз",
    "Актау",
    "Туркестан",
    "Кокшетау",
    "Талдыкорган",
]

CITIES_CSS = """
<style data-rk-cities="1">
.rk-cities{margin:24px auto 8px;max-width:1200px;padding:0 16px;box-sizing:border-box}
.rk-cities__grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px}
@media(max-width:1100px){.rk-cities__grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:640px){.rk-cities__grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}
.rk-cities__card{display:flex;flex-direction:column;background:#6b2fd6;border-radius:14px;overflow:hidden;text-decoration:none;color:#fff;box-shadow:0 8px 24px rgba(60,20,120,.18);transition:transform .2s ease,box-shadow .2s ease}
.rk-cities__card:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(60,20,120,.28);color:#fff}
.rk-cities__photo{aspect-ratio:4/3;background:#4a1fa0 center/cover no-repeat}
.rk-cities__label{padding:12px 10px 14px;font:600 14px/1.35 "Open Sans",Arial,sans-serif;text-align:center}
.rk-old-cities{display:none!important}
</style>
"""


def abs_assets(html: str, *, depth: int) -> str:
    """Convert ../../ or ../../../assets to /assets for mask/img reliability."""
    if depth >= 3:
        html = html.replace("../../../assets/", "/assets/")
    html = html.replace("../../assets/", "/assets/")
    return html


def fix_case_links(html: str) -> str:
    for drive_id, url in CASE_HREFS.items():
        html = re.sub(
            rf'href="[^"]*{re.escape(drive_id)}[^"]*"',
            f'href="{url}"',
            html,
        )
    # Eurasia card is gallery-image--3 and wrongly points to pilates drive id.
    # After generic replace both 0 and 3 point to keysy — fix card 3 specifically.
    html = re.sub(
        r'(class="section__gallery-image section__gallery-image--3"[^>]*href=")[^"]+(")',
        rf'\1{EURASIA_URL}\2',
        html,
        count=1,
    )
    # Also if href comes before class
    html = re.sub(
        r'(href=")[^"]+("\s+target="_blank"\s+class="section__gallery-image section__gallery-image--3")',
        rf'\1{EURASIA_URL}\2',
        html,
        count=1,
    )
    return html


def linkify_price_titles(html: str, in_phrase: str | None) -> str:
    """Make price title names into <a>. Optionally insert city phrase before «от»."""
    for title, href in PRICE_LINKS:
        pattern = re.compile(
            re.escape(title)
            + r"(?:\s+в\s+[А-Яа-яЁё\-]+)?"
            + r"(\s+от\s+[\d.]+\s+тенге)"
        )

        def safe_repl(m: re.Match, _title=title, _href=href) -> str:
            start = m.start()
            window = html[max(0, start - 100) : start]
            last_a = window.rfind("<a ")
            last_close = window.rfind("</a>")
            if last_a > last_close:
                return m.group(0)
            label = f"{_title} {in_phrase}" if in_phrase else _title
            return (
                f'<a href="{_href}" data-page-link="{_href}" '
                f'style="color:inherit;text-decoration:underline;text-underline-offset:3px">'
                f"{label}</a>{m.group(1)}"
            )

        html, n = pattern.subn(safe_repl, html)
        if n == 0:
            print(f"  WARN: price title not found: {title}")
        else:
            print(f"  price linked x{n}: {title}")
    return html


def mottor_img_for_hash(file_hash: str, asset_prefix: str) -> str:
    """Best-effort path to an existing mottor crop for known hashes."""
    # Prefer any existing resized webp under that hash folder
    base = MIRROR / "assets" / "m-files.cdn1.cc" / "lpfile"
    # hash path a/b/c/hash
    a, b, c = file_hash[0], file_hash[1], file_hash[2]
    folder = base / a / b / c / file_hash
    if folder.exists():
        webs = list(folder.rglob("*.webp"))
        if webs:
            # pick a mid-size-ish
            webs.sort(key=lambda p: p.stat().st_size)
            rel = webs[len(webs) // 2].relative_to(MIRROR / "assets").as_posix()
            return f"{asset_prefix}{rel}"
    return ""


def ensure_city_photos() -> dict[str, str]:
    """Return slug → /assets/... URL for card photo."""
    CITIES_DIR.mkdir(parents=True, exist_ok=True)
    out: dict[str, str] = {}
    for city, slug in CITY_SLUG.items():
        if slug in EXISTING_CITY_IMGS:
            path = mottor_img_for_hash(EXISTING_CITY_IMGS[slug], "/assets/")
            if path:
                out[slug] = path
                continue
        dest = CITIES_DIR / f"{slug}.jpg"
        if not dest.exists() or dest.stat().st_size < 1000:
            urls = [CITY_PHOTO_URLS[slug]] if slug in CITY_PHOTO_URLS else []
            ok = False
            for url in urls:
                try:
                    req = urllib.request.Request(
                        url,
                        headers={"User-Agent": "RaskrutovCityFix/1.0"},
                    )
                    with urllib.request.urlopen(req, timeout=25) as resp:
                        data = resp.read()
                    if len(data) > 2000:
                        dest.write_bytes(data)
                        ok = True
                        print(f"  downloaded photo {slug} ({len(data)} bytes)")
                        break
                except Exception as e:
                    print(f"  photo fail {slug} {url[:60]}…: {e}")
            if not ok and not dest.exists():
                # 1x1 purple jpeg-ish placeholder via minimal SVG saved as .svg
                svg = CITIES_DIR / f"{slug}.svg"
                svg.write_text(
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480">'
                    f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
                    f'<stop stop-color="#7b3ff2"/><stop offset="1" stop-color="#3d1a8c"/></linearGradient></defs>'
                    f'<rect width="100%" height="100%" fill="url(#g)"/>'
                    f'<text x="50%" y="52%" fill="#fff" font-size="42" font-family="Arial" '
                    f'text-anchor="middle">{city}</text></svg>',
                    encoding="utf-8",
                )
                out[slug] = f"/assets/rk-cities/{slug}.svg"
                continue
        if dest.exists():
            out[slug] = f"/assets/rk-cities/{slug}.jpg"
        else:
            out[slug] = f"/assets/rk-cities/{slug}.svg"
    return out


def build_cities_html(photos: dict[str, str]) -> str:
    cards = []
    for city in CITY_ORDER:
        slug = CITY_SLUG[city]
        in_phrase = CITY_IN[city]
        # «Создание сайтов в Астане» — CITY_IN already has «в …»
        label = f"Создание сайтов {in_phrase}"
        href = f"/web-studiya/sozdanie-saitov/{slug}/"
        photo = photos.get(slug, "")
        cards.append(
            f'<a class="rk-cities__card" href="{href}" data-page-link="{href}">'
            f'<span class="rk-cities__photo" style="background-image:url(\'{photo}\')"></span>'
            f'<span class="rk-cities__label">{label}</span></a>'
        )
    return (
        CITIES_CSS
        + '<div class="rk-cities" data-rk-cities-grid="1">'
        + '<div class="rk-cities__grid">'
        + "".join(cards)
        + "</div></div>"
    )


def inject_cities_block(html: str, photos: dict[str, str]) -> str:
    # Remove previous injection
    html = re.sub(
        r'<style data-rk-cities="1">[\s\S]*?</style>\s*',
        "",
        html,
        count=1,
    )
    html = re.sub(
        r'<div class="rk-cities"[^>]*>[\s\S]*?</div>\s*',
        "",
        html,
        count=1,
    )
    html = re.sub(r"<!-- rk: old mottor cities removed -->\s*", "", html)

    # Hard-remove Mottor 5-city columns block (and any orphan columns)
    old_id = "63d1e42879dc48978a61f28aa874e3c4"
    start = html.find(f'id="{old_id}"')
    if start >= 0:
        start = html.rfind('<div class="blk blk_ms', 0, start)
        if start >= 0:
            i, depth, end = start, 0, None
            while i < len(html):
                if html.startswith("<div", i):
                    depth += 1
                    i = html.find(">", i) + 1
                    continue
                if html.startswith("</div>", i):
                    depth -= 1
                    i += 6
                    if depth == 0:
                        end = i
                        break
                    continue
                i += 1
            if end:
                html = html[:start] + "<!-- rk: old mottor cities removed -->" + html[end:]

    for col in range(0, 5):
        marker = f"m-columns__column--{col} m-columns__column--{old_id}"
        while marker in html:
            pos = html.find(marker)
            s = html.rfind("<div", 0, pos)
            if s < 0:
                break
            i, depth, end = s, 0, None
            while i < len(html):
                if html.startswith("<div", i):
                    depth += 1
                    i = html.find(">", i) + 1
                    continue
                if html.startswith("</div>", i):
                    depth -= 1
                    i += 6
                    if depth == 0:
                        end = i
                        break
                    continue
                i += 1
            if end is None:
                break
            html = html[:s] + html[end:]

    block = build_cities_html(photos)
    marker = "Мы работаем по всему Казахстану"
    idx = html.find(marker)
    if idx < 0:
        print("  WARN: cities heading not found")
        return html

    h2_end = html.find("</h2>", idx)
    if h2_end < 0:
        return html
    insert_at = h2_end + len("</h2>")
    html = html[:insert_at] + block + html[insert_at:]
    return html


def fix_existing_city_links(html: str) -> str:
    """Legacy no-op: old Mottor city cards are removed."""
    return html


def patch_html(html: str, *, in_phrase: str | None, photos: dict[str, str], depth: int) -> str:
    html = fix_case_links(html)
    html = linkify_price_titles(html, in_phrase)
    html = inject_cities_block(html, photos)
    html = fix_existing_city_links(html)
    # abs_assets disabled — breaks file:// and was unnecessary on HTTP with deepen
# html = abs_assets(html, depth=depth)
    # Eurasia title card: after CASE_HREFS, gallery--3 may still need EURASIA
    # Fix duplicate pilates link on card 3 by title proximity
    if "Eurasia Polymer" in html:
        # ensure the <a> immediately before Eurasia points to sherdar
        html = re.sub(
            r'(<a href=")[^"]+("\s+target="_blank"\s+class="section__gallery-image section__gallery-image--3">[\s\S]{0,1200}?Eurasia Polymer)',
            rf"\1{EURASIA_URL}\2",
            html,
            count=1,
        )
    return html


def main() -> None:
    photos = ensure_city_photos()
    print("Photos ready:", len(photos))

    donor = DONOR.read_text(encoding="utf-8")
    donor = patch_html(donor, in_phrase=None, photos=photos, depth=2)
    DONOR.write_text(donor, encoding="utf-8")
    print("Updated donor", DONOR)

    meta = load_final_meta()
    matrix = load_matrix_sozdanie()
    for row in matrix:
        city = row["Город"].strip()
        slug = CITY_SLUG[city]
        in_phrase = CITY_IN[city]
        pretty = f"/web-studiya/sozdanie-saitov/{slug}"
        m = meta.get(city) or {}
        h1 = m.get("h1") or f"Создание сайтов {in_phrase}"
        title = m.get("title") or f"Создание сайтов {in_phrase} под ключ | Raskrutov"
        description = m.get("description") or (
            f"Создаём сайты для бизнеса {in_phrase}: лендинги, корпоративные сайты и "
            f"интернет-магазины с подготовкой к SEO, рекламе и продажам."
        )
        html = deepen_prefixes(donor)
        # donor already has abs /assets/ — deepen shouldn't break those
        # keep relative assets from deepen_prefixes
        html = replace_seo(
            html, h1=h1, title=title, description=description, pretty=pretty
        )
        # Re-linkify prices WITH city (donor had no city phrase)
        # Strip existing price <a> wrappers first then re-apply with city
        for t, href in PRICE_LINKS:
            html = re.sub(
                rf'<a href="{re.escape(href)}"[^>]*>'
                + re.escape(t)
                + r"(?:\s+в\s+[А-Яа-яЁё\-]+)?"
                + r"</a>",
                t,
                html,
            )
        html = linkify_price_titles(html, in_phrase)

        # Soft-regionalize portfolio descriptions only (not the cities grid!)
        def regionalize_desc(m: re.Match) -> str:
            s = m.group(0)
            s = s.replace("в городе Петропавловск", f"в городе {city}")
            s = s.replace("в Петропавловске", in_phrase)
            s = s.replace("в Алматы", in_phrase)
            s = s.replace("в Астане", in_phrase)
            return s

        html = re.sub(
            r'<div class="content__desc[^"]*">[\s\S]*?</div>',
            regionalize_desc,
            html,
        )

        out = MIRROR / pretty.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"OK geo {slug}")

    print("DONE")


if __name__ == "__main__":
    main()
