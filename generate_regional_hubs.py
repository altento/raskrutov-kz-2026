# -*- coding: utf-8 -*-
"""Generate city hubs: /web-studiya/{city}/

Donor: site_mirror/web-studiya/index.html (depth 1 → ../assets)
Hub depth 2 → ../../assets
Links city services to existing geo pages (sozdanie + seo) and parent services.
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
DONOR = MIRROR / "web-studiya" / "index.html"
MATRIX = ROOT / "docs" / "seo-regional" / "REGIONAL_MATRIX.csv"
FINAL = ROOT / "docs" / "seo-regional" / "FINAL_SEO_MAP.csv"
SITEMAP = MIRROR / "sitemap.xml"
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

MOTTOR_PHOTOS = {
    "astana": "assets/m-files.cdn1.cc/lpfile/3/2/e/32e8eac576d37936896bba2a35b52bdc/-/crop/0x21x650x391/-/resize/330/f__q_47567714.webp",
    "almaty": "assets/m-files.cdn1.cc/lpfile/0/5/f/05fba2f37e0d0ebf16bf74efc995e0b9/-/crop/384x0x1154x700/-/resize/330/f__q_36994489.webp",
    "shymkent": "assets/m-files.cdn1.cc/lpfile/d/8/e/d8eb27b3bca04551081de512908b16a5/-/crop/0x38x1280x779/-/resize/330/f__q_10804456.webp",
    "karaganda": "assets/m-files.cdn1.cc/lpfile/4/1/6/4164fcbd8cd10da83d49ff55b12a2220/-/crop/25x94x689x418/-/resize/330/f__q_78422993.webp",
    "petropavlovsk": "assets/m-files.cdn1.cc/lpfile/c/6/9/c6937ec1201641a5666bc4606abdb165/-/crop/0x6x1024x607/-/resize/327/f__q_73159820.webp",
}

# Services under /web-studiya/ — stay as ../X from hub
SERVICE_DIRS = {
    "sozdanie-saitov",
    "seo-prodvizhenie",
    "dizayn",
    "aeo-prodvizhenie",
    "aeo-geo-prodvizhenie",
    "kontekstnaya-reklama",
    "lidogeneratsiya",
    "podderzhka-saytov",
    "digital-konsalting",
}

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

HUB_CSS = """
<style data-rk-hub-services-css="1">
.rk-hub-services{display:flow-root !important;width:100% !important;max-width:1200px !important;margin:48px auto 8px !important;padding:0 16px 8px !important;box-sizing:border-box !important;float:none !important;clear:both !important;text-align:center !important}
.rk-hub-services__title{display:block !important;width:100% !important;margin:0 0 28px !important;padding:0 !important;font:700 28px/1.25 Montserrat,"Open Sans",Arial,sans-serif !important;color:#1e1e1e !important;text-align:center !important}
.rk-hub-services__grid{display:grid !important;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;text-align:left;margin:0 auto;max-width:100%}
@media(max-width:700px){.rk-hub-services__grid{grid-template-columns:1fr}.rk-hub-services__title{font-size:22px !important;margin:0 0 20px !important}}
.rk-hub-services__card{display:block;padding:16px 18px;border-radius:12px;background:#f7f9fc;border:1px solid #d7e6f7;color:#1e1e1e;text-decoration:none;font:600 15px/1.35 "Open Sans",Arial,sans-serif;transition:border-color .15s ease,box-shadow .15s ease;text-align:left}
.rk-hub-services__card:hover{border-color:#006fdc;box-shadow:0 6px 18px rgba(0,111,220,.12);color:#006fdc}
.rk-hub-services__card span{display:block;margin-top:4px;font:400 13px/1.4 "Open Sans",Arial,sans-serif;color:#5a6b7d}
</style>
"""


def load_matrix_hubs() -> list[dict]:
    rows = list(csv.DictReader(MATRIX.open(encoding="utf-8-sig"), delimiter=";"))
    return [r for r in rows if r["Направление"] == "Веб-студия"]


def load_final_meta() -> dict[str, dict]:
    out: dict[str, dict] = {}
    rows = list(csv.DictReader(FINAL.open(encoding="utf-8-sig"), delimiter=";"))
    for r in rows:
        name = (r.get("Название страницы") or "").strip()
        if not name.startswith("Веб-студия в "):
            continue
        city = name.replace("Веб-студия в ", "", 1).strip()
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


def deepen_from_depth1(html: str) -> str:
    """Donor depth1 uses ../assets → hub depth2 needs ../../assets.
    ../service stays ../service (still under web-studiya).
    ../ (site root from donor) → ../../ from hub.
    """
    html = html.replace("../assets/", "../../assets/")
    html = html.replace("../favicon", "../../favicon")

    def fix_href(m: re.Match) -> str:
        attr, q, path = m.group(1), m.group(2), m.group(3)
        if path.startswith(("http", "mailto", "tel", "#", "data:", "javascript:")):
            return m.group(0)
        if "assets/" in path or path.startswith("../../"):
            return m.group(0)
        if path.startswith("/") and not path.startswith("//"):
            return m.group(0)

        # exact parent-up to site root from donor: ../ or ../index
        if path in ("../", "..", "../index.html", "../index"):
            return f"{attr}={q}../../{q}"

        if path.startswith("../") and not path.startswith("../../"):
            rest = path[3:]
            first = rest.split("/")[0].split("?")[0]
            if first in SERVICE_DIRS:
                # still one level up to sibling service
                return m.group(0)
            # going to site-root section (keysy, o-kompanii, …)
            return f"{attr}={q}../../{rest}{q}"

        # same-dir relative service: sozdanie-saitov/ → ../sozdanie-saitov/
        bare = path.strip("/").split("/")[0]
        if bare in SERVICE_DIRS and not path.startswith("."):
            return f"{attr}={q}../{path.lstrip('./')}{q}"

        return m.group(0)

    return re.sub(
        r'\b(href|src|data-page-link|action)=([\'"])([^\'"]+)\2',
        fix_href,
        html,
        flags=re.I,
    )


def replace_seo(html: str, *, h1: str, title: str, description: str, pretty: str, city: str) -> str:
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
    html = html.replace("Вебстудия Raskrutov — создание сайтов, продвижение и digital-решения", title, 2)
    html = html.replace("Веб-студия полного цикла для роста вашего бизнеса", h1, 3)
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
    return prefix + f"assets/rk-cities/{slug}.jpg"


def cities_block(depth: int, link_prefix: str, title: str) -> str:
    cards = []
    for city in CITY_ORDER:
        slug = CITY_SLUG[city]
        href = f"{link_prefix.rstrip('/')}/{slug}/"
        src = photo_for(slug, depth)
        label = f"Веб-студия {CITY_IN[city]}"
        cards.append(
            f'<a class="rk-cities__card" href="{href}" data-page-link="{href}">'
            f'<img class="rk-cities__photo" src="{src}" alt="" loading="lazy" decoding="async" width="330" height="248"/>'
            f'<span class="rk-cities__label">{label}</span></a>'
        )
    return (
        CITIES_CSS
        + f'<div class="rk-cities" data-rk-cities-grid="1">'
        + f'<h2 class="rk-cities__title">{title}</h2>'
        + '<div class="rk-cities__grid">'
        + "".join(cards)
        + "</div></div>"
    )


def hub_services_block(slug: str, city: str, in_phrase: str) -> str:
    """Internal links: geo where exist, else parent service."""
    items = [
        (
            f"Создание сайтов {in_phrase}",
            f"/web-studiya/sozdanie-saitov/{slug}/",
            "Лендинги, корпоративные сайты и интернет-магазины",
        ),
        (
            f"SEO-продвижение {in_phrase}",
            f"/web-studiya/seo-prodvizhenie/{slug}/",
            "Google и Яндекс: семантика, техника, контент",
        ),
        (
            "Дизайн",
            "/web-studiya/dizayn/",
            "Логотип, брендбук, нейминг",
        ),
        (
            "Контекстная реклама",
            "/web-studiya/kontekstnaya-reklama/",
            "Google Ads и Яндекс Директ",
        ),
        (
            "Лидогенерация",
            "/web-studiya/lidogeneratsiya/",
            "Заявки и продажи из digital-каналов",
        ),
        (
            "Поддержка сайтов",
            "/web-studiya/podderzhka-saytov/",
            "Сопровождение и развитие после запуска",
        ),
        (
            "Digital-консалтинг",
            "/web-studiya/digital-konsalting/",
            "Аудит, стратегия, консультации",
        ),
        (
            "AEO / GEO",
            "/web-studiya/aeo-prodvizhenie/",
            "Продвижение в AI-поиске",
        ),
    ]
    cards = []
    for title, href, sub in items:
        cards.append(
            f'<a class="rk-hub-services__card" href="{href}" data-page-link="{href}">'
            f"{title}<span>{sub}</span></a>"
        )
    return (
        HUB_CSS
        + '<div class="rk-hub-services" data-rk-hub-services="1">'
        f'<h2 class="rk-hub-services__title">Услуги веб-студии {in_phrase}</h2>'
        f'<div class="rk-hub-services__grid">{"".join(cards)}</div></div>'
    )


def inject_before_contacts(html: str, block: str) -> str:
    html = re.sub(r'<style data-rk-cities="1">[\s\S]*?</style>\s*', "", html)
    html = re.sub(r'<style data-rk-hub-services-css="1">[\s\S]*?</style>\s*', "", html)
    html = re.sub(
        r'<div class="rk-cities"[^>]*data-rk-cities-grid="1"[\s\S]*?</div>\s*</div>\s*',
        "",
        html,
    )
    html = re.sub(
        r'<div class="rk-hub-services"[^>]*>[\s\S]*?</div>\s*</div>\s*',
        "",
        html,
    )
    # Outside Mottor header-slot: before contacts section (tpl 1087)
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
            f"    <priority>0.75</priority>\n"
            f"  </url>\n"
        )
        text = text.replace("</urlset>", entry + "</urlset>")
    SITEMAP.write_text(text, encoding="utf-8")


def prepare_parent(donor: str) -> str:
    html = fix_showpopup(donor)
    # parent stays depth 1
    html = inject_before_contacts(
        html,
        cities_block(1, "/web-studiya", "Веб-студия в городах Казахстана"),
    )
    DONOR.write_text(html, encoding="utf-8")
    return html


def main() -> int:
    raw = DONOR.read_text(encoding="utf-8")
    # strip old cities if re-run on already-patched parent before prepare
    parent = prepare_parent(raw)
    # re-read after prepare (prepare wrote)
    parent = DONOR.read_text(encoding="utf-8")

    matrix = load_matrix_hubs()
    meta = load_final_meta()
    created: list[str] = []

    for row in matrix:
        city = row["Город"].strip()
        slug = CITY_SLUG[city]
        pretty = f"/web-studiya/{slug}"
        in_phrase = CITY_IN[city]
        m = meta.get(city) or {}
        h1 = m.get("h1") or f"Веб-студия {in_phrase}"
        title = m.get("title") or f"Веб-студия {in_phrase}: сайты, SEO и реклама | Raskrutov"
        description = m.get("description") or (
            f"Веб-студия Raskrutov {in_phrase}: создаём сайты, продвигаем в поиске и AI-выдаче, "
            f"настраиваем рекламу и лидогенерацию для бизнеса."
        )

        # Start from raw donor WITHOUT parent cities block — clone from prepared parent is messy.
        # Use original-ish: re-read donor after prepare has cities; deepen then replace cities for hub.
        html = DONOR.read_text(encoding="utf-8")
        # Remove parent cities to rebuild for hub depth
        html = re.sub(r'<style data-rk-cities="1">[\s\S]*?</style>\s*', "", html)
        html = re.sub(
            r'<div class="rk-cities"[^>]*data-rk-cities-grid="1"[\s\S]*?</div>\s*</div>\s*',
            "",
            html,
        )
        html = deepen_from_depth1(html)
        html = fix_showpopup(html)
        html = replace_seo(
            html, h1=h1, title=title, description=description, pretty=pretty, city=city
        )
        block = hub_services_block(slug, city, in_phrase) + cities_block(
            2, "/web-studiya", f"Веб-студия в других городах"
        )
        html = inject_before_contacts(html, block)

        out = MIRROR / pretty.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        created.append(pretty)
        print(f"OK {pretty}  H1={h1!r}")

    upsert_sitemap(created)
    print(f"\nCreated {len(created)} hubs; parent cities grid updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
