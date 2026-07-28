#!/usr/bin/env python3
import argparse
import json
import mimetypes
import posixpath
import re
import sys
import time
from collections import deque
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

TEXT_EXTENSIONS = {
    ".css",
    ".js",
    ".json",
    ".svg",
    ".txt",
    ".xml",
    ".html",
    ".htm",
    ".map",
}
DOWNLOADABLE_EXTENSIONS = {
    ".css",
    ".js",
    ".json",
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".avif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
    ".mp4",
    ".webm",
    ".mp3",
    ".pdf",
}

HTML_PAGE_EXTENSIONS = {"", ".html", ".htm", ".php", ".asp", ".aspx", ".jsp"}
ASSET_ATTRS = [
    "src",
    "href",
    "srcset",
    "poster",
    "content",
    "data-src",
    "data-srcset",
    "data-lazy-src",
    "data-lazy-srcset",
    "data-bg",
    "data-background",
    "data-bg-src",
    "data-original",
    "data-url",
    "data-image",
    "data-thumb",
    "data-thumb-src",
    "data-fancybox",
    "data-page-link",
    "action",
]

ATTR_PATTERN_TEMPLATE = r"""(?P<prefix>\b{attr}\s*=\s*)(?P<quote>["'])(?P<value>.*?)(?P=quote)"""
CSS_URL_PATTERN = re.compile(r"""url\(\s*(?P<quote>["']?)(?P<url>[^)"']+)(?P=quote)\s*\)""", re.I)
CSS_IMPORT_PATTERN = re.compile(r"""@import\s+(?:url\()?["']?(?P<url>[^)"';]+)""", re.I)
JS_URL_PATTERN = re.compile(
    r"""(?P<quote>["'])(?P<url>(?:https?:)?\/\/[^"'\\]+|\/[^"'\\]+)(?P=quote)""",
    re.I,
)


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def strip_fragment(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))


def is_ignorable_url(url: str) -> bool:
    if not url:
        return True
    lowered = url.strip().lower()
    return (
        lowered.startswith("#")
        or lowered.startswith("javascript:")
        or lowered.startswith("mailto:")
        or lowered.startswith("tel:")
        or lowered.startswith("data:")
        or lowered.startswith("blob:")
    )


def looks_like_resource_url(url: str) -> bool:
    if not url:
        return False
    probe = unescape(url.strip())
    if is_ignorable_url(probe):
        return False
    if any(ch.isspace() for ch in probe):
        return False
    if probe.startswith(("http://", "https://", "//")):
        return True
    if probe.startswith(("/", "./", "../")):
        return True
    return False


def normalize_url(raw_url: str, base_url: str) -> str:
    raw_url = unescape(raw_url.strip())
    if raw_url.startswith("//"):
        parsed_base = urlsplit(base_url)
        return f"{parsed_base.scheme}:{raw_url}"
    return urljoin(base_url, raw_url)


def guess_extension(url: str, content_type: str, current_ext: str) -> str:
    if current_ext:
        return current_ext
    if content_type:
        mime = content_type.split(";")[0].strip().lower()
        ext = mimetypes.guess_extension(mime)
        if ext:
            return ext
    return ".bin"


def sanitized_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


