#!/usr/bin/env python3
"""Mirror missing sitemap pages (fetch or stub) and wire navigation."""
from __future__ import annotations

import csv
import json
import re
import ssl
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

ROOT = Path(r"C:\Users\user\Projects\раскрутов")
MIRROR = ROOT / "site_mirror"
PAGES = MIRROR / "pages"
CSV_PATH = Path(
    r"C:\Users\user\Downloads\САЙТ RASKRUTOV.KZ  СТРАНИЦЫ И ХОД ВЫПОЛНЕНИЯ - Карта сайта.csv"
)
BASE = "https://raskrutov.kz"

PATH_ALIASES = {
    "/web-studiya/aeo-prodvizhenie": "web-studiya_aeo-geo-prodvizhenie.html",
}

HUB_DEFAULTS = {
    "/crm": "index.html",
}

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def load_sitemap() -> list[dict]:
    text = CSV_PATH.read_text(encoding="utf-8-sig")
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("ID,")]
    rows = list(csv.reader(lines))
    if rows and not rows[0][0].strip():
        rows[0][0] = "1"
    out = []
    for row in rows:
        if len(row) < 5 or not row[4].startswith("/"):
            continue
        out.append(
            {
                "url": row[4].strip(),
                "title": row[3].strip() if len(row) > 3 else "",
                "page_title": row[7].strip() if len(row) > 7 else row[3].strip(),
                "description": row[9].strip() if len(row) > 9 else "",
                "plan_status": row[11].strip() if len(row) > 11 else "",
            }
        )
    return out


def url_to_local(url_path: str) -> str:
    if url_path == "/":
        return "index.html"
    if url_path in PATH_ALIASES:
        return f"pages/{PATH_ALIASES[url_path]}"
    slug = url_path.strip("/").replace("/", "_")
    return f"pages/{slug}.html"


def local_exists(rel: str) -> bool:
    return (MIRROR / rel).exists()


def find_parent_local(url_path: str) -> str | None:
    if url_path in HUB_DEFAULTS:
        rel = HUB_DEFAULTS[url_path]
        return rel if local_exists(rel) else None
    parts = url_path.strip("/").split("/")
    while len(parts) > 0:
        parts.pop()
        if not parts:
            return "index.html" if local_exists("index.html") else None
        parent_url = "/" + "/".join(parts)
        if parent_url in PATH_ALIASES:
            rel = f"pages/{PATH_ALIASES[parent_url]}"
            if local_exists(rel):
                return rel
        rel = url_to_local(parent_url)
        if local_exists(rel):
            return rel
    return "index.html"


def try_fetch(url_path: str) -> str | None:
    url = BASE + url_path
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25, context=CTX) as resp:
            if resp.status != 200:
                return None
            raw = resp.read()
            ct = resp.headers.get("Content-Type", "")
            if "html" not in ct.lower() and b"<html" not in raw[:500].lower():
                return None
            return raw.decode("utf-8", errors="ignore")
    except (HTTPError, URLError, OSError):
        return None


def patch_page_meta(html: str, page_title: str, description: str, url_path: str) -> str:
    if page_title:
        html = re.sub(r"<title>.*?</title>", f"<title>{page_title}</title>", html, count=1, flags=re.I | re.S)
        html = re.sub(
            r'(<meta\s+property="og:title"\s+content=")[^"]*(")',
            rf"\1{page_title}\2",
            html,
            count=1,
            flags=re.I,
        )
    if description:
        html = re.sub(
            r'(<meta\s+name="description"\s+content=")[^"]*(")',
            rf"\1{description}\2",
            html,
            count=1,
            flags=re.I,
        )
        html = re.sub(
            r'(<meta\s+property="og:description"\s+content=")[^"]*(")',
            rf"\1{description}\2",
            html,
            count=1,
            flags=re.I,
        )
    marker = f'<!-- local-page: {url_path} -->'
    if marker not in html:
        html = html.replace("<html", marker + "\n<html", 1)
    return html


