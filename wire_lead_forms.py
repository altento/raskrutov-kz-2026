#!/usr/bin/env python3
"""Wire all Mottor lead forms to unified Supabase lead-forms.js."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "site_mirror"

# form id → human base name (page label appended)
FORM_BASE_NAME = {
    "msf1991300": "Контакты — отправьте заявку",
    "msf1974746": "Попап — обсудить проект",
    "msf2015027": "CTA — заказать digital-аудит",
    "msf2015014": "CTA — консультация по Digital-консалтингу",
    "msf2014788": "CTA — рассчитать рекламный бюджет",
    "msf2014786": "CTA — получить стратегию рекламы",
}

HONEYPOT = (
    '<input type="text" name="website" autocomplete="off" tabindex="-1" '
    'aria-hidden="true" class="lead-form-honeypot" value=""/>'
)
STATUS = '<div data-form-status aria-live="polite" class="lead-form-status"></div>'

FORM_RE = re.compile(
    r'(<form\b)([^>]*)(>)(.*?)(</form>)',
    re.I | re.S,
)


def page_label(rel: str) -> str:
    if rel in ("index.html",):
        return "главная"
    parts = Path(rel).parts
    if parts[-1] == "index.html":
        parts = parts[:-1]
    # last 1–2 segments
    nice = {
        "web-studiya": "студия",
        "sozdanie-saitov": "создание сайтов",
        "landing": "лендинги",
        "internet-magazin": "интернет-магазины",
        "korporativnyy-sayt": "корпоративный сайт",
        "mnogostranichnye-sayty": "многостраничные сайты",
        "onlayn-shkola": "онлайн-школы",
        "sayt-vizitka": "сайт-визитка",
        "redizayn-sayta": "редизайн",
        "obsluzhivanie-saytov": "обслуживание сайтов",
        "integratsii": "интеграции",
        "onlayn-kalkulyatory": "онлайн-калькуляторы",
        "ai-konsultanty": "AI-консультанты",
        "crm-sistemy": "CRM для сайта",
        "seo-prodvizhenie": "SEO-продвижение",
        "google": "Google",
        "yandex": "Яндекс",
        "aeo-prodvizhenie": "AEO",
        "kontekstnaya-reklama": "контекстная реклама",
        "google-ads": "Google Ads",
        "yandex-direct": "Яндекс Директ",
        "lidogeneratsiya": "лидогенерация",
        "podderzhka-saytov": "поддержка сайтов",
        "digital-konsalting": "Digital-консалтинг",
        "audit-sayta": "аудит сайта",
        "audit-prodvizheniya": "аудит продвижения",
        "digital-strategiya": "digital-стратегия",
        "konsultatsiya-dlya-biznesa": "консультация",
        "dizayn": "дизайн",
        "logotip": "логотип",
        "brendbuk": "брендбук",
        "neyming": "нейминг",
        "crm": "CRM",
        "vnedrenie-crm": "внедрение CRM",
        "avtomatizatsiya-prodazh": "автоматизация продаж",
        "integratsiya-s-crm": "интеграция с CRM",
        "akademiya": "академия",
        "r-builder": "R-Builder",
        "partneram": "партнёрам",
        "keysy": "кейсы",
        "faq": "FAQ",
        "o-kompanii": "о компании",
        "kontakty": "контакты",
    }
    labels = [nice.get(p, p) for p in parts[-2:]] if parts else ["сайт"]
    return " — ".join(labels)


def depth_prefix(rel: str) -> str:
    depth = len(Path(rel).parts) - 1
    return "../" * depth if depth > 0 else ""


def form_name_for(fid: str, rel: str) -> str:
    base = FORM_BASE_NAME.get(fid, f"Форма {fid}")
    return f"{base} — {page_label(rel)}"


def patch_form(match: re.Match, rel: str) -> str:
    open_tag, attrs, gt, body, close = match.groups()
    # skip already non-lead tiny forms if any
    fid_m = re.search(r'\bid=["\'](msf\d+)["\']', attrs, re.I)
    if not fid_m:
        # only wire Mottor lead forms
        if "msf-form" not in attrs and "msf-form" not in body[:200]:
            return match.group(0)
        fid = "unknown"
    else:
        fid = fid_m.group(1)

    if "data-lead-form" not in attrs:
        attrs += ' data-lead-form'
    # refresh form name each run
    fname = form_name_for(fid, rel).replace('"', "&quot;")
    if re.search(r'data-form-name=', attrs, re.I):
        attrs = re.sub(
            r'\s*data-form-name=(["\'])[^"\']*\1',
            f' data-form-name="{fname}"',
            attrs,
            flags=re.I,
        )
    else:
        attrs += f' data-form-name="{fname}"'

    # Enable browser validation
    attrs = re.sub(r'\s*novalidate(?:\s*=\s*(["\'][^"\']*["\']|novalidate))?', "", attrs, flags=re.I)

    # honeypot
    if 'name="website"' not in body and "lead-form-honeypot" not in body:
        # before closing, after last field / before ms_meta if present
        if re.search(r'<input[^>]*name=["\']ms_meta["\']', body, re.I):
            body = re.sub(
                r'(<input[^>]*name=["\']ms_meta["\'][^>]*>)',
                HONEYPOT + r"\1",
                body,
                count=1,
                flags=re.I,
            )
        else:
            body = body + HONEYPOT

    # status
    if "data-form-status" not in body:
        # after submit button block if possible
        if "msf-submit" in body:
            body = re.sub(
                r'(</div>\s*</div>\s*</div>\s*)(<input[^>]*name=["\']ms_meta["\'])',
                r"\1" + STATUS + r"\2",
                body,
                count=1,
                flags=re.I,
            )
            if "data-form-status" not in body:
                body = body + STATUS
        else:
            body = body + STATUS

    return f"{open_tag}{attrs}{gt}{body}{close}"


def _lead_css_inline() -> str:
    css = (MIRROR / "assets/css/lead-forms.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css).strip()
    return f'<style data-lead-forms-inline="1">{css}</style>'


def inject_assets(html: str, rel: str) -> str:
    pref = depth_prefix(rel)
    js_src = f'{pref}assets/js/lead-forms.js'
    css_tag = _lead_css_inline()
    js_tag = f'<script src="{js_src}" defer data-lead-forms-js></script>'

    # Drop old blocking stylesheet if present
    html = re.sub(
        r'<link[^>]*(?:data-lead-forms-css|lead-forms\.css)[^>]*/?>',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'<style\s+data-lead-forms-inline=["\']1["\']\s*>.*?</style>',
        "",
        html,
        flags=re.I | re.S,
    )
    if "</head>" in html:
        html = html.replace("</head>", css_tag + "\n</head>", 1)
    else:
        html = css_tag + html

    if "data-lead-forms-js" not in html:
        if "</body>" in html:
            html = html.replace("</body>", js_tag + "\n</body>", 1)
        else:
            html = html + js_tag
    else:
        html = re.sub(
            r'<script[^>]*data-lead-forms-js[^>]*>\s*</script>',
            js_tag,
            html,
            count=1,
            flags=re.I,
        )
    return html


def process_page(path: Path) -> bool:
    rel = path.relative_to(MIRROR).as_posix()
    html = path.read_text(encoding="utf-8", errors="replace")
    if "<form" not in html.lower():
        return False
    if "msf-form" not in html and "msf1991300" not in html:
        return False

    def repl(m: re.Match) -> str:
        return patch_form(m, rel)

    new_html, n = FORM_RE.subn(repl, html)
    new_html = inject_assets(new_html, rel)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8", newline="\n")
        return True
    return n > 0


def main() -> None:
    changed = 0
    forms = 0
    for p in sorted(MIRROR.rglob("*.html")):
        if "assets" in p.relative_to(MIRROR).parts:
            continue
        if p.parent.name == "pages":
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        forms += len(re.findall(r"<form\b", t, re.I))
        if process_page(p):
            changed += 1
            print("wired", p.relative_to(MIRROR).as_posix())
    print(f"done: pages_changed={changed}, forms_seen~={forms}")


if __name__ == "__main__":
    main()
