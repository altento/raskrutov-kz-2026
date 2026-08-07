# -*- coding: utf-8 -*-
"""Full link audit after rewrite. Writes reports/full-link-audit.md"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror")
CSV = Path("docs/site-map.csv")
DOMAIN = "https://raskrutov.kz"
REPORT = Path("reports/full-link-audit.md")

# load allowed
text = CSV.read_text(encoding="utf-8", errors="replace")
ALLOWED = set()
for r in csv.reader(text.splitlines()):
    if len(r) < 5:
        continue
    url = r[4].strip() if r[4].startswith("/") else None
    if not url:
        continue
    ALLOWED.add(url.rstrip("/") or "/")
ALLOWED |= {"/consent", "/regulation"}
ALLOWED.add("/web-studiya/aeo-prodvizhenie")

# disk pages
DISK = set()
for f in ROOT.rglob("index.html"):
    rel = f.relative_to(ROOT).as_posix()
    if rel.startswith("assets/"):
        continue
    if rel == "index.html":
        DISK.add("/")
    else:
        DISK.add("/" + str(Path(rel).parent.as_posix()))

content_pages = [
    p
    for p in ROOT.rglob("*.html")
    if "assets" not in p.relative_to(ROOT).parts and p.parent.name != "pages"
]


def normalize(u: str) -> str:
    if u.startswith(DOMAIN):
        u = u[len(DOMAIN) :] or "/"
    u = u.split("?")[0].split("#")[0]
    return u.rstrip("/") or "/"


broken = []
html_links = []
relative = []
empty_action = []
double_slash = []
bad_canonical = []
bad_jsonld = []
total_links = 0

ATTR = re.compile(
    r'\b(href|data-page-link)=("|\')([^"\']*)\2'
)

for page in content_pages:
    html = page.read_text(encoding="utf-8", errors="ignore")
    rel = page.relative_to(ROOT).as_posix()

    # canonical
    cans = re.findall(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', html, re.I)
    if len(cans) != 1:
        bad_canonical.append((rel, f"count={len(cans)} {cans}"))
    elif not cans[0].startswith(DOMAIN):
        bad_canonical.append((rel, cans[0]))
    elif ".html" in cans[0]:
        bad_canonical.append((rel, cans[0]))

    # expected page url
    if rel == "index.html":
        expect = "/"
    else:
        expect = "/" + str(page.parent.relative_to(ROOT).as_posix())
    if cans and normalize(cans[0]) != expect and expect in ALLOWED:
        # allow if alias
        if not (normalize(cans[0]) == expect):
            bad_canonical.append((rel, f"mismatch expect={expect} got={cans[0]}"))

    for m in ATTR.finditer(html):
        attr, val = m.group(1), m.group(3)
        total_links += 1
        if val.startswith(("mailto:", "tel:", "javascript:", "data:", "sms:")):
            continue
        if val.startswith(("http://", "https://", "//")):
            host = re.sub(r"^(?:https?:)?//(?:www\.)?", "", val).split("/")[0]
            if host != "raskrutov.kz":
                continue
            path = normalize(val)
        else:
            if not val or val == "#":
                # empty data-page-link is often intentional for non-nav blocks
                if attr == "href" and val == "#":
                    empty_action.append((rel, attr, val))
                continue
            if "assets/" in val or val.endswith((".css", ".js", ".webp", ".png", ".svg", ".woff", ".ico")):
                continue
            if val.startswith("../") or (not val.startswith("/") and not val.startswith("#")):
                relative.append((rel, attr, val))
                continue
            if "//" in val.replace("://", ""):
                double_slash.append((rel, attr, val))
            if ".html" in val:
                html_links.append((rel, attr, val))
            path = normalize(val)

        if path not in DISK and path not in ALLOWED:
            # anchors only?
            if path == "/" or path in DISK:
                continue
            broken.append((rel, attr, val, path))

    # JSON-LD
    for m in re.finditer(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    ):
        body = m.group(1)
        if "aeo-geo-prodvizhenie" in body or ".html" in body and "raskrutov.kz" in body:
            bad_jsonld.append((rel, "legacy url in json-ld"))
        if "../" in body:
            bad_jsonld.append((rel, "relative ../ in json-ld"))

# orphan pages: in ALLOWED/DISK but never linked
linked = set()
for page in content_pages:
    html = page.read_text(encoding="utf-8", errors="ignore")
    for m in ATTR.finditer(html):
        val = m.group(3)
        if val.startswith("/") or DOMAIN in val:
            linked.add(normalize(val if val.startswith("/") else val))

orphans = sorted((ALLOWED & DISK) - linked - {"/"})

# buttons without action: m-button-wrapper with empty dpl and no popup and onclick linkRedirect
no_action = []
for page in content_pages:
    html = page.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(
        r'data-page-link=""[^>]*class="[^"]*m-button-wrapper|class="[^"]*m-button-wrapper[^"]*"[^>]*data-page-link=""',
        html,
    ):
        # check nearby popup
        ctx = html[max(0, m.start() - 200) : m.end() + 200]
        if "data-popup-id" in ctx or "showPopup" in ctx or "sectionScroll" in ctx:
            continue
        # only count if onclick linkRedirect nearby
        if "linkRedirect" in ctx:
            no_action.append(page.relative_to(ROOT).as_posix())

no_action = sorted(set(no_action))

lines = []
lines.append("# Full link audit — Raskrutov.kz")
lines.append("")
lines.append(f"- Content pages checked: **{len(content_pages)}**")
lines.append(f"- Link attributes scanned: **{total_links}**")
lines.append(f"- Allowed URLs (CSV+legal): **{len(ALLOWED)}**")
lines.append(f"- Pages on disk: **{len(DISK)}**")
lines.append("")
lines.append("## Summary")
lines.append("")
lines.append(f"| Check | Count |")
lines.append(f"|---|---|")
lines.append(f"| Broken internal targets | {len(broken)} |")
lines.append(f"| Remaining relative (non-root) | {len(relative)} |")
lines.append(f"| Links still containing `.html` | {len(html_links)} |")
lines.append(f"| Double slashes | {len(double_slash)} |")
lines.append(f"| Bad canonical | {len(bad_canonical)} |")
lines.append(f"| Bad JSON-LD URLs | {len(bad_jsonld)} |")
lines.append(f"| href=\"#\" | {len(empty_action)} |")
lines.append(f"| Orphan pages (no inbound) | {len(orphans)} |")
lines.append(f"| Pages with empty linkRedirect buttons | {len(no_action)} |")
lines.append("")

def dump(title, rows, limit=80):
    lines.append(f"## {title}")
    lines.append("")
    if not rows:
        lines.append("_none_")
        lines.append("")
        return
    for row in rows[:limit]:
        lines.append("- `" + "` | `".join(str(x) for x in row) + "`")
    if len(rows) > limit:
        lines.append(f"- … and {len(rows) - limit} more")
    lines.append("")

dump("Broken internal targets", broken)
dump("Remaining relative links", relative)
dump("`.html` links", html_links)
dump("Bad canonical", bad_canonical)
dump("Bad JSON-LD", bad_jsonld)
dump("Orphan pages", [(o,) for o in orphans])
dump("Pages with empty linkRedirect", [(p,) for p in no_action])

missing_disk = sorted(ALLOWED - DISK - {"/consent", "/regulation"})
dump("In CSV but missing on disk", [(u,) for u in missing_disk])

REPORT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[:60]))
print("\nWrote", REPORT)
print("BROKEN", len(broken), "RELATIVE", len(relative), "HTML", len(html_links))
