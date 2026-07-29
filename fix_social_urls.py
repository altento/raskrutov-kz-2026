#!/usr/bin/env python3
"""Fix remaining corrupted YouTube/TikTok URLs (containing '..' artifacts) across pages."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

REAL = {
    "youtube": "https://www.youtube.com/@raskrutov-kz",
    "tiktok": "https://www.tiktok.com/@raskrutov.kz",
}

pat = re.compile(r"https?://[^\s\"'<>]*\.\.[^\s\"'<>]*")
fam = {
    "youtube": re.compile(r"youtube|youtu\.be"),
    "tiktok": re.compile(r"tiktok"),
}

total = 0
for f in M.rglob("*.html"):
    if "assets" in f.relative_to(M).parts:
        continue
    h = f.read_text(encoding="utf-8", errors="ignore")

    def repl(m: re.Match) -> str:
        global total
        url = m.group(0)
        for name, rx in fam.items():
            if rx.search(url):
                total += 1
                return REAL[name]
        return url

    fixed = pat.sub(repl, h)
    if fixed != h:
        f.write_text(fixed, encoding="utf-8")

print(f"Fixed corrupted URLs: {total}")
