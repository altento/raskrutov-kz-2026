# -*- coding: utf-8 -*-
"""QA audit for pretty-URL site_mirror/**/index.html pages.

Checks: broken internal refs, empty CTA buttons, H1 count, breadcrumbs,
canonical, JSON-LD, favicon, public.bundle sync, lead-forms, obvious
text/layout red flags.
"""
from __future__ import annotations

import posixpath
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("site_mirror")
PROD = "https://raskrutov.kz"

real_files: set[str] = set()
real_dirs: set[str] = set()
for f in ROOT.rglob("*"):
    rel = f.relative_to(ROOT).as_posix()
    if f.is_file():
        real_files.add(rel)
    elif f.is_dir():
        real_dirs.add(rel)

PAGES = sorted(
    p for p in ROOT.rglob("index.html") if "assets" not in p.parts
)


def page_beaut(p: Path) -> str:
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return ""
    return rel[: -len("/index.html")]


def resolve(base_dir: str, path: str) -> str | None:
    path = path.split("#")[0].split("?")[0].strip().strip("'\"")
    if not path:
        return None
    if re.match(r"^(https?://|mailto:|tel:|javascript:|//|data:|blob:)", path):
        return None
    # Root-absolute site paths
    if path.startswith("/"):
        path = path.lstrip("/")
        if not path or path == "/":
            return None  # site root OK
        r = posixpath.normpath(path).replace("\\", "/")
        return None if r in (".", "") else r
    r = (
        posixpath.normpath(posixpath.join(base_dir, path))
        if base_dir
        else posixpath.normpath(path)
    )
    r = r.replace("\\", "/").lstrip("/")
    if r in (".", ""):
        return None
    return r


def exists(r: str) -> bool:
    return (
        r in real_files
        or r in real_dirs
        or (r + "/index.html") in real_files
        or (r.rstrip("/") + "/index.html") in real_files
    )


issues: dict[str, list[str]] = {}


def add(page: str, msg: str) -> None:
    issues.setdefault(page, []).append(msg)


broken_refs = 0
empty_btns = 0

for page in PAGES:
    beaut = page_beaut(page)
    rel = page.relative_to(ROOT).as_posix()
    html = page.read_text(encoding="utf-8", errors="replace")

    # --- refs ---
    for kind, pat in (
        ("href/src", re.compile(r'(?:href|src)="([^"]*)"')),
        ("dpl", re.compile(r'data-page-link="([^"]*)"')),
    ):
        for m in pat.finditer(html):
            url = m.group(1)
            if url == "" and kind == "dpl":
                # empty dpl is OK for popups / scroll — checked separately for linkRedirect
                continue
            r = resolve(beaut, url)
            if r and not exists(r):
                broken_refs += 1
                add(rel, f"BROKEN {kind}: {url[:90]}")

    for m in re.finditer(r'url\(([^)]+)\)', html):
        raw = m.group(1).strip().strip("'\"")
        r = resolve(beaut, raw)
        if r and not exists(r) and not raw.startswith("data:"):
            # skip Mottor runtime placeholders
            if "undefined" in raw or raw in ("none",):
                continue
            broken_refs += 1
            add(rel, f"BROKEN url(): {raw[:70]}")

    # --- empty linkRedirect buttons (no popup) ---
    for m in re.finditer(
        r'<div class="m-button-wrapper\s*"[^>]*data-page-link=""[^>]*>',
        html,
    ):
        ctx = html[m.start() : m.start() + 500]
        if "showPopup" in ctx or "data-popup" in ctx or "scrollTo" in ctx:
            continue
        if "linkRedirect" not in ctx:
            continue
        txt_m = re.search(
            r'ms-active-string[^>]*>([^<]{0,60})', ctx
        )
        label = (txt_m.group(1).strip() if txt_m else "?").replace("\xa0", " ")
        if not label or label == "?":
            continue
        empty_btns += 1
        add(rel, f"EMPTY-BTN: {label[:40]!r}")

    # --- href="" or href without value on content links ---
    for m in re.finditer(r'<a\b([^>]*)>', html, re.I):
        attrs = m.group(1)
        if re.search(r'\bhref\s*=\s*""', attrs) or (
            "href" not in attrs.lower() and "name=" not in attrs.lower()
        ):
            # skip anchors that are menu wrappers sometimes without href in odd markup
            if "ms-menu" in html[max(0, m.start() - 200) : m.start()]:
                continue
            add(rel, "EMPTY-A-HREF")

    # --- structure ---
    h1s = len(re.findall(r"<h1[\s>]", html, re.I))
    if beaut and h1s == 0:
        add(rel, "NO-H1")
    elif h1s > 3:
        add(rel, f"H1x{h1s}")

    if beaut and 'data-rk-breadcrumbs>' not in html and 'data-rk-breadcrumbs"' not in html and "data-rk-breadcrumbs" not in html:
        # homepage intentionally skipped
        add(rel, "NO-VISUAL-BREADCRUMBS")
    if 'application/ld+json' not in html:
        add(rel, "NO-JSONLD")
    elif html.count("application/ld+json") > 1:
        add(rel, f"JSONLDx{html.count('application/ld+json')}")
    if 'rel="icon"' not in html and "rel='icon'" not in html:
        add(rel, "NO-FAVICON")

    cans = re.findall(r'<link rel="canonical" href="([^"]*)"', html)
    expect = f"{PROD}/" if not beaut else f"{PROD}/{beaut}"
    # allow with or without trailing slash variants for hubs
    if len(cans) != 1:
        add(rel, f"CANONICAL-COUNT:{len(cans)}")
    elif beaut and cans[0].rstrip("/") != expect.rstrip("/"):
        add(rel, f"CANONICAL-MISMATCH:{cans[0]}")

    # public.bundle must be sync
    if re.search(
        r'public\.bundle[^>]+(?:defer|async)', html, re.I
    ) or re.search(
        r'<(?:link[^>]+preload[^>]+public\.bundle|script[^>]+defer[^>]+public\.bundle)',
        html,
        re.I,
    ):
        add(rel, "BUNDLE-DEFER-OR-PRELOAD")

    # lead forms wired?
    if "data-lead-form" in html and "lead-forms.js" not in html:
        add(rel, "LEAD-FORM-NO-JS")

    # breadcrumbs CSS when nav present
    if "data-rk-breadcrumbs" in html and "breadcrumbs.css" not in html and beaut:
        add(rel, "BC-NAV-NO-CSS")

# summarize
print(f"pages={len(PAGES)} broken_ref_hits={broken_refs} empty_btn_hits={empty_btns}")
print(f"pages_with_issues={len(issues)}")

# group by issue prefix
by_kind: Counter[str] = Counter()
for msgs in issues.values():
    for m in msgs:
        by_kind[m.split(":")[0].split(" ")[0]] += 1
print("by_kind:", dict(by_kind.most_common(20)))

out_lines = []
for name in sorted(issues):
    out_lines.append(name)
    for m in issues[name][:12]:
        out_lines.append(f"   - {m}")
    if len(issues[name]) > 12:
        out_lines.append(f"   - … +{len(issues[name]) - 12} more")
Path("reports/qa_pretty_pages.txt").write_text(
    "\n".join(out_lines) if out_lines else "ALL CLEAR\n",
    encoding="utf-8",
)
print("wrote reports/qa_pretty_pages.txt")
if not issues:
    print("ALL CLEAR")
