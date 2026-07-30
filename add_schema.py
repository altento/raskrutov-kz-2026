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

M = Path(__file__).resolve().parent / "site_mirror"
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
    ("Создание сайтов", "web-studiya/sozdanie-saitov/"),
    ("Услуги дизайнера", "web-studiya/dizayn/"),
    ("SEO-продвижение", "web-studiya/seo-prodvizhenie/"),
    ("AEO — оптимизация под ИИ-поиск", "web-studiya/aeo-prodvizhenie/"),
    ("Контекстная реклама", "web-studiya/kontekstnaya-reklama/"),
    ("Лидогенерация", "web-studiya/lidogeneratsiya/"),
    ("Поддержка сайтов", "web-studiya/podderzhka-saytov/"),
    ("Digital-консалтинг", "web-studiya/digital-konsalting/"),
]

# Fallback labels when parent page title is a redirect stub / missing
CRUMB_LABELS = {
    "web-studiya": "Студия",
    "sozdanie-saitov": "Создание сайтов",
    "landing": "Лендинги",
    "mnogostranichnye-sayty": "Многостраничные сайты",
    "korporativnyy-sayt": "Корпоративный сайт",
    "internet-magazin": "Интернет-магазин",
    "onlayn-shkola": "Онлайн-школа",
    "sayt-vizitka": "Сайт-визитка",
    "redizayn-sayta": "Редизайн",
    "obsluzhivanie-saytov": "Обслуживание сайтов",
    "integratsii": "Интеграции",
    "onlayn-kalkulyatory": "Онлайн-калькуляторы",
    "ai-konsultanty": "AI-консультанты",
    "crm-sistemy": "CRM для сайта",
    "seo-prodvizhenie": "SEO-продвижение",
    "aeo-prodvizhenie": "AEO-продвижение",
    "dizayn": "Дизайн",
    "neyming": "Нейминг",
    "brendbuk": "Брендбук",
    "logotip": "Логотип",
    "kontekstnaya-reklama": "Контекстная реклама",
    "google-ads": "Google Ads",
    "yandex-direct": "Яндекс Директ",
    "google": "Google",
    "yandex": "Яндекс",
    "digital-konsalting": "Digital-консалтинг",
    "audit-sayta": "Аудит сайта",
    "audit-prodvizheniya": "Аудит продвижения",
    "digital-strategiya": "Digital-стратегия",
    "konsultatsiya-dlya-biznesa": "Консультация",
    "lidogeneratsiya": "Лидогенерация",
    "podderzhka-saytov": "Поддержка сайтов",
    "r-builder": "R-Builder",
    "chto-takoe-r-builder": "Что такое R-Builder",
    "ai-r-builder": "AI R-Builder",
    "vozmozhnosti": "Возможности",
    "dlya-biznesa": "Для бизнеса",
    "akademiya": "Академия",
    "obuchenie-sozdaniyu-saytov": "Обучение созданию сайтов",
    "obuchenie-seo-aeo": "Обучение SEO и AEO",
    "obuchenie-r-builder": "Обучение R-Builder",
    "korporativnoe-obuchenie": "Корпоративное обучение",
    "partneram": "Партнёрам",
    "franshiza": "Франшиза",
    "pakety-partnerstva": "Пакеты партнёрства",
    "dlya-reklamnyh-agentstv": "Для рекламных агентств",
    "deystvuyushchie-partnery": "Действующие партнёры",
    "o-kompanii": "О компании",
    "o-nas": "О нас",
    "komanda": "Команда",
    "blagodarstvennye-pisma": "Благодарственные письма",
    "klienty": "Клиенты",
    "blog": "Блог",
    "vakansii": "Вакансии",
    "keysy": "Кейсы",
    "sayty": "Сайты",
    "prodvizhenie": "Продвижение",
    "partnery": "Партнёры",
    "kontakty": "Контакты",
    "faq": "FAQ",
    "aeo": "AEO",
    "seo": "SEO",
    "crm": "CRM",
    "partnerstvo": "Партнёрство",
    "vnedrenie-crm": "Внедрение CRM",
    "avtomatizatsiya-prodazh": "Автоматизация продаж",
    "integratsiya-s-crm": "Интеграция с CRM",
    "consent": "Согласие",
    "regulation": "Положение",
}


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


def is_redirect_stub(path: Path) -> bool:
    if path.parent.name != "pages":
        return False
    head = path.read_text(encoding="utf-8", errors="ignore")[:800]
    return 'http-equiv="refresh"' in head.lower() or "Страница переехала" in head


