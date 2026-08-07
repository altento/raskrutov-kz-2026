# -*- coding: utf-8 -*-
"""Round 2: consent/regulation root paths, JSON-LD cleanup, social target=_blank."""
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
pages = [
    p
    for p in ROOT.rglob("*.html")
    if "assets" not in p.relative_to(ROOT).parts and p.parent.name != "pages"
]

CONSENT_RE = re.compile(
    r'\b(href|data-page-link|data-original-url)=("|\')((?:\.\./)*(?:pages/)?consent(?:\.html)?)(\2)'
)
REG_RE = re.compile(
    r'\b(href|data-page-link|data-original-url)=("|\')((?:\.\./)*(?:pages/)?regulation(?:\.html)?)(\2)'
)

# social hosts to add target=_blank
SOCIAL = re.compile(
    r'<a\s+([^>]*href=("|\')(https?://(?:www\.)?(?:instagram\.com|youtube\.com|youtu\.be|t\.me|tiktok\.com|wa\.me|api\.whatsapp\.com)[^"\']*)\2)([^>]*)>',
    re.I,
)

stats = {"consent": 0, "regulation": 0, "jsonld": 0, "blank": 0, "files": 0}


def write(p, t):
    for _ in range(5):
        try:
            p.write_text(t, encoding="utf-8")
            return
        except OSError:
            time.sleep(1)


for page in pages:
    html = page.read_text(encoding="utf-8", errors="ignore")
    orig = html

    def c_repl(m):
        stats["consent"] += 1
        return f'{m.group(1)}={m.group(2)}/consent/{m.group(2)}'

    def r_repl(m):
        stats["regulation"] += 1
        return f'{m.group(1)}={m.group(2)}/regulation/{m.group(2)}'

    html = CONSENT_RE.sub(c_repl, html)
    html = REG_RE.sub(r_repl, html)

    # JSON-LD: strip .html from raskrutov URLs, fix aeo-geo
    def jl(m):
        body = m.group(2)
        new = body.replace("aeo-geo-prodvizhenie", "aeo-prodvizhenie")
        new = re.sub(
            r'(https://raskrutov\.kz/[^"\\]*?)\.html',
            r"\1",
            new,
        )
        # also /pages/foo paths if any
        new = re.sub(
            r'https://raskrutov\.kz/pages/([A-Za-z0-9_-]+)',
            lambda mm: "https://raskrutov.kz/" + mm.group(1).replace("_", "/"),
            new,
        )
        if new != body:
            stats["jsonld"] += 1
        return m.group(1) + new + m.group(3)

    html = re.sub(
        r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
        jl,
        html,
        flags=re.I | re.S,
    )

    def a_repl(m):
        before, q, url, after = m.group(1), m.group(2), m.group(3), m.group(4)
        full = before + after
        if re.search(r'target\s*=', full, re.I):
            return m.group(0)
        stats["blank"] += 1
        # inject into opening tag
        return f'<a {before}{after} target="_blank" rel="noopener noreferrer">'

    # careful: SOCIAL captures wrong - rewrite differently
    def social_tag(m):
        tag = m.group(0)
        if re.search(r'\btarget\s*=', tag, re.I):
            if "noopener" not in tag:
                tag = tag[:-1] + ' rel="noopener noreferrer">'
                stats["blank"] += 1
            return tag
        stats["blank"] += 1
        return tag[:-1] + ' target="_blank" rel="noopener noreferrer">'

    html = SOCIAL.sub(social_tag, html)

    if html != orig:
        write(page, html)
        stats["files"] += 1

print(stats)
