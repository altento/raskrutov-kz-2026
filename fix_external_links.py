#!/usr/bin/env python3
"""Fix broken email artifacts and external social/messenger links across all pages."""
import re
from pathlib import Path

MIRROR = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")
ORIG_DIR = MIRROR / "assets" / "raskrutov.kz"

EMAIL_RE = re.compile(r"info@[^\"'<>\s]*")
GOOD_EMAIL = "info@raskrutov.kz"

FAMILIES = {
    "instagram": re.compile(r"instagram\.com"),
    "youtube": re.compile(r"youtube\.com|youtu\.be"),
    "telegram": re.compile(r"t\.me|telegram\.me"),
    "whatsapp": re.compile(r"whatsapp|wa\.me"),
}

EXT_RE = re.compile(
    r'href="([^"]*(?:instagram|youtube|youtu\.be|t\.me|telegram|whatsapp|wa\.me)[^"]*)"',
    re.IGNORECASE,
)


def harvest_real_urls() -> dict[str, str]:
    """Pull genuine external social URLs from the original mirrored pages."""
    found: dict[str, str] = {}
    pat = re.compile(
        r'href="(https?://[^"]*(?:instagram\.com|youtube\.com|youtu\.be|t\.me|telegram\.me|api\.whatsapp\.com|wa\.me)[^"]*)"',
        re.IGNORECASE,
    )
    fallback = {
        "instagram": "https://www.instagram.com/raskrutov.kz/",
        "youtube": "https://www.youtube.com/@raskrutov-kz",
        "telegram": "https://t.me/Raskrutov_web",
        "whatsapp": "https://api.whatsapp.com/send?phone=77000216900",
    }
    if ORIG_DIR.exists():
        for f in ORIG_DIR.rglob("*.html"):
            try:
                html = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for url in pat.findall(html):
                if ".." in url or ".html" in url:
                    continue  # corrupted rewrite artifact, not a real URL
                for name, fam in FAMILIES.items():
                    if name not in found and fam.search(url):
                        found[name] = url
    for name, url in fallback.items():
        found.setdefault(name, url)
    return found


def fix_file(path: Path, real: dict[str, str]) -> tuple[int, int]:
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0, 0
    orig = html

    html = html.replace(
        "https://../www.youtube.com/@raskrutov-kz/index.html",
        "https://www.youtube.com/@raskrutov-kz",
    )

    def email_repl(m: re.Match) -> str:
        return GOOD_EMAIL if m.group(0) != GOOD_EMAIL else m.group(0)

    html = EMAIL_RE.sub(email_repl, html)
    n_email = 0 if html == orig else 1

    def ext_repl(m: re.Match) -> str:
        url = m.group(1)
        if url.startswith("http"):
            return m.group(0)
        for name, fam in FAMILIES.items():
            if fam.search(url):
                return f'href="{real[name]}"'
        return m.group(0)

    html, n_ext = EXT_RE.subn(ext_repl, html)

    if html != orig:
        path.write_text(html, encoding="utf-8")
    return n_email, n_ext


def main():
    real = harvest_real_urls()
    print("Real external URLs:")
    for k, v in real.items():
        print(f"  {k}: {v}")
    total_e = total_x = files = 0
    for f in MIRROR.rglob("*.html"):
        if "assets" in f.relative_to(MIRROR).parts:
            continue  # skip mirrored originals/CDN dumps
        ne, nx = fix_file(f, real)
        if ne or nx:
            files += 1
            total_e += ne
            total_x += nx
    print(f"Files fixed: {files}, email fixes: {total_e}, external link fixes: {total_x}")


if __name__ == "__main__":
    main()
