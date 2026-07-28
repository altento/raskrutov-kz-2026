#!/usr/bin/env python3
import csv
import json
import re
import ssl
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

ROOT = Path(r"C:\Users\user\Projects\раскрутов")
INDEX = ROOT / "site_mirror" / "index.html"
PAGES = ROOT / "site_mirror" / "pages"
SITEMAP = Path(
    r"C:\Users\user\Downloads\САЙТ RASKRUTOV.KZ  СТРАНИЦЫ И ХОД ВЫПОЛНЕНИЯ - Карта сайта.csv"
)
BASE = "https://raskrutov.kz"

# Homepage list item text -> original URL path (from sitemap / card semantics)
LI_TO_PATH = {
    "Лендинги": "/web-studiya/sozdanie-saitov/landing",
    "Корпоративные сайты": "/web-studiya/sozdanie-saitov/korporativnyy-sayt",
    "Интернет-магазины": "/web-studiya/sozdanie-saitov/internet-magazin",
    "Брендбук": "/web-studiya/dizayn/brendbuk",
    "Логотип и фирменный стиль": "/web-studiya/dizayn/logotip",
    "UI/UX дизайн": "/web-studiya/dizayn",
    "Продвижение в Google": "/web-studiya/seo-prodvizhenie/google",
    "Продвижение в Яндекс": "/web-studiya/seo-prodvizhenie/yandex",
    "Техническая оптимизация": "/web-studiya/seo-prodvizhenie",
    "Оптимизация под ИИ-поиск": "/web-studiya/aeo-prodvizhenie",
    "Яндекс Нейро и Google SGE": "/web-studiya/aeo-prodvizhenie",
    "Структурированные ответы": "/web-studiya/aeo-prodvizhenie",
    "Google ADS": "/web-studiya/kontekstnaya-reklama/google-ads",
    "Яндекс Директ": "/web-studiya/kontekstnaya-reklama/yandex-direct",
    "Оптимизация и аналитика": "/web-studiya/kontekstnaya-reklama",
    "Воронки продаж": "/web-studiya/lidogeneratsiya",
    "Формы и квизы": "/web-studiya/lidogeneratsiya",
    "Заявки и CRM-интеграции": "/web-studiya/lidogeneratsiya",
    "Техническая поддержка": "/web-studiya/podderzhka-saytov",
    "Обновление и безопасность": "/web-studiya/podderzhka-saytov",
    "Резервное копирование": "/web-studiya/podderzhka-saytov",
    "Аудит и аналитика": "/web-studiya/digital-konsalting/audit-sayta",
    "Стратегия и план действий": "/web-studiya/digital-konsalting/digital-strategiya",
    "Рост и масштабирование": "/web-studiya/digital-konsalting",
}

# Card h3 title -> parent hub path (for arrow links)
CARD_TO_PATH = {
    "Создание сайтов": "/web-studiya/sozdanie-saitov",
    "Услуги дизайнера": "/web-studiya/dizayn",
    "SEO-продвижение": "/web-studiya/seo-prodvizhenie",
    "AEO": "/web-studiya/aeo-prodvizhenie",
    "Контекстная реклама": "/web-studiya/kontekstnaya-reklama",
    "Лидогенерация": "/web-studiya/lidogeneratsiya",
    "Поддержка сайтов": "/web-studiya/podderzhka-saytov",
    "Digital-консалтинг": "/web-studiya/digital-konsalting",
}

PATH_ALIASES = {
    "/web-studiya/aeo-prodvizhenie": "pages/web-studiya_aeo-geo-prodvizhenie.html",
    "/web-studiya/seo-prodvizhenie": "pages/web-studiya.html",
}

LOCAL_NAV = {
    "index.html": "/",
    "pages/web-studiya.html": "/web-studiya",
    "pages/web-studiya_sozdanie-saitov.html": "/web-studiya/sozdanie-saitov",
    "pages/web-studiya_dizayn.html": "/web-studiya/dizayn",
    "pages/web-studiya_aeo-geo-prodvizhenie.html": "/web-studiya/aeo-prodvizhenie",
    "pages/web-studiya_kontekstnaya-reklama.html": "/web-studiya/kontekstnaya-reklama",
    "pages/web-studiya_lidogeneratsiya.html": "/web-studiya/lidogeneratsiya",
    "pages/web-studiya_podderzhka-saytov.html": "/web-studiya/podderzhka-saytov",
    "pages/web-studiya_digital-konsalting.html": "/web-studiya/digital-konsalting",
    "pages/r-builder.html": "/r-builder",
    "pages/akademiya.html": "/akademiya",
    "pages/partneram.html": "/partneram",
    "pages/o-kompanii.html": "/o-kompanii",
    "pages/keysy.html": "/keysy",
    "pages/kontakty.html": "/kontakty",
    "pages/faq.html": "/faq",
}


