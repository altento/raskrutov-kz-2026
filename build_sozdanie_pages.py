#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build unique sozdanie-saitov child pages from landing/corporate templates."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from sozdanie_content import PAGES

ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "site_mirror"
OUT_DIR = MIRROR / "web-studiya" / "sozdanie-saitov"
DOMAIN = "https://raskrutov.kz"
BASE_PATH = "/web-studiya/sozdanie-saitov"
GEN_ROOT = MIRROR / "assets" / "generated" / "sozdanie"

TEMPLATES = {
    "landing": OUT_DIR / "landing" / "index.html",
    "corporate": OUT_DIR / "korporativnyy-sayt" / "index.html",
    "shop": OUT_DIR / "internet-magazin" / "index.html",
}

# Depth from sozdanie/<slug>/ to site root assets = ../../../assets/...
ASSET_PREFIX = "../../../assets/generated/sozdanie"


def demote_extra_h1(html: str) -> str:
    count = [0]

    def repl(m: re.Match) -> str:
        count[0] += 1
        if count[0] == 1:
            return m.group(0)
        return "<h2" + m.group(1) + ">" + m.group(2) + "</h2>"

    return re.sub(r"<h1([^>]*)>(.*?)</h1>", repl, html, flags=re.S)


def replace_h1s(html: str, h1s: dict[int, str]) -> str:
    matches = list(re.finditer(r"<h1([^>]*)>(.*?)</h1>", html, flags=re.S))
    if not matches:
        raise RuntimeError("no h1 found in template")
    for i in range(len(matches) - 1, -1, -1):
        if i not in h1s:
            continue
        m = matches[i]
        html = html[: m.start()] + f"<h1{m.group(1)}>{h1s[i]}</h1>" + html[m.end() :]
    return html


def replace_meta(html: str, title: str, description: str, pretty: str) -> str:
    canon = DOMAIN + pretty.rstrip("/")
    html = re.sub(
        r"<title[^>]*>.*?</title>",
        f"<title>{title}</title>",
        html,
        count=1,
        flags=re.I | re.S,
    )
    if re.search(r'name=["\']description["\']', html, re.I):
        html = re.sub(
            r'(name=["\']description["\']\s+content=["\'])[^"\']*(["\'])',
            rf"\g<1>{description}\2",
            html,
            count=1,
            flags=re.I,
        )
        html = re.sub(
            r'(content=["\'])[^"\']*(["\']\s+name=["\']description["\'])',
            rf"\g<1>{description}\2",
            html,
            count=1,
            flags=re.I,
        )
    html = re.sub(
        r'(property=["\']og:title["\']\s+content=["\'])[^"\']*(["\'])',
        rf"\g<1>{title}\2",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'(property=["\']og:description["\']\s+content=["\'])[^"\']*(["\'])',
        rf"\g<1>{description}\2",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'(property=["\']og:url["\']\s+content=["\'])[^"\']*(["\'])',
        rf"\g<1>{canon}\2",
        html,
        flags=re.I,
    )
    if re.search(r'rel=["\']canonical["\']', html, re.I):
        html = re.sub(
            r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\']\s*/?>',
            f'<link rel="canonical" href="{canon}"/>',
            html,
            flags=re.I,
        )
    else:
        html = html.replace("</head>", f'<link rel="canonical" href="{canon}"/>\n</head>', 1)
    return html


def replace_trust(html: str, trust: list[str], template: str) -> str:
    if not trust:
        return html
    if template == "landing":
        # landing trust texts vary; skip soft replace if unknown
        old_candidates = [
            [
                "10+ лет опыта в разработке и маркетинге",
                "200+ лендингов <br>запущено <br>для клиентов",
                "98% клиентов <br>продолжают <br>работу с нами",
                "Поддержка и <br>развитие <br>после запуска",
            ],
            [
                "10+ лет опыта в разработке и маркетинге",
                "200+ сайтов <br>запущено <br>для клиентов",
                "98% клиентов <br>продолжают <br>работу с нами",
                "Поддержка и <br>развитие <br>после запуска",
            ],
        ]
    else:
        old_candidates = [
            [
                "10+ лет опыта в разработке и маркетинге",
                "200+ сайтов <br>запущено <br>для клиентов",
                "98% клиентов <br>продолжают <br>работу с нами",
                "Поддержка и <br>развитие <br>после запуска",
            ],
            [
                "10+ лет опыта в разработке и маркетинге",
                "200+ магазинов <br>запущено <br>для клиентов",
                "98% клиентов <br>продолжают <br>работу с нами",
                "Поддержка и <br>развитие <br>после запуска",
            ],
        ]
    for old in old_candidates:
        if all(a in html for a in old[:1]):
            for a, b in zip(old, trust):
                if a in html:
                    html = html.replace(a, b, 1)
            break
    return html


