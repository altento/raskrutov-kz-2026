# Full link audit — Raskrutov.kz

- Content pages checked: **75**
- Link attributes scanned: **12927**
- Allowed URLs (CSV+legal): **75**
- Pages on disk: **75**

## Summary

| Check | Count |
|---|---|
| Broken internal targets | 0 |
| Remaining relative (non-root) | 0 |
| Links still containing `.html` | 0 |
| Double slashes | 0 |
| Bad canonical | 0 |
| Bad JSON-LD URLs | 0 |
| href="#" | 0 |
| Orphan pages (no inbound) | 0 |
| Pages with empty linkRedirect buttons | 18 |

## Broken internal targets

_none_

## Remaining relative links

_none_

## `.html` links

_none_

## Bad canonical

_none_

## Bad JSON-LD

_none_

## Orphan pages

_none_

## Pages with empty linkRedirect

- `akademiya/index.html`
- `akademiya/korporativnoe-obuchenie/index.html`
- `akademiya/obuchenie-r-builder/index.html`
- `akademiya/obuchenie-seo-aeo/index.html`
- `akademiya/obuchenie-sozdaniyu-saytov/index.html`
- `web-studiya/sozdanie-saitov/ai-konsultanty/index.html`
- `web-studiya/sozdanie-saitov/crm-sistemy/index.html`
- `web-studiya/sozdanie-saitov/index.html`
- `web-studiya/sozdanie-saitov/integratsii/index.html`
- `web-studiya/sozdanie-saitov/internet-magazin/index.html`
- `web-studiya/sozdanie-saitov/korporativnyy-sayt/index.html`
- `web-studiya/sozdanie-saitov/landing/index.html`
- `web-studiya/sozdanie-saitov/mnogostranichnye-sayty/index.html`
- `web-studiya/sozdanie-saitov/obsluzhivanie-saytov/index.html`
- `web-studiya/sozdanie-saitov/onlayn-kalkulyatory/index.html`
- `web-studiya/sozdanie-saitov/onlayn-shkola/index.html`
- `web-studiya/sozdanie-saitov/redizayn-sayta/index.html`
- `web-studiya/sozdanie-saitov/sayt-vizitka/index.html`

## In CSV but missing on disk

_none_

## Notes on “empty linkRedirect”

The 18 pages above contain CTA buttons with empty `data-page-link` that call `showPopup`, `sectionScroll`, or `reachGoals`. These open forms, scroll in-page, or fire analytics — they are **not** broken navigation. No change required.

## Structural rename (CSV)

| Old | New | Redirect |
|---|---|---|
| `/web-studiya/aeo-geo-prodvizhenie/` | `/web-studiya/aeo-prodvizhenie/` | 301 in `.htaccess` + `pages/` stub |

## External policy applied

- WhatsApp → `https://wa.me/77000216900`
- `mailto:` → `ceo@raskrutov.kz` (visible text unchanged)
- Social/messenger links → `target="_blank" rel="noopener noreferrer"`

## Changes volume (`fix_all_links.py` + round 2)

- Files touched: 75 content pages + stubs + `.htaccess` + `sitemap.xml`
- href rewrites ≈ 1172
- data-page-link / original-url ≈ 1536
- WhatsApp normalizations ≈ 659
- consent/regulation → root-absolute: 182
- JSON-LD URL cleanups: 75
- Social `target=_blank`: 438

## Verdict

**PASS** — 0 broken internal targets, 0 relative leftovers, 0 `.html` internals, 0 bad canonical, 0 bad JSON-LD, 0 orphans, 0 missing CSV pages.
