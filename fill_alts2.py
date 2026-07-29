#!/usr/bin/env python3
"""Fill ALL remaining missing/empty alt attributes using broader context.

Context search order per image:
1. img title attribute
2. wrapping <a> title attribute
3. nearest heading text before the image (16 KB window)
4. first heading text right after the image (4 KB window) — card layouts
5. page H1
6. page <title>
Duplicate alts within a page get a numeric suffix.
"""
import html as html_mod
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
HEAD_RE = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def clean(text: str) -> str:
    text = TAG_RE.sub(" ", text)
    text = html_mod.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace('"', "'").replace("​", "").strip(" -–—,.")
    return text[:125]


def get_attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{name}\s*=\s*"([^"]*)"', tag, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(rf"\b{name}\s*=\s*'([^']*)'", tag, re.IGNORECASE)
    return m.group(1) if m else None


def nearest_heading_before(before: str) -> str:
    heads = HEAD_RE.findall(before[-16000:])
    return clean(heads[-1][1]) if heads else ""


def nearest_heading_after(after: str) -> str:
    m = HEAD_RE.search(after[:4000])
    return clean(m.group(2)) if m else ""


def wrapping_link_title(html: str, img_start: int) -> str:
    """If the img is inside <a ... title="...">, use that title."""
    a_open = html.rfind("<a ", max(0, img_start - 2000), img_start)
    if a_open == -1:
        return ""
    a_close = html.find("</a>", a_open)
    if a_close == -1 or a_close < img_start:
        return ""
    tag = html[a_open : html.find(">", a_open) + 1]
    t = get_attr(tag, "title")
    return clean(t) if t else ""


def process(path: Path) -> tuple[int, int]:
    html = path.read_text(encoding="utf-8", errors="ignore")
    h1 = ""
    m1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    if m1:
        h1 = clean(m1.group(1))
    mt = TITLE_RE.search(html)
    page_title = clean(mt.group(1)) if mt else ""
    page_title = page_title.split("—")[0].split("|")[0].strip()

    used: dict[str, int] = {}
    filled = 0
    out: list[str] = []
    last = 0

    for m in IMG_RE.finditer(html):
        tag = m.group(0)
        alt = get_attr(tag, "alt")
        if alt is not None and alt.strip() != "":
            continue

        text = ""
        t = get_attr(tag, "title")
        if t and t.strip():
            text = clean(t)
        if not text:
            text = wrapping_link_title(html, m.start())
        if not text:
            text = nearest_heading_before(html[: m.start()])
        if not text:
            text = nearest_heading_after(html[m.end():])
        if not text:
            text = h1 or page_title
        if not text:
            text = "Raskrutov — digital-агентство"

        base = text
        n = used.get(base, 0) + 1
        used[base] = n
        if n > 1:
            text = f"{base} ({n})"

        new_tag = tag
        if alt is None:
            new_tag = new_tag.rstrip(">").rstrip("/").rstrip() + f' alt="{text}">'
        else:
            new_tag = re.sub(r'\balt\s*=\s*"\s*"', f'alt="{text}"', new_tag, count=1, flags=re.IGNORECASE)
            new_tag = re.sub(r"\balt\s*=\s*'\s*'", f'alt="{text}"', new_tag, count=1, flags=re.IGNORECASE)

        filled += 1
        out.append(html[last : m.start()])
        out.append(new_tag)
        last = m.end()

    if not out:
        return 0, 0
    out.append(html[last:])
    new_html = "".join(out)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        return filled, 1
    return 0, 0


def main() -> None:
    total = files = 0
    for f in M.rglob("*.html"):
        if "assets" in f.relative_to(M).parts:
            continue
        n, changed = process(f)
        total += n
        files += changed
    print(f"files changed: {files}, alts filled: {total}")


if __name__ == "__main__":
    main()
