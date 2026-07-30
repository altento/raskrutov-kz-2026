# -*- coding: utf-8 -*-
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def show(rev):
    r = subprocess.run(["git", "show", rev], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

for rev, label in [
    ("d5bda87:site_mirror/pages/web-studiya.html", "old flat web-studiya.html"),
    ("83afca4:site_mirror/pages/web-studiya.html", "before all fixes (yesterday)"),
]:
    t = show(rev)
    print(f"== {label} ({rev})")
    print("   size KB:", len(t) // 1024)
    for probe in ["Кейсы", "VIP Company", "Верона", "Абсолют", "keysy_sayty", "keysy"]:
        print(f"   {probe!r}:", t.count(probe))
    print()

t = show("65c68d6:site_mirror/web-studiya/index.html")
print("== new web-studiya/index.html @65c68d6")
print("   size KB:", len(t) // 1024)
for probe in ["Кейсы", "VIP Company", "Верона", "Абсолют"]:
    print(f"   {probe!r}:", t.count(probe))
