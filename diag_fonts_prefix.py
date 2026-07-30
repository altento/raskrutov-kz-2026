# -*- coding: utf-8 -*-
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path("site_mirror")

t = (ROOT / "faq/aeo/index.html").read_text(encoding="utf-8")
m = re.search(r".{80}inter_bold\.woff.{40}", t, re.S)
print("faq/aeo woff ctx:", " ".join(m.group(0).split()) if m else "none")
m2 = re.search(r"@font-face[^}]{0,400}", t)
print("font-face:", " ".join(m2.group(0).split())[:420] if m2 else "none")

# what did the OLD page look like? (stub from git history is gone locally; check current stub pages sibling: faq/index.html depth1)
t1 = (ROOT / "faq/index.html").read_text(encoding="utf-8")
m3 = re.search(r".{80}inter_bold\.woff.{30}", t1, re.S)
print("faq/ woff ctx:", " ".join(m3.group(0).split()) if m3 else "none")

# disk checks
for rel in [
    "assets/m-files.cdn1.cc/web/user/fonts/inter/inter_bold.woff",
    "assets/m-files.cdn1.cc/web/user/fonts/inter/inter_bold.ttf",
    "assets/m-files.cdn1.cc/lpfile/d/1/d/d1d22c9a0b75e167f47bc53b44094ea5.svg",
    "assets/m-files.cdn1.cc/lpfile/4/9/5/4959ca5021b91e34f49b1c7b213e4f13.svg",
    "assets/m-files.cdn1.cc/lpfile/8/1/a/81a3fe2ab76d8a7d4df2ea1900ce0265/-/crop/0x0x955x221/-/resize/211/-/scale/x3/-/resize/1920/f.webp",
    "assets/m-files.cdn1.cc/lpfile/8/0/8/808cf00d47e2cab21591bb8ea0db6556/-/crop/0x0x1672x935/-/resize/330/-/resize/1920/f.webp",
]:
    print(("EXISTS " if (ROOT / rel).exists() else "MISSING") , rel[:110])

# what variants exist for 808cf00d and 81a3fe2a
import glob
for h in ["808cf00d47e2cab21591bb8ea0db6556", "81a3fe2ab76d8a7d4df2ea1900ce0265"]:
    hits = [f.as_posix()[12:] for f in ROOT.rglob("*") if h in f.as_posix()]
    print(h[:12], "variants on disk:", len(hits))
    for x in hits[:6]:
        print("   ", x[:130])
