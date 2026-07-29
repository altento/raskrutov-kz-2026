#!/usr/bin/env python3
"""Recon for schema.org generation: logo files, page inventory, FAQ sections, dates."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

print("=== logo candidates ===")
for f in M.rglob("*"):
    if f.is_file() and "logo" in f.name.lower() and f.suffix.lower() in (".png", ".svg", ".webp"):
        print(f"  {f.relative_to(M)} ({f.stat().st_size//1024} KB)")

print("\n=== pages inventory (name -> H1, has FAQ) ===")
TAG_RE = re.compile(r"<[^>]+>")
import html as html_mod

def clean(t: str) -> str:
    return re.sub(r"\s+", " ", html_mod.unescape(TAG_RE.sub(" ", t))).strip()

for f in sorted((M / "pages").glob("*.html")):
    h = f.read_text(encoding="utf-8", errors="ignore")
    h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", h, re.IGNORECASE | re.DOTALL)
    h1t = clean(h1.group(1))[:70] if h1 else "?"
    faq = "Вопросы и ответы" in h or "FAQ" in h
    h3s = len(re.findall(r"<h3\b", h))
    print(f"  {f.name[:52]:54} faq={int(faq)} h3={h3s:2}  {h1t}")

print("\n=== blog dates ===")
for f in sorted((M / "pages").glob("blog*.html")):
    h = f.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"(\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+\d{4})", h)
    print(f"  {f.name}: {m.group(1) if m else 'no date'}")
