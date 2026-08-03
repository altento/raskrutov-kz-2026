# -*- coding: utf-8 -*-
"""Extract + split Mottor CSS on sozdanie-saitov parent + geo pages."""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("site_mirror")
CSS_DIR = ROOT / "assets" / "css"
PARENT = ROOT / "web-studiya" / "sozdanie-saitov" / "index.html"
HERO = "1928a98fbb6447c7bb1413d2b56c3267"
LCP_IMG = "a48f76b29b68f1c814592122216e6e86.webp"

CITIES = [
    "almaty", "astana", "shymkent", "aktau", "aktobe", "atyrau", "karaganda",
    "kokshetau", "kostanay", "kyzylorda", "pavlodar", "petropavlovsk", "semey",
    "taldykorgan", "taraz", "turkestan", "uralsk", "ust-kamenogorsk",
]


def split_rules(css: str) -> list[str]:
    rules: list[str] = []
    i, n = 0, len(css)
    while i < n:
        while i < n and css[i].isspace():
            i += 1
        if i >= n:
            break
        start = i
        while i < n and css[i] != "{":
            i += 1
        if i >= n:
            break
        depth = 0
        while i < n:
            if css[i] == "{":
                depth += 1
            elif css[i] == "}":
                depth -= 1
                if depth == 0:
                    i += 1
                    rules.append(css[start:i].strip())
                    break
            i += 1
    return rules


def collect_critical_ids(html: str) -> set[str]:
    ids: set[str] = {HERO}
    # hero section chunk until next blk_section
    m = re.search(rf'\bid="{HERO}"', html)
    if not m:
        raise SystemExit("hero id missing")
    # next section after hero
    rest = html[m.start() :]
    nexts = list(re.finditer(r'class="[^"]*blk_section[^"]*"[^>]*\bid="([0-9a-f]{32})"|id="([0-9a-f]{32})"[^>]*class="[^"]*blk_section', rest))
    # first is hero itself possibly; take span to 2nd section
    end = len(rest)
    for mm in nexts:
        sid = mm.group(1) or mm.group(2)
        if sid != HERO:
            end = mm.start()
            break
    chunk = rest[: max(end, 60000)]
    ids.update(re.findall(r'\bid="([0-9a-f]{32})"', chunk))
    # menus: fixed / ms-menu
    for mm in re.finditer(
        r'id="([0-9a-f]{32})"[^>]{0,200}(?:ms-menu|menu-bar|is_fixed)|(?:ms-menu|menu-bar|is_fixed)[^>]{0,200}id="([0-9a-f]{32})"',
        html,
        re.I,
    ):
        ids.add(mm.group(1) or mm.group(2))
    # also common menu wrapper nearby
    for mid in list(ids):
        pos = html.find(f'id="{mid}"')
        if pos >= 0:
            ids.update(re.findall(r'\bid="([0-9a-f]{32})"', html[max(0, pos - 500) : pos + 25000]))
    return ids


def rule_is_critical(rule: str, ids: set[str]) -> bool:
    if re.search(
        r"mockup|ms-menu|site_wrapper|blk_section_inner|is_fixed|section-image|section_image|menu-bar|font-face|@font-face",
        rule,
        re.I,
    ):
        return True
    for i in ids:
        if i in rule:
            return True
        if len(i) == 32 and i[0].isdigit():
            # CSS escape form #\30 xxx
            if i[1:10] in rule and ("\\" in rule or "#" in rule):
                # loose match for escaped id
                if i[1:8] in rule:
                    return True
    return False


def normalize_css_urls(css: str) -> str:
    """Rewrite ../../assets or ../../../assets → ../ (from assets/css/)."""
    css = re.sub(r"url\((['\"]?)\.\./\.\./\.\./assets/", r"url(\1../", css)
    css = re.sub(r"url\((['\"]?)\.\./\.\./assets/", r"url(\1../", css)
    css = re.sub(r"url\((['\"]?)/assets/", r"url(\1../", css)
    return css


def extract_style(html: str, style_id: str) -> str | None:
    m = re.search(rf'<style id="{re.escape(style_id)}">(.*?)</style>', html, re.S)
    return m.group(1) if m else None


def remove_style(html: str, style_id: str) -> str:
    return re.sub(rf'\s*<style id="{re.escape(style_id)}">.*?</style>', "", html, count=1, flags=re.S)


def asset_prefix(depth: int) -> str:
    return "../" * depth + "assets/"


