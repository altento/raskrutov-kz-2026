#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


TEXT_SUFFIXES = {".html", ".htm", ".css", ".js", ".svg"}
IGNORE_PREFIXES = ("http://", "https://", "//", "data:", "mailto:", "tel:", "javascript:", "#", "blob:")
ATTR_PATTERN = re.compile(
    r"""(?ix)
    \b(?:src|href|poster|action|data-src|data-srcset|data-lazy-src|data-lazy-srcset|data-bg|data-background|data-url)\s*=\s*["'](?P<value>.*?)["']
    """
)
CSS_URL_PATTERN = re.compile(r"""url\(\s*['"]?(?P<url>[^)"']+)""", re.I)
JS_STRING_URL_PATTERN = re.compile(r"""["'](?P<url>(?:\.{0,2}/|assets/|pages/)[^"'#?]+(?:\?[^"']*)?)["']""")


def should_ignore(url: str) -> bool:
    return not url or url.startswith(IGNORE_PREFIXES)


def split_srcset(value: str):
    for chunk in [x.strip() for x in value.split(",") if x.strip()]:
        yield chunk.split()[0]


def discover_refs(text: str, suffix: str):
    refs = set()
    for match in ATTR_PATTERN.finditer(text):
        value = match.group("value").strip()
        if "<" in value or ">" in value:
            continue
        if "," in value and ("srcset" in match.group(0).lower()):
            refs.update(split_srcset(value))
        else:
            refs.add(value)
    if suffix in {".css", ".html", ".htm", ".svg"}:
        for match in CSS_URL_PATTERN.finditer(text):
            candidate = match.group("url").strip()
            if "<" not in candidate and ">" not in candidate:
                refs.add(candidate)
    if suffix == ".js":
        for match in JS_STRING_URL_PATTERN.finditer(text):
            candidate = match.group("url").strip()
            if "<" not in candidate and ">" not in candidate:
                refs.add(candidate)
    return sorted(refs)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check missing local asset references.")
    parser.add_argument("--root", default="site_mirror", help="Mirror root directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    missing = []

    for file_path in root.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            missing.append({"file": str(file_path.relative_to(root)), "ref": "<read_error>", "error": str(exc)})
            continue

        for ref in discover_refs(text, file_path.suffix.lower()):
            if should_ignore(ref):
                continue
            clean_ref = ref.split("#", 1)[0]
            if not clean_ref:
                continue
            if clean_ref.startswith("/"):
                target = (root / clean_ref.lstrip("/")).resolve()
            else:
                target = (file_path.parent / clean_ref).resolve()
            if not target.exists():
                try:
                    resolved = str(target.relative_to(root))
                except ValueError:
                    resolved = str(target)
                missing.append(
                    {
                        "file": str(file_path.relative_to(root)),
                        "ref": ref,
                        "resolved": resolved,
                    }
                )

    report = {
        "root": str(root),
        "missingCount": len(missing),
        "missing": missing,
    }
    out_path = root / "missing_assets_report.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
