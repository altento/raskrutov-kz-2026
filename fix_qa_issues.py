# -*- coding: utf-8 -*-
"""Fix real QA issues across pretty-URL pages:
1) empty «Смотреть кейсы» linkRedirect → /keysy/
2) sozdanie pages: dedupe canonical, ensure favicon
3) demote excess <h1> beyond first 2 (pc/mobile) to <h2>
"""
from __future__ import annotations

import os
import re
import time
from pathlib import Path

ROOT = Path("site_mirror")
PAGES = sorted(p for p in ROOT.rglob("index.html") if "assets" not in p.parts)

FAVICON_PNG = 'm-files.cdn1.cc/lpfile/favicon/favicon__q_1.png'
FAVICON_BLOCK = (
    '<link href="{prefix}assets/m-files.cdn1.cc/lpfile/favicon/favicon__q_1.png" '
    'type="image/png" rel="icon"/>'
    '<link href="{prefix}favicon.ico" sizes="16x16 32x32 48x48" rel="icon" '
    'type="image/x-icon"/>'
)


def depth_prefix(rel: str) -> str:
    parts = Path(rel).parts
    depth = len(parts) - 1
    return "../" * depth if depth > 0 else ""


def page_beaut(rel: str) -> str:
    if rel == "index.html":
        return ""
    return rel[: -len("/index.html")]


def write_atomic(path: Path, html: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(html, encoding="utf-8", newline="\n")
    last = None
    for attempt in range(8):
        try:
            os.replace(tmp, path)
            return
        except (PermissionError, OSError) as e:
            last = e
            time.sleep(0.25 * (attempt + 1))
    path.write_text(html, encoding="utf-8", newline="\n")
    if tmp.exists():
        tmp.unlink(missing_ok=True)
    if last:
        pass


def fix_empty_keysy(html: str) -> tuple[str, int]:
    """Set data-page-link=/keysy/ on empty wrappers labeled «Смотреть кейсы»."""
    n = 0
    label = "Смотреть кейсы"
    start = 0
    while True:
        idx = html.find(label, start)
        if idx < 0:
            break
        # find nearest data-page-link="" before label within 900 chars
        window = html[max(0, idx - 900) : idx]
        dpl = window.rfind('data-page-link=""')
        if dpl < 0:
            start = idx + len(label)
            continue
        abs_dpl = max(0, idx - 900) + dpl
        ctx = html[abs_dpl : idx + len(label)]
        if "showPopup" in ctx or "data-popup" in ctx:
            start = idx + len(label)
            continue
        html = (
            html[:abs_dpl]
            + 'data-page-link="/keysy/"'
            + html[abs_dpl + len('data-page-link=""') :]
        )
        n += 1
        start = idx + len(label) + len('/keysy/')  # advance past edit
    return html, n


def fix_canonical_favicon(html: str, beaut: str, prefix: str) -> tuple[str, int, int]:
    fixed_can = 0
    fixed_fav = 0
    expect = "https://raskrutov.kz/" if not beaut else f"https://raskrutov.kz/{beaut}"

    cans = list(re.finditer(r'<link rel="canonical" href="([^"]*)"\s*/?>', html))
    if len(cans) > 1:
        # keep first correct or first; remove rest
        keep_idx = 0
        for i, m in enumerate(cans):
            if m.group(1).rstrip("/") == expect.rstrip("/"):
                keep_idx = i
                break
        # rebuild without extras
        parts = []
        last = 0
        for i, m in enumerate(cans):
            if i == keep_idx:
                # ensure href correct
                parts.append(html[last : m.start()])
                parts.append(f'<link rel="canonical" href="{expect}"/>')
                last = m.end()
            else:
                parts.append(html[last : m.start()])
                last = m.end()
                fixed_can += 1
        parts.append(html[last:])
        html = "".join(parts)
    elif len(cans) == 1:
        if cans[0].group(1).rstrip("/") != expect.rstrip("/"):
            html = (
                html[: cans[0].start()]
                + f'<link rel="canonical" href="{expect}"/>'
                + html[cans[0].end() :]
            )
            fixed_can += 1
    elif len(cans) == 0:
        html = html.replace(
            "</head>",
            f'<link rel="canonical" href="{expect}"/>\n</head>',
            1,
        )
        fixed_can += 1

    if 'rel="icon"' not in html:
        html = html.replace(
            "</head>",
            FAVICON_BLOCK.format(prefix=prefix) + "\n</head>",
            1,
        )
        fixed_fav += 1

    return html, fixed_can, fixed_fav


def demote_extra_h1(html: str, keep: int = 2) -> tuple[str, int]:
    """Keep first `keep` h1 tags; demote the rest to h2 (Mottor often duplicates)."""
    count = 0
    demoted = 0

    def repl(m: re.Match) -> str:
        nonlocal count, demoted
        count += 1
        if count <= keep:
            return m.group(0)
        demoted += 1
        tag = m.group(0)
        # <h1 ...> -> <h2 ...>  and closing
        return tag

    # Only open tags first — then closings is harder; do pair-wise scan
    out = []
    pos = 0
    seen = 0
    for m in re.finditer(r"</?h1\b[^>]*>", html, flags=re.I):
        out.append(html[pos : m.start()])
        token = m.group(0)
        if token.lower().startswith("</"):
            # closing — only demote if we already passed keep opens that were demoted
            # Track with a stack of whether current open was demoted
            pass
        pos = m.start()
        break  # rewrite with stack below
    # stack approach
    out = []
    pos = 0
    stack: list[bool] = []  # True if this h1 level was demoted
    demoted = 0
    open_seen = 0
    for m in re.finditer(r"</?h1\b([^>]*)>", html, flags=re.I):
        out.append(html[pos : m.start()])
        attrs = m.group(1)
        is_close = m.group(0).startswith("</")
        if not is_close:
            open_seen += 1
            demote = open_seen > keep
            stack.append(demote)
            if demote:
                demoted += 1
                out.append(f"<h2{attrs}>")
            else:
                out.append(m.group(0))
        else:
            demote = stack.pop() if stack else False
            out.append("</h2>" if demote else m.group(0))
        pos = m.end()
    out.append(html[pos:])
    return "".join(out), demoted


stats = {
    "keysy": 0,
    "canonical": 0,
    "favicon": 0,
    "h1_demoted": 0,
    "files": 0,
}

for page in PAGES:
    rel = page.relative_to(ROOT).as_posix()
    html = page.read_text(encoding="utf-8", errors="replace")
    orig = html
    beaut = page_beaut(rel)
    prefix = depth_prefix(rel)

    html, n = fix_empty_keysy(html)
    stats["keysy"] += n

    html, nc, nf = fix_canonical_favicon(html, beaut, prefix)
    stats["canonical"] += nc
    stats["favicon"] += nf

    # Only demote on pages with crazy h1 counts (imported Mottor dumps)
    h1n = len(re.findall(r"<h1[\s>]", html, re.I))
    if h1n > 3:
        html, nd = demote_extra_h1(html, keep=2)
        stats["h1_demoted"] += nd

    if html != orig:
        write_atomic(page, html)
        stats["files"] += 1
        print("fixed", rel)

print(stats)
