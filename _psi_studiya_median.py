# -*- coding: utf-8 -*-
"""PSI mobile x5 for /web-studiya/ -> median score + metrics.

Anonymous quota: expect occasional 429, we back off and report how many runs
actually landed. Never invent numbers for failed runs.
"""
from __future__ import annotations

import json
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://raskrutov.kz/web-studiya/"
API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
STRATEGY = "mobile"
RUNS = 5
GAP_SEC = 12

METRICS = {
    "first-contentful-paint": "FCP",
    "largest-contentful-paint": "LCP",
    "total-blocking-time": "TBT",
    "cumulative-layout-shift": "CLS",
    "speed-index": "SI",
}

OUT_DIR = Path("reports/web-studiya-clean")


def fetch(retries: int = 4) -> dict:
    qs = urllib.parse.urlencode(
        {"url": URL, "strategy": STRATEGY, "category": "performance"}
    )
    req = urllib.request.Request(
        API + "?" + qs, headers={"User-Agent": "RaskrutovPSI/1.0"}
    )
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:200]
            last = f"HTTP {e.code}: {body}"
            print(f"    retry {i + 1}/{retries}: {last}", flush=True)
            if e.code in (429, 500, 503):
                time.sleep(20 * (i + 1))
                continue
            raise
        except Exception as e:  # noqa: BLE001
            last = str(e)
            print(f"    retry {i + 1}/{retries}: {last}", flush=True)
            time.sleep(10 * (i + 1))
    raise RuntimeError(last or "unknown")


def summarize(data: dict) -> dict:
    lh = data["lighthouseResult"]
    audits = lh["audits"]
    row = {"score": round((lh["categories"]["performance"]["score"] or 0) * 100)}
    for aid, label in METRICS.items():
        a = audits.get(aid) or {}
        row[label] = a.get("numericValue")
        row[label + "_disp"] = a.get("displayValue")
    lcp_el = (audits.get("largest-contentful-paint-element") or {}).get("details") or {}
    items = lcp_el.get("items") or []
    if items:
        sub = (items[0].get("items") or [{}])[0]
        row["lcp_element"] = sub.get("node", {}).get("selector") or sub.get("node", {}).get("snippet")
    return row


def main() -> int:
    runs: list[dict] = []
    failures: list[str] = []
    for i in range(RUNS):
        print(f"=== run {i + 1}/{RUNS} ===", flush=True)
        try:
            row = summarize(fetch())
            runs.append(row)
            print(
                f"  score={row['score']}  FCP={row.get('FCP_disp')}  LCP={row.get('LCP_disp')}"
                f"  TBT={row.get('TBT_disp')}  CLS={row.get('CLS_disp')}  SI={row.get('SI_disp')}",
                flush=True,
            )
        except Exception as e:  # noqa: BLE001
            failures.append(f"run {i + 1}: {e}")
            print(f"  FAILED: {e}", flush=True)
        if i < RUNS - 1:
            time.sleep(GAP_SEC)

    if not runs:
        print("\nALL RUNS FAILED — no numbers to report.", flush=True)
        for f in failures:
            print("  " + f, flush=True)
        return 1

    scores = sorted(r["score"] for r in runs)
    med = {
        "url": URL,
        "strategy": STRATEGY,
        "runs_ok": len(runs),
        "runs_failed": len(failures),
        "scores": scores,
        "score_median": statistics.median(scores),
        "score_min": scores[0],
        "score_max": scores[-1],
        "failures": failures,
    }
    for label in METRICS.values():
        vals = [r[label] for r in runs if r.get(label) is not None]
        if vals:
            med[label + "_median"] = statistics.median(vals)
    med["lcp_elements"] = sorted({r.get("lcp_element") for r in runs if r.get("lcp_element")})

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "psi-mobile-median.json").write_text(
        json.dumps({"median": med, "runs": runs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n===== MEDIAN (mobile) =====", flush=True)
    print(f"URL: {URL}", flush=True)
    print(f"runs ok: {len(runs)}/{RUNS}  failed: {len(failures)}", flush=True)
    print(f"scores: {scores}", flush=True)
    print(f"MEDIAN SCORE: {med['score_median']}  (min {med['score_min']} / max {med['score_max']})", flush=True)
    print(f"FCP {med.get('FCP_median', 0) / 1000:.2f}s | LCP {med.get('LCP_median', 0) / 1000:.2f}s "
          f"| TBT {med.get('TBT_median', 0):.0f}ms | CLS {med.get('CLS_median', 0):.3f} "
          f"| SI {med.get('SI_median', 0) / 1000:.2f}s", flush=True)
    print(f"LCP element(s): {med['lcp_elements']}", flush=True)
    for f in failures:
        print("  FAIL " + f, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
