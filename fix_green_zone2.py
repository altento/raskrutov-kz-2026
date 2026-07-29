# -*- coding: utf-8 -*-
"""Round 2: remaining contrast (n12S button, inline blue links),
footer-bar icon aspect fix, demote JS preload to free bandwidth for LCP."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror")
PAGES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

def color_lum(bg: str):
    bg = bg.strip()
    m = re.match(r"#([0-9a-fA-F]{3,8})$", bg)
    if m:
        h = m.group(1)
        if len(h) == 3:
            r, g, b = (int(c * 2, 16) for c in h)
        elif len(h) >= 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        else:
            return None
    else:
        m = re.match(r"rgba?\(([^)]+)\)", bg)
        if not m:
            return None
        parts = [x.strip() for x in m.group(1).split(",")]
        try:
            r, g, b = (float(parts[0]), float(parts[1]), float(parts[2]))
        except (ValueError, IndexError):
            return None
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def ctx_is_dark(html: str, pos: int) -> bool:
    ctx = html[max(0, pos - 700):pos]
    bgs = re.findall(r"background(?:-color)?\s*:\s*([^;}]+)", ctx)
    for bg in reversed(bgs):
        bg = bg.strip()
        if "url(" in bg or "gradient" in bg:
            continue
        lum = color_lum(bg)
        if lum is None:
            continue
        return lum < 0.35
    return False

stats = {}
for page in PAGES:
    html = page.read_text(encoding="utf-8")
    orig = html

    # 1. n12S button blue on white
    html, n = re.subn(r"(\.m-button-n12S-An \{ cursor: pointer; color: )#1f89da", r"\g<1>#006FDC", html)
    stats["btn_n12S"] = stats.get("btn_n12S", 0) + n

    # 2. footer-bar icon aspect: 20x22 -> 20x20
    html, n = re.subn(
        r"\.footer-bar__wrapper-icon-item img \{ height: 22px; width: 20px;",
        ".footer-bar__wrapper-icon-item img { height: 20px; width: 20px;",
        html,
    )
    stats["footer_icon"] = stats.get("footer_icon", 0) + n

    # 3. inline brand blue rgba(36,160,255,1) on light contexts
    out, last, changed = [], 0, 0
    for m in re.finditer(r"rgba\(36,160,255,1\)", html):
        out.append(html[last:m.start()])
        if ctx_is_dark(html, m.start()):
            out.append(m.group(0))
        else:
            out.append("rgba(0,111,220,1)")
            changed += 1
        last = m.end()
    out.append(html[last:])
    html = "".join(out)
    stats["inline_blue"] = stats.get("inline_blue", 0) + changed

    # 4. demote JS bundle preload (bandwidth priority for CSS/hero)
    html, n = re.subn(r'<link rel="preload" as="script" href="[^"]*public\.bundle[^"]*" />\n?', "", html)
    if not n:
        html, n = re.subn(r'<link rel="preload" as="script" href="[^"]*public\.bundle[^"]*"/>\n?', "", html)
    stats["js_preload_removed"] = stats.get("js_preload_removed", 0) + n

    if html != orig:
        page.write_text(html, encoding="utf-8")

print("stats:", stats)
