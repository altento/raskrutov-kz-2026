# -*- coding: utf-8 -*-
"""
Rewrite all internal navigation links to root-absolute paths from CSV map.
Does NOT touch design/text/images. Only links, canonical, og:url, JSON-LD URLs,
data-page-link, redirects, sitemap.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror")
CSV = Path("docs/site-map.csv")
DOMAIN = "https://raskrutov.kz"

# ---------------------------------------------------------------------------
# 1. Load allowed URLs from CSV
# ---------------------------------------------------------------------------

def load_csv_urls() -> dict[str, str]:
    """url (no trailing slash, / for home) -> title"""
    text = CSV.read_text(encoding="utf-8", errors="replace")
    reader = csv.reader(text.splitlines())
    out: dict[str, str] = {}
    for r in reader:
        if len(r) < 5:
            continue
        url = r[4].strip() if r[4].startswith("/") else None
        if not url:
            for c in r:
                if c.startswith("/") and " " not in c:
                    url = c.strip()
                    break
        if not url:
            continue
        url = url.rstrip("/") or "/"
        title = r[3].strip() if len(r) > 3 else ""
        out[url] = title
    return out


CSV_URLS = load_csv_urls()
# legal pages kept but not in CSV
EXTRA_OK = {"/consent", "/regulation"}
ALLOWED = set(CSV_URLS) | EXTRA_OK

# Alias: old disk slug -> CSV slug
ALIASES = {
    "/web-studiya/aeo-geo-prodvizhenie": "/web-studiya/aeo-prodvizhenie",
}


def pretty(url: str, trailing: bool = True) -> str:
    """Normalize to root-absolute path with optional trailing slash."""
    if not url:
        return url
    u = url.strip()
    # strip domain
    if u.startswith(DOMAIN):
        u = u[len(DOMAIN) :] or "/"
    if u.startswith("https://raskrutov.kz"):
        u = u[len("https://raskrutov.kz") :] or "/"
    # strip query/hash for mapping, reattach later
    hashpart = ""
    qpart = ""
    if "#" in u:
        u, hashpart = u.split("#", 1)
        hashpart = "#" + hashpart
    if "?" in u:
        u, qpart = u.split("?", 1)
        qpart = "?" + qpart
    u = u.rstrip("/") or "/"
    # apply alias
    u = ALIASES.get(u, u)
    if u == "/":
        return "/" + qpart + hashpart
    if trailing:
        return u + "/" + qpart + hashpart
    return u + qpart + hashpart


# Build map from old relative filenames / paths -> pretty URL
# e.g. web-studiya_sozdanie-saitov_landing.html -> /web-studiya/sozdanie-saitov/landing/
FILE_TO_URL: dict[str, str] = {}
for url in CSV_URLS:
    if url == "/":
        FILE_TO_URL["index.html"] = "/"
        continue
    parts = url.strip("/").split("/")
    # flat legacy name
    flat = "_".join(parts) + ".html"
    FILE_TO_URL[flat] = url
    FILE_TO_URL[url.lstrip("/")] = url
    FILE_TO_URL[url] = url

# also map aeo-geo old
FILE_TO_URL["web-studiya_aeo-geo-prodvizhenie.html"] = "/web-studiya/aeo-prodvizhenie"
FILE_TO_URL["web-studiya/aeo-geo-prodvizhenie"] = "/web-studiya/aeo-prodvizhenie"

stats = {
    "files": 0,
    "href": 0,
    "dpl": 0,
    "canonical": 0,
    "og": 0,
    "jsonld": 0,
    "whatsapp": 0,
    "email": 0,
    "changes": [],
}


def resolve_internal(val: str) -> str | None:
    """If val is an internal site link, return pretty root-absolute URL; else None."""
    if val is None:
        return None
    v = val.strip()
    if not v or v in ("#",):
        return None
    if v.startswith(("mailto:", "tel:", "javascript:", "data:", "sms:")):
        return None
    # external non-raskrutov
    if v.startswith(("http://", "https://", "//")):
        host = re.sub(r"^(?:https?:)?//(?:www\.)?", "", v).split("/")[0].split("?")[0]
        if host == "raskrutov.kz":
            path = v.split("raskrutov.kz", 1)[1]
            return pretty(path or "/")
        return None  # leave other externals
    # assets / static files — leave
    if "assets/" in v or v.endswith((".css", ".js", ".webp", ".png", ".jpg", ".svg", ".woff", ".ico", ".xml")):
        return None
    # strip leading ./ and collapse ../
    # For relative paths from any depth, try to map by basename / known patterns
    clean = v
    # remove leading ../ sequences and pages/
    while clean.startswith("../"):
        clean = clean[3:]
    if clean.startswith("./"):
        clean = clean[2:]
    if clean.startswith("pages/"):
        clean = clean[6:]
    clean = clean.split("?")[0].split("#")[0]
    # empty after strip -> home
    if clean in ("", "index.html"):
        return pretty("/")
    # already root absolute
    if v.startswith("/"):
        return pretty(v)
    # flat html or path without leading slash
    key = clean
    if key in FILE_TO_URL:
        return pretty(FILE_TO_URL[key])
    # try without .html
    if key.endswith(".html"):
        key2 = key[:-5]
        # convert underscores to path
        if key2 in FILE_TO_URL:
            return pretty(FILE_TO_URL[key2])
        # underscore form -> slash form
        slash = "/" + key2.replace("_", "/")
        slash = ALIASES.get(slash.rstrip("/") or "/", slash.rstrip("/") or "/")
        if slash in ALLOWED or slash in ALIASES.values():
            return pretty(slash)
    # slash path relative
    if "/" in clean and not clean.startswith("assets"):
        slash = "/" + clean.strip("/")
        slash = ALIASES.get(slash, slash)
        if slash in ALLOWED:
            return pretty(slash)
        # maybe partial path matching a CSV url
        for u in ALLOWED:
            if u.endswith("/" + clean.strip("/")) or u == "/" + clean.strip("/"):
                return pretty(u)
    return None


ATTR_RE = re.compile(
    r'\b(href|data-page-link|data-original-url|data-link|data-url|data-href)=("|\')([^"\']*)\2'
)


def rewrite_attrs(html: str, page: Path) -> str:
    def repl(m: re.Match) -> str:
        attr, q, val = m.group(1), m.group(2), m.group(3)
        new = resolve_internal(val)
        if new is None or new == val:
            # special: whatsapp variants
            if attr in ("href", "data-page-link", "data-original-url") and (
                "whatsapp" in val.lower() or "wa.me" in val.lower() or "api.whatsapp" in val.lower()
            ):
                if "77000216900" in val.replace(" ", ""):
                    fixed = "https://wa.me/77000216900"
                    if fixed != val:
                        stats["whatsapp"] += 1
                        stats["changes"].append((str(page), attr, val, fixed, "whatsapp normalize"))
                        return f"{attr}={q}{fixed}{q}"
            return m.group(0)
        # don't rewrite data-original-url to relative-looking — keep absolute https for original
        if attr == "data-original-url":
            fixed = DOMAIN + (new if new != "/" else "/")
            # canonical form without forcing double slash
            if new == "/":
                fixed = DOMAIN + "/"
            else:
                fixed = DOMAIN + new.rstrip("/")  # CSV style without trailing for original-url
            if fixed != val:
                stats["dpl"] += 1
                stats["changes"].append((str(page), attr, val, fixed, "original-url"))
                return f"{attr}={q}{fixed}{q}"
            return m.group(0)
        if new != val:
            key = "href" if attr == "href" else "dpl"
            stats[key] += 1
            stats["changes"].append((str(page), attr, val, new, "internal root-absolute"))
            return f"{attr}={q}{new}{q}"
        return m.group(0)

    return ATTR_RE.sub(repl, html)


def rewrite_canonical_og(html: str, page_url: str) -> str:
    """Force single absolute canonical + og:url matching page."""
    canon = DOMAIN + ("" if page_url == "/" else page_url.rstrip("/"))
    if page_url == "/":
        canon = DOMAIN + "/"

    def canon_repl(m: re.Match) -> str:
        stats["canonical"] += 1
        return f'<link rel="canonical" href="{canon}"/>'

    html2, n = re.subn(
        r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\']\s*/?>',
        canon_repl,
        html,
        count=1,
        flags=re.I,
    )
    if n == 0:
        # insert if missing
        html2 = html.replace("</head>", f'<link rel="canonical" href="{canon}"/>\n</head>', 1)
        stats["canonical"] += 1
    html = html2

    # og:url
    if re.search(r'property=["\']og:url["\']', html, re.I):
        html, n = re.subn(
            r'(property=["\']og:url["\']\s+content=["\'])[^"\']*(["\'])',
            rf"\g<1>{canon}\2",
            html,
            flags=re.I,
        )
        if n:
            stats["og"] += n
    return html


JSONLD_RE = re.compile(
    r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.I | re.S,
)


def rewrite_jsonld(html: str) -> str:
    def repl(m: re.Match) -> str:
        head, body, tail = m.group(1), m.group(2), m.group(3)
        try:
            data = json.loads(body)
        except Exception:
            # try fix aeo alias in raw
            new_body = body.replace(
                "web-studiya/aeo-geo-prodvizhenie", "web-studiya/aeo-prodvizhenie"
            )
            if new_body != body:
                stats["jsonld"] += 1
            return head + new_body + tail

        changed = [False]

        def walk(obj):
            if isinstance(obj, dict):
                for k, v in list(obj.items()):
                    if isinstance(v, str) and ("raskrutov.kz" in v or v.startswith("/")):
                        nv = v
                        if "aeo-geo-prodvizhenie" in nv:
                            nv = nv.replace("aeo-geo-prodvizhenie", "aeo-prodvizhenie")
                            changed[0] = True
                        # normalize .html paths
                        if ".html" in nv and "raskrutov.kz" in nv:
                            path = nv.split("raskrutov.kz", 1)[-1]
                            resolved = resolve_internal(path)
                            if resolved:
                                nv = DOMAIN + ("" if resolved == "/" else resolved.rstrip("/"))
                                if resolved == "/":
                                    nv = DOMAIN + "/"
                                changed[0] = True
                        obj[k] = nv
                    else:
                        walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)

        walk(data)
        if changed[0]:
            stats["jsonld"] += 1
            return head + json.dumps(data, ensure_ascii=False, indent=2) + tail
        return m.group(0)

    return JSONLD_RE.sub(repl, html)


def page_url_from_path(p: Path) -> str | None:
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith("assets/") or "/assets/" in rel:
        return None
    if p.parent.name == "pages":
        return None  # stubs handled separately
    if rel == "index.html":
        return "/"
    if p.name == "index.html":
        url = "/" + str(p.parent.relative_to(ROOT).as_posix())
        return ALIASES.get(url, url)
    return None


def write_text(path: Path, text: str) -> None:
    for _ in range(5):
        try:
            path.write_text(text, encoding="utf-8")
            return
        except OSError:
            time.sleep(1)


# ---------------------------------------------------------------------------
# 2. Rename aeo-geo -> aeo-prodvizhenie on disk
# ---------------------------------------------------------------------------

old_dir = ROOT / "web-studiya" / "aeo-geo-prodvizhenie"
new_dir = ROOT / "web-studiya" / "aeo-prodvizhenie"
if old_dir.exists() and not new_dir.exists():
    shutil.move(str(old_dir), str(new_dir))
    print("RENAMED", old_dir, "->", new_dir)
elif old_dir.exists() and new_dir.exists():
    # merge: prefer new, remove old
    shutil.rmtree(old_dir)
    print("REMOVED duplicate old aeo-geo dir")


# ---------------------------------------------------------------------------
# 3. Process all content pages
# ---------------------------------------------------------------------------

content_pages = [
    p
    for p in ROOT.rglob("*.html")
    if "assets" not in p.relative_to(ROOT).parts and p.parent.name != "pages"
]

for page in content_pages:
    purl = page_url_from_path(page)
    if purl is None:
        continue
    html = page.read_text(encoding="utf-8", errors="ignore")
    orig = html
    html = rewrite_attrs(html, page)
    html = rewrite_canonical_og(html, purl)
    html = rewrite_jsonld(html)
    # email normalize only for mailto:info@ or similar to ceo if user asked — careful
    # User said mailto:ceo@raskrutov.kz — update info@ only in mailto links
    def email_repl(m: re.Match) -> str:
        stats["email"] += 1
        return m.group(1) + "ceo@raskrutov.kz" + m.group(3)

    html2, n = re.subn(
        r'(href=["\']mailto:)(?:info|ceo)@raskrutov\.kz(["\'])',
        r"\1ceo@raskrutov.kz\2",
        html,
        flags=re.I,
    )
    if n:
        stats["email"] += n
        html = html2
    # visible email text left as-is (design/text rule)

    if html != orig:
        write_text(page, html)
        stats["files"] += 1


# ---------------------------------------------------------------------------
# 4. Update redirect stubs in pages/
# ---------------------------------------------------------------------------

STUB = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<meta http-equiv="refresh" content="0;url={target}"/>
<link rel="canonical" href="{canon}"/>
<title>Redirect</title>
</head>
<body>
<p>Страница переехала: <a href="{target}">{canon}</a></p>
</body>
</html>
"""

