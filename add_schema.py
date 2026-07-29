#!/usr/bin/env python3
"""Schema.org JSON-LD generator for the Raskrutov mirror.

IDEMPOTENT: removes previously injected blocks (data-schema="raskrutov")
before adding fresh markup. RUN AGAIN after adding new pages:

    python add_schema.py

Markup per page type:
- index.html            Organization, ProfessionalService, WebSite, WebPage,
                        FAQPage (parsed from the FAQ section), ItemList of
                        services, BreadcrumbList
- web-studiya_*.html    Service + WebPage + BreadcrumbList
- crm*.html             Service + WebPage + BreadcrumbList
- akademiya_obuchenie-* Course + WebPage + BreadcrumbList
- r-builder*.html       SoftwareApplication + WebPage + BreadcrumbList
- keysy*.html           CollectionPage + BreadcrumbList
- o-kompanii*.html      AboutPage + BreadcrumbList
- kontakty.html         ContactPage + BreadcrumbList
- faq*.html             WebPage + FAQPage + BreadcrumbList
- other                 WebPage + BreadcrumbList

Every page also carries a compact Organization + WebSite node so references
resolve on each page individually.
"""
import html as html_mod
import json
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
BASE = "https://raskrutov.kz"
ORG_ID = f"{BASE}/#organization"
SITE_ID = f"{BASE}/#website"
LOGO = f"{BASE}/assets/m-files.cdn1.cc/web/images/raskrutov/logo.png"

SAME_AS = [
    "https://www.instagram.com/raskrutov.kz/",
    "https://www.youtube.com/@raskrutov-kz",
    "https://t.me/Raskrutov_web",
    "https://www.tiktok.com/@raskrutov.kz",
    "https://wa.me/77000216900",
]

TAG_RE = re.compile(r"<[^>]+>")
H2_RE = re.compile(r"<h2\b[^>]*>(.*?)</h2>", re.IGNORECASE | re.DOTALL)
H3_RE = re.compile(r"<h3\b[^>]*>(.*?)</h3>", re.IGNORECASE | re.DOTALL)
INJECT_RE = re.compile(r'<script type="application/ld\+json" data-schema="raskrutov">.*?</script>\s*', re.DOTALL)

SERVICE_LINKS = [
    ("Создание сайтов", "pages/web-studiya_sozdanie-saitov.html"),
    ("Услуги дизайнера", "pages/web-studiya_dizayn.html"),
    ("SEO-продвижение", "pages/web-studiya_seo-prodvizhenie.html"),
    ("AEO — оптимизация под ИИ-поиск", "pages/web-studiya_aeo-geo-prodvizhenie.html"),
    ("Контекстная реклама", "pages/web-studiya_kontekstnaya-reklama.html"),
    ("Лидогенерация", "pages/web-studiya_lidogeneratsiya.html"),
    ("Поддержка сайтов", "pages/web-studiya_podderzhka-saytov.html"),
    ("Digital-консалтинг", "pages/web-studiya_digital-konsalting.html"),
]


def clean(t: str) -> str:
    t = TAG_RE.sub(" ", t)
    t = html_mod.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    return t.replace("​", "").strip(" -–—,")


def meta(html: str, name: str) -> str:
    m = re.search(rf'<meta[^>]*name="{name}"[^>]*content="([^"]*)"', html, re.IGNORECASE)
    if not m:
        m = re.search(rf'<meta[^>]*content="([^"]*)"[^>]*name="{name}"', html, re.IGNORECASE)
    return clean(m.group(1)) if m else ""


def page_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return clean(m.group(1)) if m else ""


def page_h1(html: str) -> str:
    m = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    return clean(m.group(1)) if m else ""


def extract_faq(html: str) -> list[dict]:
    """Parse Q&A pairs from every FAQ section ('Вопросы...' / '(FAQ)' h2 headers)."""
    h2s = list(H2_RE.finditer(html))
    questions: list[dict] = []
    seen: set[str] = set()
    for i, m in enumerate(h2s):
        h2t = clean(m.group(1)).lower()
        if "вопрос" not in h2t and "faq" not in h2t:
            continue
        start = m.end()
        end = h2s[i + 1].start() if i + 1 < len(h2s) else len(html)
        region = html[start:end]
        h3s = list(H3_RE.finditer(region))
        for j, q_m in enumerate(h3s):
            q = clean(q_m.group(1)).strip(" ?") + "?"
            if len(q) < 8 or len(q) > 220 or q in seen:
                continue
            a_start = q_m.end()
            a_end = h3s[j + 1].start() if j + 1 < len(h3s) else len(region)
            a = clean(region[a_start:a_end])[:2000]
            if len(a) < 10:
                continue
            seen.add(q)
            questions.append({
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            })
    return questions


