# Geo pages — PageSpeed baseline (ЭТАП 2)

- Дата: 2026-08-03
- Ветка: `performance/pagespeed-raskrutov`
- PageSpeed Insights API: **Quota exceeded (429)** — дневной лимит `pagespeedonline.googleapis.com`
- Локальный Lighthouse (`npx`/`node`): **не установлен** на этой машине
- Chrome: установлен (`C:\Program Files\Google\Chrome\Application\chrome.exe`)
- **Цифры Performance/CWV для 76 URL в этой сессии НЕ выдуманы** — полный baseline = **POST-DEPLOY** (или после установки Lighthouse + API key)

## Что удалось / не удалось

| Проверка | Статус |
|---|---|
| PSI API × representative (3 города × 4 шаблона × mobile/desktop × 3) | BLOCKED — 429 на первом запросе |
| Локальный Lighthouse | BLOCKED — нет node/npx |
| Инвентаризация HTML (ЭТАП 1) | DONE — `geo-pages-performance-inventory.md` |

## Ориентиры из HANDOFF / прошлых прогонов (не путать с сегодняшним baseline)

| Страница | Источник | Mobile Perf | LCP | TBT | CLS | Примечание |
|---|---|---:|---:|---:|---:|---|
| `/` (clean home) | HANDOFF 2026-08-03 | **99** | 2.0s | 10ms | 0.001 | clean rebuild, не Mottor |
| `/web-studiya/sozdanie-saitov/` | HANDOFF hotfix | **86** | 3.1s | 20ms | 0.11 | Mottor + CSS extract; потолок ~80–90 |
| `/web-studiya/sozdanie-saitov/` (регрессия) | HANDOFF | **53** | — | — | — | bogus img width=1920 — откатили |

## Выводы из инвентаризации → ожидаемые блокеры PSI

### Общее для всех 4 шаблонов
- **`public.bundle.css` + `public.bundle.js` на 76/76** — sync JS нельзя defer (меню/попапы).
- HTML **~444–943 KiB** — Mottor разметка + куча inline `<style>` / init scripts.
- Canonical + JSON-LD + lead-forms: **76/76 OK**.
- Alt у img: **OK** (missing=0).
- `width`+`height` только у части img (~21/66 hubs/seo, 18/75 sozdanie) — CLS-риск, но массово ставить 1920 **запрещено** (уже жгли Perf до 53).

### По шаблонам
| Шаблон | HTML avg | Особенность | Вероятный потолок без clean rebuild |
|---|---:|---|---|
| `sozdanie-saitov` | ~445 KiB | Уже есть `sozdanie-critical/deferred` + GTM + **5 iframe** + kinescope | ~80–90 (сейчас ~86) |
| `web-studiya` (хабы) | ~917 KiB | Толстый Mottor, без CSS-extract | ниже sozdanie, скорее 50–75 |
| `seo-prodvizhenie` | ~914 KiB | Как хабы (клон Mottor) | аналогично хабам |
| `dizayn` | ~942 KiB | **60 style tags**, 10 bg-image — самый жирный HEAD | хуже хабов |

### Внешние риски
- sozdanie: GTM, VK, Kinescope iframes, кейс-сайты
- остальные: youtube/vimeo ссылки, WA/TG/IG (не обязательно в critical path)
- maps: детект по разметке на всех — проверить lazy `lazy_ymaps`

## POST-DEPLOY чеклист baseline (когда появится квота / Lighthouse)

Representative URL (обязательно 3× прогон, медиана):

1. `/web-studiya/{astana,almaty,petropavlovsk}/`
2. `/web-studiya/sozdanie-saitov/{…}/`
3. `/web-studiya/seo-prodvizhenie/{…}/`
4. `/web-studiya/dizayn/{…}/`

+ 4 родителя. Mobile + desktop. Категории: Perf / A11y / BP / SEO.

Скрипт готов: `_baseline_geo_psi.py` (сейчас упирается в 429).

## Решение для ЭТАПОВ 3+

Идти в **безопасные** правки без фейка цифр:
1. Не трогать `public.bundle.js` sync.
2. Не вешать гигантские width/height.
3. Приоритет: CSS-extract для **dizayn / seo / hubs** по образцу sozdanie (самый жирный выигрыш) — только после карты зависимостей и визуального QA.
4. sozdanie: точечно (iframe/video lazy уже частично есть) — не ломать 86.
5. Шрифты / preload / prefers-reduced-motion / image dims аккуратно.
