#!/usr/bin/env python3
"""Rewrite image references to converted WebP (resumable, robust).

Rebuilds the old->new tail list from sibling .webp files created by
convert_webp.py, then replaces exact path tails in text files.
"""
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
ASSETS = M / "assets"
TEXT_EXT = {".html", ".css", ".js", ".json"}
SRC_EXT = {".png", ".jpg", ".jpeg"}

tails: list[tuple[str, str]] = []
for f in ASSETS.rglob("*"):
    if not f.is_file() or f.suffix.lower() not in SRC_EXT:
        continue
    webp = f.with_suffix(".webp")
    if webp.exists() and "favicon" not in f.name.lower():
        tails.append(
            (f.relative_to(ASSETS).as_posix(), webp.relative_to(ASSETS).as_posix())
        )
tails.sort(key=lambda c: len(c[0]), reverse=True)
print(f"tail pairs: {len(tails)}")

repl_files = 0
repl_count = 0
failures: list[str] = []
for tf in M.rglob("*"):
    if not tf.is_file() or tf.suffix.lower() not in TEXT_EXT:
        continue
    try:
        text = tf.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    orig = text
    for old_tail, new_tail in tails:
        if old_tail in text:
            repl_count += text.count(old_tail)
            text = text.replace(old_tail, new_tail)
    if text != orig:
        try:
            tf.write_text(text, encoding="utf-8")
            repl_files += 1
        except OSError as e:
            failures.append(f"{tf.relative_to(M)}: {e}")

print(f"References rewritten: {repl_count} in {repl_files} files")
print(f"Write failures: {len(failures)}")
for x in failures[:10]:
    print("  FAIL:", x)