def create_page(url_path: str, entry: dict) -> tuple[str, str]:
    """Returns (local_rel, source) where source is fetch|stub|exists."""
    rel = url_to_local(url_path)
    if local_exists(rel):
        return rel, "exists"

    fetched = try_fetch(url_path)
    if fetched:
        html = patch_page_meta(fetched, entry["page_title"], entry["description"], url_path)
        dest = MIRROR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        return rel, "fetch"

    parent = find_parent_local(url_path)
    if not parent:
        parent = "index.html"
    parent_html = (MIRROR / parent).read_text(encoding="utf-8", errors="ignore")
    html = patch_page_meta(parent_html, entry["page_title"], entry["description"], url_path)
    dest = MIRROR / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    return rel, "stub"


def rel_link(from_file: str, target_rel: str) -> str:
    from_path = MIRROR / from_file
    target_path = MIRROR / target_rel
    return Path(
        __import__("posixpath").relpath(target_path.as_posix(), start=from_path.parent.as_posix())
    ).as_posix()


def build_url_map() -> dict[str, str]:
    m = {}
    for p in load_sitemap():
        m[p["url"]] = url_to_local(p["url"])
    return m


def wire_file(path: Path, url_map: dict[str, str]) -> list[str]:
    rel = path.relative_to(MIRROR).as_posix()
    html = path.read_text(encoding="utf-8", errors="ignore")
    orig = html
    changes = []

    # Fix broken SEO link
    if "web-studiya_seo-prodvizhenie-.html" in html:
        fix = rel_link(rel, "pages/web-studiya_seo-prodvizhenie.html")
        html = html.replace("web-studiya_seo-prodvizhenie-.html", fix.split("/")[-1] if "/" in fix else fix)
        changes.append("fix seo typo")

    # Вопросы -> faq (all pages share same block id)
    faq_target = rel_link(rel, "pages/faq.html")
    old_faq = (
        'act="reachGoals" onclick="return msJsWrapper(event,\'e9f6db4135fe402392d50a5d4cdda964\',\'reachGoals\');" data-page-link=""'
    )
    new_faq = (
        f'act="linkRedirect" onclick="return msJsWrapper(event,\'e9f6db4135fe402392d50a5d4cdda964\',\'linkRedirect\');" '
        f'data-page-link="{faq_target}" data-original-url="{BASE}/faq"'
    )
    if old_faq in html:
        html = html.replace(old_faq, new_faq)
        changes.append("wire faq nav")

    # Map absolute site paths in data-page-link and data-original-url hrefs
    for url_path, target_rel in sorted(url_map.items(), key=lambda x: -len(x[0])):
        if url_path == "/":
            continue
        local_ref = rel_link(rel, target_rel)
        full = BASE + url_path
        # data-page-link to full URL
        html = html.replace(f'data-page-link="{full}"', f'data-page-link="{local_ref}"')
        html = html.replace(f"data-page-link='{full}'", f"data-page-link='{local_ref}'")
        # home-sub-link href updates
        pat = rf'(<a class="home-sub-link" href=")[^"]*(" data-page-link="[^"]*" data-original-url="{re.escape(full)}")'
        rep = rf'\1{local_ref}\2'
        html, n = re.subn(pat, rep, html)
        if n:
            changes.append(f"home-sub {url_path}")
        pat2 = rf'(<a class="home-sub-link" href=")[^"]*(" data-page-link=")[^"]*(" data-original-url="{re.escape(full)}")'
        html, n2 = re.subn(pat2, rf"\1{local_ref}\2{local_ref}\3", html)
        if n2:
            changes.append(f"home-sub2 {url_path}")

    # hidden nav entries
    for url_path, target_rel in url_map.items():
        if url_path == "/":
            continue
        full = BASE + url_path
        local_ref = rel_link(rel, target_rel)
        html = re.sub(
            rf'<a href="[^"]*" data-original-url="{re.escape(full)}"',
            f'<a href="{local_ref}" data-original-url="{full}"',
            html,
        )

    if html != orig:
        path.write_text(html, encoding="utf-8")
    return changes


