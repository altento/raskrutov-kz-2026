# -*- coding: utf-8 -*-
"""Scoped post-pipeline for /web-studiya/ parent + city hubs."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import wire_lead_forms
import fix_breadcrumbs
import add_schema

BASE = Path(__file__).resolve().parent
ROOT = BASE / "site_mirror" / "web-studiya"
CITIES = [
    "almaty",
    "astana",
    "shymkent",
    "aktau",
    "aktobe",
    "atyrau",
    "karaganda",
    "kokshetau",
    "kostanay",
    "kyzylorda",
    "pavlodar",
    "petropavlovsk",
    "semey",
    "taldykorgan",
    "taraz",
    "turkestan",
    "uralsk",
    "ust-kamenogorsk",
]


def pages() -> list[Path]:
    out = [ROOT / "index.html"]
    for c in CITIES:
        out.append(ROOT / c / "index.html")
    return out


def main() -> int:
    w = b = s = 0
    for p in pages():
        if not p.exists():
            print("MISSING", p)
            continue
        if wire_lead_forms.process_page(p):
            w += 1
            print("wired", p.as_posix())
        if fix_breadcrumbs.process(p):
            b += 1
            print("crumbs", p.as_posix())
        ok = False
        for attempt in range(5):
            try:
                if add_schema.inject(p):
                    s += 1
                    print("schema", p.as_posix())
                ok = True
                break
            except PermissionError:
                time.sleep(0.4 * (attempt + 1))
        if not ok:
            print("SCHEMA FAIL", p.as_posix())
    print(f"done wired={w} crumbs={b} schema={s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