def page_url(rel: str) -> str:
    """Pretty canonical URL from mirror-relative path."""
    if rel in ("index.html", ""):
        return f"{BASE}/"
    # Directory pages: web-studiya/sozdanie-saitov/landing/index.html
    if rel.endswith("/index.html"):
        return f"{BASE}/" + rel[: -len("/index.html")]
    if rel.endswith("index.html") and "/" in rel:
        return f"{BASE}/" + rel[: -len("index.html")].rstrip("/")
    # Legacy flat pages/*.html (redirect stubs / rare leftovers)
    if rel.startswith("pages/"):
        stem = Path(rel).stem.replace("_", "/")
        return f"{BASE}/{stem}"
    stem = Path(rel).stem.replace("_", "/")
    return f"{BASE}/{stem}"


def breadcrumb_chain(rel: str, self_html: str) -> list[tuple[str, str]]:
    """Главная -> каждый существующий префикс-родитель -> текущая страница."""
    chain = [("Главная", f"{BASE}/")]
    if rel == "index.html":
        return chain

    url = page_url(rel)
    path_parts = [p for p in url.replace(BASE, "").strip("/").split("/") if p]

    # Pretty directory layout
    if rel.endswith("/index.html") or (rel.endswith("index.html") and "/" in rel):
        built: list[str] = []
        for i, part in enumerate(path_parts):
            built.append(part)
            parent_rel = "/".join(built)
            parent_file = M / parent_rel / "index.html"
            is_self = i == len(path_parts) - 1
            # Prefer short canonical labels for hubs/parents
            short = CRUMB_LABELS.get(part)
            if is_self:
                label = short or page_h1(self_html) or page_title(self_html) or part
            elif short:
                label = short
            elif parent_file.exists() and not is_redirect_stub(parent_file):
                label = crumb_label(parent_file)
                if label.lower() in ("redirect", ""):
                    label = part
            else:
                label = part
            label = label.split("—")[0].split("|")[0].strip()[:60]
            chain.append((label, f"{BASE}/{parent_rel}"))
        return chain

    # Legacy pages/*.html
    stem = Path(rel).stem
    parts = stem.split("_")
    for i in range(1, len(parts)):
        parent = M / "pages" / ("_".join(parts[:i]) + ".html")
        pretty = "/".join(parts[:i])
        if parent.exists() and not is_redirect_stub(parent):
            chain.append((crumb_label(parent), f"{BASE}/{pretty}"))
        else:
            chain.append((CRUMB_LABELS.get(parts[i - 1], parts[i - 1]), f"{BASE}/{pretty}"))
    self_label = page_h1(self_html) or page_title(self_html) or stem
    self_label = self_label.split("—")[0].split("|")[0].strip()[:60]
    if self_label.lower() != "redirect":
        chain.append((self_label, url))
    return chain


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


def path_kind(rel: str) -> str:
    """Classify page for schema type selection."""
    pretty = page_url(rel).replace(BASE, "").strip("/")
    parts = pretty.split("/") if pretty else []
    joined = "/".join(parts)
    stem = Path(rel).stem
    if joined.startswith("web-studiya") or stem.startswith("web-studiya") or joined.startswith("crm") or stem.startswith("crm"):
        return "service"
    if "akademiya/obuchenie" in joined or stem.startswith("akademiya_obuchenie") or "korporativnoe-obuchenie" in joined:
        return "course"
    if joined.startswith("r-builder") or stem.startswith("r-builder"):
        return "rbuilder"
    if joined.startswith("keysy") or stem.startswith("keysy"):
        return "keysy"
    if joined.startswith("o-kompanii") or stem.startswith("o-kompanii"):
        return "about"
    if joined == "kontakty" or stem == "kontakty":
        return "contact"
    if joined.startswith("faq") or stem.startswith("faq"):
        return "faq"
    return "page"


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

    kind = path_kind(rel)
    if kind == "service":
        graph.append(service_node(rel, name, desc))
        graph.append(webpage(url, title or name, desc))
    elif kind == "course":
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
        graph.append(webpage(url, title or name, desc))
    elif kind == "rbuilder":
        graph.append({
            "@type": "SoftwareApplication",
            "name": "R-Builder — конструктор сайтов",
            "url": url,
            "applicationCategory": "WebApplication",
            "operatingSystem": "Web",
            "description": desc,
            "creator": {"@id": ORG_ID},
        })
        graph.append(webpage(url, title or name, desc))
    elif kind == "keysy":
        graph.append(webpage(url, title or name, desc, "CollectionPage"))
    elif kind == "about":
        graph.append(webpage(url, title or name, desc, "AboutPage"))
    elif kind == "contact":
        graph.append(webpage(url, title or name, desc, "ContactPage"))
    elif kind == "faq":
        graph.append(webpage(url, title or name, desc))
        faq = extract_faq(html)
        if faq:
            graph.append({"@type": "FAQPage", "mainEntity": faq})
    else:
        graph.append(webpage(url, title or name, desc))

    return {"@context": "https://schema.org", "@graph": graph}