# Homepage + hub list item wiring (text -> url)
LI_WIRE = {
    "Лендинги": "/web-studiya/sozdanie-saitov/landing",
    "Корпоративные сайты": "/web-studiya/sozdanie-saitov/korporativnyy-sayt",
    "Интернет-магазины": "/web-studiya/sozdanie-saitov/internet-magazin",
    "Многостраничные сайты": "/web-studiya/sozdanie-saitov/mnogostranichnye-sayty",
    "многостраничные": "/web-studiya/sozdanie-saitov/mnogostranichnye-sayty",
    "Брендбук": "/web-studiya/dizayn/brendbuk",
    "Логотип и фирменный стиль": "/web-studiya/dizayn/logotip",
    "UI/UX дизайн": "/web-studiya/dizayn",
    "Продвижение в Google": "/web-studiya/seo-prodvizhenie/google",
    "Продвижение в Яндекс": "/web-studiya/seo-prodvizhenie/yandex",
    "Техническая оптимизация": "/web-studiya/seo-prodvizhenie",
    "Google ADS": "/web-studiya/kontekstnaya-reklama/google-ads",
    "Яндекс Директ": "/web-studiya/kontekstnaya-reklama/yandex-direct",
    "Оптимизация и аналитика": "/web-studiya/kontekstnaya-reklama",
    "Аудит и аналитика": "/web-studiya/digital-konsalting/audit-sayta",
    "Стратегия и план действий": "/web-studiya/digital-konsalting/digital-strategiya",
    "О нас": "/o-kompanii/o-nas",
    "Команда": "/o-kompanii/komanda",
    "Кейсы: сайты": "/keysy/sayty",
    "Кейсы по сайтам": "/keysy/sayty",
    "Сайты": "/keysy/sayty",
    "Кейсы: продвижение": "/keysy/prodvizhenie",
    "Продвижение": "/keysy/prodvizhenie",
    "Что такое R-Builder": "/r-builder/chto-takoe-r-builder",
    "AI R-Builder": "/r-builder/ai-r-builder",
    "Возможности платформы": "/r-builder/vozmozhnosti",
    "R-Builder для бизнеса": "/r-builder/dlya-biznesa",
    "Франшиза": "/partneram/franshiza",
    "Пакеты партнёрства": "/partneram/pakety-partnerstva",
}


def wire_list_items(path: Path, url_map: dict[str, str]) -> int:
    rel = path.relative_to(MIRROR).as_posix()
    html = path.read_text(encoding="utf-8", errors="ignore")
    count = 0
    for text, url_path in LI_WIRE.items():
        target = url_map.get(url_path)
        if not target or not local_exists(target):
            continue
        local_ref = rel_link(rel, target)
        full = BASE + url_path
        old_plain = f"<li>{text}</li>"
        anchor = (
            f'<a class="home-sub-link" href="{local_ref}" '
            f'data-page-link="{local_ref}" data-original-url="{full}">{text}</a>'
        )
        new = f"<li>{anchor}</li>"
        if old_plain in html:
            html = html.replace(old_plain, new, 1)
            count += 1
            continue
        # upgrade existing link without adding another <li> wrapper
        pat = rf'<a class="home-sub-link"[^>]*>{re.escape(text)}</a>'
        if re.search(pat, html):
            html = re.sub(pat, anchor, html, count=1)
            count += 1
    if count:
        path.write_text(html, encoding="utf-8")
    return count


