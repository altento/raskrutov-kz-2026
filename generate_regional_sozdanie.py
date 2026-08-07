# -*- coding: utf-8 -*-
"""Generate pretty regional pages for /web-studiya/sozdanie-saitov/{city}.

Donor: site_mirror/web-studiya/sozdanie-saitov/index.html (depth 2)
Target depth 3 → deepen ../../ → ../../../ for assets/root-relative paths.
Legacy URLs from SEO matrix get 301 → pretty in .htaccess.
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
DONOR = MIRROR / "web-studiya" / "sozdanie-saitov" / "index.html"
MATRIX = ROOT / "docs" / "seo-regional" / "REGIONAL_MATRIX.csv"
FINAL = ROOT / "docs" / "seo-regional" / "FINAL_SEO_MAP.csv"
URL_MAP = ROOT / "url_mapping.json"
SITEMAP = MIRROR / "sitemap.xml"
HTACCESS = MIRROR / ".htaccess"

# Город → pretty slug (как у /web-studiya/podderzhka-saytov/{slug} в карте)
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

# Предложный оборот для фраз «в …»
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


def load_matrix_sozdanie() -> list[dict]:
    rows = list(
        csv.DictReader(MATRIX.open(encoding="utf-8-sig"), delimiter=";")
    )
    return [r for r in rows if r["Направление"] == "Создание сайтов"]


def load_final_meta() -> dict[str, dict]:
    """Map city name → {h1,title,description} from FINAL_SEO_MAP geo sozdanie rows."""
    out: dict[str, dict] = {}
    rows = list(csv.DictReader(FINAL.open(encoding="utf-8-sig"), delimiter=";"))
    for r in rows:
        name = (r.get("Название страницы") or "").strip()
        if not name.startswith("Создание сайтов в "):
            continue
        city = name.replace("Создание сайтов в ", "", 1).strip()
        out[city] = {
            "h1": (r.get("H1") or name).strip(),
            "title": (r.get("Title") or "").strip(),
            "description": (r.get("Description") or "").strip(),
            "legacy": (r.get("Итоговый URL") or "").strip().split(";")[0].strip(),
        }
    return out


def deepen_prefixes(html: str) -> str:
    """Donor depth=2 uses ../../ → city depth=3 needs ../../../."""
    # assets / favicon / root files
    html = html.replace("../../assets/", "../../../assets/")
    html = html.replace("../../favicon", "../../../favicon")
    # Already-deepened safety: don't triple-run
    # Relative pretty links that pointed up one level from donor:
    # From /web-studiya/sozdanie-saitov/ X → ../Y was web-studiya/Y
    # From /web-studiya/sozdanie-saitov/city/ need ../../Y for same
    # Heuristic: rewrite href="../X" that are NOT assets to href="../../X"
    # but keep href="../landing" style siblings as ../landing (still under sozdanie-saitov)

    def fix_href(m: re.Match) -> str:
        attr, q, path = m.group(1), m.group(2), m.group(3)
        if path.startswith(("http", "mailto", "tel", "#", "data:", "javascript:")):
            return m.group(0)
        if "assets/" in path or path.startswith("../../../"):
            return m.group(0)
        # sibling service under sozdanie-saitov (landing, internet-magazin, …)
        sibling = {
            "landing",
            "internet-magazin",
            "korporativnyy-sayt",
            "mnogostranichnye-sayty",
            "sayt-vizitka",
            "redizayn-sayta",
            "integratsii",
            "onlayn-kalkulyatory",
            "ai-konsultanty",
            "crm-sistemy",
            "onlayn-shkola",
            "obsluzhivanie-saytov",
        }
        bare = path.strip("/").split("/")[0]
        if path.startswith("../") and not path.startswith("../../"):
            rest = path[3:]  # after ../
            first = rest.split("/")[0]
            if first in sibling or rest in ("", "."):
                # sibling: ../landing stays ../landing from city folder? 
                # city is under sozdanie-saitov/almaty → sibling landing is ../landing ✓
                return m.group(0)
            # parent section link: ../dizayn was web-studiya/dizayn from donor
            # from city need ../../dizayn
            return f"{attr}={q}../../{rest}{q}"
        if path.startswith("/") and not path.startswith("//"):
            # site-root absolute path — OK keep
            return m.group(0)
        # same-dir relative like "landing" → "../landing"
        if not path.startswith(".") and "/" not in path.strip("/").rstrip("/") or (
            path.count("/") <= 1 and not path.startswith("..")
        ):
            if bare in sibling:
                return f"{attr}={q}../{path.lstrip('./')}{q}"
        return m.group(0)

    html = re.sub(
        r'\b(href|src|data-page-link|action)=([\'"])([^\'"]+)\2',
        fix_href,
        html,
        flags=re.I,
    )
    return html


def replace_seo(html: str, *, h1: str, title: str, description: str, pretty: str) -> str:
    canon = "https://raskrutov.kz" + pretty.rstrip("/")

    html = re.sub(
        r"<title>[^<]*</title>",
        f"<title>{title}</title>",
        html,
        count=1,
        flags=re.I,
    )
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

    # Replace first visible H1 text content (keep markup wrappers)
    def h1_repl(m: re.Match) -> str:
        inner = m.group(1)
        # if nested spans, replace innermost text-ish
        if re.search(r">[^<]{3,}<", inner):
            # replace last text node-ish chunk
            return (
                "<h1"
                + m.group(0)[3 : m.group(0).find(">") + 1]
                + re.sub(
                    r"(>)([^<>]{3,})(<)",
                    rf"\1{h1}\3",
                    inner,
                    count=1,
                )
                + "</h1>"
            )
        return f"<h1{m.group(0)[3:m.group(0).find('>')+1]}{h1}</h1>"

    html2, n = re.subn(
        r"<h1([^>]*)>([\s\S]*?)</h1>",
        lambda m: f"<h1{m.group(1)}>{h1}</h1>",
        html,
        count=1,
        flags=re.I,
    )
    if n:
        html = html2

    # Soft body unique: Kazakhstan → city phrase in description-like blocks near top
    # Avoid mass replace of all Казахстан (breaks org schema). Only a couple safe strings.
    html = html.replace(
        "Создание сайтов под ключ в Казахстане",
        h1,
        3,
    )
    html = html.replace(
        "создание сайта под ключ в веб-студии Raskrutov",
        f"создание сайта под ключ {CITY_IN.get(h1.replace('Создание сайтов ', '').replace('в ', 'в '), '')} в веб-студии Raskrutov".replace(
            "в в ", "в "
        ),
        2,
    )
    return html


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
    marker = "# Regional sozdanie-saitov pretty redirects (auto)"
    block_lines = [marker]
    for legacy, pretty in legacy_to_pretty:
        old = legacy.strip().strip("/")
        new = pretty.rstrip("/") + "/"
        # Apache Redirect
        block_lines.append(f"Redirect 301 /{old} {new}")
        block_lines.append(f"Redirect 301 /{old}/ {new}")
    block = "\n".join(block_lines) + "\n"

    if marker in text:
        # replace existing auto block until next blank+comment or EOF-ish
        text = re.sub(
            rf"{re.escape(marker)}[\s\S]*?(?=\n# [A-Z]|\nRedirect 301 /web-studiya/aeo|\Z)",
            block,
            text,
            count=1,
        )
    else:
        # append before final notes if any
        text = text.rstrip() + "\n\n" + block
    HTACCESS.write_text(text, encoding="utf-8")


def upsert_url_mapping(items: list[tuple[str, str]]) -> None:
    data = json.loads(URL_MAP.read_text(encoding="utf-8"))
    for pages_name, pretty in items:
        data[pages_name] = pretty.strip("/")
    URL_MAP.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


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


def main() -> None:
    donor = DONOR.read_text(encoding="utf-8")
    matrix = load_matrix_sozdanie()
    meta = load_final_meta()

    created = []
    redirects = []
    url_map_items = []

    for row in matrix:
        city = row["Город"].strip()
        slug = CITY_SLUG.get(city)
        if not slug:
            raise SystemExit(f"No slug for city {city!r}")
        pretty = f"/web-studiya/sozdanie-saitov/{slug}"
        legacy = (row.get("Региональный URL") or "").strip()
        m = meta.get(city) or {}
        # Prefer FINAL meta; fallback synthesize
        in_phrase = CITY_IN[city]
        h1 = m.get("h1") or f"Создание сайтов {in_phrase}"
        title = m.get("title") or f"Создание сайтов {in_phrase} под ключ | Raskrutov"
        description = m.get("description") or (
            f"Создаём сайты для бизнеса {in_phrase}: лендинги, корпоративные сайты и "
            f"интернет-магазины с подготовкой к SEO, рекламе и продажам."
        )
        if m.get("legacy"):
            legacy = m["legacy"] or legacy

        html = deepen_prefixes(donor)
        html = replace_seo(
            html, h1=h1, title=title, description=description, pretty=pretty
        )

        out = MIRROR / pretty.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        created.append(pretty)

        if legacy and legacy.startswith("/") and "sozdanie-saitov-v-" in legacy:
            redirects.append((legacy, pretty))
            # pages stub name from legacy slug
            leaf = legacy.strip("/").replace("/", "_") + ".html"
            write_pages_stub(leaf, pretty)
            url_map_items.append((leaf, pretty.strip("/")))

        print(f"OK {pretty}  ← {legacy or 'NEW'}  H1={h1!r}")

    upsert_sitemap(created)
    upsert_htaccess(redirects)
    upsert_url_mapping(url_map_items)
    print(f"\nCreated {len(created)} pages, {len(redirects)} legacy redirects")


if __name__ == "__main__":
    main()
