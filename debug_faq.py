#!/usr/bin/env python3
"""Debug FAQ extraction on faq_seo.html."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
h = (M / "pages" / "faq_seo.html").read_text(encoding="utf-8", errors="ignore")
TAG_RE = re.compile(r"<[^>]+>")
import html as html_mod

def clean(t):
    return re.sub(r"\s+", " ", html_mod.unescape(TAG_RE.sub(" ", t))).strip()

H2_RE = re.compile(r"<h2\b[^>]*>(.*?)</h2>", re.IGNORECASE | re.DOTALL)
for m in H2_RE.finditer(h):
    print("H2:", clean(m.group(1))[:80])

i = h.lower().find("вопрос")
print("\nfirst 'вопрос' context:")
print(re.sub(r"\s+", " ", h[max(0, i-400): i+300]))
