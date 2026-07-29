#!/usr/bin/env python3
"""Add meaningful alt attributes to <img> tags, plus lazy-loading hints.

Regex-based, in-place tag rewriting: the rest of each file stays byte-identical.
Alt text priority: title attr -> nearest preceding heading text -> leave empty.
"""
import html as html_mod
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
HEAD_RE = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SKIP_LAZY_FIRST_N = 3  # keep first images eager for LCP


def clean(text: str) -> str:
    text = TAG_RE.sub(" ", text)
    text = html_mod.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace('"', "'").replace("​", "").strip()
    return text[:125]


def nearest_heading(before: str) -> str:
    heads = HEAD_RE.findall(before[-8000:])
    if not heads:
        return ""
    return clean(heads[-1][1])


def get_attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{name}\s*=\s*"([^"]*)"', tag, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(rf"\b{name}\s*=\s*'([^']*)'", tag, re.IGNORECASE)
    return m.group(1) if m else None


def process(path: Path) -> tuple[int, int, int]:
    html = path.read_text(encoding="utf-8", errors="ignore")
    filled = lazy = 0
    img_idx = 0
    out: list[str] = []
    last = 0
    for m in IMG_RE.finditer(html):
        tag = m.group(0)
        new_tag = tag
        alt = get_attr(new_tag, "alt")
        if alt is None or alt.strip() == "":
            text = ""
            t = get_attr(new_tag, "title")
            if t and t.strip():
                text = clean(t)
            if not text:
                text = nearest_heading(html[: m.start()])
            if text:
                if alt is None:
                    new_tag = new_tag.rstrip(">").rstrip("/").rstrip()
                    new_tag += f' alt="{text}">'
                else:
                    new_tag = re.sub(
                        r'\balt\s*=\s*"\s*"',
                        f'alt="{text}"',
                        new_tag,
                        count=1,
                        flags=re.IGNORECASE,
                    )
                    new_tag = re.sub(
                        r"\balt\s*=\s*'\s*'",
                        f'alt="{text}"',
                        new_tag,
                        count=1,
                        flags=re.IGNORECASE,
                    )
                filled += 1
        if get_attr(new_tag, "loading") is None:
            new_tag = new_tag.rstrip(">").rstrip("/").rstrip() + ' loading="lazy">'
            if img_idx < SKIP_LAZY_FIRST_N:
                new_tag = new_tag.replace(' loading="lazy"', ' loading="eager"', 1)
            lazy += 1
        if get_attr(new_tag, "decoding") is None:
            new_tag = new_tag.rstrip(">").rstrip("/").rstrip() + ' decoding="async">'
        img_idx += 1
        out.append(html[last : m.start()])
        out.append(new_tag)
        last = m.end()
    if not out:
        return 0, 0, 0
    out.append(html[last:])
    new_html = "".join(out)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
    return filled, lazy, 1


def main():
    total_f = total_l = files = 0
    for f in M.rglob("*.html"):
        if "assets" in f.relative_to(M).parts:
            continue
        nf, nl, changed = process(f)
        total_f += nf
        total_l += nl
        files += changed
    print(f"Files changed: {files}")
    print(f"Alt attributes filled: {total_f}")
    print(f"loading attr added: {total_l}")


if __name__ == "__main__":
    main()
