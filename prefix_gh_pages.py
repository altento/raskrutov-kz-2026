#!/usr/bin/env python3
"""Prefix root-absolute site paths for GitHub Pages project site.

raskrutov.kz lives at domain root → href=\"/web-studiya/\" is correct there.
GitHub Pages serves from /raskrutov-kz-2026/ → the same href jumps to
https://altento.github.io/web-studiya/ (broken). Rewrite ONLY inside site_deploy.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "site_deploy"
BASE = "/raskrutov-kz-2026"

# Site path prefixes that must be rewritten when absolute from /
SITE_PREFIXES = (
    "web-studiya",
    "r-builder",
    "akademiya",
    "partneram",
    "o-kompanii",
    "keysy",
    "kontakty",
    "faq",
    "crm",
    "consent",
    "regulation",
    "assets",
    "favicon",
    "pages",
    "index.html",
)

PREFIX_RE = re.compile(
    r'(?P<attr>href|src|data-page-link|action|poster|data-original-url)'
    r'(?P<eq>=)(?P<q>["\'])'
    r'(?P<path>/)'
    r'(?P<rest>[^"\']*)'
    r'(?P=q)'
)

# url(/...) in CSS / inline styles
URL_RE = re.compile(r'url\(\s*(["\']?)(/)([^)"\']+)\1\s*\)')


def should_prefix(path_after_slash: str) -> bool:
    if not path_after_slash:
        return True  # href="/" → home
    if path_after_slash.startswith(BASE.lstrip("/") + "/") or path_after_slash == BASE.lstrip("/"):
        return False  # already prefixed
    if path_after_slash.startswith(("http:", "https:", "//", "#", "mailto:", "tel:", "data:", "wa.me")):
        return False
    first = path_after_slash.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    if first in SITE_PREFIXES or first.endswith((".html", ".xml", ".ico", ".png", ".webp", ".svg", ".js", ".css", ".woff", ".woff2")):
        return True
    # bare known top-level files
    return first in {"robots.txt", "sitemap.xml", ".htaccess"}


def rewrite_text(text: str) -> tuple[str, int]:
    n = 0

    def attr_repl(m: re.Match) -> str:
        nonlocal n
        rest = m.group("rest")
        # data-original-url should stay production absolute https — skip if already https
        if m.group("attr") == "data-original-url":
            return m.group(0)
        if not should_prefix(rest):
            return m.group(0)
        n += 1
        return f'{m.group("attr")}{m.group("eq")}{m.group("q")}{BASE}/{rest}{m.group("q")}'

    text = PREFIX_RE.sub(attr_repl, text)

    def url_repl(m: re.Match) -> str:
        nonlocal n
        q, slash, rest = m.group(1), m.group(2), m.group(3)
        if not should_prefix(rest):
            return m.group(0)
        n += 1
        return f"url({q}{BASE}/{rest}{q})"

    text = URL_RE.sub(url_repl, text)

    # window / JS string paths that start with '/assets' or '/web-studiya'
    def js_path_repl(m: re.Match) -> str:
        nonlocal n
        q, path = m.group(1), m.group(2)
        rest = path[1:]  # drop leading /
        if not should_prefix(rest):
            return m.group(0)
        n += 1
        return f"{q}{BASE}{path}{q}"

    text = re.sub(
        r"(['\"])(/(?:web-studiya|r-builder|akademiya|partneram|o-kompanii|keysy|kontakty|faq|crm|consent|regulation|assets|pages|favicon)[^'\"]*)\1",
        js_path_repl,
        text,
    )
    return text, n


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"missing {ROOT}")
    files = 0
    total = 0
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".html", ".css", ".js", ".xml", ".json"}:
            continue
        if ".git" in p.parts:
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        new, n = rewrite_text(raw)
        if n and new != raw:
            p.write_text(new, encoding="utf-8", newline="\n")
            files += 1
            total += n
    print(f"prefixed {total} refs in {files} files with base {BASE}")


if __name__ == "__main__":
    main()