def inject(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="ignore")
    graph = build_graph(path)
    payload = json.dumps(graph, ensure_ascii=False, indent=2)
    block = f'<script type="application/ld+json" data-schema="raskrutov">\n{payload}\n</script>\n'
    html = INJECT_RE.sub("", html)
    # Also strip unmarked Mottor JSON-LD on pages that rebuilt without schema
    html = ORIG_JSONLD_RE.sub("", html)
    head_end = html.find("</head>")
    if head_end == -1:
        return False
    html = html[:head_end] + block + html[head_end:]
    tmp = path.with_suffix(".schema-tmp.html")
    tmp.write_text(html, encoding="utf-8", newline="\n")
    tmp.replace(path)
    return True


FORCE_REPLACE_SCHEMA = {
    "web-studiya/sozdanie-saitov/landing/index.html",
    "web-studiya/sozdanie-saitov/internet-magazin/index.html",
    "web-studiya/sozdanie-saitov/korporativnyy-sayt/index.html",
}


ORIG_JSONLD_RE = re.compile(
    r'<script type="application/ld\+json">.*?</script>\s*',
    re.DOTALL | re.IGNORECASE,
)


def strip_original_jsonld(path: Path) -> bool:
    """Remove Mottor plain JSON-LD so our data-schema block is the source of truth."""
    html = path.read_text(encoding="utf-8", errors="ignore")
    html2, n = ORIG_JSONLD_RE.subn("", html)
    if n:
        path.write_text(html2, encoding="utf-8")
    return n > 0


def fix_title_from_h1(path: Path) -> bool:
    """If title still looks like parent hub, set from H1."""
    html = path.read_text(encoding="utf-8", errors="ignore")
    h1 = page_h1(html)
    title = page_title(html)
    if not h1:
        return False
    if "лендинг" in h1.lower() or "интернет-магазин" in h1.lower().replace(" ", "") or "корпоративн" in h1.lower():
        new_title = f"{h1} | Raskrutov"
        if title == new_title:
            return False
        html2, n = re.subn(
            r"<title[^>]*>.*?</title>",
            f"<title>{new_title}</title>",
            html,
            count=1,
            flags=re.I | re.S,
        )
        if n:
            # og:title too
            html2 = re.sub(
                r'(property=["\']og:title["\']\s+content=["\'])[^"\']*(["\'])',
                rf"\g<1>{new_title}\2",
                html2,
                flags=re.I,
            )
            path.write_text(html2, encoding="utf-8")
            return True
    return False


def main() -> None:
    done = skipped = stripped = titled = 0
    for f in sorted(M.rglob("*.html")):
        rel = f.relative_to(M).as_posix()
        if "assets" in f.relative_to(M).parts:
            continue
        if is_redirect_stub(f):
            skipped += 1
            continue
        if rel in FORCE_REPLACE_SCHEMA:
            if strip_original_jsonld(f):
                stripped += 1
            if fix_title_from_h1(f):
                titled += 1
        if inject(f):
            done += 1
    print(
        f"pages with JSON-LD: {done} (skipped stubs: {skipped}, "
        f"stripped original: {stripped}, titles fixed: {titled})"
    )
    sample = build_graph(M / "index.html")
    types = [n["@type"] for n in sample["@graph"]]
    faq_n = next((n for n in sample["@graph"] if n["@type"] == "FAQPage"), None)
    print(f"index.html graph: {types}")
    if faq_n:
        print(f"homepage FAQ questions: {len(faq_n['mainEntity'])}")
    landing = M / "web-studiya" / "sozdanie-saitov" / "landing" / "index.html"
    if landing.exists():
        g = build_graph(landing)
        print("landing graph:", [n["@type"] for n in g["@graph"]])
        for n in g["@graph"]:
            if n.get("@type") == "Service":
                print("landing service:", n.get("name"), n.get("url"))
            if n.get("@type") == "BreadcrumbList":
                for it in n["itemListElement"]:
                    print(" ", it["position"], it["name"], "->", it["item"])


if __name__ == "__main__":
    main()
