#!/usr/bin/env python3
"""Subset site fonts to Cyrillic + Latin + symbols actually used on the site.

Ranges kept: basic latin, latin-1 supplement, cyrillic, cyrillic supplement,
tenge sign, numero, general punctuation, arrows (long arrows used in cards),
dingbats (checkmarks in lists).
"""
from pathlib import Path
from fontTools import subset

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

UNICODES = (
    "U+0000-00FF,"   # basic latin + latin-1
    "U+0400-052F,"   # cyrillic + supplement
    "U+2010-2027,"   # hyphens, quotes, ellipsis
    "U+2030-205E,"   # per mille, bullets
    "U+20B8,"        # tenge sign
    "U+2116,"        # numero sign
    "U+2190-21FF,"   # arrows
    "U+2700-27BF,"   # dingbats (checkmarks)
    "U+27F0-27FF"    # supplemental arrows (long right arrow in cards)
)

total_old = total_new = converted = errors = 0
for f in M.rglob("*.woff"):
    if f.name == "slick.woff":
        continue  # tiny icon font, leave as is
    old_sz = f.stat().st_size
    out = f.with_suffix(".subset.woff")
    try:
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.notdef_outline = True
        opts.recalc_bounds = True
        font = subset.load_font(str(f), opts, lazy=False)
        ss = subset.Subsetter(opts)
        ss.populate(unicodes=subset.parse_unicodes(UNICODES))
        ss.subset(font)
        font.save(str(out))
        font.close()
    except Exception as e:
        errors += 1
        print(f"  ERROR {f.name}: {e}")
        if out.exists():
            out.unlink()
        continue
    new_sz = out.stat().st_size
    if new_sz < old_sz * 0.95:
        import os, stat as stat_mod, time
        os.chmod(f, stat_mod.S_IWRITE)
        replaced = False
        for _attempt in range(8):
            try:
                f.unlink()
                out.rename(f)
                replaced = True
                break
            except OSError:
                time.sleep(2)
        if not replaced:
            out.unlink()
            errors += 1
            print(f"  LOCKED {f.name}, skipped")
            continue
        total_old += old_sz
        total_new += new_sz
        converted += 1
        print(f"  {f.name}: {old_sz/1024:.0f} KB -> {new_sz/1024:.0f} KB")
    else:
        out.unlink()

print(f"\nSubsetted: {converted} fonts, {total_old/1024:.0f} KB -> {total_new/1024:.0f} KB (errors: {errors})")