pages_dir = ROOT / "pages"
if pages_dir.exists():
    for stub in pages_dir.glob("*.html"):
        name = stub.name
        target_url = FILE_TO_URL.get(name)
        if not target_url:
            # try underscore mapping
            key = name
            if key.endswith(".html"):
                slash = "/" + key[:-5].replace("_", "/")
                slash = ALIASES.get(slash, slash)
                if slash in ALLOWED:
                    target_url = slash
        if not target_url:
            continue
        target = pretty(target_url)
        canon = DOMAIN + ("" if target_url == "/" else target_url)
        if target_url == "/":
            canon = DOMAIN + "/"
        write_text(stub, STUB.format(target=target, canon=canon))


# ---------------------------------------------------------------------------
# 5. .htaccess 301 for aeo rename + ensure stubs
# ---------------------------------------------------------------------------

ht = ROOT / ".htaccess"
extra_rules = [
    "Redirect 301 /web-studiya/aeo-geo-prodvizhenie /web-studiya/aeo-prodvizhenie/",
    "Redirect 301 /web-studiya/aeo-geo-prodvizhenie/ /web-studiya/aeo-prodvizhenie/",
    "Redirect 301 /pages/web-studiya_aeo-geo-prodvizhenie.html /web-studiya/aeo-prodvizhenie/",
]
if ht.exists():
    ht_text = ht.read_text(encoding="utf-8", errors="ignore")
    for rule in extra_rules:
        if "aeo-geo-prodvizhenie" not in ht_text or rule not in ht_text:
            if rule not in ht_text:
                ht_text = ht_text.rstrip() + "\n" + rule + "\n"
    # replace any old aeo-geo targets pointing wrong
    ht_text = ht_text.replace(
        "/web-studiya/aeo-geo-prodvizhenie/", "/web-studiya/aeo-prodvizhenie/"
    )
    write_text(ht, ht_text)
    print("Updated .htaccess")


# ---------------------------------------------------------------------------
# 6. sitemap.xml
# ---------------------------------------------------------------------------

urls_sorted = sorted(CSV_URLS.keys(), key=lambda u: (u.count("/"), u))
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls_sorted:
    loc = DOMAIN + "/" if u == "/" else DOMAIN + u
    sm.append("  <url>")
    sm.append(f"    <loc>{loc}</loc>")
    sm.append("  </url>")
sm.append("</urlset>")
write_text(ROOT / "sitemap.xml", "\n".join(sm) + "\n")
print("Wrote sitemap.xml", len(urls_sorted), "urls")

print("STATS", {k: v for k, v in stats.items() if k != "changes"})
print("sample changes:", len(stats["changes"]))
# dump change log
log = Path("reports/link-changes.tsv")
with log.open("w", encoding="utf-8") as f:
    f.write("page\tattr\told\tnew\treason\n")
    for row in stats["changes"][:50000]:
        f.write("\t".join(row) + "\n")
print("Wrote", log)
