# -*- coding: utf-8 -*-
"""Restore Mottor img srcs from git; keep width/height attrs from pass2."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("site_mirror")
CITIES = [
    "almaty", "astana", "shymkent", "aktau", "aktobe", "atyrau", "karaganda",
    "kokshetau", "kostanay", "kyzylorda", "pavlodar", "petropavlovsk", "semey",
    "taldykorgan", "taraz", "turkestan", "uralsk", "ust-kamenogorsk",
]


def git_show(rel: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"HEAD:{rel.replace(chr(92), '/')}"],
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def extract_srcs(html: str) -> list[str]:
    return re.findall(r'<img\b[^>]*\ssrc="([^"]+)"', html, flags=re.I)


def restore_page(path: Path) -> None:
    rel = path.as_posix()
    # HEAD may already include pass1 CSS extract; use last committed version for srcs
    try:
        old = git_show(rel)
    except subprocess.CalledProcessError:
        print("skip git", rel)
        return
    old_srcs = extract_srcs(old)
    cur = path.read_text(encoding="utf-8")

    idx = 0

    def repl(m: re.Match) -> str:
        nonlocal idx
        tag = m.group(0)
        if idx >= len(old_srcs):
            return tag
        old_src = old_srcs[idx]
        idx += 1
        return re.sub(r'src="[^"]+"', f'src="{old_src}"', tag, count=1)

    new, n = re.subn(r"<img\b[^>]*>", repl, cur, flags=re.I)
    path.write_text(new, encoding="utf-8")
    print(path.parent.name, "restored", idx, "of", n, "old had", len(old_srcs))


def add_missing_dims(path: Path) -> None:
    html = path.read_text(encoding="utf-8")

    def patch(m: re.Match) -> str:
        tag = m.group(0)
        if "width=" in tag and "height=" in tag:
            return tag
        # decorative / unknown webp near hero titles — use reasonable placeholder
        if tag.endswith("/>"):
            return tag[:-2] + ' width="600" height="400" />'
        return tag[:-1] + ' width="600" height="400">'

    html2, n = re.subn(r"<img\b[^>]*>", patch, html, flags=re.I)
    path.write_text(html2, encoding="utf-8")
    print("dims fill", path.parent.name, n)


def main() -> int:
    pages = [ROOT / "web-studiya/sozdanie-saitov/index.html"] + [
        ROOT / "web-studiya/sozdanie-saitov" / c / "index.html" for c in CITIES
    ]
    for p in pages:
        restore_page(p)
        add_missing_dims(p)

    # verify icons restore
    t = pages[0].read_text(encoding="utf-8")
    print("scale/x3 left", t.count("/-/scale/x3/-/resize/1920/"))
    print("missing dims", sum(1 for i in re.findall(r"<img\b[^>]*>", t, re.I) if "width=" not in i or "height=" not in i))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
