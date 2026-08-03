# -*- coding: utf-8 -*-
"""Generate regional design pages: /web-studiya/dizayn/{city}/

Donor: site_mirror/web-studiya/dizayn/index.html (depth 2 → ../../assets)
Geo depth 3 → ../../../assets
No legacy redirects (all NEW pretty URLs).
Also: cities grid on parent+geo, fix showPopup, wire hubs → dizayn/{city}.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "site_mirror"
DONOR = MIRROR / "web-studiya" / "dizayn" / "index.html"
MATRIX = ROOT / "docs" / "seo-regional" / "REGIONAL_MATRIX.csv"
FINAL = ROOT / "docs" / "seo-regional" / "FINAL_SEO_MAP.csv"
SITEMAP = MIRROR / "sitemap.xml"
CITIES_DIR = MIRROR / "assets" / "rk-cities"
HUBS_ROOT = MIRROR / "web-studiya"

CITY_SLUG = {
    "Алматы": "almaty",
    "Астана": "astana",
    "Шымкент": "shymkent",
    "Актау": "aktau",
    "Актобе": "aktobe",
    "Атырау": "atyrau",
    "Караганда": "karaganda",
    "Кокшетау": "kokshetau",
    "Костанай": "kostanay",
    "Кызылорда": "kyzylorda",
    "Павлодар": "pavlodar",
    "Петропавловск": "petropavlovsk",
    "Семей": "semey",
    "Талдыкорган": "taldykorgan",
    "Тараз": "taraz",
    "Туркестан": "turkestan",
    "Уральск": "uralsk",
    "Усть-Каменогорск": "ust-kamenogorsk",
}

CITY_IN = {
    "Алматы": "в Алматы",
    "Астана": "в Астане",
    "Шымкент": "в Шымкенте",
    "Актау": "в Актау",
    "Актобе": "в Актобе",
    "Атырау": "в Атырау",
    "Караганда": "в Караганде",
    "Кокшетау": "в Кокшетау",
    "Костанай": "в Костанае",
    "Кызылорда": "в Кызылорде",
    "Павлодар": "в Павлодаре",
    "Петропавловск": "в Петропавловске",
    "Семей": "в Семее",
    "Талдыкорган": "в Талдыкоргане",
    "Тараз": "в Таразе",
    "Туркестан": "в Туркестане",
    "Уральск": "в Уральске",
    "Усть-Каменогорск": "в Усть-Каменогорске",
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

MOTTOR_PHOTOS = {
    "astana": "assets/m-files.cdn1.cc/lpfile/3/2/e/32e8eac576d37936896bba2a35b52bdc/-/crop/0x21x650x391/-/resize/330/f__q_47567714.webp",
    "almaty": "assets/m-files.cdn1.cc/lpfile/0/5/f/05fba2f37e0d0ebf16bf74efc995e0b9/-/crop/384x0x1154x700/-/resize/330/f__q_36994489.webp",
    "shymkent": "assets/m-files.cdn1.cc/lpfile/d/8/e/d8eb27b3bca04551081de512908b16a5/-/crop/0x38x1280x779/-/resize/330/f__q_10804456.webp",
    "karaganda": "assets/m-files.cdn1.cc/lpfile/4/1/6/4164fcbd8cd10da83d49ff55b12a2220/-/crop/25x94x689x418/-/resize/330/f__q_78422993.webp",
    "petropavlovsk": "assets/m-files.cdn1.cc/lpfile/c/6/9/c6937ec1201641a5666bc4606abdb165/-/crop/0x6x1024x607/-/resize/327/f__q_73159820.webp",
}

SIBLINGS = {"neyming", "logotip", "brendbuk"}

SHOWPOPUP_RE = re.compile(
    r'act="showPopup"\s+onclick="return msJsWrapper\(event,\'([^\']+)\',\'showPopup\'\);"\s+'
    r'data-page-link="([^"]*)"\s+data-popup-id="([^"]+)"'
)

CITIES_CSS = """
<style data-rk-cities="1">
.rk-cities{display:flow-root;margin:56px auto 0 !important;max-width:1200px;padding:16px 16px 72px !important;box-sizing:border-box;text-align:center}
.rk-cities__title{display:block;width:100%;margin:0 0 40px !important;padding:0;font:700 28px/1.25 Montserrat,"Open Sans",Arial,sans-serif;color:#1e1e1e;text-align:center !important}
.rk-cities__grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px;margin:0;text-align:left}
@media(max-width:1100px){.rk-cities__grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:640px){.rk-cities__grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.rk-cities{margin:40px auto 0 !important;padding:12px 16px 48px !important}.rk-cities__title{margin:0 0 28px !important;font-size:22px}}
.rk-cities__card{display:flex;flex-direction:column;background:#006fdc;border-radius:14px;overflow:hidden;text-decoration:none;color:#fff;box-shadow:0 8px 24px rgba(0,111,220,.16);transition:transform .2s ease,box-shadow .2s ease}
.rk-cities__card:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(0,111,220,.26);color:#fff}
.rk-cities__photo{display:block;width:100%;height:auto;aspect-ratio:4/3;min-height:140px;object-fit:cover;background:#d7ebff}
.rk-cities__label{padding:12px 10px 14px;font:600 14px/1.35 "Open Sans",Arial,sans-serif;text-align:center;background:#006fdc;color:#fff}
.rk-cities + h2,.rk-cities + h2.blk-data{margin-top:32px !important;padding-top:16px !important}
</style>
"""


def load_matrix() -> list[dict]:
    rows = list(csv.DictReader(MATRIX.open(encoding="utf-8-sig"), delimiter=";"))
    return [r for r in rows if r["Направление"] == "Услуги дизайнера"]


def load_final_meta() -> dict[str, dict]:
    out: dict[str, dict] = {}
    rows = list(csv.DictReader(FINAL.open(encoding="utf-8-sig"), delimiter=";"))
    for r in rows:
        name = (r.get("Название страницы") or "").strip()
        if not name.startswith("Услуги дизайнера в "):
            continue
        city = name.replace("Услуги дизайнера в ", "", 1).strip()
        out[city] = {
            "h1": (r.get("H1") or name).strip(),
            "title": (r.get("Title") or "").strip(),
            "description": (r.get("Description") or "").strip(),
        }
    return out


def fix_showpopup(html: str) -> str:
    def repl(m: re.Match) -> str:
        popup = m.group(3)
        return (
            f'act="showPopup" onclick="showSectionPopup(\'{popup}\'); return false;" '
            f'data-page-link="{m.group(2)}" data-popup-id="{popup}"'
        )

    return SHOWPOPUP_RE.sub(repl, html)


def deepen_prefixes(html: str) -> str:
    html = html.replace("../../assets/", "../../../assets/")
    html = html.replace("../../favicon", "../../../favicon")

    def fix_href(m: re.Match) -> str:
        attr, q, path = m.group(1), m.group(2), m.group(3)
        if path.startswith(("http", "mailto", "tel", "#", "data:", "javascript:")):
            return m.group(0)
        if "assets/" in path or path.startswith("../../../"):
            return m.group(0)
        if path.startswith("../") and not path.startswith("../../"):
            rest = path[3:]
            first = rest.split("/")[0]
            if first in SIBLINGS or rest in ("", "."):
                return m.group(0)
            return f"{attr}={q}../../{rest}{q}"
        if path.startswith("/") and not path.startswith("//"):
            return m.group(0)
        bare = path.strip("/").split("/")[0]
        if bare in SIBLINGS and not path.startswith("."):
            return f"{attr}={q}../{path.lstrip('./')}{q}"
        return m.group(0)

    return re.sub(
        r'\b(href|src|data-page-link|action)=([\'"])([^\'"]+)\2',
        fix_href,
        html,
        flags=re.I,
    )


def replace_seo(
    html: str,
    *,
    h1: str,
    title: str,
    description: str,
    pretty: str,
    city: str | None = None,
) -> str:
    canon = "https://raskrutov.kz" + pretty.rstrip("/")
    html = re.sub(r"<title>[^<]*</title>", f"<title>{title}</title>", html, count=1, flags=re.I)
    html = re.sub(
        r'(<meta\s+name=["\']description["\']\s+content=["\'])[^"\']*(["\'])',
        rf"\1{description}\2",
        html,
        count=1,
        flags=re.I,
    )
    html = re.sub(
        r'(property=["\']og:title["\']\s+content=["\'])[^"\']*(["\'])',
        rf"\1{title}\2",
        html,
        count=1,
        flags=re.I,
    )
    html = re.sub(
        r'(property=["\']og:description["\']\s+content=["\'])[^"\']*(["\'])',
        rf"\1{description}\2",
        html,
        count=1,
        flags=re.I,
    )
    html = re.sub(
        r'(property=["\']og:url["\']\s+content=["\'])[^"\']*(["\'])',
        rf"\1{canon}\2",
        html,
        count=1,
        flags=re.I,
    )
    html = re.sub(
        r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\']\s*/?>',
        f'<link rel="canonical" href="{canon}"/>',
        html,
        count=1,
        flags=re.I,
    )
    html, _ = re.subn(
        r"<h1([^>]*)>([\s\S]*?)</h1>",
        lambda m: f"<h1{m.group(1)}>{h1}</h1>",
        html,
        count=1,
        flags=re.I,
    )
    # Do NOT blanket-replace «Услуги дизайнера» — geo H1 starts with that substring.
    html = html.replace(
        "Дизайн для бизнеса - логотип, брендбук и визуальная упаковка",
        title,
        2,
    )
    html = html.replace(
        "Дизайн для бизнеса — логотип, брендбук и визуальная упаковка",
        title,
        2,
    )
    html = html.replace(
        "Разрабатываем визуальную основу бренда: нейминг, логотип, брендбук, фирменный стиль и дизайн-материалы.",
        description,
        2,
    )
    if city:
        html = re.sub(
            r'("areaServed"\s*:\s*\{[^}]*"name"\s*:\s*")Казахстан(")',
            rf"\1{city}\2",
            html,
            count=1,
        )
    return html


def photo_for(slug: str, depth: int) -> str:
    prefix = "../" * depth
    if slug in MOTTOR_PHOTOS:
        return prefix + MOTTOR_PHOTOS[slug]
    jpg = CITIES_DIR / f"{slug}.jpg"
    if jpg.exists():
        return prefix + f"assets/rk-cities/{slug}.jpg"
    return prefix + f"assets/rk-cities/{slug}.svg"


def cities_block(depth: int, title: str) -> str:
    cards = []
    for city in CITY_ORDER:
        slug = CITY_SLUG[city]
        href = f"/web-studiya/dizayn/{slug}/"
        src = photo_for(slug, depth)
        label = f"Дизайн {CITY_IN[city]}"
        cards.append(
            f'<a class="rk-cities__card" href="{href}" data-page-link="{href}">'
            f'<img class="rk-cities__photo" src="{src}" alt="" loading="lazy" decoding="async" width="330" height="248"/>'
            f'<span class="rk-cities__label">{label}</span></a>'
        )
    return (
        CITIES_CSS
        + '<div class="rk-cities" data-rk-cities-grid="1">'
        + f'<h2 class="rk-cities__title">{title}</h2>'
        + '<div class="rk-cities__grid">'
        + "".join(cards)
        + "</div></div>"
    )


def inject_cities(html: str, depth: int, title: str) -> str:
    html = re.sub(r'<style data-rk-cities="1">[\s\S]*?</style>\s*', "", html)
    html = re.sub(
        r'<div class="rk-cities"[^>]*data-rk-cities-grid="1"[\s\S]*?</div>\s*</div>\s*',
        "",
        html,
    )
    block = cities_block(depth, title)
    m = re.search(
        r'<div\s+blk_class="section"[^>]*data-tpl-id="1087"[^>]*>',
        html,
        flags=re.I,
    )
    if not m:
        m = re.search(r"<h2[^>]*>\s*Контакты\s*</h2>", html, flags=re.I)
    if m:
        return html[: m.start()] + block + html[m.start() :]
    return html.replace("</body>", block + "</body>", 1)


def upsert_sitemap(urls: list[str]) -> None:
    text = SITEMAP.read_text(encoding="utf-8")
    for pretty in urls:
        loc = f"https://raskrutov.kz{pretty.rstrip('/')}"
        if loc in text:
            continue
        entry = (
            f"  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <changefreq>weekly</changefreq>\n"
            f"    <priority>0.7</priority>\n"
            f"  </url>\n"
        )
        text = text.replace("</urlset>", entry + "</urlset>")
    SITEMAP.write_text(text, encoding="utf-8")


def wire_hubs_to_dizayn_geo() -> int:
    """Point hub «Дизайн» cards at /web-studiya/dizayn/{slug}/."""
    n = 0
    for city, slug in CITY_SLUG.items():
        p = HUBS_ROOT / slug / "index.html"
        if not p.exists():
            continue
        html = p.read_text(encoding="utf-8")
        old = 'href="/web-studiya/dizayn/" data-page-link="/web-studiya/dizayn/"'
        new = (
            f'href="/web-studiya/dizayn/{slug}/" '
            f'data-page-link="/web-studiya/dizayn/{slug}/"'
        )
        if old not in html:
            # already geo or different markup
            if f"/web-studiya/dizayn/{slug}/" in html:
                continue
            continue
        html = html.replace(old, new, 1)
        # also title line "Дизайн" → "Дизайн в …" if plain
        html = html.replace(
            f">{new}>Дизайн<span>",
            f"{new}>Дизайн {CITY_IN[city]}<span>",
            1,
        )
        p.write_text(html, encoding="utf-8")
        n += 1
    return n


def prepare_parent() -> str:
    html = DONOR.read_text(encoding="utf-8")
    html = fix_showpopup(html)
    html = replace_seo(
        html,
        h1="Услуги дизайнера",
        title="Дизайн для бизнеса — логотип, брендбук и визуальная упаковка | Raskrutov",
        description=(
            "Разрабатываем визуальную основу бренда: нейминг, логотип, брендбук, "
            "фирменный стиль и дизайн-материалы."
        ),
        pretty="/web-studiya/dizayn",
        city=None,
    )
    html = inject_cities(html, 2, "Дизайн в городах Казахстана")
    DONOR.write_text(html, encoding="utf-8")
    return html


def main() -> int:
    prepare_parent()
    donor = DONOR.read_text(encoding="utf-8")
    matrix = load_matrix()
    meta = load_final_meta()
    created: list[str] = []

    for row in matrix:
        city = row["Город"].strip()
        slug = CITY_SLUG[city]
        pretty = f"/web-studiya/dizayn/{slug}"
        in_phrase = CITY_IN[city]
        m = meta.get(city) or {}
        h1 = m.get("h1") or f"Услуги дизайнера и веб-дизайн {in_phrase}"
        title = m.get("title") or f"Услуги дизайнера {in_phrase} | Raskrutov"
        description = m.get("description") or (
            f"Дизайн для бизнеса {in_phrase}: сайты, логотипы, фирменный стиль, "
            f"брендбук и визуальные материалы с понятным процессом и результатом."
        )

        html = deepen_prefixes(donor)
        # strip parent cities before re-inject at depth 3
        html = re.sub(r'<style data-rk-cities="1">[\s\S]*?</style>\s*', "", html)
        html = re.sub(
            r'<div class="rk-cities"[^>]*data-rk-cities-grid="1"[\s\S]*?</div>\s*</div>\s*',
            "",
            html,
        )
        html = fix_showpopup(html)
        html = replace_seo(
            html, h1=h1, title=title, description=description, pretty=pretty, city=city
        )
        html = inject_cities(html, 3, "Дизайн в других городах")

        out = MIRROR / pretty.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        created.append(pretty)
        print(f"OK {pretty}  H1={h1!r}")

    upsert_sitemap(created)
    hubs = wire_hubs_to_dizayn_geo()
    print(f"\nCreated {len(created)} dizayn geo; hubs wired={hubs}; parent cities updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
