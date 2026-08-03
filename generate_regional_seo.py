# -*- coding: utf-8 -*-
"""Generate pretty regional SEO pages: /web-studiya/seo-prodvizhenie/{city}.

Donor: site_mirror/web-studiya/seo-prodvizhenie/index.html (depth 2)
Target depth 3 → deepen ../../ → ../../../
Legacy /seo-prodvizhenie-sajtov-v-* → 301 pretty.
Also: cities grid on parent+geo, fix broken Mottor showPopup.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "site_mirror"
DONOR = MIRROR / "web-studiya" / "seo-prodvizhenie" / "index.html"
MATRIX = ROOT / "docs" / "seo-regional" / "REGIONAL_MATRIX.csv"
FINAL = ROOT / "docs" / "seo-regional" / "FINAL_SEO_MAP.csv"
URL_MAP = ROOT / "url_mapping.json"
SITEMAP = MIRROR / "sitemap.xml"
HTACCESS = MIRROR / ".htaccess"
CITIES_DIR = MIRROR / "assets" / "rk-cities"

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
    "Астана", "Алматы", "Шымкент", "Караганда", "Петропавловск", "Актобе",
    "Атырау", "Павлодар", "Усть-Каменогорск", "Семей", "Костанай", "Кызылорда",
    "Уральск", "Тараз", "Актау", "Туркестан", "Кокшетау", "Талдыкорган",
]

CITIES_CSS = """
<style data-rk-cities="1">
.rk-cities{margin:24px auto 8px;max-width:1200px;padding:0 16px;box-sizing:border-box}
.rk-cities__title{margin:0 0 16px;font:700 28px/1.25 Montserrat,"Open Sans",Arial,sans-serif;color:#222;text-align:center}
.rk-cities__grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px}
@media(max-width:1100px){.rk-cities__grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:640px){.rk-cities__grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}
.rk-cities__card{display:flex;flex-direction:column;background:#6b2fd6;border-radius:14px;overflow:hidden;text-decoration:none;color:#fff;box-shadow:0 8px 24px rgba(60,20,120,.18);transition:transform .2s ease,box-shadow .2s ease}
.rk-cities__card:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(60,20,120,.28);color:#fff}
.rk-cities__photo{aspect-ratio:4/3;background:#4a1fa0 center/cover no-repeat}
.rk-cities__label{padding:12px 10px 14px;font:600 14px/1.35 "Open Sans",Arial,sans-serif;text-align:center}
</style>
"""

SHOWPOPUP_RE = re.compile(
    r'act="showPopup"\s+onclick="return msJsWrapper\(event,\'([^\']+)\',\'showPopup\'\);"\s+'
    r'data-page-link="([^"]*)"\s+data-popup-id="([^"]+)"'
)


def load_matrix_seo() -> list[dict]:
    rows = list(csv.DictReader(MATRIX.open(encoding="utf-8-sig"), delimiter=";"))
    return [r for r in rows if r["Направление"] == "SEO-продвижение"]


def load_final_meta() -> dict[str, dict]:
    out: dict[str, dict] = {}
    rows = list(csv.DictReader(FINAL.open(encoding="utf-8-sig"), delimiter=";"))
    for r in rows:
        name = (r.get("Название страницы") or "").strip()
        if not name.startswith("SEO-продвижение сайтов в "):
            continue
        city = name.replace("SEO-продвижение сайтов в ", "", 1).strip()
        out[city] = {
            "h1": (r.get("H1") or name).strip(),
            "title": (r.get("Title") or "").strip(),
            "description": (r.get("Description") or "").strip(),
            "legacy": (r.get("Итоговый URL") or "").strip().split(";")[0].strip(),
        }
    return out


def deepen_prefixes(html: str) -> str:
    html = html.replace("../../assets/", "../../../assets/")
    html = html.replace("../../favicon", "../../../favicon")

    siblings = {"google", "yandex"}

    def fix_href(m: re.Match) -> str:
        attr, q, path = m.group(1), m.group(2), m.group(3)
        if path.startswith(("http", "mailto", "tel", "#", "data:", "javascript:")):
            return m.group(0)
        if "assets/" in path or path.startswith("../../../"):
            return m.group(0)
        bare = path.strip("/").split("/")[0]
        if path.startswith("../") and not path.startswith("../../"):
            rest = path[3:]
            first = rest.split("/")[0]
            if first in siblings or rest in ("", "."):
                return m.group(0)
            return f"{attr}={q}../../{rest}{q}"
        if path.startswith("/") and not path.startswith("//"):
            return m.group(0)
        if bare in siblings and not path.startswith("."):
            return f"{attr}={q}../{path.lstrip('./')}{q}"
        return m.group(0)

    return re.sub(
        r'\b(href|src|data-page-link|action)=([\'"])([^\'"]+)\2',
        fix_href,
        html,
        flags=re.I,
    )


def fix_showpopup(html: str) -> str:
    def repl(m: re.Match) -> str:
        popup = m.group(3)
        return (
            f'act="showPopup" onclick="showSectionPopup(\'{popup}\'); return false;" '
            f'data-page-link="{m.group(2)}" data-popup-id="{popup}"'
        )

    return SHOWPOPUP_RE.sub(repl, html)


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

    # Soft unique strings (don't mass-replace Казахстан in schema org)
    html = html.replace("SEO-продвижение сайтов в Казахстане", h1, 4)
    html = html.replace(
        "Продвигаем сайты в Google и Яндекс: структура, семантика, контент, техническая оптимизация и рост коммерческих запросов.",
        description,
        2,
    )
    if city:
        # schema areaServed name if present as Казахстан near Service
        html = re.sub(
            r'("areaServed"\s*:\s*\{[^}]*"name"\s*:\s*")Казахстан(")',
            rf"\1{city}\2",
            html,
            count=1,
        )
        html = re.sub(
            r'("name"\s*:\s*")Казахстан("\s*\})',
            rf"\1{city}\2",
            html,
            count=2,
        )
    return html


def cities_block(asset_prefix: str, link_prefix: str) -> str:
    """asset_prefix e.g. ../../assets/rk-cities/ ; link_prefix e.g. /web-studiya/seo-prodvizhenie/"""
    cards = []
    for city in CITY_ORDER:
        slug = CITY_SLUG[city]
        href = f"{link_prefix.rstrip('/')}/{slug}/"
        photo = f"{asset_prefix.rstrip('/')}/{slug}.jpg"
        jpg = CITIES_DIR / f"{slug}.jpg"
        if not jpg.exists():
            photo = f"{asset_prefix.rstrip('/')}/{slug}.svg"
        label = f"SEO {CITY_IN[city]}"
        cards.append(
            f'<a class="rk-cities__card" href="{href}" data-page-link="{href}">'
            f'<span class="rk-cities__photo" style="background-image:url(\'{photo}\')"></span>'
            f'<span class="rk-cities__label">{label}</span></a>'
        )
    return (
        CITIES_CSS
        + '<div class="rk-cities" data-rk-cities-grid="1">'
        + '<h2 class="rk-cities__title">SEO-продвижение по городам Казахстана</h2>'
        + '<div class="rk-cities__grid">'
        + "".join(cards)
        + "</div></div>"
    )


def inject_cities(html: str, asset_prefix: str, link_prefix: str) -> str:
    html = re.sub(r'<style data-rk-cities="1">[\s\S]*?</style>\s*', "", html)
    html = re.sub(
        r'<div class="rk-cities"[^>]*>[\s\S]*?</div>\s*(?=<div class="rk-cities"|<h2[^>]*>Контакты|$)',
        "",
        html,
        count=1,
    )
    # simpler: remove prior grid markers
    html = re.sub(r'<div class="rk-cities"[^>]*data-rk-cities-grid="1"[\s\S]*?</div>\s*</div>\s*', "", html)
    block = cities_block(asset_prefix, link_prefix)
    # insert before Контакты heading
    m = re.search(r"<h2[^>]*>\s*Контакты\s*</h2>", html, flags=re.I)
    if m:
        return html[: m.start()] + block + html[m.start() :]
    # fallback before </body>
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


def upsert_htaccess(legacy_to_pretty: list[tuple[str, str]]) -> None:
    text = HTACCESS.read_text(encoding="utf-8")
    marker = "# Regional seo-prodvizhenie pretty redirects (auto)"
    block_lines = [marker]
    for legacy, pretty in legacy_to_pretty:
        old = legacy.strip().strip("/")
        new = pretty.rstrip("/") + "/"
        block_lines.append(f"Redirect 301 /{old} {new}")
        block_lines.append(f"Redirect 301 /{old}/ {new}")
    block = "\n".join(block_lines) + "\n"

    if marker in text:
        text = re.sub(
            rf"{re.escape(marker)}[\s\S]*?(?=\n# [A-Za-z]|\Z)",
            block,
            text,
            count=1,
        )
    else:
        text = text.rstrip() + "\n\n" + block
    HTACCESS.write_text(text, encoding="utf-8")


def upsert_url_mapping(items: list[tuple[str, str]]) -> None:
    data = json.loads(URL_MAP.read_text(encoding="utf-8"))
    for pages_name, pretty in items:
        data[pages_name] = pretty.strip("/")
    URL_MAP.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_pages_stub(pages_name: str, pretty: str) -> None:
    pages = MIRROR / "pages"
    pages.mkdir(exist_ok=True)
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
    (pages / pages_name).write_text(stub, encoding="utf-8")


def prepare_donor() -> str:
    """Fix parent SEO page H1/CTA/cities, return donor html for cloning."""
    html = DONOR.read_text(encoding="utf-8")
    html = fix_showpopup(html)
    parent_h1 = "SEO-продвижение сайтов в Казахстане"
    parent_title = "SEO-продвижение сайтов в Казахстане | Raskrutov"
    parent_desc = (
        "Продвигаем сайты в Google и Яндекс: семантика, структура, контент, "
        "техническая оптимизация, аналитика и развитие коммерческих страниц."
    )
    html = replace_seo(
        html,
        h1=parent_h1,
        title=parent_title,
        description=parent_desc,
        pretty="/web-studiya/seo-prodvizhenie",
        city=None,
    )
    html = inject_cities(html, "../../assets/rk-cities", "/web-studiya/seo-prodvizhenie")
    DONOR.write_text(html, encoding="utf-8")
    return html


def main() -> int:
    donor = prepare_donor()
    matrix = load_matrix_seo()
    meta = load_final_meta()

    created: list[str] = []
    redirects: list[tuple[str, str]] = []
    url_map_items: list[tuple[str, str]] = []

    for row in matrix:
        city = row["Город"].strip()
        slug = CITY_SLUG.get(city)
        if not slug:
            raise SystemExit(f"No slug for city {city!r}")
        pretty = f"/web-studiya/seo-prodvizhenie/{slug}"
        legacy = (row.get("Региональный URL") or "").strip()
        m = meta.get(city) or {}
        in_phrase = CITY_IN[city]
        h1 = m.get("h1") or f"SEO-продвижение сайтов {in_phrase}"
        title = m.get("title") or f"SEO-продвижение сайтов {in_phrase} | Raskrutov"
        description = m.get("description") or (
            f"SEO-продвижение сайтов компаний {in_phrase}: семантика, структура, "
            f"техническая оптимизация, контент, аналитика и рост видимости в поиске."
        )
        if m.get("legacy"):
            legacy = m["legacy"] or legacy

        html = deepen_prefixes(donor)
        html = fix_showpopup(html)
        html = replace_seo(
            html, h1=h1, title=title, description=description, pretty=pretty, city=city
        )
        # re-inject cities with depth-3 asset prefix (donor already had depth-2)
        html = inject_cities(html, "../../../assets/rk-cities", "/web-studiya/seo-prodvizhenie")

        out = MIRROR / pretty.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        created.append(pretty)

        if legacy and legacy.startswith("/") and "seo-prodvizhenie-sajtov-v-" in legacy:
            redirects.append((legacy, pretty))
            leaf = legacy.strip("/").replace("/", "_") + ".html"
            write_pages_stub(leaf, pretty)
            url_map_items.append((leaf, pretty.strip("/")))

        print(f"OK {pretty}  ← {legacy or 'NEW'}  H1={h1!r}")

    upsert_sitemap(created)
    upsert_htaccess(redirects)
    upsert_url_mapping(url_map_items)
    print(f"\nCreated {len(created)} pages, {len(redirects)} legacy redirects")
    print("Parent cities injected + H1 fixed + showPopup fixed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