def organization() -> dict:
    return {
        "@type": "Organization",
        "@id": ORG_ID,
        "name": "Raskrutov",
        "alternateName": "Raskrutov — экосистема цифрового роста бизнеса",
        "url": f"{BASE}/",
        "logo": {"@type": "ImageObject", "url": LOGO},
        "description": "Digital-агентство полного цикла: создание сайтов, SEO и AEO-продвижение, "
                       "контекстная реклама, CRM, обучение digital-навыкам и конструктор сайтов R-Builder.",
        "email": "info@raskrutov.kz",
        "telephone": "+7 700 021 69 00",
        "address": {
            "@type": "PostalAddress",
            "addressCountry": "KZ",
            "addressLocality": "Петропавловск",
            "streetAddress": "ул. М. Жумабаева, 109, 6 этаж, офис 606а",
        },
        "sameAs": SAME_AS,
        "knowsAbout": ["создание сайтов", "SEO", "AEO", "контекстная реклама",
                       "CRM", "digital-маркетинг", "обучение digital"],
    }


def website() -> dict:
    return {
        "@type": "WebSite",
        "@id": SITE_ID,
        "url": f"{BASE}/",
        "name": "Raskrutov",
        "publisher": {"@id": ORG_ID},
        "inLanguage": "ru",
    }


def local_business() -> dict:
    return {
        "@type": "ProfessionalService",
        "@id": f"{BASE}/#localbusiness",
        "name": "Raskrutov — digital-агентство",
        "image": LOGO,
        "url": f"{BASE}/",
        "telephone": "+7 700 021 69 00",
        "email": "info@raskrutov.kz",
        "priceRange": "от 180 000 KZT",
        "currenciesAccepted": "KZT",
        "address": {
            "@type": "PostalAddress",
            "addressCountry": "KZ",
            "addressLocality": "Петропавловск",
            "streetAddress": "ул. М. Жумабаева, 109, 6 этаж, офис 606а",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 54.8753, "longitude": 69.1620},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "10:00",
            "closes": "19:00",
        }],
        "areaServed": {"@type": "Country", "name": "Казахстан"},
        "sameAs": SAME_AS,
        "parentOrganization": {"@id": ORG_ID},
    }


def breadcrumb(items: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(items)
        ],
    }


def webpage(url: str, title: str, desc: str, ptype: str = "WebPage") -> dict:
    node = {
        "@type": ptype,
        "@id": url,
        "url": url,
        "name": title,
        "isPartOf": {"@id": SITE_ID},
        "about": {"@id": ORG_ID},
        "inLanguage": "ru",
    }
    if desc:
        node["description"] = desc
    return node


# title cache for breadcrumb parents
_title_cache: dict[str, str] = {}

def crumb_label(path: Path) -> str:
    key = path.as_posix()
    if key not in _title_cache:
        html = path.read_text(encoding="utf-8", errors="ignore")
        t = page_title(html) or page_h1(html)
        _title_cache[key] = t.split("—")[0].split("|")[0].strip()[:60]
    return _title_cache[key]


def breadcrumb_chain(rel: str, self_html: str) -> list[tuple[str, str]]:
    """Главная -> каждый существующий префикс-родитель -> текущая страница."""
    chain = [("Главная", f"{BASE}/")]
    if rel == "index.html":
        return chain
    stem = Path(rel).stem  # e.g. web-studiya_sozdanie-saitov_landing
    parts = stem.split("_")
    for i in range(1, len(parts)):
        parent = M / "pages" / ("_".join(parts[:i]) + ".html")
        if parent.exists():
            chain.append((crumb_label(parent), f"{BASE}/pages/{parent.name}"))
    chain.append((crumb_label(M / rel), f"{BASE}/{rel}"))
    return chain


