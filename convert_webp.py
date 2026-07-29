#!/usr/bin/env python3
"""Convert PNG/JPG/JPEG images to WebP and rewrite references.

- Converts files under site_mirror/assets (skips favicons, animations,
  and cases where WebP ends up bigger than the original).
- Rewrites references in all text files (.html/.css/.js/.json) by replacing
  the full path tail (relative to assets/), which is prefix-agnostic.
- Originals stay on disk as a fallback.
"""
from pathlib import Path
from PIL import Image

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
ASSETS = M / "assets"
CONVERT_EXT = {".png", ".jpg", ".jpeg"}
TEXT_EXT = {".html", ".css", ".js", ".json"}
QUALITY = 82

converted: list[tuple[str, str, int, int]] = []  # old_tail, new_tail, old_sz, new_sz
skipped_anim = skipped_bigger = skipped_favicon = skipped_exists = errors = 0

for f in ASSETS.rglob("*"):
    if not f.is_file() or f.suffix.lower() not in CONVERT_EXT:
        continue
    rel = f.relative_to(ASSETS).as_posix()
    if "favicon" in f.name.lower():
        skipped_favicon += 1
        continue
    target = f.with_suffix(".webp")
    if target.exists():
        skipped_exists += 1
        continue
    try:
        with Image.open(f) as im:
            if getattr(im, "n_frames", 1) > 1:
                skipped_anim += 1
                continue
            im.save(target, "WEBP", quality=QUALITY, method=6)
    except Exception:
        errors += 1
        continue
    old_sz = f.stat().st_size
    new_sz = target.stat().st_size
    if new_sz >= old_sz:
        target.unlink()
        skipped_bigger += 1
        continue
    converted.append((rel, target.relative_to(ASSETS).as_posix(), old_sz, new_sz))

old_total = sum(c[2] for c in converted)
new_total = sum(c[3] for c in converted)
print(f"Converted: {len(converted)} files, {old_total/1024/1024:.1f} MB -> {new_total/1024/1024:.1f} MB")
print(f"Skipped: favicon={skipped_favicon} anim={skipped_anim} bigger={skipped_bigger} exists={skipped_exists} errors={errors}")

# Rewrite references
tails = sorted(converted, key=lambda c: len(c[0]), reverse=True)
repl_files = 0
repl_count = 0
for tf in M.rglob("*"):
    if not tf.is_file() or tf.suffix.lower() not in TEXT_EXT:
        continue
    try:
        text = tf.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    orig = text
    for old_tail, new_tail, _, _ in tails:
        n = text.count(old_tail)
        if n:
            text = text.replace(old_tail, new_tail)
            repl_count += n
    if text != orig:
        tf.write_text(text, encoding="utf-8")
        repl_files += 1

print(f"References rewritten: {repl_count} in {repl_files} files")
