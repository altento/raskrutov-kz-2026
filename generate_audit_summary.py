#!/usr/bin/env python3
import json
from pathlib import Path

MIRROR = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
audit = json.loads((MIRROR / "full_sitemap_audit.json").read_text(encoding="utf-8"))
cross = json.loads((MIRROR / "crosslink_audit.json").read_text(encoding="utf-8"))
incoming = {r["page"]: r["linked_from"] for r in cross["all"]}

rows = []
for item in audit["all"]:
    url = item["url"]
    local = item.get("local_file") or "—"
    live = item.get("live_status", "?")
    plan = item.get("plan_status", "")
    lf = item.get("local_file")
    links = incoming.get(lf, []) if lf else []
    from_home = "index.html" in links
    from_hub = [x for x in links if x != "index.html" and x != lf]
    status = "OK live" if live == 200 else f"404"
    if lf:
        if not links:
            link_status = "СИРОТА — нет входящих ссылок"
        elif not from_home and from_hub:
            link_status = f"только с {from_hub[0]}"
        elif from_home:
            link_status = "главная ✓"
        else:
            link_status = f"с {', '.join(links[:2])}"
    else:
        if plan == "Опубликована":
            link_status = "нет файла (опубликована в CSV)"
        elif plan == "Создана":
            link_status = "нет файла (создана в CSV)"
        else:
            link_status = "не зеркалилась"
    rows.append((url, item["title"], plan, status, local.replace("pages/", "") if local != "—" else "—", link_status))

# group stats
lines = [
    "ПРОВЕРКА ВСЕХ 73 СТРАНИЦ ИЗ КАРТЫ САЙТА",
    "=" * 70,
    f"Live 200: {audit['summary']['live_200']} из 73 (только главная)",
    f"Локально в зеркале: {audit['summary']['local_found']} из 73",
    f"Опубликовано в CSV, но 404 online: {audit['summary']['published_but_404']}",
    "",
    "ЛЕГЕНДА:",
    "  готовая страница = есть pages/*.html",
    "  СИРОТА = файл есть, но ни одна кнопка/ссылка на неё не ведёт",
    "  только с X = доступна только со страницы X, не с главного меню",
    "",
]

sections = [
    ("✅ ЛОКАЛЬНО ЕСТЬ + ПРИВЯЗАНА К ГЛАВНОЙ", lambda r: r[5].startswith("главная")),
    ("⚠️ ЛОКАЛЬНО ЕСТЬ, НО НЕ С ГЛАВНОЙ (живут сами / только с хаба)", lambda r: r[4] != "—" and not r[5].startswith("главная") and "СИРОТА" not in r[5]),
    ("🔴 ЛОКАЛЬНО ЕСТЬ, СИРОТЫ (вообще без ссылок)", lambda r: "СИРОТА" in r[5]),
    ("📋 В CSV ОПУБЛИКОВАНА, НО ФАЙЛА НЕТ", lambda r: r[4] == "—" and r[2] == "Опубликована"),
    ("📝 В CSV СОЗДАНА, НО ФАЙЛА НЕТ", lambda r: r[4] == "—" and r[2] == "Создана"),
    ("⏳ ЗАПЛАНИРОВАНО (нет файла)", lambda r: r[4] == "—" and r[2] == "Запланировано"),
]

for title, pred in sections:
    items = [r for r in rows if pred(r)]
    if not items:
        continue
    lines.append(title)
    lines.append("-" * 50)
    for url, name, plan, live, local, link in items:
        lines.append(f"  {url}")
        lines.append(f"    {name} | CSV:{plan} | live:{live} | {link}")
    lines.append("")

lines += [
    "ВАЖНО О КНОПКАХ НА ГЛАВНОЙ:",
    "  • «Вопросы» → pages/faq.html (linkRedirect)",
    "  • «Кейсы» → pages/keysy.html; подстраницы — с hub-навигации на keysy.html",
    "  • Карточка CRM → pages/crm.html (экосистема на главной)",
    "  • Услуги студии (landing, SEO, AEO…) — home-sub-link на главной + hub-child-links",
    "  • Подстраницы хабов доступны с соответствующих разделов (crm, faq, keysy…)",
    "",
    "Отчёты: site_mirror/full_sitemap_audit.json, crosslink_audit.json",
]

out = MIRROR / "full_sitemap_audit_summary.txt"
out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {out} ({len(rows)} URLs, orphans: {len([r for r in rows if 'СИРОТА' in r[5]])})")
