#!/usr/bin/env python3
"""Sync clean site_mirror → site_plesk (branch `plesk`) for Plesk/raskrutov.kz.

Unlike site_deploy / `deploy` branch, this copy has NO /raskrutov-kz-2026 prefix.
Download ZIP of branch `plesk` from GitHub and upload its contents to httpdocs.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "site_mirror"
DST = ROOT / "site_plesk"


def main() -> int:
    if not SRC.is_dir():
        print("ERROR: site_mirror missing", file=sys.stderr)
        return 1
    DST.mkdir(parents=True, exist_ok=True)
    # /MIR mirrors; exclude .git so worktree metadata stays
    cmd = [
        "robocopy",
        str(SRC),
        str(DST),
        "/MIR",
        "/XD",
        ".git",
        "/XF",
        ".git",
        "/NFL",
        "/NDL",
        "/NJH",
        "/NJS",
        "/nc",
        "/ns",
        "/np",
    ]
    rc = subprocess.call(cmd)
    # robocopy: 0-7 success
    if rc >= 8:
        print(f"ERROR: robocopy failed with code {rc}", file=sys.stderr)
        return 1
    # sanity: must not contain GH Pages base in homepage
    index = DST / "index.html"
    if index.is_file() and "raskrutov-kz-2026" in index.read_text(encoding="utf-8", errors="ignore"):
        print("ERROR: site_plesk/index.html still has raskrutov-kz-2026 prefix", file=sys.stderr)
        return 1
    print(f"OK: synced {SRC.name} → {DST.name} (Plesk-ready, no GH prefix)")
    print("Next: commit & push inside site_plesk (branch plesk)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
