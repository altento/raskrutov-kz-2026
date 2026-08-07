#!/usr/bin/env python3
"""Strip /raskrutov-kz-2026 prefix from HTML/CSS/JS (reverse of prefix_gh_pages.py).

Use when a GitHub Pages build was mixed into files meant for Plesk/raskrutov.kz.
Default target: site_mirror
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent / "site_mirror")
BASE = "/raskrutov-kz-2026"
BASE_ESC = re.escape(BASE)

ATTR_RE = re.compile(
    rf'(?P<attr>href|src|data-page-link|action|poster)'
    rf'(?P<eq>=)(?P<q>["\'])'
    rf"(?:{BASE_ESC}/?|{BASE_ESC}/(?P<rest>[^\"']*))"
    rf"(?P=q)"
)
URL_RE = re.compile(rf'url\(\s*(["\']?){BASE_ESC}/([^)"\']+)\1\s*\)')


def rewrite(text: str) -> tuple[str, int]:
    n = 0

    def attr_repl(m: re.Match) -> str:
        nonlocal n
        n += 1
        rest = m.group("rest")
        path = "/" if rest is None or rest == "" else "/" + rest
        return f'{m.group("attr")}{m.group("eq")}{m.group("q")}{path}{m.group("q")}'

    text = ATTR_RE.sub(attr_repl, text)

    def url_repl(m: re.Match) -> str:
        nonlocal n
        n += 1
        q, rest = m.group(1), m.group(2)
        return f"url({q}/{rest}{q})"

    text = URL_RE.sub(url_repl, text)
    return text, n


def main() -> None:
    exts = {".html", ".css", ".js", ".xml", ".json", ".txt", ".svg"}
    files = 0
    total = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in exts:
            continue
        if ".git" in path.parts:
            continue
        raw = path.read_text(encoding="utf-8", errors="surrogateescape")
        if BASE not in raw:
            continue
        new, n = rewrite(raw)
        if n:
            path.write_text(new, encoding="utf-8", errors="surrogateescape", newline="\n")
            files += 1
            total += n
            print(f"{n:4d}  {path.relative_to(ROOT).as_posix()}")
    print(f"Done: {total} replacements in {files} files under {ROOT}")


if __name__ == "__main__":
    main()
