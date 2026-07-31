# -*- coding: utf-8 -*-
"""Fix FOUC/layout race: keep Mottor CSS blocking; only defer true popup CSS.

Root cause: async public.bundle.css + deferred sp-2782231 (mobile menu styles)
let FE measure --height:1110px before mobile menu CSS applied.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HTML = Path("site_mirror/index.html")
html = HTML.read_text(encoding="utf-8")
BUNDLE = "assets/m-files.cdn1.cc/web/build/pages/public.bundle__q_v_1784122059.css"

# 1) Restore blocking bundle stylesheet (remove async preload-swap pattern for bundle)
async_pat = re.compile(
    rf'<link rel="preload" href="{re.escape(BUNDLE)}" as="style" '
    rf'onload="this\.onload=null;this\.rel=\'stylesheet\'">\s*'
    rf'<noscript><link rel="stylesheet" href="{re.escape(BUNDLE)}"></noscript>',
    re.I,
)
if async_pat.search(html):
    html = async_pat.sub(f'<link href="{BUNDLE}" rel="stylesheet"/>', html, count=1)
    print("restored blocking bundle CSS")
else:
    # already blocking?
    if f'href="{BUNDLE}" rel="stylesheet"' in html or f"href='{BUNDLE}' rel='stylesheet'" in html:
        print("bundle CSS already blocking")
    else:
        print("WARN: bundle CSS pattern not found — injecting blocking link before </head>")
        html = html.replace("</head>", f'<link href="{BUNDLE}" rel="stylesheet"/>\n</head>', 1)

# Keep early preload for bundle (ok to have both preload + stylesheet)
if f'rel="preload" as="style" href="{BUNDLE}"' not in html and f'href="{BUNDLE}"' in html:
    # ensure early preload exists (may already from early_head_block)
    pass

# 2) Move home-popup-2782231.css from deferred body to blocking head
#    (contains mobile menu show/hide + padding vars)
popup_menu = "assets/css/home-popup-2782231.css"
popup_true = "assets/css/home-popup-2773676.css"

# Remove any existing links to popup-2782231 (deferred or not)
html = re.sub(
    rf'<link rel="stylesheet" href="{re.escape(popup_menu)}"[^>]*>\s*'
    rf'(?:<noscript><link rel="stylesheet" href="{re.escape(popup_menu)}"></noscript>\s*)?',
    "",
    html,
)
# Insert blocking before </head>
html = html.replace(
    "</head>",
    f'<link rel="stylesheet" href="{popup_menu}"/>\n</head>',
    1,
)
print("popup-2782231 -> blocking in head (mobile menu critical)")

# Ensure 2773676 stays deferred at body end only once
html = re.sub(
    rf'<link rel="stylesheet" href="{re.escape(popup_true)}"[^>]*>\s*'
    rf'(?:<noscript><link rel="stylesheet" href="{re.escape(popup_true)}"></noscript>\s*)?',
    "",
    html,
)
defer = (
    f'<link rel="stylesheet" href="{popup_true}" media="print" '
    f'onload="this.media=\'all\'">'
    f'<noscript><link rel="stylesheet" href="{popup_true}"></noscript>\n'
)
if "</body>" in html:
    html = html.replace("</body>", defer + "</body>", 1)
else:
    html += defer
print("popup-2773676 stays deferred")

# 3) Also preload the critical menu CSS early
if f'href="{popup_menu}"' in html and f'as="style" href="{popup_menu}"' not in html:
    html = html.replace(
        '<head>',
        f'<head><link rel="preload" as="style" href="{popup_menu}"/>',
        1,
    )
    # handle <head> with attrs
    if f'as="style" href="{popup_menu}"' not in html:
        html = re.sub(
            r"(<head[^>]*>)",
            rf'\1<link rel="preload" as="style" href="{popup_menu}"/>',
            html,
            count=1,
        )
    print("added preload for menu CSS")

tmp = HTML.with_suffix(".html.tmp")
tmp.write_bytes(html.encode("utf-8"))
tmp.replace(HTML)
print("HEAD KiB", html.find("</head>") / 1024)
print("done")
