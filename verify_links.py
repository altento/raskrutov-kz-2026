#!/usr/bin/env python3
"""Verify no broken email/social artifacts remain after fix_external_links.py."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
bad_email = bad_http = stub = 0
examples: list[str] = []
for f in M.rglob("*.html"):
    if "assets" in f.relative_to(M).parts:
        continue
    h = f.read_text(encoding="utf-8", errors="ignore")
    for m in re.findall(r"info@[^\"'<>\s]*", h):
        if m != "info@raskrutov.kz":
            bad_email += 1
            if len(examples) < 5:
                examples.append(f"{f.name}: {m}")
    n = len(re.findall(r"https?://\.\.", h))
    bad_http += n
    for m in re.findall(r'href="assets/[^"]*(?:instagram|youtube|t\.me|whatsapp)[^"]*"', h):
        stub += 1
        if len(examples) < 5:
            examples.append(f"{f.name}: {m}")
print(f"bad_email={bad_email} bad_http={bad_http} stub_social={stub}")
for e in examples:
    print("  ", e)
