#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix / inject sitewide visual breadcrumbs for Raskrutov mirror.

- Builds chain from URL path + short Russian labels
- Injects accessible <nav class="rk-breadcrumbs">
- Hides legacy Mottor «Главная →» button rows
- Links CSS once per page
- Idempotent

Usage:
    python fix_breadcrumbs.py
"""
from __future__ import annotations

import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "site_mirror"

# Short crumb labels (path segment → visible name)
CRUMB_LABELS: dict[str, str] = {
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
    "dizayn": "Дизайн",
    "neyming": "Нейминг",
    "brendbuk": "Брендбук",
    "logotip": "Логотип",
    "seo-prodvizhenie": "SEO-продвижение",
    "google": "Google",
    "yandex": "Яндекс",
    "aeo-prodvizhenie": "AEO-продвижение",
    "kontekstnaya-reklama": "Контекстная реклама",
    "google-ads": "Google Ads",
    "yandex-direct": "Яндекс Директ",
    "lidogeneratsiya": "Лидогенерация",
    "podderzhka-saytov": "Поддержка сайтов",
    "digital-konsalting": "Digital-консалтинг",
    "audit-sayta": "Аудит сайта",
    "audit-prodvizheniya": "Аудит продвижения",
    "digital-strategiya": "Digital-стратегия",
    "konsultatsiya-dlya-biznesa": "Консультация",
    "crm": "CRM",
    "vnedrenie-crm": "Внедрение CRM",
    "avtomatizatsiya-prodazh": "Автоматизация продаж",
    "integratsiya-s-crm": "Интеграция с CRM",
    "akademiya": "Академия",
    "obuchenie-sozdaniyu-saytov": "Обучение созданию сайтов",
    "obuchenie-seo-aeo": "Обучение SEO и AEO",
    "obuchenie-r-builder": "Обучение R-Builder",
    "korporativnoe-obuchenie": "Корпоративное обучение",
    "r-builder": "R-Builder",
    "chto-takoe-r-builder": "Что такое R-Builder",
    "ai-r-builder": "AI R-Builder",
    "vozmozhnosti": "Возможности",
    "dlya-biznesa": "Для бизнеса",
    "partneram": "Партнёрам",
    "franshiza": "Франшиза",
    "pakety-partnerstva": "Пакеты партнёрства",
    "dlya-reklamnyh-agentstv": "Для рекламных агентств",
    "deystvuyushchie-partnery": "Действующие партнёры",
    "keysy": "Кейсы",
    "sayty": "Сайты",
    "prodvizhenie": "Продвижение",
    "partnery": "Партнёры",
    "faq": "FAQ",
    "aeo": "AEO",
    "seo": "SEO",
    "partnerstvo": "Партнёрство",
    "o-kompanii": "О компании",
    "o-nas": "О нас",
    "komanda": "Команда",
    "blagodarstvennye-pisma": "Благодарственные письма",
    "klienty": "Клиенты",
    "blog": "Блог",
    "vakansii": "Вакансии",
    "kontakty": "Контакты",
    "consent": "Согласие",
    "regulation": "Положение",
}

SKIP_VISUAL = {
    "index.html",  # homepage: no crumbs
}

CSS_MARK = 'data-rk-breadcrumbs-css'
NAV_MARK = 'data-rk-breadcrumbs'
OLD_WRAP_CLASS = "rk-old-breadcrumbs-wrap"

NAV_RE = re.compile(
    r'<nav\b[^>]*data-rk-breadcrumbs[^>]*>.*?</nav>\s*',
    re.I | re.S,
)
CSS_RE = re.compile(
    r'<link\b[^>]*data-rk-breadcrumbs-css[^>]*/?>\s*',
    re.I,
)


def depth_prefix(rel: str) -> str:
    # rel like web-studiya/sozdanie-saitov/landing/index.html
    parts = Path(rel).parts
    depth = len(parts) - 1  # exclude filename
    return "../" * depth if depth > 0 else ""


def path_parts(rel: str) -> list[str]:
    if rel in ("index.html", ""):
        return []
    p = Path(rel)
    if p.name == "index.html":
        return list(p.parent.parts)
    return list(p.with_suffix("").parts)


def chain_for(rel: str) -> list[tuple[str, str]]:
    """Return [(label, href_or_empty), ...] including current page (empty href)."""
    parts = path_parts(rel)
    if not parts:
        return []
    chain: list[tuple[str, str]] = [("Главная", "/")]
    built: list[str] = []
    for i, part in enumerate(parts):
        built.append(part)
        label = CRUMB_LABELS.get(part, part.replace("-", " "))
        is_last = i == len(parts) - 1
        href = "" if is_last else "/" + "/".join(built) + "/"
        chain.append((label, href))
    return chain


def render_nav(chain: list[tuple[str, str]]) -> str:
    if not chain:
        return ""
    items = []
    for i, (label, href) in enumerate(chain):
        is_last = i == len(chain) - 1
        if is_last or not href:
            items.append(
                f'<li aria-current="page"><span>{_esc(label)}</span></li>'
            )
        else:
            items.append(
                f'<li><a href="{_esc(href)}">{_esc(label)}</a></li>'
            )
    return (
        f'<nav class="rk-breadcrumbs" aria-label="Хлебные крошки" {NAV_MARK}>\n'
        f"  <ol>\n    "
        + "\n    ".join(items)
        + "\n  </ol>\n</nav>\n"
    )


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def ensure_css(html: str, rel: str) -> str:
    html = CSS_RE.sub("", html)
    html = re.sub(
        r'<style\s+data-rk-breadcrumbs-inline=["\']1["\']\s*>.*?</style>\s*',
        "",
        html,
        flags=re.I | re.S,
    )
    css_path = MIRROR / "assets/css/breadcrumbs.css"
    css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css).strip()
    tag = f'<style data-rk-breadcrumbs-inline="1">{css}</style>\n'
    if re.search(r"</head>", html, re.I):
        return re.sub(r"</head>", tag + "</head>", html, count=1, flags=re.I)
    return tag + html


def _unwrap_old_crumb_wraps(html: str) -> str:
    """Remove previously applied rk-old-breadcrumbs-wrap layers (may be nested)."""
    open_tag = f'<div class="{OLD_WRAP_CLASS}" hidden aria-hidden="true">'
    while open_tag in html:
        start = html.find(open_tag)
        if start < 0:
            break
        inner_start = start + len(open_tag)
        # Find matching close for this wrap div
        i = start
        depth = 0
        end = None
        while i < len(html) and i < start + 80000:
            if html.startswith("<div", i) and (
                i + 4 >= len(html) or html[i + 4] in " \t\r\n/>"
            ):
                depth += 1
                gt = html.find(">", i)
                i = gt + 1 if gt > 0 else i + 4
                continue
            if html.startswith("</div>", i):
                depth -= 1
                i += 6
                if depth == 0:
                    end = i
                    break
                continue
            i += 1
        if not end:
            break
        # unwrap: keep inner HTML, drop wrap open/close
        inner = html[inner_start : end - 6]
        html = html[:start] + inner + html[end:]
    return html


def _find_m_columns_row(html: str, before: int) -> int:
    """Nearest parent ``m-columns`` row start (not ``m-columns__column``)."""
    search_from = before
    while search_from > 0:
        i = html.rfind('<div class="m-columns', 0, search_from)
        if i < 0:
            return -1
        # Reject m-columns__column / m-columns__*
        rest = html[i + len('<div class="') : i + 40]
        if rest.startswith("m-columns__"):
            search_from = i
            continue
        if rest.startswith("m-columns"):
            return i
        search_from = i
    return -1


def _balanced_div_end(html: str, start: int, limit: int = 40000) -> int | None:
    i = start
    depth = 0
    while i < len(html) and i < start + limit:
        if html.startswith("<div", i) and (
            i + 4 >= len(html) or html[i + 4] in " \t\r\n/>"
        ):
            depth += 1
            gt = html.find(">", i)
            i = gt + 1 if gt > 0 else i + 4
            continue
        if html.startswith("</div>", i):
            depth -= 1
            i += 6
            if depth == 0:
                return i
            continue
        i += 1
    return None


def hide_old_mottor_crumbs(html: str) -> str:
    """Hide Mottor button-breadcrumb rows (Главная → / Студия → / …)."""
    html = _unwrap_old_crumb_wraps(html)

    # Any crumb-like button label with an arrow
    needle_re = re.compile(
        r"(?:Главная|Студия|Создание сайтов|Raskrutov|Academy|Studio)"
        r"[\xa0 ]*→",
        re.I,
    )
    start = 0
    while True:
        m = needle_re.search(html, start)
        if not m:
            break
        idx = m.start()
        lookback = html[max(0, idx - 200) : idx]
        if OLD_WRAP_CLASS in lookback:
            start = m.end()
            continue
        col_start = _find_m_columns_row(html, idx)
        if col_start < 0:
            start = m.end()
            continue
        end = _balanced_div_end(html, col_start)
        if not end:
            start = m.end()
            continue
        block = html[col_start:end]
        # Must look like a crumb strip (2+ arrows or Главная/Студия + arrow)
        arrow_n = block.count("→") + block.count("\u2192")
        if arrow_n < 1:
            start = m.end()
            continue
        wrapped = f'<div class="{OLD_WRAP_CLASS}" hidden aria-hidden="true">{block}</div>'
        html = html[:col_start] + wrapped + html[end:]
        start = col_start + len(wrapped)
    return html


SECTION_OPEN_RE = re.compile(
    # Require word-boundary so we don't match blk_section_inner
    r'<div\b[^>]*class="[^"]*\bblk_section\b[^"]*"[^>]*>',
    re.I,
)


def insert_nav(html: str, nav: str) -> str:
    """Insert nav once: before first real content section (under fixed menu).

    Mottor pages put the menu in an ``is_fixed`` blk_section (and often a
    second ``blk-section--ms`` variant). Do not insert before those, and do
    not match ``blk_section_inner``.
    """
    html = NAV_RE.sub("", html)
    if not nav:
        return html

    for m in SECTION_OPEN_RE.finditer(html):
        tag = m.group(0).lower()
        if "is_fixed" in tag:
            continue
        if "popup" in tag or "section_popup" in tag:
            continue
        if "blk-section--ms" in tag:
            continue  # alternate/mobile menu blocks
        return html[: m.start()] + nav + html[m.start() :]

    # Fallback: after #fixed-sections closes
    m = re.search(r'<div\s+id="fixed-sections">', html, re.I)
    if m:
        i = m.start()
        depth = 0
        while i < len(html):
            if html.startswith("<div", i) and (
                i + 4 >= len(html) or html[i + 4] in " \t\r\n/>"
            ):
                depth += 1
                gt = html.find(">", i)
                i = gt + 1 if gt > 0 else i + 4
                continue
            if html.startswith("</div>", i):
                depth -= 1
                i += 6
                if depth == 0:
                    return html[:i] + "\n" + nav + html[i:]
                continue
            i += 1

    m = re.search(r"<body[^>]*>", html, re.I)
    if m:
        return html[: m.end()] + "\n" + nav + html[m.end() :]
    return nav + html


def process(path: Path) -> bool:
    rel = path.relative_to(MIRROR).as_posix()
    if "assets" in path.parts:
        return False
    html = path.read_text(encoding="utf-8", errors="replace")
    original = html

    html = ensure_css(html, rel)

    if rel in SKIP_VISUAL:
        html = NAV_RE.sub("", html)
        html = hide_old_mottor_crumbs(html)
    else:
        chain = chain_for(rel)
        nav = render_nav(chain)
        html = hide_old_mottor_crumbs(html)
        html = insert_nav(html, nav)

    if html != original:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(html, encoding="utf-8", newline="\n")
        last_err: Exception | None = None
        for attempt in range(8):
            try:
                os.replace(tmp, path)
                last_err = None
                break
            except (PermissionError, OSError) as e:
                last_err = e
                time.sleep(0.25 * (attempt + 1))
        if last_err is not None:
            # Last resort: overwrite in place
            try:
                path.write_text(html, encoding="utf-8", newline="\n")
                if tmp.exists():
                    tmp.unlink(missing_ok=True)
            except Exception:
                raise last_err
        return True
    return False


def main() -> None:
    changed = 0
    total = 0
    for p in sorted(MIRROR.rglob("index.html")):
        if "assets" in p.parts:
            continue
        total += 1
        if process(p):
            changed += 1
            print("fixed", p.relative_to(MIRROR).as_posix())
    print(f"done: changed={changed}/{total}")


if __name__ == "__main__":
    main()