def url_path_to_local(url_path: str) -> str:
    if url_path in PATH_ALIASES and (PAGES.parent / PATH_ALIASES[url_path]).exists():
        return PATH_ALIASES[url_path]
    slug = url_path.strip("/").replace("/", "_")
    candidate = f"pages/{slug}.html"
    if (PAGES.parent / candidate).exists():
        return candidate
    parts = url_path.strip("/").split("/")
    while len(parts) > 1:
        parts.pop()
        parent = f"pages/{'_'.join(parts)}.html"
        if (PAGES.parent / parent).exists():
            return parent
    return candidate


def link_li(text: str, url_path: str) -> str:
    local = url_path_to_local(url_path)
    orig = f"{BASE}{url_path}"
    return (
        f'<li><a class="home-sub-link" href="{local}" '
        f'data-page-link="{local}" data-original-url="{orig}">{text}</a></li>'
    )


def update_index(html: str) -> tuple[str, list[str]]:
    changes: list[str] = []

    for text, path in LI_TO_PATH.items():
        old = f"<li>{text}</li>"
        if old in html:
            html = html.replace(old, link_li(text, path), 1)
            changes.append(f"li: {text} -> {path}")

    for title, path in CARD_TO_PATH.items():
        local = url_path_to_local(path)
        orig = f"{BASE}{path}"
        # upgrade arrow link after this card title
        pattern = re.compile(
            rf'(<h3 class="blk-data[^"]*"><span[^>]*>{re.escape(title)}</span></h3>.*?)'
            rf'(data-page-link=")(pages/web-studiya[^"]*)(")',
            re.S,
        )

        def repl(m: re.Match) -> str:
            return m.group(1) + m.group(2) + local + '" data-original-url="' + orig + m.group(4)

        new_html, n = pattern.subn(repl, html, count=1)
        if n:
            html = new_html
            changes.append(f"card arrow: {title} -> {path}")

    def add_orig_attr(m: re.Match) -> str:
        full = m.group(0)
        if "data-original-url=" in full:
            return full
        link = m.group(1)
        path = LOCAL_NAV.get(link)
        if not path:
            return full
        return f'data-page-link="{link}" data-original-url="{BASE}{path}"'

    html2, n = re.subn(r'data-page-link="([^"]+)"', add_orig_attr, html)
    if n:
        changes.append(f"annotated data-page-link attrs ({n} total tags scanned)")

    marker = "<!-- LOCAL-SUBPAGE-LINKS -->"
    if marker not in html2:
        block = marker + '\n<nav id="local-subpage-links" style="display:none" aria-hidden="true">\n'
        seen = set()
        for path in list(LI_TO_PATH.values()) + list(CARD_TO_PATH.values()) + list(LOCAL_NAV.values()):
            if path in seen or path == "/":
                continue
            seen.add(path)
            local = url_path_to_local(path)
            block += f'  <a href="{local}" data-original-url="{BASE}{path}"></a>\n'
        block += "</nav>\n"
        html2 = html2.replace("</body>", block + "</body>", 1)
        changes.append("inserted hidden subpage link map")

    return html2, changes


def load_sitemap_paths() -> list[dict]:
    rows = []
    with SITEMAP.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        next(reader)  # skip garbled header row
        for row in reader:
            if len(row) < 5 or row[0] in ("ID", ""):
                continue
            if row[0].strip().isdigit():
                rows.append(
                    {
                        "id": row[0].strip(),
                        "title": row[3].strip(),
                        "url": row[4].strip(),
                        "status": row[10].strip() if len(row) > 10 else "",
                    }
                )
    return rows


def check_urls(paths: list[str]) -> list[dict]:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    out = []
    for path in paths:
        url = BASE + path
        row = {"path": path, "status": None, "local": url_path_to_local(path), "local_exists": False}
        row["local_exists"] = (PAGES.parent / row["local"]).exists()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
                row["status"] = resp.status
        except HTTPError as exc:
            row["status"] = exc.code
        except URLError as exc:
            row["error"] = str(exc.reason)
        except Exception as exc:
            row["error"] = str(exc)
        out.append(row)
    return out


def main() -> None:
    html = INDEX.read_text(encoding="utf-8", errors="ignore")
    updated, changes = update_index(html)
    if updated != html:
        INDEX.write_text(updated, encoding="utf-8")
    print("Homepage updates:")
    for c in changes:
        print(" ", c)

    paths = sorted(set(LI_TO_PATH.values()) | set(CARD_TO_PATH.values()))
    home_subpaths = [p for p in paths if p.startswith("/web-studiya/")]
    results = check_urls(home_subpaths)

    report = {
        "homepage_changes": changes,
        "checked_at": "live",
        "subpaths": results,
        "available": [r for r in results if r.get("status") == 200],
        "unavailable": [r for r in results if r.get("status") != 200],
    }
    out = ROOT / "site_mirror" / "homepage_subpaths_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nAvailability (homepage studio subpaths):")
    for r in results:
        st = r.get("status")
        loc = "local OK" if r["local_exists"] else "local MISSING"
        if st == 200:
            print(f"  OK   {r['path']} | {loc}")
        elif st:
            print(f"  HTTP {st} {r['path']} | {loc}")
        else:
            print(f"  FAIL {r['path']} | {r.get('error','')} | {loc}")

    print(f"\nReport: {out}")


if __name__ == "__main__":
    main()
