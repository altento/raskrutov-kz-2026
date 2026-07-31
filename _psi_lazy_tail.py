# -*- coding: utf-8 -*-
from pathlib import Path
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
path = Path("site_mirror/index.html")
html = path.read_text(encoding="utf-8")

hero = html.find('id="9466bf80aa894ca9b20b37b4d9409cc1"')
next_sec = html.find('id="2d69865c', hero)
if hero < 0 or next_sec < 0:
    raise SystemExit("markers missing")

head_part, tail_part = html[:next_sec], html[next_sec:]
n = 0


def add_lazy(m: re.Match) -> str:
    global n
    tag = m.group(0)
    if "loading=" in tag:
        return tag
    n += 1
    if tag.endswith("/>"):
        return tag[:-2] + ' loading="lazy" decoding="async"/>'
    return tag[:-1] + ' loading="lazy" decoding="async">'


tail2 = re.sub(r"<img\b[^>]*>", add_lazy, tail_part, flags=re.I)
html = head_part + tail2
print("added lazy to", n, "below-fold imgs")

old = '<script src="assets/js/lead-forms.js"></script>'
new = '<script src="assets/js/lead-forms.js" defer></script>'
if old in html:
    html = html.replace(old, new, 1)
    print("lead-forms.js deferred")
elif new in html:
    print("lead-forms already deferred")
else:
    print("lead-forms tag not found")

tmp = path.with_suffix(".html.tmp")
tmp.write_bytes(html.encode("utf-8"))
tmp.replace(path)
print("ok")
