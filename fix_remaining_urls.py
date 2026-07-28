#!/usr/bin/env python3
import argparse
import json
import posixpath
import re
import sys
from pathlib import Path


TEXT_SUFFIXES = {".html", ".htm", ".css", ".js", ".svg", ".json", ".xml", ".txt"}


def escaped_variants(url: str):
    stripped = url.replace("https://", "").replace("http://", "")
    variants = {
        url,
        url.replace("https://", "http://"),
        url.replace("http://", "https://"),
        url.replace("https://", "//"),
        url.replace("http://", "//"),
        url.replace("/", r"\/"),
        url.replace("https://", r"https:\/\/"),
        url.replace("http://", r"http:\/\/"),
        stripped,
    }
    return {v for v in variants if v}


def rewrite_text(text: str, current_file: Path, root: Path, manifest: dict[str, str]) -> tuple[str, int]:
    changes = 0
    relative_cache = {}
    start_dir = current_file.parent.relative_to(root).as_posix()
    for original, local in manifest.items():
        relative = relative_cache.get(local)
        if relative is None:
            relative = Path(local).as_posix()
            relative_cache[local] = relative
        relative_from_file = posixpath.relpath(relative, start=start_dir)

        for variant in escaped_variants(original):
            if variant not in text:
                continue
            replacement = relative_from_file
            if variant.startswith("http") or variant.startswith("//") or variant.startswith("/"):
                replacement = relative_from_file
            if variant.endswith(r"\/"):
                replacement = replacement.replace("/", r"\/")
            text = text.replace(variant, replacement)
            changes += 1

    return text, changes


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix hidden or escaped remaining source URLs.")
    parser.add_argument("--root", default="site_mirror", help="Mirror root directory")
    parser.add_argument("--manifest", default="site_mirror/asset_manifest.json", help="Manifest path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest_path = Path(args.manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    total_files = 0
    total_replacements = 0
    touched = []

    for file_path in root.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        rewritten, changes = rewrite_text(text, file_path, root, manifest)
        if changes:
            file_path.write_text(rewritten, encoding="utf-8")
            touched.append(str(file_path.relative_to(root)))
            total_replacements += changes
        total_files += 1

    report = {
        "root": str(root),
        "filesScanned": total_files,
        "filesTouched": len(touched),
        "replacements": total_replacements,
        "touched": touched,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