def page_depth(path: Path) -> int:
    # site_mirror/web-studiya/sozdanie-saitov/index.html → 2
    # site_mirror/web-studiya/sozdanie-saitov/astana/index.html → 3
    rel = path.relative_to(ROOT)
    return len(rel.parts) - 1


def wire_page(html: str, depth: int) -> str:
    prefix = asset_prefix(depth)

    # Drop old sozdanie css wiring if re-run
    html = re.sub(
        r'<link[^>]+href="[^"]*assets/css/sozdanie-[^"]+"[^>]*>\s*',
        "",
        html,
    )
    html = re.sub(
        r'<noscript><link rel="stylesheet" href="[^"]*assets/css/sozdanie-[^"]+"></noscript>\s*',
        "",
        html,
    )

    # Reduce font preloads: keep only montserrat bold (prefer woff2 if present later)
    # Remove inter / open_sans / montserrat normal+medium preloads
    html = re.sub(
        r'<link rel="preload" href="[^"]*/fonts/(?:inter|open_sans)/[^"]+"[^>]*>\s*',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'<link rel="preload" href="[^"]*/fonts/montserrat/montserrat_(?:normal|medium)\.woff[^"]*"[^>]*>\s*',
        "",
        html,
        flags=re.I,
    )

    # Drop preload of public.bundle.css (stylesheet remains sync — like stage2 home)
    html = re.sub(
        r'<link rel="preload" as="style" href="[^"]*public\.bundle[^"]*\.css"[^>]*>\s*',
        "",
        html,
    )

    # Ensure LCP image preload exists once
    if LCP_IMG not in html.split("</head>")[0] or 'rel="preload"' not in html.split(LCP_IMG)[0][-200:]:
        pass  # already has preload typically

    # Inject CSS links after charset/meta area — right after <head...>
    preload_crit = f'<link rel="preload" as="style" href="{prefix}css/sozdanie-critical.v1.css"/>'
    preload_popup = f'<link rel="preload" as="style" href="{prefix}css/sozdanie-popup-menu.v1.css"/>'
    links = (
        f'{preload_crit}{preload_popup}'
        f'<link rel="stylesheet" href="{prefix}css/sozdanie-popup-menu.v1.css"/>'
        f'<link rel="stylesheet" href="{prefix}css/sozdanie-critical.v1.css"/>'
        f'<link rel="stylesheet" href="{prefix}css/sozdanie-deferred.v1.css" media="print" onload="this.media=\'all\'">'
        f'<noscript><link rel="stylesheet" href="{prefix}css/sozdanie-deferred.v1.css"></noscript>'
        f'<link rel="stylesheet" href="{prefix}css/sozdanie-popup-other.v1.css" media="print" onload="this.media=\'all\'">'
        f'<noscript><link rel="stylesheet" href="{prefix}css/sozdanie-popup-other.v1.css"></noscript>'
    )
    html = re.sub(r"(<head[^>]*>)", r"\1" + links, html, count=1, flags=re.I)

    # Hero CLS reserve (idempotent)
    if 'data-sozdanie-hero-reserve' not in html:
        reserve = (
            f'<style data-sozdanie-hero-reserve="1">'
            f'#{HERO} .section_image_container,[data-id="s-{HERO}"] .section_image_container{{min-height:280px;}}'
            f'@media (max-width:500px){{#{HERO} .section_image_container,[data-id="s-{HERO}"] .section_image_container{{min-height:320px;}}}}'
            f"</style>"
        )
        html = html.replace("</head>", reserve + "</head>", 1)

    # Un-lazy any img that is the LCP preload target
    html = re.sub(
        rf'(<img\b[^>]*src="[^"]*{re.escape(LCP_IMG)}"[^>]*?)\s*loading="lazy"',
        r'\1 loading="eager" fetchpriority="high"',
        html,
        count=1,
        flags=re.I,
    )
    # If LCP is CSS background only, leave preload as-is

    # Lazy-load third-party video player scripts (same pattern as homepage)
    if "data-rk-video-lazy" not in html:
        html = re.sub(
            r"<script([^>]*\bid=['\"]ms-(?:vk|kinescope|vimeo|youtube)-script['\"][^>]*)>",
            lambda m: m.group(0).replace("<script", "<script type=\"text/plain\" data-rk-video-src-hold", 1)
            if "src=" in m.group(0)
            else m.group(0),
            html,
            flags=re.I,
        )
        # Better: convert src scripts to data-src
        def hold_video(m: re.Match) -> str:
            tag = m.group(0)
            if "data-rk-video" in tag:
                return tag
            src_m = re.search(r'\ssrc=(["\'])([^"\']+)\1', tag)
            if not src_m:
                return tag
            src = src_m.group(2)
            if not any(k in src for k in ("youtube", "vimeo", "kinescope", "vk.com/js")):
                return tag
            tag2 = re.sub(r'\ssrc=(["\'])([^"\']+)\1', r' data-rk-video-src=\1\2\1', tag, count=1)
            if "type=" not in tag2:
                tag2 = tag2.replace("<script", '<script type="text/plain"', 1)
            return tag2

        html = re.sub(r"<script\b[^>]*>", hold_video, html, flags=re.I)
        boot = (
            '<script data-rk-video-lazy="1">(function(){function boot(){var ns=document.querySelectorAll("script[data-rk-video-src]");'
            "for(var i=0;i<ns.length;i++){var o=ns[i],s=document.createElement('script');s.src=o.getAttribute('data-rk-video-src');"
            "if(o.id)s.id=o.id;if(o.className)s.className=o.className;o.parentNode.insertBefore(s,o);o.parentNode.removeChild(o);}}"
            "function arm(){if(!('IntersectionObserver' in window)){boot();return;}var io=new IntersectionObserver(function(es){"
            "for(var i=0;i<es.length;i++){if(es[i].isIntersecting){io.disconnect();boot();break;}}},{rootMargin:'400px'});"
            "var nodes=document.querySelectorAll('.blk_video, .video, [data-video], iframe');if(!nodes.length){setTimeout(boot,4000);return;}"
            "for(var j=0;j<nodes.length;j++)io.observe(nodes[j]);}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',arm);else arm();})();</script>"
        )
        html = html.replace("</body>", boot + "</body>", 1) if "</body>" in html else html + boot

    return html


