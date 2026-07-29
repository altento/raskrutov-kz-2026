#!/usr/bin/env python3
from pathlib import Path
js = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\assets\m-files.cdn1.cc\web\build\pages\public.bundle__q_v_1784122069.js").read_text(encoding="utf-8", errors="ignore")
i = js.find("document.write")
print("context around document.write:")
print(js[max(0, i-300): i+300])
i2 = js.find("runOnObjectReady")
print("\ncontext around runOnObjectReady definition:")
print(js[max(0, i2-200): i2+200])
