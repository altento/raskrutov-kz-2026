# Geo pages performance — итоговый отчёт

> Дата: 2026-08-04 (обновлён после mobile H1 fix)  
> Ветка: `performance/pagespeed-raskrutov`  
> **Commit / push / deploy: НЕ делались** (ждём отдельную команду)

---

## Статус этапов

| Этап | Статус | Комментарий |
|---|---|---|
| 1. Инвентаризация | **DONE** | `reports/geo-pages-performance-inventory.md` (+ `.json`) — 76/76 |
| 2. Baseline PSI | **POST-DEPLOY** | PSI API 429 quota; локальный Lighthouse/npx нет. См. `geo-pages-performance-baseline.md` |
| 3. HTML | PARTIAL | Без агрессивного minify DOM; CSS-extract сильно ужал HTML |
| 4. CSS | **COMPLETED** | Extract critical/deferred/popup/extra для hub/seo/dizayn; sozdanie уже было |
| 5. JS | PARTIAL | `public.bundle.js` **оставлен sync**; video-lazy на sozdanie уже был |
| 6. Images | NOT DONE | Осторожные dims / srcset — после PSI |
| 7. Fonts | PARTIAL | Убраны лишние preload inter/open_sans/montserrat normal+medium |
| 8. CWV / hero | PARTIAL | hero min-height reserve + prefers-reduced-motion |
| 9. .htaccess | NOT TOUCHED | Уже есть cache/gzip; HTML не трогали |
| 10. SEO/a11y | NOT AUDITED anew | Inventory: canonical/JSON-LD/alt OK на 76 |
| 11. Visual QA | **PASS** | 4 URL × 360–1920; mobile H1 hub/seo **FIXED** |
| 12. Итоговый PSI | **POST-DEPLOY** | После публикации + квоты API / установки Lighthouse |

---

## ЭТАП 4 — CSS-extract: COMPLETED

Паттерн как у sozdanie: вынести `all_blocks-style` + popup styles в файлы, critical blocking, deferred через `media="print" onload`.

### Новые CSS
| Файл | Роль |
|---|---|
| `assets/css/hub-critical.v1.css` | blocking |
| `assets/css/hub-deferred.v1.css` | deferred |
| `assets/css/hub-popup-menu.v1.css` | blocking (моб. меню) |
| `assets/css/hub-popup-other.v1.css` | deferred |
| `assets/css/hub-extra.v1.css` | deferred leftovers |
| то же для `seo-*` и `dizayn-*` (+ `dizayn-extra`) | |

### HTML вес после (родители)

| Шаблон | HTML было → стало | HEAD было → стало |
|---|---|---|
| hub `/web-studiya/` | ~913 → **~379 KiB** | ~543 → **~9 KiB** |
| seo parent | ~912 → **~378 KiB** | ~543 → **~9 KiB** |
| dizayn parent | ~942 → **~420 KiB** | ~531 → **~9 KiB** |
| sozdanie | ~443 (без изменений) | ~10 KiB |

Затронуто: **57 страниц** (19 hub + 19 seo + 19 dizayn). Sozdanie не трогали.

Скрипты: `_psi_opt_geo_templates.py`, `_psi_dizayn_extra.py`, `_psi_hub_seo_extra.py`.

### Жёсткие ограничения соблюдены
- `public.bundle.js` — **sync**, без defer/async
- URL / H1 / Title / Description / canonical / JSON-LD — не переписывались ради перфа
- Формы / endpoint — не трогались
- Commit/push/deploy — нет

---

## ЭТАП 11 — Visual QA (обязательный)

**База:** `http://127.0.0.1:8767` из `site_mirror`  
**Ширины:** 360, 390, 430, 768, 1024, 1440, 1920 px  
**Представители:**

| URL | Шаблон | Вердикт |
|---|---|---|
| `/web-studiya/astana/` | hub | **PASS** (mobile H1 **FIXED**) |
| `/web-studiya/sozdanie-saitov/almaty/` | sozdanie | **PASS** |
| `/web-studiya/seo-prodvizhenie/shymkent/` | seo | **PASS** (mobile H1 **FIXED**) |
| `/web-studiya/dizayn/petropavlovsk/` | dizayn | **PASS** |

Артефакты: `reports/geo-pages-visual-qa.json`, `reports/geo-pages-visual-qa-assets.json`, `reports/geo-pages-visual-qa-matrix.md`.

