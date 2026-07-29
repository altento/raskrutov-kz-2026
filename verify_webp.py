#!/usr/bin/env python3
"""Verify WebP conversion: no stale references, all referenced images exist."""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
ASSETS = M / "assets"

# Collect all referenced image tails in served pages
ref_re = re.compile(
    r"(?:src|srcset|href)\s*=\s*\"([^\"]+\.(?:png|jpe?g|webp|gif|svg|ico))\"",
    re.IGNORECASE,
)
missing: list[str] = []
stale_png = 0
checked: set[str] = set()
for f in M.rglob("*.html"):
    if "assets" in f.relative_to(M).parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    for ref in ref_re.findall(html):
        # normalize: strip leading ../ and assets/
        tail = ref.split("assets/")[-1] if "assets/" in ref else ref.lstrip("./").lstrip("../")
        if tail.startswith("http"):
            continue
        if tail in checked:
            continue
        checked.add(tail)
        p = ASSETS / tail
        if not p.exists():
            # try the other known prefix variants
            alt = M / ref.replace("../", "")
            if not alt.exists():
                missing.append(ref)
        if ref.lower().endswith((".png", ".jpg", ".jpeg")) and "favicon" not in ref.lower():
            stale_png += 1

print(f"unique refs checked: {len(checked)}")
print(f"missing files: {len(missing)}")
for m in missing[:10]:
    print("  MISS:", m[:120])
print(f"remaining png/jpg refs (non-favicon): {stale_png}")
