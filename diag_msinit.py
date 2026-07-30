# -*- coding: utf-8 -*-
"""Find how MsJs blocks get registered and whether our DOMContentLoaded wrap broke ordering."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t = Path("site_mirror/web-studiya/index.html").read_text(encoding="utf-8")

print("=== occurrences ===")
for probe in ["MsJsPublishedManager", "new MsJsObject", "MsBaseJsObject", "DOMContentLoaded", "storage["]:
    print(f"  {probe!r}: {t.count(probe)}")

print()
print("=== contexts of MsJsPublishedManager ===")
for m in re.finditer(r".{150}MsJsPublishedManager.{200}", t):
    print("  ...", " ".join(m.group(0).split())[:330])
    print("  ---")

print()
print("=== inline scripts wrapped in DOMContentLoaded (our wrap) ===")
for m in re.finditer(r'<script(?![^>]*src)[^>]*>(.{0,120})', t):
    frag = " ".join(m.group(1).split())
    print("  >", frag[:120])
