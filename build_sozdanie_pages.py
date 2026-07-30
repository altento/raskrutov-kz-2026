#!/usr/bin/env python3
"""Build unique sozdanie-saitov child pages from internet-magazin template."""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from sozdanie_content import PAGES

ROOT = Path(__file__).resolve().parent
MIRROR = ROOT / "site_mirror"
TEMPLATE = MIRROR / "web-studiya" / "sozdanie-saitov" / "internet-magazin" / "index.html"
OUT_DIR = MIRROR / "web-studiya" / "sozdanie-saitov"
DOMAIN = "https://raskrutov.kz"
BASE_PATH = "/web-studiya/sozdanie-saitov"


def demote_extra_h1(html: str) -> str:
    """Keep first <h1>…</h1>, demote the rest to h2."""
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
    # replace from end so offsets stay valid
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


def replace_trust(html: str, trust: list[str]) -> str:
    old = [
        "10+ лет опыта в разработке и маркетинге",
        "200+ магазинов <br>запущено <br>для клиентов",
        "98% клиентов <br>продолжают <br>работу с нами",
        "Поддержка и <br>развитие <br>после запуска",
    ]
    for a, b in zip(old, trust):
        if a in html:
            html = html.replace(a, b, 1)
    return html


def replace_faq(html: str, faq: list[tuple[str, str]]) -> str:
    # Known leftover korporativnyy FAQ strings in IM template
    old_pairs = [
        (
            "Сколько стоит создание корпоративного сайта?",
            None,
        ),
        (
            "Стоимость корпоративного сайта начинается от 550 000 ₸. Итоговая цена зависит от количества страниц,",
            None,
        ),
        (
            "Что входит в стоимость корпоративного сайта?",
            None,
        ),
        (
            "Да. Архитектура корпоративного сайта предусматривает дальнейшее развитие. Можно добавлять новые услуги, на",
            None,
        ),
    ]
    # Broader: replace any remaining "корпоративного сайта" FAQ titles if still present
    # Apply new FAQ into first N known title/answer slots found in spoilers JSON + visible text.
    if not faq:
        return html

    # Replace first FAQ Q/A visibly if korporativnyy leftovers exist
    if faq:
        html = html.replace(
            "Сколько стоит создание корпоративного сайта?",
            faq[0][0],
        )
        # Truncated answer start in template
        html = html.replace(
            "Стоимость корпоративного сайта начинается от 550 000 ₸. Итоговая цена зависит от количества страниц,",
            faq[0][1][:120] if len(faq[0][1]) > 120 else faq[0][1],
        )
    if len(faq) > 1:
        html = html.replace("Что входит в стоимость корпоративного сайта?", faq[1][0])
    if len(faq) > 3:
        html = html.replace(
            "Да. Архитектура корпоративного сайта предусматривает дальнейшее развитие. Можно добавлять новые услуги, на",
            faq[3][1][:120],
        )

    # Inject / replace spoilers JSON block if present
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
    else:
        # Try alternate spoilers embedding
        html2, n = re.subn(
            r'"spoilers":\{[^}]*\}',
            '"spoilers":' + payload,
            html,
            count=1,
            flags=re.S,
        )
        if n:
            html = html2
    return html


def _json_str(s: str) -> str:
    import json

    return json.dumps(s, ensure_ascii=False)


def apply_phrase_map(html: str, pairs: list[tuple[str, str]]) -> str:
    # longest first
    for old, new in sorted(pairs, key=lambda x: len(x[0]), reverse=True):
        html = html.replace(old, new)
    return html


def strip_old_schema(html: str) -> str:
    html = re.sub(
        r'<script type="application/ld\+json"[^>]*>.*?</script>\s*',
        "",
        html,
        flags=re.I | re.S,
    )
    return html


def rewrite_path_refs(html: str, slug: str) -> str:
    """Fix any remaining internet-magazin path leftovers in canonical-ish places."""
    old = f"{BASE_PATH}/internet-magazin"
    new = f"{BASE_PATH}/{slug}"
    return html.replace(old, new)


def build_one(slug: str) -> Path:
    if slug not in PAGES:
        raise KeyError(slug)
    pack = PAGES[slug]
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)
    html = TEMPLATE.read_text(encoding="utf-8", errors="replace")
    pretty = f"{BASE_PATH}/{slug}/"

    html = replace_h1s(html, pack["h1s"])
    if pack.get("hero_lead"):
        old_lead = (
            "Разрабатываем интернет-магазины под ключ: удобный каталог, быстрый заказ, "
            "онлайн-оплата, интеграции с CRM и маркетплейсами — всё для стабильного роста ваших продаж"
        )
        # after phrase_map hero may already change; try both
        html = html.replace(old_lead, pack["hero_lead"])
    html = apply_phrase_map(html, pack.get("phrase_map", []))
    # hero_lead again in case phrase_map changed the old lead first
    if pack.get("hero_lead") and pack["hero_lead"] not in html:
        # try shortened unique prefix
        pass
    html = replace_trust(html, pack.get("trust", []))
    html = replace_faq(html, pack.get("faq", []))
    html = replace_meta(html, pack["title"], pack["description"], pretty)
    html = rewrite_path_refs(html, slug)
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
    print(f"OK {slug}: size={path.stat().st_size} h1_count={len(plains)} first={plains[0][:70]!r}")
    if "корпоративного сайта" in t and slug != "korporativnyy-sayt":
        print(f"  WARN leftover korporativnyy phrases in {slug}")
    if "internet-magazin" in t and f"/{slug}" not in t[t.find("canonical") : t.find("canonical") + 200]:
        # soft check
        pass
    bad_parent = "Создание сайтов под ключ" in (plains[0] if plains else "")
    if bad_parent:
        print("  ERROR still parent H1")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*", help="slugs to build (default: all)")
    args = ap.parse_args()
    slugs = args.slugs or list(PAGES.keys())
    for slug in slugs:
        out = build_one(slug)
        verify(out, slug)


if __name__ == "__main__":
    main()
