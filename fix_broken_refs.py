# -*- coding: utf-8 -*-
"""Fix corrupted/mangled references:
1. Remove corrupted plain JSON-LD blocks (garbage @id URLs) — clean block will
   be re-injected by add_schema.py afterwards
2. Garbage URL string -> https://raskrutov.kz/ (builder JS contexts)
3. Case-study links ../assets/../assets/X.kz/index.htmlindex.html -> https://X.kz
4. Mangled social/messenger attribute values -> correct external URLs
5. crm*.html: add missing ../ prefixes (assets/, pages/, index.html)
6. Remove duplicate relative canonical tags
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

GARBAGE = "../assets/../assets/../index.html/index.htmlindex.html"

SOCIAL_MAP = {
    "assets/api.whatsapp.com/send/index__q_phone_77000216900.html": "https://api.whatsapp.com/send?phone=77000216900",
    "assets/t.me/Raskrutov_web/index.html/index.html": "https://t.me/Raskrutov_web",
    "assets/assets/t.me/Raskrutov_web/index.html/index.html": "https://t.me/Raskrutov_web",
    "assets/www.assets/www.instagram.com/index.html": "https://www.instagram.com/raskrutov",
    "assets/assets/www.assets/www.instagram.com/index.html": "https://www.instagram.com/raskrutov",
    "assets/www.youtube.com/@raskrutov-kz/index.html/index.html": "https://www.youtube.com/@raskrutov-kz",
    "assets/assets/www.youtube.com/@raskrutov-kz/index.html/index.html": "https://www.youtube.com/@raskrutov-kz",
    "assets/www.tiktok.com/@raskrutov__q__r_1__t_ZS-96qj8121sRd.kz": "https://www.tiktok.com/@raskrutov?_r=1&_t=ZS-96qj8121sRd",
    "assets/assets/www.tiktok.com/@raskrutov__q__r_1__t_ZS-96qj8121sRd.kz": "https://www.tiktok.com/@raskrutov?_r=1&_t=ZS-96qj8121sRd",
}

PLAIN_LD = re.compile(r'\s*<script type="application/ld\+json">(.*?)</script>', re.S)
CASE_LINK = re.compile(r'\.\./assets/\.\./assets/([a-z0-9-]+(?:\.[a-z0-9-]+)*\.kz)/index\.htmlindex\.html')

stats = {k: 0 for k in ["ld_removed", "garbage", "case_links", "social", "crm_prefix", "crm_pages", "crm_index", "canon_dup"]}
ld_pages = []

for page in PAGES:
    html = page.read_text(encoding="utf-8")
    orig = html

    # 1. remove corrupted plain JSON-LD (keep our data-schema block if present)
    def drop_plain(m):
        nonlocal_html = m.group(1)
        if GARBAGE in nonlocal_html or "index.htmlindex.html" in nonlocal_html:
            stats["ld_removed"] += 1
            ld_pages.append(page.name)
            return ""
        return m.group(0)
    html = PLAIN_LD.sub(drop_plain, html)

    # 2. garbage URL string (JS contexts etc.)
    if GARBAGE in html:
        stats["garbage"] += html.count(GARBAGE)
        html = html.replace(GARBAGE, "https://raskrutov.kz/")

    # 3. case-study links -> external
    html, n = CASE_LINK.subn(r"https://\1", html)
    stats["case_links"] += n

    # 4. mangled socials
    for bad, good in SOCIAL_MAP.items():
        if bad in html:
            stats["social"] += html.count(bad)
            html = html.replace(bad, good)

    # 5. pages-dir files: fix wrong relative prefixes
    if page.parent != ROOT:
        # href/src="assets/ -> ../assets/ (pages/assets does not exist)
        html, n = re.subn(r'(href|src)="assets/', r'\1="../assets/', html)
        stats["crm_prefix"] += n
        # href="pages/X.html -> href="X.html (same dir; pages/pages does not exist)
        html, n = re.subn(r'href="pages/', 'href="', html)
        stats["crm_pages"] += n
        # data-page-link="pages/X.html -> "X.html"
        html, n = re.subn(r'data-page-link="pages/', 'data-page-link="', html)
        stats["crm_pages"] += n
        # href="index.html" -> "../index.html"; data-page-link="index.html" -> "../index.html"
        html, n = re.subn(r'href="index\.html"', 'href="../index.html"', html)
        stats["crm_index"] += n
        html, n = re.subn(r'data-page-link="index\.html"', 'data-page-link="../index.html"', html)
        stats["crm_index"] += n

    # 6. duplicate relative canonicals
    cans = re.findall(r'<link rel="canonical" href="([^"]*)"\s*/?>', html)
    if len(cans) > 1:
        def keep_abs(m):
            return m.group(0)
        # remove relative ones only
        def strip_rel(m):
            nonlocal_html = m.group(1)
            if nonlocal_html.startswith("http"):
                return m.group(0)
            stats["canon_dup"] += 1
            return ""
        html = re.sub(r'<link rel="canonical" href="([^"]*)"\s*/>\s*', strip_rel, html)

    if html != orig:
        page.write_text(html, encoding="utf-8")

print("stats:", stats)
print("ld cleaned pages:", len(set(ld_pages)))
