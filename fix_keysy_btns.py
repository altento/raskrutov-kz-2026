# -*- coding: utf-8 -*-
"""Fix remaining empty Смотреть кейсы buttons."""
from __future__ import annotations

import os
import re
import time
from pathlib import Path

ROOT = Path("site_mirror")
LABEL_RE = re.compile(r"Смотреть\s+кейсы")


def write_atomic(path: Path, html: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(html, encoding="utf-8", newline="\n")
    for attempt in range(8):
        try:
            os.replace(tmp, path)
            return
        except (PermissionError, OSError):
            time.sleep(0.25 * (attempt + 1))
    path.write_text(html, encoding="utf-8", newline="\n")
    if tmp.exists():
        tmp.unlink(missing_ok=True)


n_files = 0
n_fix = 0
for page in sorted(ROOT.rglob("index.html")):
    if "assets" in page.parts:
        continue
    html = page.read_text(encoding="utf-8", errors="replace")
    orig = html
    # Walk from end so positions stay valid when editing earlier matches
    matches = list(LABEL_RE.finditer(html))
    for m in reversed(matches):
        idx = m.start()
        window_start = max(0, idx - 1500)
        window = html[window_start:idx]
        # nearest empty dpl in window
        dpl = window.rfind('data-page-link=""')
        if dpl < 0:
            continue
        abs_dpl = window_start + dpl
        ctx = html[abs_dpl:idx]
        if "showPopup" in ctx or "data-popup" in ctx:
            continue
        html = (
            html[:abs_dpl]
            + 'data-page-link="/keysy/"'
            + html[abs_dpl + len('data-page-link=""') :]
        )
        n_fix += 1
    if html != orig:
        write_atomic(page, html)
        n_files += 1
        print("fixed", page.relative_to(ROOT).as_posix())
print({"files": n_files, "fixes": n_fix})
