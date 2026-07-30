# -*- coding: utf-8 -*-
"""Compare current web-studiya page vs original mirror commit for:
- arrow buttons (m-button-wrapper) data-page-link values
- popup markup/JS
- list item (points) markup
"""
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def git_show(rev):
    return subprocess.run(["git", "show", rev], capture_output=True).stdout.decode("utf-8", errors="replace")

orig = git_show("b7ffe07:site_mirror/pages/web-studiya.html")
cur = Path("site_mirror/web-studiya/index.html").read_text(encoding="utf-8")

def dpl_map(t):
    """block-id -> data-page-link for m-button wrappers"""
    out = {}
    # capture data-id near data-page-link
    for m in re.finditer(r'data-page-link="([^"]*)"[^>]*>', t):
        # find nearest preceding data-id
        s = t.rfind("data-id=", max(0, m.start() - 400), m.start())
        did = t[s + 9:s + 50].split('"')[0] if s != -1 else "?"
        out.setdefault(did, []).append(m.group(1))
    return out

o = dpl_map(orig)
c = dpl_map(cur)
print("=== data-page-link diffs (orig -> current) ===")
diffs = 0
for k in o:
    if k in c and o[k] != c[k]:
        diffs += 1
        if diffs <= 25:
            print(f"  block {k[:12]}: {o[k]} -> {c[k]}")
print("total diff blocks:", diffs)

print()
print("=== empty dpl in current: original values ===")
shown = 0
for m in re.finditer(r'data-page-link=""', cur):
    s = cur.rfind("data-id=", max(0, m.start() - 400), m.start())
    did = cur[s + 9:s + 50].split('"')[0] if s != -1 else "?"
    # what did orig have for this block?
    om = re.search(r'data-id="' + re.escape(did) + r'"[^>]*data-page-link="([^"]*)"', orig)
    if not om:
        # search wider: block near data-id
        oi = orig.find('data-id="' + did)
        if oi != -1:
            seg = orig[oi:oi + 500]
            om2 = re.search(r'data-page-link="([^"]*)"', seg)
            ov = om2.group(1) if om2 else "(no dpl attr)"
        else:
            ov = "(block not in orig)"
    else:
        ov = om.group(1)
    shown += 1
    if shown <= 25:
        print(f"  block {did[:12]}: orig dpl = {ov!r}")
print("empty dpl count:", shown)

print()
print("=== popup counts ===")
for label, t in [("orig", orig), ("cur", cur)]:
    print(f"  {label}: data-popup-id={t.count('data-popup-id')}, popup sections={len(re.findall(chr(39)+'is_popup'+chr(39), t)) or t.count('is_popup')}, showPopup={t.count('showPopup')}")

print()
print("=== onclick handlers comparison ===")
for label, t in [("orig", orig), ("cur", cur)]:
    oc = re.findall(r"onclick=\"return msJsWrapper\(event,'\w+','([^']*)'\)", t)
    from collections import Counter
    cnt = Counter(x.split("(")[0] for x in oc)
    print(f"  {label}: {dict(cnt)}")
