import re
from pathlib import Path

h = Path(r"C:\Users\user\Projects\раскрутов\site_mirror\index.html").read_text(encoding="utf-8")
for m in re.finditer(r'<a class="home-sub-link"[^>]*>.*?</a>', h):
    if "Лендинг" in m.group(0) or "landing" in m.group(0):
        print(m.group(0)[:300])

print("landing original urls:", len(re.findall(r"sozdanie-saitov/landing", h)))