### Чеклист (сводка)

| Проверка | Результат |
|---|---|
| Hero / первый экран | OK на desktop; mockups/фоны грузятся |
| Фоновые изображения / mockup | OK после settle; lazy Mottor imgs → broken=0 |
| Кнопки / CTA | Видимы; «Получить консультацию» работает |
| Меню desktop | Ссылки в шапке на ≥768 |
| Меню mobile | Burger открывает drawer (hub Astana verified) |
| Popup | Dizayn: CTA → `open_popup` + форма «Обсудим Ваш проект?» OK |
| Формы | Lead-формы на странице видны |
| FAQ | OK на sozdanie + dizayn; на hub/seo FAQ-блока нет (ожидаемо) |
| Изображения / галерея | Sampled local assets **0×404** (50/page) |
| Футер / контакты | Контакты + телефоны/email; sticky `footer-bar` hide на desktop |
| Console JS | Ошибок страницы в probes не поймано |
| 404 ресурсов | **0** на sampled CSS/JS/webp локальных ассетов |
| FOUC | Critical CSS loaded; H1 не Times-fallback |
| Layout shift | Mid-session resize CLS шумный; **формальный CLS → Lighthouse POST-DEPLOY** |

### Mobile H1 — FIXED (2026-08-04)

**Причина:** `@media(max-width:500px)` в Mottor deferred CSS: `.blk-data--pc` → `display:none`, `.blk-data--mobile370` → `display:block`. Гео-H1 был в `--pc`, дубль «полного цикла…» — в `--mobile370` (блок `b-aa35398c497a44568f98430c09d8d76c`).

**Фикс:** inline `<style data-rk-mobile-h1-fix>` на **36** city pages (18 hub + 18 seo): на mobile показать H1, скрыть только Mottor-дубль этого блока. CSS-extract **не** меняли; sozdanie/dizayn/parents не трогали.

**Проверка:** Astana hub + Shymkent SEO @ 360/390/430 — гео-H1 visible, дубль hidden; desktop 1440 OK.

Горизонтальный «overflow» на части ширин — артефакт absolute `CANVAS` (виджет), не поломка layout секций.

---

## ЭТАП 2 / 12 — PSI требует POST-DEPLOY

**Нельзя фейкать цифры.** После деплоя:

1. Установить Node + `npx lighthouse` **или** дождаться квоты PSI / API key  
2. Прогнать `_baseline_geo_psi.py` (3× медиана)  
3. Representative: Astana / Almaty / Petropavlovsk × 4 шаблона × mobile/desktop  

Ожидание по опыту sozdanie: Mottor + CSS extract → mobile Perf порядка **80–90**, не гарантированные 100 из‑за sync `public.bundle.js` + GTM/iframe на sozdanie.

Известные прошлые якоря (не сегодня):
- Home clean: **99**
- Sozdanie: **86** (после hotfix CLS)

---

## Оставшиеся ограничения

1. **PSI / Lighthouse scores** — только POST-DEPLOY (API 429 / нет локального LH)  
2. ~~Mobile H1 duplicate на hub/seo~~ — **FIXED** (inline override; при регене страниц нужен `_fix_mobile_h1_geo.py` или вшить в генератор)  
3. Images srcset/AVIF / массовые width-height — риск регрессии как с 1920; не делали  
4. Отложенный Mottor JS — запрещён правилами (`public.bundle.js` sync)  
5. Lazy iframe/maps на всех 76 — частично на sozdanie; не гоняли массово  
6. Незакоммиченный мусор akademiya/crm/`_*.py` — **не трогали**  
7. Formal CLS/LCP/INP метрики — через Lighthouse после публикации  

---

## Рекомендуемые следующие шаги (по команде)

1. `commit` feature + точечный copy в `site_plesk` + push `plesk`  
2. PSI baseline после деплоя → images/fonts если цифры скажут куда бить  
3. (Опционально) вшить mobile-H1 override в `generate_regional_hubs.py` / seo generator  

---

## Файлы отчётов

- `reports/geo-pages-performance-inventory.md` (+ `.json`)
- `reports/geo-pages-performance-baseline.md` (+ `.json`)
- `reports/geo-pages-visual-qa.json`
- `reports/geo-pages-visual-qa-assets.json`
- `reports/geo-pages-visual-qa-matrix.md` (+ `.json`)
- `reports/geo-pages-performance-final.md` ← этот файл
