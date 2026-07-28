#!/usr/bin/env python3
"""Cross-link audit: which local pages exist but aren't linked from anywhere."""
import json
import re
from pathlib import Path

MIRROR = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
AUDIT = MIRROR / "full_sitemap_audit.json"


def normalize_link(link: str, from_file: str) -> str | None:
    link = link.strip()
    if not link or link.startswith(("tel:", "mailto:", "http", "#")):
        return None
    if link.startswith("assets/"):
        return None
    if from_file.startswith("pages/"):
        if link.startswith("../"):
            link = link[3:]
        elif not link.startswith("pages/"):
            link = f"pages/{link}" if not link.startswith("index") else link
    if link == "index.html":
        return "index.html"
    if link.startswith("pages/"):
        return link
    if link.endswith(".html") and "/" not in link:
        return f"pages/{link}"
    return link


def collect_links() -> dict[str, set[str]]:
    incoming: dict[str, set[str]] = {}
    for html_path in [MIRROR / "index.html", * (MIRROR / "pages").glob("*.html")]:
        rel = html_path.relative_to(MIRROR).as_posix()
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        targets = set()
        for m in re.finditer(r'data-page-link="([^"]+)"', text):
            t = normalize_link(m.group(1), rel)
            if t:
                targets.add(t)
        for m in re.finditer(r'<a class="home-sub-link" href="([^"]+)"', text):
            t = normalize_link(m.group(1), rel)
            if t:
                targets.add(t)
        for t in targets:
            incoming.setdefault(t, set()).add(rel)
    return incoming


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    incoming = collect_links()

    local_pages = ["index.html"] + [
        f"pages/{p.name}" for p in (MIRROR / "pages").glob("*.html")
    ]

    rows = []
    for page in sorted(local_pages):
        refs = sorted(incoming.get(page, []))
        rows.append({"page": page, "linked_from_count": len(refs), "linked_from": refs})

    orphans = [r for r in rows if r["linked_from_count"] == 0]
    weak = [r for r in rows if 0 < r["linked_from_count"] <= 1 and r["page"] != "index.html"]

    # sitemap cross-ref
    sitemap_local = {item["local_file"]: item for item in audit["all"] if item.get("local_file")}

    lines = [
        "=== Локальные страницы без входящих ссылок ===",
    ]
    for r in orphans:
        sm = sitemap_local.get(r["page"], {})
        lines.append(f"  {r['page']} | {sm.get('title','')} | {sm.get('url','')}")

    lines += ["", "=== Слабо связаны (1 ссылка) ==="]
    for r in weak:
        sm = sitemap_local.get(r["page"], {})
        lines.append(f"  {r['page']} <- {r['linked_from']} | {sm.get('url','')}")

    lines += ["", "=== Карта: есть локально, нет ни одной входящей ссылки ==="]
    for item in audit["all"]:
        lf = item.get("local_file")
        if lf and not incoming.get(lf):
            lines.append(
                f"  {item['url']} | {item['title']} | {lf} | live:{item['live_status']} | plan:{item['plan_status']}"
            )

    lines += ["", "=== Карта: опубликована, локально нет файла ==="]
    for item in audit["all"]:
        if item["plan_status"] == "Опубликована" and not item.get("local_file") and item["url"] != "/":
            lines.append(f"  {item['url']} | {item['title']} | live:{item['live_status']}")

    out = MIRROR / "crosslink_audit.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))

    json_out = MIRROR / "crosslink_audit.json"
    json_out.write_text(json.dumps({"orphans": orphans, "weak": weak, "all": rows}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