def main() -> int:
    parent_html = PARENT.read_text(encoding="utf-8")
    ids = collect_critical_ids(parent_html)
    print("critical ids", len(ids))

    all_blocks = extract_style(parent_html, "all_blocks-style")
    pop_menu = extract_style(parent_html, "sp-2782231__blocks-style")
    pop_other = extract_style(parent_html, "sp-2773676__blocks-style")
    if not all_blocks or not pop_menu or not pop_other:
        raise SystemExit("missing style blocks")

    all_blocks = normalize_css_urls(all_blocks)
    pop_menu = normalize_css_urls(pop_menu)
    pop_other = normalize_css_urls(pop_other)

    rules = split_rules(all_blocks)
    crit, rest = [], []
    for r in rules:
        (crit if rule_is_critical(r, ids) else rest).append(r)
    crit_css = "/* sozdanie critical v1 */\n" + "".join(crit)
    def_css = "/* sozdanie deferred v1 */\n" + "".join(rest)

    CSS_DIR.mkdir(parents=True, exist_ok=True)
    (CSS_DIR / "sozdanie-critical.v1.css").write_text(crit_css, encoding="utf-8")
    (CSS_DIR / "sozdanie-deferred.v1.css").write_text(def_css, encoding="utf-8")
    (CSS_DIR / "sozdanie-popup-menu.v1.css").write_text(
        "/* sozdanie popup menu (mobile) — blocking */\n" + pop_menu, encoding="utf-8"
    )
    (CSS_DIR / "sozdanie-popup-other.v1.css").write_text(
        "/* sozdanie popup other — deferred */\n" + pop_other, encoding="utf-8"
    )
    print(
        f"critical {len(crit_css.encode())/1024:.1f} KiB / deferred {len(def_css.encode())/1024:.1f} KiB / "
        f"menu {len(pop_menu.encode())/1024:.1f} / other {len(pop_other.encode())/1024:.1f}"
    )

    pages = [PARENT] + [ROOT / "web-studiya" / "sozdanie-saitov" / c / "index.html" for c in CITIES]
    for path in pages:
        if not path.exists():
            print("SKIP missing", path)
            continue
        html = path.read_text(encoding="utf-8")
        # remove extracted style tags
        for sid in ("all_blocks-style", "sp-2782231__blocks-style", "sp-2773676__blocks-style"):
            html = remove_style(html, sid)
        depth = page_depth(path)
        html = wire_page(html, depth)
        path.write_text(html, encoding="utf-8")
        head = html[: html.find("</head>")]
        print(
            "OK",
            path.relative_to(ROOT).as_posix(),
            f"head={len(head.encode())/1024:.1f}KiB",
            "depth",
            depth,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
