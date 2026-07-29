#!/usr/bin/env python3
"""Lazy-load Yandex Maps: trap api-maps script injection until the map block
is near the viewport (IntersectionObserver, rootMargin 900px, 15s safety net).

Why: the builder bundle (deferred) eagerly loads ~600KB of ymaps API + tiles at
DOMContentLoaded even though the map sits at the bottom of the page, competing
for slow-4G bandwidth with LCP resources and adding main-thread work.

The guard is a plain inline script placed BEFORE the deferred bundle tag, so it
executes during HTML parsing and installs an HTMLScriptElement.src trap before
the bundle ever runs. Pages without .blk_yandex_map release immediately (no-op).
Idempotent: skips pages already containing data-lazy-ymaps.
"""
import re
from pathlib import Path

M = Path(r"C:\Users\user\Projects\раскрутов\site_mirror")

BUNDLE_RE = re.compile(
    r'(<script src="(?:\.\./)*assets/m-files\.cdn1\.cc/web/build/pages/public\.bundle[^"]*\.js" type="text/javascript" defer></script>)'
)

GUARD = """<script data-lazy-ymaps="raskrutov">(function(){if(!('IntersectionObserver' in window))return;var armed=true;var KEY='api-maps.yandex';var registry=[];var origAppend=Node.prototype.appendChild;var origInsert=Node.prototype.insertBefore;function held(n){if(!n||n.tagName!=='SCRIPT')return false;var u=(n.src||'')+((n.getAttribute&&n.getAttribute('src'))||'');return u.indexOf(KEY)!==-1;}Node.prototype.appendChild=function(n){if(armed&&held(n)){registry.push({p:this,n:n});return n;}return origAppend.call(this,n);};Node.prototype.insertBefore=function(n,r){if(armed&&held(n)){registry.push({p:this,n:n,r:r});return n;}return origInsert.call(this,n,r);};function release(){if(!armed)return;armed=false;var seen={};for(var i=0;i<registry.length;i++){var it=registry[i];var u=it.n.src||it.n.getAttribute('src');if(seen[u])continue;seen[u]=1;if(it.r){origInsert.call(it.p,it.n,it.r);}else{origAppend.call(it.p,it.n);}}registry=[];}function attach(t){var io=new IntersectionObserver(function(es){for(var i=0;i<es.length;i++){if(es[i].isIntersecting){io.disconnect();release();break;}}},{rootMargin:'900px'});io.observe(t);}document.addEventListener('DOMContentLoaded',function(){setTimeout(release,45000);var tries=0;var iv=setInterval(function(){tries++;var t=document.querySelector('.blk_yandex_map');if(!t){clearInterval(iv);release();return;}var top=t.getBoundingClientRect().top+window.scrollY;if(top>2500){clearInterval(iv);attach(t);}else if(tries>=20){clearInterval(iv);release();}},500);});})();</script>"""

files_changed = 0
guards_added = 0
for f in sorted(M.rglob("*.html")):
    rel = f.relative_to(M)
    if "assets" in rel.parts:
        continue
    html = f.read_text(encoding="utf-8", errors="ignore")
    if 'data-lazy-ymaps' in html:
        continue
    new, n = BUNDLE_RE.subn(GUARD + r"\1", html, count=1)
    if n:
        f.write_text(new, encoding="utf-8")
        files_changed += 1
        guards_added += 1

print(f"files changed: {files_changed}, lazy-ymaps guards added: {guards_added}")

# sanity: pages with actual map blocks
maps = 0
for f in sorted(M.rglob("*.html")):
    rel = f.relative_to(M)
    if "assets" in rel.parts:
        continue
    if 'blk_yandex_map' in f.read_text(encoding="utf-8", errors="ignore"):
        maps += 1
print(f"pages containing blk_yandex_map: {maps}")
