#!/usr/bin/env python3
"""Full audit: sitemap CSV vs live vs local vs homepage links."""
import csv
import json
import re
import ssl
import urllib.request
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(r"C:\Users\user\Projects\раскрутов")
MIRROR = ROOT / "site_mirror"
CSV_PATH = Path(
    r"C:\Users\user\Downloads\САЙТ RASKRUTOV.KZ  СТРАНИЦЫ И ХОД ВЫПОЛНЕНИЯ - Карта сайта.csv"
)
BASE = "https://raskrutov.kz"

PATH_ALIASES = {
    "/web-studiya/aeo-prodvizhenie": "pages/web-studiya_aeo-geo-prodvizhenie.html",
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
                "id": row[0].strip(),
                "section": row[1].strip() if len(row) > 1 else "",
                "title": row[3].strip() if len(row) > 3 else "",
                "url": row[4].strip(),
                "type": row[5].strip() if len(row) > 5 else "",
                "plan_status": row[11].strip() if len(row) > 11 else "",
                "note": row[16].strip() if len(row) > 16 else "",
            }
        )
    return out


def url_to_local_candidates(url_path: str) -> list[str]:
    slug = url_path.strip("/").replace("/", "_")
    cands = [
        f"pages/{slug}.html",
        f"assets/raskrutov.kz/{url_path.strip('/')}/index.html",
        f"assets/raskrutov.kz/{url_path.strip('/')}.html",
    ]
    if url_path in PATH_ALIASES:
        cands.insert(0, PATH_ALIASES[url_path])
    if url_path == "/":
        cands.insert(0, "index.html")
    return cands


def find_local(url_path: str) -> tuple[str | None, str | None]:
    for rel in url_to_local_candidates(url_path):
        full = MIRROR / rel
        if full.exists():
            return rel, "exact" if slug_match(rel, url_path) else "alias"
    # fuzzy: search assets/raskrutov.kz tree
    parts = url_path.strip("/").split("/")
    if parts and parts[0]:
        base = MIRROR / "assets" / "raskrutov.kz"
        if base.exists():
            for html in base.rglob("index.html"):
                rel_url = html.relative_to(base).as_posix()
                rel_url = "/" + rel_url.replace("/index.html", "").replace("index.html", "")
                if rel_url.rstrip("/") == url_path.rstrip("/"):
                    return html.relative_to(MIRROR).as_posix(), "assets_tree"
    return None, None


def slug_match(rel: str, url_path: str) -> bool:
    expected = f"pages/{url_path.strip('/').replace('/', '_')}.html"
    return rel.replace("\\", "/") == expected or rel.endswith("index.html")


def check_live(url_path: str) -> int | str:
    try:
        req = urllib.request.Request(
            BASE + url_path, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=20, context=CTX) as resp:
            return resp.status
    except HTTPError as exc:
        return exc.code
    except Exception:
        return "ERR"


def load_all_html() -> dict[str, str]:
    files = {}
    for p in [MIRROR / "index.html", * (MIRROR / "pages").glob("*.html")]:
        if p.exists():
            files[p.relative_to(MIRROR).as_posix()] = p.read_text(encoding="utf-8", errors="ignore")
    return files


def link_audit(url_path: str, html_files: dict[str, str]) -> dict:
    patterns = [
        url_path,
        url_path.lstrip("/"),
        url_path.replace("/", "_"),
        BASE + url_path,
    ]
    linked_from = []
    for fname, content in html_files.items():
        for pat in patterns:
            if pat and pat in content:
                # must be in link context
                if re.search(
                    rf'(data-page-link|data-original-url|href)=["\'][^"\']*{re.escape(pat[-40:])}',
                    content,
                ) or (pat in content and "home-sub-link" in content):
                    linked_from.append(fname)
                    break
    # precise: data-original-url exact match
    orig = BASE + url_path
    precise = []
    for fname, content in html_files.items():
        if f'data-original-url="{orig}"' in content:
            precise.append(fname)
        local_slug = url_path.strip("/").replace("/", "_")
        if f"pages/{local_slug}.html" in content and fname == "index.html":
            precise.append("index.html (local path)")
    return {"linked_from": sorted(set(linked_from)), "precise_original_url": sorted(set(precise))}


def main() -> None:
    rows = load_sitemap()
    html_files = load_all_html()
    report = []

    for row in rows:
        url = row["url"]
        local, local_kind = find_local(url)
        live = check_live(url)
        links = link_audit(url, html_files)
        entry = {
            **row,
            "live_status": live,
            "local_file": local,
            "local_kind": local_kind,
            "linked_from": links["linked_from"],
            "homepage_linked": "index.html" in links["linked_from"]
            or any("index.html" in x for x in links["precise_original_url"]),
            "original_url_on_home": "index.html" in str(links["precise_original_url"]),
        }
        report.append(entry)

    # classify
    ready_unlinked = [
        r
        for r in report
        if r["local_file"]
        and not r["homepage_linked"]
        and r["plan_status"] in ("Опубликована", "Создана", "Структура/SEO")
    ]
    live_ok = [r for r in report if r["live_status"] == 200]
    local_ok = [r for r in report if r["local_file"]]
    orphan_local = [
        r for r in report if r["local_file"] and r["live_status"] != 200 and not r["homepage_linked"]
    ]
    published_404 = [
        r for r in report if r["plan_status"] == "Опубликована" and r["live_status"] != 200
    ]

    out = {
        "summary": {
            "total": len(report),
            "live_200": len(live_ok),
            "local_found": len(local_ok),
            "ready_but_not_on_homepage": len(ready_unlinked),
            "local_orphans": len(orphan_local),
            "published_but_404": len(published_404),
        },
        "live_available": live_ok,
        "local_pages_not_linked": ready_unlinked,
        "all": report,
    }

    out_path = MIRROR / "full_sitemap_audit.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # human-readable summary
    lines = [
        f"Всего в карте: {len(report)}",
        f"Live 200: {len(live_ok)}",
        f"Локально найдено: {len(local_ok)}",
        f"Есть локально, но НЕ на главной: {len(ready_unlinked)}",
        "",
        "=== LIVE 200 ===",
    ]
    for r in live_ok:
        lines.append(f"  {r['url']} | {r['title']} | local: {r['local_file'] or '—'}")

    lines += ["", "=== Локально есть, кнопки не привязаны (главная) ==="]
    for r in ready_unlinked:
        lines.append(
            f"  {r['url']} | {r['title']} | {r['local_file']} | live:{r['live_status']} | plan:{r['plan_status']}"
        )

    lines += ["", "=== Опубликована в CSV, но 404 online ==="]
    for r in published_404[:30]:
        loc = "LOCAL" if r["local_file"] else "NO LOCAL"
        lines.append(f"  {r['url']} | {r['title']} | {loc}")

    txt = MIRROR / "full_sitemap_audit.txt"
    txt.write_text("\n".join(lines), encoding="utf-8")
    print(txt.read_text(encoding="utf-8"))
    print(f"\nJSON: {out_path}")


if __name__ == "__main__":
    main()
