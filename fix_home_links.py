#!/usr/bin/env python3
import json
import re
import ssl
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

ROOT = Path(r"C:\Users\user\Projects\раскрутов")
INDEX = ROOT / "site_mirror" / "index.html"
PAGES = ROOT / "site_mirror" / "pages"
BASE = "https://raskrutov.kz"

PATH_ALIASES = {
    "/web-studiya/aeo-prodvizhenie": "pages/web-studiya_aeo-geo-prodvizhenie.html",
    "/web-studiya/seo-prodvizhenie": "pages/web-studiya_seo-prodvizhenie.html",
}

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
        parent_path = "/" + "/".join(parts)
        if parent_path in PATH_ALIASES and (PAGES.parent / PATH_ALIASES[parent_path]).exists():
            return PATH_ALIASES[parent_path]
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


def dedupe_tag_attributes(html: str) -> str:
    def fix_tag(m: re.Match) -> str:
        tag = m.group(0)
        seen = {}
        for attr in re.finditer(r'(\w[\w-]*)="([^"]*)"', tag):
            key = attr.group(1)
            val = attr.group(2)
            if key == "data-original-url" and key in seen:
                # keep the more specific (longer) URL path
                if len(val) > len(seen[key]):
                    seen[key] = val
            else:
                seen[key] = val
        if not seen:
            return tag
        name = re.match(r"<(\w+)", tag).group(1)
        attrs = " ".join(f'{k}="{v}"' for k, v in seen.items())
        return f"<{name} {attrs}>"

    return re.sub(r"<a class=\"home-sub-link\"[^>]*>", fix_tag, html)


def annotate_page_links(html: str) -> str:
    def repl(m: re.Match) -> str:
        pos = m.start()
        tag_start = html.rfind("<", 0, pos)
        tag_end = html.find(">", pos)
        tag = html[tag_start : tag_end + 1]
        if "home-sub-link" in tag or "data-original-url=" in tag:
            return m.group(0)
        link = m.group(1)
        path = LOCAL_NAV.get(link)
        if not path:
            return m.group(0)
        return f'data-page-link="{link}" data-original-url="{BASE}{path}"'

    return re.sub(r'data-page-link="([^"]+)"', repl, html)


def fix_home_sub_links(html: str) -> tuple[str, int]:
    count = 0
    for text, path in LI_TO_PATH.items():
        local = url_path_to_local(path)
        orig = f"{BASE}{path}"
        anchor = (
            f'<a class="home-sub-link" href="{local}" '
            f'data-page-link="{local}" data-original-url="{orig}">{text}</a>'
        )
        # already linked — update href only, never wrap in extra <li>
        pat_linked = re.compile(
            rf'<a class="home-sub-link"[^>]*>{re.escape(text)}</a>'
        )
        html, n = pat_linked.subn(anchor, html)
        count += n
        if n:
            continue
        # plain list item
        pat_plain = re.compile(rf"<li>{re.escape(text)}</li>")
        html, n2 = pat_plain.subn(f"<li>{anchor}</li>", html, count=1)
        count += n2
    return html, count


def main() -> None:
    html = INDEX.read_text(encoding="utf-8", errors="ignore")
    html = dedupe_tag_attributes(html)
    html, n = fix_home_sub_links(html)
    html = annotate_page_links(html)

    # fix hidden nav aeo link
    html = html.replace(
        'href="pages/web-studiya.html" data-original-url="https://raskrutov.kz/web-studiya/aeo-prodvizhenie"',
        'href="pages/web-studiya_aeo-geo-prodvizhenie.html" data-original-url="https://raskrutov.kz/web-studiya/aeo-prodvizhenie"',
    )

    INDEX.write_text(html, encoding="utf-8")
    print(f"Fixed {n} home-sub-link tags, deduped attributes")

    paths = sorted(set(LI_TO_PATH.values()))
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    results = []
    for path in paths:
        row = {"path": path, "status": None, "local": url_path_to_local(path)}
        row["local_exists"] = (PAGES.parent / row["local"]).exists()
        try:
            req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
                row["status"] = resp.status
        except HTTPError as exc:
            row["status"] = exc.code
        except Exception as exc:
            row["error"] = str(exc)
        results.append(row)

    report = ROOT / "site_mirror" / "homepage_subpaths_report.json"
    report.write_text(
        json.dumps({"subpaths": results, "available": [r for r in results if r.get("status") == 200]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ok = [r for r in results if r.get("status") == 200]
    print(f"Live OK: {len(ok)}/{len(results)}")
    for r in results:
        print(f"  {r.get('status','ERR'):>4} {r['path']}")


if __name__ == "__main__":
    main()