class SiteMirror:
    def __init__(self, start_url: str, output_dir: Path, max_pages: int = 40):
        self.start_url = strip_fragment(start_url)
        self.output_dir = output_dir
        self.assets_dir = self.output_dir / "assets"
        self.pages_dir = self.output_dir / "pages"
        self.max_pages = max_pages
        self.host = urlsplit(self.start_url).netloc
        self.scheme = urlsplit(self.start_url).scheme

        self.mapping = {}
        self.reverse_mapping = {}
        self.failures = []
        self.downloaded = set()
        self.page_queue = deque([self.start_url])
        self.page_seen = set()
        self.pages_written = []

    def fetch(self, url: str):
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=45) as response:
            raw = response.read()
            headers = {k.lower(): v for k, v in response.headers.items()}
            content_type = headers.get("content-type", "")
            final_url = response.geturl()
            return final_url, raw, content_type, headers

    def local_path_for_url(self, url: str, content_type: str = "") -> Path:
        parsed = urlsplit(url)
        host = sanitized_name(parsed.netloc or self.host)
        path = parsed.path or "/"
        if path.endswith("/"):
            path = path + "index.html"

        pure = Path(path.lstrip("/"))
        suffix = pure.suffix.lower()
        if not suffix:
            suffix = guess_extension(url, content_type, "")
            if suffix in {".html", ".htm"}:
                pure = pure / "index.html"
            else:
                pure = pure.with_suffix(suffix)

        if parsed.query:
            stem = pure.stem
            query_hash = sanitized_name(parsed.query)[:80]
            pure = pure.with_name(f"{stem}__q_{query_hash}{pure.suffix}")

        return Path("assets") / host / pure

    def page_local_path(self, url: str) -> Path:
        parsed = urlsplit(strip_fragment(url))
        rel = parsed.path.strip("/")
        if not rel:
            return Path("index.html")
        rel = rel.replace("/", "_")
        if parsed.query:
            rel = f"{rel}__q_{sanitized_name(parsed.query)[:80]}"
        if not rel.endswith((".html", ".htm")):
            rel = f"{rel}.html"
        return Path("pages") / rel

    def queue_page_if_needed(self, url: str) -> None:
        clean = strip_fragment(url)
        if not self.should_queue_page(clean):
            return
        if clean in self.page_seen or clean in self.page_queue:
            return
        if len(self.page_seen) + len(self.page_queue) >= self.max_pages:
            return
        self.page_queue.append(clean)

    def relative_ref(self, from_file: Path, target_file: Path) -> str:
        return posixpath.relpath(target_file.as_posix(), start=from_file.parent.as_posix())

    def should_queue_page(self, url: str) -> bool:
        parsed = urlsplit(url)
        if parsed.netloc != self.host:
            return False
        suffix = Path(parsed.path).suffix.lower()
        return suffix in HTML_PAGE_EXTENSIONS

    def should_download_from_js(self, raw_url: str, base_url: str) -> bool:
        if not looks_like_resource_url(raw_url):
            return False
        absolute = strip_fragment(normalize_url(raw_url, base_url))
        parsed = urlsplit(absolute)
        suffix = Path(parsed.path).suffix.lower()
        if parsed.netloc == self.host:
            return True
        return suffix in DOWNLOADABLE_EXTENSIONS

    def download_binary_or_text(self, url: str) -> Path | None:
        clean_url = strip_fragment(url)
        if clean_url in self.downloaded:
            return self.mapping.get(clean_url)
        try:
            final_url, raw, content_type, _headers = self.fetch(clean_url)
            local_path = self.local_path_for_url(final_url, content_type)
            absolute_local = self.output_dir / local_path
            ensure_dir(absolute_local)

            suffix = absolute_local.suffix.lower()
            if suffix in TEXT_EXTENSIONS or content_type.startswith("text/"):
                text = raw.decode("utf-8", errors="ignore")
                if suffix == ".css" or "text/css" in content_type:
                    text = self.rewrite_css_like(text, final_url, local_path)
                elif suffix == ".js" or "javascript" in content_type or "json" in content_type:
                    text = self.rewrite_js_like(text, final_url, local_path)
                absolute_local.write_text(text, encoding="utf-8")
            else:
                absolute_local.write_bytes(raw)

            self.downloaded.add(clean_url)
            self.mapping[clean_url] = local_path
            self.reverse_mapping[local_path.as_posix()] = clean_url
            return local_path
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            self.failures.append({"url": clean_url, "error": str(exc)})
            return None

    def rewrite_srcset_value(self, value: str, base_url: str, current_file: Path) -> str:
        parts = []
        for chunk in [p.strip() for p in value.split(",") if p.strip()]:
            segments = chunk.split()
            if not segments:
                continue
            candidate = segments[0]
            if is_ignorable_url(candidate):
                parts.append(chunk)
                continue
            absolute = strip_fragment(normalize_url(candidate, base_url))
            local = self.download_binary_or_text(absolute)
            if local:
                segments[0] = self.relative_ref(current_file, local)
            parts.append(" ".join(segments))
        return ", ".join(parts)

    def rewrite_css_like(self, text: str, base_url: str, current_file: Path) -> str:
        def repl_url(match):
            raw = match.group("url").strip()
            if is_ignorable_url(raw):
                return match.group(0)
            absolute = strip_fragment(normalize_url(raw, base_url))
            local = self.download_binary_or_text(absolute)
            if not local:
                return match.group(0)
            quote = match.group("quote") or ""
            relative = self.relative_ref(current_file, local)
            return f"url({quote}{relative}{quote})"

        def repl_import(match):
            raw = match.group("url").strip()
            if is_ignorable_url(raw):
                return match.group(0)
            absolute = strip_fragment(normalize_url(raw, base_url))
            local = self.download_binary_or_text(absolute)
            if not local:
                return match.group(0)
            relative = self.relative_ref(current_file, local)
            return match.group(0).replace(raw, relative)

        text = CSS_URL_PATTERN.sub(repl_url, text)
        text = CSS_IMPORT_PATTERN.sub(repl_import, text)
        return text

    def rewrite_js_like(self, text: str, base_url: str, current_file: Path) -> str:
        def repl_js(match):
            raw = match.group("url")
            if not self.should_download_from_js(raw, base_url):
                return match.group(0)
            absolute = strip_fragment(normalize_url(raw, base_url))
            local = self.download_binary_or_text(absolute)
            if not local:
                return match.group(0)
            quote = match.group("quote")
            relative = self.relative_ref(current_file, local)
            return f"{quote}{relative}{quote}"

        return JS_URL_PATTERN.sub(repl_js, text)

    def rewrite_html(self, html_text: str, page_url: str, page_file: Path) -> str:
        for attr in ASSET_ATTRS:
            pattern = re.compile(ATTR_PATTERN_TEMPLATE.format(attr=re.escape(attr)), re.I | re.S)

            def attr_repl(match):
                raw = match.group("value").strip()
                if is_ignorable_url(raw):
                    return match.group(0)

                if attr == "content" and not looks_like_resource_url(raw):
                    return match.group(0)

                if attr in {"href", "data-page-link"}:
                    absolute = strip_fragment(normalize_url(raw, page_url))
                    if self.should_queue_page(absolute):
                        self.queue_page_if_needed(absolute)
                        relative = self.relative_ref(page_file, self.page_local_path(absolute))
                        return f"{match.group('prefix')}{match.group('quote')}{relative}{match.group('quote')}"

                    parsed = urlsplit(absolute)
                    if parsed.scheme in {"http", "https"}:
                        local = self.download_binary_or_text(absolute)
                        if local:
                            relative = self.relative_ref(page_file, local)
                            return f"{match.group('prefix')}{match.group('quote')}{relative}{match.group('quote')}"
                        return match.group(0)

                if attr == "srcset" or attr.endswith("srcset"):
                    rewritten = self.rewrite_srcset_value(raw, page_url, page_file)
                    return f"{match.group('prefix')}{match.group('quote')}{rewritten}{match.group('quote')}"

                absolute = strip_fragment(normalize_url(raw, page_url))
                local = self.download_binary_or_text(absolute)
                if not local:
                    return match.group(0)
                relative = self.relative_ref(page_file, local)
                return f"{match.group('prefix')}{match.group('quote')}{relative}{match.group('quote')}"

            html_text = pattern.sub(attr_repl, html_text)

        style_attr_pattern = re.compile(r"""(?P<prefix>\bstyle\s*=\s*)(?P<quote>["'])(?P<value>.*?)(?P=quote)""", re.I | re.S)

        def style_repl(match):
            rewritten = self.rewrite_css_like(match.group("value"), page_url, page_file)
            return f"{match.group('prefix')}{match.group('quote')}{rewritten}{match.group('quote')}"

        html_text = style_attr_pattern.sub(style_repl, html_text)

        style_block_pattern = re.compile(r"(<style[^>]*>)(.*?)(</style>)", re.I | re.S)

        def style_block_repl(match):
            rewritten = self.rewrite_css_like(match.group(2), page_url, page_file)
            return f"{match.group(1)}{rewritten}{match.group(3)}"

        html_text = style_block_pattern.sub(style_block_repl, html_text)

        script_block_pattern = re.compile(r"(<script\b(?![^>]*\bsrc=)[^>]*>)(.*?)(</script>)", re.I | re.S)

        def script_repl(match):
            rewritten = self.rewrite_js_like(match.group(2), page_url, page_file)
            return f"{match.group(1)}{rewritten}{match.group(3)}"

        html_text = script_block_pattern.sub(script_repl, html_text)

        html_text = html_text.replace('href="//', f'href="{self.scheme}://')
        html_text = html_text.replace("href='//", f"href='{self.scheme}://")
        html_text = html_text.replace('src="//', f'src="{self.scheme}://')
        html_text = html_text.replace("src='//", f"src='{self.scheme}://")
        return html_text

    def mirror_page(self, page_url: str) -> None:
        clean_page = strip_fragment(page_url)
        if clean_page in self.page_seen:
            return
        self.page_seen.add(clean_page)

        try:
            final_url, raw, _content_type, _headers = self.fetch(clean_page)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            self.failures.append({"url": clean_page, "error": str(exc)})
            return

        html_text = raw.decode("utf-8", errors="ignore")
        page_file = self.page_local_path(final_url)
        rewritten = self.rewrite_html(html_text, final_url, page_file)
        destination = self.output_dir / page_file
        ensure_dir(destination)
        destination.write_text(rewritten, encoding="utf-8")
        self.pages_written.append(page_file.as_posix())
        self.mapping[clean_page] = page_file
        self.reverse_mapping[page_file.as_posix()] = clean_page

    def run(self) -> dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        while self.page_queue and len(self.page_seen) < self.max_pages:
            self.mirror_page(self.page_queue.popleft())

        report = {
            "generatedAt": now(),
            "startUrl": self.start_url,
            "outputDir": str(self.output_dir),
            "pagesWritten": self.pages_written,
            "downloadedCount": len(self.downloaded),
            "mappedCount": len(self.mapping),
            "failureCount": len(self.failures),
            "failures": self.failures,
        }
        (self.output_dir / "asset_manifest.json").write_text(
            json.dumps({k: v.as_posix() for k, v in self.mapping.items()}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.output_dir / "mirror_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror a page and its assets locally.")
    parser.add_argument("--url", default="https://raskrutov.kz/", help="Page URL to mirror")
    parser.add_argument("--output", default="site_mirror", help="Output directory")
    parser.add_argument("--max-pages", type=int, default=100, help="Maximum same-origin HTML pages to mirror")
    parser.add_argument(
        "--crawl-all",
        action="store_true",
        help="Mirror all discovered same-origin HTML pages up to --max-pages",
    )
    args = parser.parse_args()

    output_dir = Path(args.output).resolve()
    max_pages = args.max_pages if args.crawl_all else 1
    mirror = SiteMirror(args.url, output_dir, max_pages=max_pages)
    report = mirror.run()

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["failureCount"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
