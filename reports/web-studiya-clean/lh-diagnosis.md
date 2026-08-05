# LH diagnosis — web-studiya/index-clean (mobile)

**Source report:** `reports/web-studiya-clean/lh-mobile-2.json`  
**URL:** `http://127.0.0.1:8767/web-studiya/index-clean.html`  
**Context:** local simulate (не прод). Median по 3 прогонам — см. `lighthouse-mobile-median.md` (Perf **29** / FCP 4.5s / LCP 6.9s / TBT ~14.5s / CLS 0.026). Ниже — разбор **run 2**.

## Metrics (run 2)

| Metric | Value |
| --- | ---: |
| Performance score | 25 (0.25) |
| FCP | 7.8 s (7781.9 ms) |
| LCP | 10.3 s (10308.6 ms) |
| Speed Index | 17.2 s |
| **TBT `numericValue`** | **13898.56 ms** (~13900 ms) |
| CLS | 0.026 |

## TBT

- **`total-blocking-time.numericValue` = 13898.562999999998** (display ~13900 ms)
- Lab TBT раздут: main-thread / Unattributable + document + Yandex Metrika — **не** ориентир для фейка 90+ на проде без третьих сторон / без throttling-артефактов.

## bootup-time (top scripts)

| Total (ms) | Scripting (ms) | URL |
| ---: | ---: | --- |
| 24361 | 20994 | Unattributable |
| 22723 | 176 | `http://127.0.0.1:8767/web-studiya/index-clean.html` |
| 2984 | 2631 | `https://mc.yandex.ru/metrika/tag.js` |
| 249 | 134 | `http://127.0.0.1:8767/assets/js/lead-forms.js` |
| 75 | 67 | `https://mc.yandex.ru/metrika/tag_phono.js` |
| 71 | 53 | `http://127.0.0.1:8767/assets/js/home-clean.js?v=21` |

**Вывод:** основной блок — Unattributable + парсинг/оценка огромного HTML document + Metrika. Свой `home-clean.js` / `lead-forms.js` мелкие относительно TBT.

## unused-css (top)

| Wasted | Total | % | URL |
| ---: | ---: | ---: | --- |
| 36881 B | 50100 B | 73.6% | `home-clean-deferred.v1.css?v=1` |
| 10508 B | 14977 B | 70.2% | `home-clean-critical.v1.css?v=1` |

`studio-clean.css` в unused-css top **не** попал (reuse home CSS на studio тянет лишнее с главной — ожидаемо).

## unused-js (top)

- **Пусто:** `items: []`, `overallSavingsBytes: 0`
- На этом прогоне unused-javascript ничего существенного не нашёл (Metrika/свои скрипты не в топе wasted).

## LCP element

- Аудит `largest-contentful-paint-element`: **ERROR**  
  `Required TraceElements gatherer encountered an error: Dependency "RootCauses" failed … Cannot read properties of undefined (reading 'frame_sequence')`
- Селектор/snippet LCP-элемента в run 2 **недоступны** из-за падения gatherer (Windows/LH trace).
- LCP timing run 2: **10.3 s**; median по 3 runs: **6.9 s**. Кандидат по вёрстке preview: hero (`assets/img/studio/` — hero-bg / hero-laptop) — подтвердить глазами / повторным LH после стабильного trace.

## render-blocking resources

| Bytes | wastedMs | URL |
| ---: | ---: | --- |
| 10939 | 3553 | `http://127.0.0.1:8767/assets/css/studio-clean.css?v=1` |

Единственный явный render-blocking в отчёте run 2 — **studio-clean.css** (~3.5 s lab wastedMs).

## CSS sizes on disk (`site_mirror/assets/css/`)

| File | Size (bytes) |
| --- | ---: |
| `home-clean-critical.v1.css` | **14977** |
| `home-clean-deferred.v1.css` | **50100** |
| `studio-clean.css` | **10752** |
| **Sum (these three)** | **75829** |

(Согласуется с resource-summary CSS ~75–77 KiB transfer в median.)

## Top findings (коротко)

1. **TBT ~14 s** — Unattributable + document + Metrika; свой JS не главный виновник.
2. **Unused CSS** — ~73% deferred + ~70% critical home CSS на studio-странице (reuse с главной).
3. **Render-blocking** — `studio-clean.css` (~11 KB, ~3.5 s lab wastedMs).
4. **LCP element** — gatherer упал; timing плохой в lab; нужен визуальный/повторный прогон.
5. **Unused JS** — 0 в этом отчёте.