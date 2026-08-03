# -*- coding: utf-8 -*-
"""Split site_plesk home-clean.css into critical (above-fold) + deferred."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SRC = Path("site_plesk/assets/css/home-clean.css")
OUT_CRIT = Path("site_plesk/assets/css/home-clean-critical.v1.css")
OUT_DEF = Path("site_plesk/assets/css/home-clean-deferred.v1.css")

# Selectors / chunks needed before first paint (mobile + desktop hero)
CRITICAL_NEEDLES = (
    ":root",
    "html",
    "body",
    "*",
    ".rk-clean",
    ".rk-container",
    ".rk-header",
    ".rk-logo",
    ".rk-nav",
    ".rk-burger",
    ".rk-wa",
    ".rk-header__",
    ".rk-mobile-nav",
    ".rk-hero",
    ".rk-check",
    ".rk-menu-open",
    "Montserrat",
    "Montserrat Fallback",
    "@font-face",  # filtered further
)

# Fonts that must stay in critical (H1 / hero)
KEEP_FONT_FAMILIES = {"Montserrat", "Montserrat Fallback"}


def split_top_level(css: str) -> list[str]:
    """Split CSS into top-level chunks (rules / @media / @font-face / comments)."""
    chunks: list[str] = []
    i = 0
    n = len(css)
    while i < n:
        while i < n and css[i].isspace():
            i += 1
        if i >= n:
            break
        if css.startswith("/*", i):
            end = css.find("*/", i + 2)
            end = n if end < 0 else end + 2
            chunks.append(css[i:end])
            i = end
            continue
        # find next { or ; for @imports etc
        if css[i] == "@" and not css.startswith("@media", i) and not css.startswith("@font-face", i) and not css.startswith("@supports", i) and not css.startswith("@keyframes", i):
            # @charset etc
            semi = css.find(";", i)
            if semi < 0:
                chunks.append(css[i:])
                break
            chunks.append(css[i : semi + 1])
            i = semi + 1
            continue
        # rule or at-rule with braces
        brace = css.find("{", i)
        if brace < 0:
            chunks.append(css[i:])
            break
        depth = 0
        j = brace
        while j < n:
            c = css[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        chunks.append(css[i:j])
        i = j
    return chunks


def is_font_face(chunk: str) -> bool:
    return chunk.lstrip().startswith("@font-face")


def font_family(chunk: str) -> str | None:
    m = re.search(r"font-family:\s*([^;]+);", chunk)
    if not m:
        return None
    return m.group(1).strip().strip("\"'")


def is_critical_chunk(chunk: str) -> bool:
    s = chunk.strip()
    if not s or s.startswith("/*"):
        return False
    if is_font_face(s):
        fam = font_family(s) or ""
        return fam in KEEP_FONT_FAMILIES
    if s.startswith("@keyframes"):
        # keep hero-related animations if any
        return "rk-hero" in s or "rk-check" in s or "rk-header" in s
    if s.startswith("@media") or s.startswith("@supports"):
        # keep media if it mentions critical selectors
        body = s
        return any(n in body for n in CRITICAL_NEEDLES if n not in ("@font-face", "Montserrat", "Montserrat Fallback"))
    # normal rule
    prelude = s.split("{", 1)[0]
    return any(n in prelude for n in CRITICAL_NEEDLES if n not in ("@font-face", "Montserrat", "Montserrat Fallback"))


def main() -> int:
    css = SRC.read_text(encoding="utf-8")
    chunks = split_top_level(css)
    crit: list[str] = []
    deferred: list[str] = []
    # keep file banner in both
    banner = "/* Raskrutov homepage clean — AUTOSPLIT critical/deferred */\n"
    for ch in chunks:
        st = ch.strip()
        if not st:
            continue
        if st.startswith("/*") and "AUTOSPLIT" not in st and len(crit) == 0 and len(deferred) == 0:
            # original banner → skip duplicate; put short note
            continue
        if is_critical_chunk(ch):
            crit.append(ch.strip())
        else:
            deferred.append(ch.strip())

    # For @media that was marked critical because it contains hero+lots of other rules,
    # we still put the WHOLE media block in critical — can be large.
    # Trim: if a critical @media is huge, split inner rules.
    refined_crit: list[str] = []
    for ch in crit:
        if ch.startswith("@media") and len(ch) > 12000:
            # re-split inner: keep only critical-looking inner rules
            m = re.match(r"(@media[^{]+)\{([\s\S]*)\}\s*$", ch)
            if not m:
                refined_crit.append(ch)
                continue
            head, inner = m.group(1), m.group(2)
            inner_chunks = split_top_level(inner)
            keep = [ic.strip() for ic in inner_chunks if ic.strip() and is_critical_chunk(ic)]
            # also keep font-face shouldn't be inside media
            if keep:
                refined_crit.append(head + "{\n" + "\n\n".join(keep) + "\n}")
            # remaining inner → wrap same media into deferred
            drop = [ic.strip() for ic in inner_chunks if ic.strip() and not is_critical_chunk(ic)]
            if drop:
                deferred.append(head + "{\n" + "\n\n".join(drop) + "\n}")
        else:
            refined_crit.append(ch)

    crit_css = banner + "\n\n".join(refined_crit) + "\n"
    def_css = banner.replace("critical/deferred", "deferred") + "\n\n".join(deferred) + "\n"
    OUT_CRIT.write_text(crit_css, encoding="utf-8")
    OUT_DEF.write_text(def_css, encoding="utf-8")
    print(f"critical: {OUT_CRIT} {len(crit_css.encode())/1024:.1f} KiB ({len(refined_crit)} chunks)")
    print(f"deferred: {OUT_DEF} {len(def_css.encode())/1024:.1f} KiB ({len(deferred)} chunks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