def _json_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def replace_faq(html: str, faq: list[tuple[str, str]]) -> str:
    if not faq:
        return html
    spoilers = []
    for q, a in faq:
        spoilers.append(
            '{"title":{"content":%s},"defaultOpen":false,"displayType":"text","text":{"content":%s,"blocks":[]}}'
            % (_json_str(q), _json_str(a))
        )
    payload = "[" + ",".join(spoilers) + "]"
    html2, n = re.subn(
        r'"spoilers":\s*\[.*?\]',
        '"spoilers":' + payload,
        html,
        count=1,
        flags=re.S,
    )
    if n:
        html = html2

    # Visible FAQ question titles — replace first N known FAQ title strings loosely
    # by rewriting <summary>/<spoiler> titles if present as plain text near "Часто"
    return html


def apply_phrase_map(html: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in sorted(pairs, key=lambda x: len(x[0]), reverse=True):
        html = html.replace(old, new)
    return html


def strip_old_schema(html: str) -> str:
    return re.sub(
        r'<script type="application/ld\+json"[^>]*>.*?</script>\s*',
        "",
        html,
        flags=re.I | re.S,
    )


def rewrite_path_refs(html: str, slug: str, template: str) -> str:
    mapping = {
        "landing": f"{BASE_PATH}/landing",
        "corporate": f"{BASE_PATH}/korporativnyy-sayt",
        "shop": f"{BASE_PATH}/internet-magazin",
    }
    old = mapping[template]
    new = f"{BASE_PATH}/{slug}"
    html = html.replace(old, new)
    # also absolute domain variants
    html = html.replace(
        f"{DOMAIN}{old}",
        f"{DOMAIN}{new}",
    )
    return html


def replace_hash_urls(html: str, hashes: list[str], new_url: str) -> tuple[str, int]:
    """Replace any URL containing one of the hashes with new_url."""
    count = 0
    for h in hashes:
        pattern = re.compile(rf'[^\s"\'<>]*{re.escape(h)}[^\s"\'<>]*')

        def repl(_m: re.Match, url: str = new_url) -> str:
            nonlocal count
            count += 1
            return url

        html, n = pattern.subn(repl, html)
        count += max(0, n - n)  # keep nonlocal increments from repl
    return html, count


def inject_images(html: str, slug: str, pack: dict) -> str:
    hero = f"{ASSET_PREFIX}/{slug}/hero.webp"
    v1 = f"{ASSET_PREFIX}/{slug}/v1.webp"
    v2 = f"{ASSET_PREFIX}/{slug}/v2.webp"

    hero_hashes = pack.get("hero_hashes") or []
    mid_hashes = pack.get("mid_hashes") or []

    if hero_hashes:
        html, n = replace_hash_urls(html, hero_hashes, hero)
        print(f"  hero replacements: {n}")

    if mid_hashes:
        # first mid hash -> v1, rest -> v2
        html, n1 = replace_hash_urls(html, [mid_hashes[0]], v1)
        print(f"  mid v1 replacements: {n1}")
        if len(mid_hashes) > 1:
            html, n2 = replace_hash_urls(html, mid_hashes[1:], v2)
            print(f"  mid v2 replacements: {n2}")
    return html


def inject_hero_lead(html: str, lead: str, template: str) -> str:
    if not lead:
        return html
    known = [
        (
            "Корпоративный сайт - это имидж компании, инструмент<br>"
            "продаж и удобная пощадка для ваших клиентов и партнеров.<br>"
            "Создаём сайты, которые повышают доверие и приносят заявки."
        ),
        (
            "Разрабатываем лендинги, которые последовательно <br>"
            "ведут пользователя от первого знакомства с предложением <br>"
            "до заявки. Продумываем оффер, структуру, тексты, дизайн, <br>"
            "формы и аналитику."
        ),
        "Лендинг — это одностраничный сайт, посвящённый одному конкретному предложению: услуге, продукту, акции, мероприятию или новому направлению бизнеса.",
    ]
    for old in known:
        if old in html:
            html = html.replace(old, lead, 1)
            return html
    return html


TYPO_FIXES = [
    ("попучаем донные", "получаем данные"),
    ("попучаем данные", "получаем данные"),
    ("оклайн", "онлайн"),
    ("Лендниг", "Лендинг"),
    ("Лендниги", "Лендинги"),
    ("создаем сайт-визитка", "создаём сайт-визитку"),
    ("Как мы создаем сайт-визитка", "Как мы создаём сайт-визитку"),
    ("Вы делаете сайт-визитка под рекламу?", "Вы делаете сайт-визитку под рекламу?"),
]


def apply_typo_fixes(html: str) -> str:
    for a, b in TYPO_FIXES:
        html = html.replace(a, b)
    return html


def rewrite_breadcrumbs(html: str, slug: str, label: str) -> str:
    # Soft: replace trailing corporate/landing breadcrumb labels when present
    for old in (
        "Корпоративные сайты",
        "корпоративные сайты",
        "Лендинги",
        "лендинги",
        "Интернет-магазины",
    ):
        # only last breadcrumb-ish occurrences — replace all is ok for cloned pages
        if old in html:
            html = html.replace(old, label)
    return html


SLUG_LABEL = {
    "mnogostranichnye-sayty": "Многостраничные сайты",
    "sayt-vizitka": "Сайт-визитка",
    "onlayn-shkola": "Онлайн-школа",
    "onlayn-kalkulyatory": "Онлайн-калькуляторы",
    "ai-konsultanty": "AI-консультанты",
    "redizayn-sayta": "Редизайн сайта",
    "obsluzhivanie-saytov": "Обслуживание сайтов",
    "integratsii": "Интеграции",
    "crm-sistemy": "CRM для сайта",
}


def ensure_assets(slug: str) -> None:
    d = GEN_ROOT / slug
    for name in ("hero.webp", "v1.webp", "v2.webp"):
        p = d / name
        if not p.exists():
            raise FileNotFoundError(p)


def build_one(slug: str) -> Path:
    if slug not in PAGES:
        raise KeyError(slug)
    pack = PAGES[slug]
    template = pack.get("template", "corporate")
    tpl_path = TEMPLATES[template]
    if not tpl_path.exists():
        raise FileNotFoundError(tpl_path)
    ensure_assets(slug)

    html = tpl_path.read_text(encoding="utf-8", errors="replace")
    pretty = f"{BASE_PATH}/{slug}/"

    html = replace_h1s(html, pack.get("h1s", {}))
    html = inject_hero_lead(html, pack.get("hero_lead", ""), template)
    html = apply_phrase_map(html, pack.get("phrase_map", []))
    # re-apply lead if phrase_map changed it
    if pack.get("hero_lead") and pack["hero_lead"] not in html:
        html = inject_hero_lead(html, pack["hero_lead"], template)
    html = apply_typo_fixes(html)
    html = replace_trust(html, pack.get("trust", []), template)
    html = replace_faq(html, pack.get("faq", []))
    html = inject_images(html, slug, pack)
    html = replace_meta(html, pack["title"], pack["description"], pretty)
    html = rewrite_path_refs(html, slug, template)
    html = rewrite_breadcrumbs(html, slug, SLUG_LABEL.get(slug, slug))
    html = strip_old_schema(html)
    html = demote_extra_h1(html)

    out = OUT_DIR / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")
    return out


def verify(path: Path, slug: str) -> None:
    t = path.read_text(encoding="utf-8", errors="replace")
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", t, flags=re.S)
    plains = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h)).strip() for h in h1s]
    gen = f"generated/sozdanie/{slug}/"
    print(
        f"OK {slug}: size={path.stat().st_size} h1={len(plains)} "
        f"gen_imgs={t.count(gen)} first={plains[0][:60]!r}"
    )
    if gen not in t:
        print(f"  ERROR: no generated images for {slug}")
    leftover_map = {
        "landing": "Создание лендингов",
        "corporate": "Создание корпоративного",
    }
    pack = PAGES[slug]
    tpl = pack.get("template")
    bad = leftover_map.get(tpl, "")
    if bad and plains and bad in plains[0]:
        print(f"  WARN first H1 still template: {plains[0]!r}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*", help="slugs to build (default: all)")
    args = ap.parse_args()
    slugs = args.slugs or list(PAGES.keys())
    for slug in slugs:
        print("building", slug, "template=", PAGES[slug].get("template"))
        out = build_one(slug)
        verify(out, slug)


if __name__ == "__main__":
    main()