def wire_hub_arrows(path: Path, url_map: dict[str, str]) -> int:
    """Wire card h3 titles to their hub URLs."""
    CARD_TITLES = {
        "Создание сайтов": "/web-studiya/sozdanie-saitov",
        "SEO-продвижение": "/web-studiya/seo-prodvizhenie",
        "Услуги дизайнера": "/web-studiya/dizayn",
        "AEO": "/web-studiya/aeo-prodvizhenie",
        "Контекстная реклама": "/web-studiya/kontekstnaya-reklama",
        "Лидогенерация": "/web-studiya/lidogeneratsiya",
        "Поддержка сайтов": "/web-studiya/podderzhka-saytov",
        "Digital-консалтинг": "/web-studiya/digital-konsalting",
        "О компании": "/o-kompanii",
        "Кейсы": "/keysy",
        "R-Builder": "/r-builder",
        "Партнёрам": "/partneram",
        "Академия": "/akademiya",
        "FAQ": "/faq",
        "CRM и автоматизация": "/crm",
    }
    rel = path.relative_to(MIRROR).as_posix()
    html = path.read_text(encoding="utf-8", errors="ignore")
    count = 0
    for title, url_path in CARD_TITLES.items():
        target = url_map.get(url_path)
        if not target:
            continue
        local_ref = rel_link(rel, target)
        full = BASE + url_path
        pattern = re.compile(
            rf'(<h3 class="blk-data[^"]*"><span[^>]*>{re.escape(title)}</span></h3>.*?)'
            rf'(data-page-link=")([^"]*)(")',
            re.S,
        )

        def repl(m, lr=local_ref, fu=full):
            return m.group(1) + m.group(2) + lr + '" data-original-url="' + fu + m.group(4)

        html2, n = pattern.subn(repl, html, count=1)
        if n:
            html = html2
            count += n
    if count:
        path.write_text(html, encoding="utf-8")
    return count


def wire_consent_footer() -> int:
    count = 0
    for html_path in [MIRROR / "index.html", *PAGES.glob("*.html")]:
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        rel = html_path.relative_to(MIRROR).as_posix()
        c = rel_link(rel, "pages/consent.html")
        r = rel_link(rel, "pages/regulation.html")
        orig = html
        if "consent.html" not in html and "Согласие" in html:
            html = html.replace(
                ">Согласие<",
                f'><a href="{c}" data-page-link="{c}">Согласие</a><',
                1,
            )
        if "regulation.html" not in html and "политик" in html.lower():
            pass  # skip if no anchor text found
        # append footer nav if missing
        marker = "<!-- LOCAL-LEGAL-LINKS -->"
        if marker not in html and html_path.name == "index.html":
            block = (
                f'{marker}<nav style="display:none" aria-hidden="true">'
                f'<a href="{c}" data-page-link="{c}">consent</a>'
                f'<a href="{r}" data-page-link="{r}">regulation</a></nav>'
            )
            html = html.replace("</body>", block + "\n</body>", 1)
        if html != orig:
            html_path.write_text(html, encoding="utf-8")
            count += 1
    return count


def update_pages_index():
    pages = sorted(p.name for p in PAGES.glob("*.html"))
    data = {"count": len(pages) + 1, "home": "index.html", "pages": pages}
    (MIRROR / "pages_index.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    sitemap = load_sitemap()
    created = {"fetch": [], "stub": [], "exists": [], "failed": []}

    for entry in sitemap:
        url = entry["url"]
        if url == "/":
            continue
        try:
            rel, src = create_page(url, entry)
            created[src].append({"url": url, "file": rel, "title": entry["title"]})
        except Exception as exc:
            created["failed"].append({"url": url, "error": str(exc)})

    url_map = build_url_map()

    html_files = [MIRROR / "index.html", *PAGES.glob("*.html")]
    wire_stats = {"files": 0, "list_items": 0, "arrows": 0}
    for fp in html_files:
        ch = wire_file(fp, url_map)
        wire_stats["list_items"] += wire_list_items(fp, url_map)
        wire_stats["arrows"] += wire_hub_arrows(fp, url_map)
        if ch:
            wire_stats["files"] += 1

    wire_consent_footer()
    update_pages_index()

    report = {
        "created": created,
        "wire_stats": wire_stats,
        "total_pages": len(list(PAGES.glob("*.html"))) + 1,
    }
    out = MIRROR / "mirror_missing_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Pages in mirror: {report['total_pages']}")
    print(f"Fetched: {len(created['fetch'])}, Stubs: {len(created['stub'])}, Existed: {len(created['exists'])}")
    print(f"Failed: {len(created['failed'])}")
    print(f"Wired files: {wire_stats['files']}, list items: {wire_stats['list_items']}, arrows: {wire_stats['arrows']}")
    print(f"Report: {out}")


if __name__ == "__main__":
    main()