def page_url(rel: str) -> str:
    return f"{BASE}/" if rel == "index.html" else f"{BASE}/{rel}"


def service_node(rel: str, name: str, desc: str) -> dict:
    node = {
        "@type": "Service",
        "name": name,
        "url": page_url(rel),
        "provider": {"@id": ORG_ID},
        "areaServed": {"@type": "Country", "name": "Казахстан"},
        "serviceType": name,
    }
    if desc:
        node["description"] = desc
    return node


def build_graph(path: Path) -> dict:
    rel = path.relative_to(M).as_posix()
    html = path.read_text(encoding="utf-8", errors="ignore")
    title = page_title(html)
    h1 = page_h1(html)
    desc = meta(html, "description") or h1
    url = page_url(rel)
    name = h1 or title

    graph: list[dict] = [organization(), website(), breadcrumb(breadcrumb_chain(rel, html))]

    if rel == "index.html":
        graph.append(local_business())
        graph.append(webpage(url, title, desc))
        faq = extract_faq(html)
        if faq:
            graph.append({"@type": "FAQPage", "mainEntity": faq})
        graph.append({
            "@type": "ItemList",
            "name": "Услуги Raskrutov",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1,
                 "item": service_node(srel, sname, "")}
                for i, (sname, srel) in enumerate(SERVICE_LINKS)
            ],
        })
        return {"@context": "https://schema.org", "@graph": graph}

    stem = Path(rel).stem
    if rel.startswith("pages/web-studiya") or stem.startswith("crm"):
        graph.append(service_node(rel, name, desc))
        graph.append(webpage(url, title, desc))
    elif stem.startswith("akademiya_obuchenie") or stem == "akademiya_korporativnoe-obuchenie":
        graph.append({
            "@type": "Course",
            "name": name,
            "description": desc,
            "url": url,
            "provider": {"@id": ORG_ID},
            "hasCourseInstance": {
                "@type": "CourseInstance",
                "courseMode": "online",
                "courseWorkload": "P10H",
            },
        })
        graph.append(webpage(url, title, desc))
    elif stem.startswith("r-builder"):
        graph.append({
            "@type": "SoftwareApplication",
            "name": "R-Builder — конструктор сайтов",
            "url": url,
            "applicationCategory": "WebApplication",
            "operatingSystem": "Web",
            "description": desc,
            "creator": {"@id": ORG_ID},
        })
        graph.append(webpage(url, title, desc))
    elif stem.startswith("keysy"):
        graph.append(webpage(url, title, desc, "CollectionPage"))
    elif stem.startswith("o-kompanii"):
        graph.append(webpage(url, title, desc, "AboutPage"))
    elif stem == "kontakty":
        graph.append(webpage(url, title, desc, "ContactPage"))
    elif stem.startswith("faq"):
        graph.append(webpage(url, title, desc))
        faq = extract_faq(html)
        if faq:
            graph.append({"@type": "FAQPage", "mainEntity": faq})
    else:
        graph.append(webpage(url, title, desc))

    return {"@context": "https://schema.org", "@graph": graph}


def inject(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="ignore")
    graph = build_graph(path)
    payload = json.dumps(graph, ensure_ascii=False, indent=2)
    block = f'<script type="application/ld+json" data-schema="raskrutov">\n{payload}\n</script>\n'
    html = INJECT_RE.sub("", html)
    head_end = html.find("</head>")
    if head_end == -1:
        return False
    html = html[:head_end] + block + html[head_end:]
    path.write_text(html, encoding="utf-8")
    return True


def main() -> None:
    done = faq_pages = 0
    for f in sorted(M.rglob("*.html")):
        if "assets" in f.relative_to(M).parts:
            continue
        if inject(f):
            done += 1
    print(f"pages with JSON-LD: {done}")
    # summary of what was generated
    sample = build_graph(M / "index.html")
    types = [n["@type"] for n in sample["@graph"]]
    faq_n = next((n for n in sample["@graph"] if n["@type"] == "FAQPage"), None)
    print(f"index.html graph: {types}")
    if faq_n:
        print(f"homepage FAQ questions: {len(faq_n['mainEntity'])}")


if __name__ == "__main__":
    main()
