# -*- coding: utf-8 -*-
"""Normalize ANY number of ../ before assets/ and favicon.ico to the correct depth prefix."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")
mapping = json.loads(Path("url_mapping.json").read_text(encoding="utf-8"))

ASSETS_ANY = re.compile(r"(?<![\w/.-])(?:\.\./)+assets/")
FAV_ANY = re.compile(r"(?<![\w/.-])(?:\.\./)+favicon\.ico")

tot_a = tot_f = 0
per_depth = {}
for beaut in mapping.values():
    p = ROOT / beaut / "index.html"
    prefix = "../" * (beaut.count("/") + 1)
    t = p.read_text(encoding="utf-8")
    t, n1 = ASSETS_ANY.subn(prefix + "assets/", t)
    t, n2 = FAV_ANY.subn(prefix + "favicon.ico", t)
    tot_a += n1
    tot_f += n2
    if n1 or n2:
        per_depth.setdefault(beaut.count("/") + 1, [0, 0])
        per_depth[beaut.count("/") + 1][0] += n1
        per_depth[beaut.count("/") + 1][1] += n2
        p.write_text(t, encoding="utf-8")

print("assets refs normalized:", tot_a, " favicon:", tot_f)
print("by depth:", per_depth)
