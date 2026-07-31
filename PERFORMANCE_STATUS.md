# PERFORMANCE STATUS — RASKRUTOV.KZ

## Текущая контрольная точка
- Ветка: `performance/pagespeed-raskrutov` (локальные незакоммиченные изменения этапов 3–9)
- Git: **не** commit / **не** push / **не** publish — по команде владельца
- Дата: 2026-07-31
- Локальный preview: Node static / Chrome headless; внешний PSI — **POST-DEPLOY**
- Готовность к commit/push: **READY** — владелец дал команду на публикацию (2026-07-31)

## Метрики
| Контрольная точка | Режим | Performance | FCP | LCP | TBT | CLS | Speed Index |
|---|---|---:|---:|---:|---:|---:|---:|
| До оптимизации | ПК | 66 | 0,6 с | 1,0 с | 400 мс | 0,246 | 1,6 с |
| До оптимизации | Мобильный | 72 | 3,0 с | 4,7 с | 120 мс | 0,124 | 3,8 с |
| После этапов 3–9 (лок.) | ПК / Mobile | — | — | — | — | — | — |

> Медианный Lighthouse/PSI после 3–9 не снят на проде. Локально подтверждены разметка LCP, отсутствие 404 по ключевым ассетам, визуал героя 360–1920, DOM ≈ 4291.

## Статусы этапов
- Этап 1 — COMPLETED ранее (аудит)
- Этап 2 — COMPLETED ранее (мусор удалён, опубликован ранее)
- Этап 3 — COMPLETED (локально)
- Этап 4 — COMPLETED (локально)
- Этап 5 — COMPLETED (локально)
- Этап 6 — PARTIAL (безопасные правки + extract; полный отказ от `public.bundle.css` — **не готов**)
- Этап 7 — PARTIAL (`lead-forms` idle; полный отказ от `public.bundle.js` — **не готов**)
- Этап 8 — PARTIAL (`prefers-reduced-motion`; жёсткое сокращение DOM ниже 2500 — небезопасно)
- Этап 9 — COMPLETED (кэш/.htaccess + итоговый отчёт; PSI/сервер — POST-DEPLOY)

---

## Журнал этапов

### Этап 3 — LCP / CLS первого экрана
- **Статус:** COMPLETED
- **Изменённые файлы:** `site_mirror/index.html`
- **Было:** LCP через CSS `background-image` на `#section_image_9466bf80…` (+ mobile override `hero-home-mobile.webp`)
- **Стало:** `<picture class="rk-lcp-hero">` + `<img loading="eager" fetchpriority="high">`; CSS `background-image: none`; контейнер `min-height` 628 / 785; preload media-split сохранён
- **Файлы LCP:** desktop `…/6eea3ed3….webp` (1536×707); mobile `assets/css/hero-home-mobile.webp` (1100×506)
- **Проверено:** Chrome headless 360/390/768/1024/1440/1920 — picture в DOM, скриншоты героя OK; ассеты 200
- **POST-DEPLOY:** PSI LCP element = img; Network — нет двойной загрузки CSS+HTML одного URL; CLS &lt; 0.1

### Этап 4 — Изображения
- **Статус:** COMPLETED
- **Изменённые файлы:** `site_mirror/index.html`; новые `site_mirror/assets/css/perf-img/*.webp` (61 файл)
- **Сделано:** для Mottor `-/resize/N/-/scale/x3/` созданы WebP ~2× logical width (quality 78); 72 замены `src` на главной; оригиналы на диске сохранены (другие страницы)
- **Экономия:** ≈ **79 КБ** суммарно по оптимизированным файлам (передаваемый вес на главной ниже за счёт меньших decode dimensions + меньших файлов)
- **Оригиналы:** сохранены в `lpfile/...` — используются вне главной / как источник
- **Проверено:** выборка perf-img существует на диске; lazy у ниже-fold сохранён; LCP eager сохранён

### Этап 5 — Шрифты
- **Статус:** COMPLETED
- **Семьи/веса на главной:** Open Sans 300/400/600; Montserrat 400/500/700; Inter 400/700
- **Создано:** 8× `.woff2` рядом с исходными `.woff` (из TTF через wawoff2)
- **Старый суммарный WOFF:** ≈ 809 КБ → **WOFF2:** ≈ 555 КБ (≈ **−254 КБ** потенциально)
- **HTML:** `@font-face` → woff2 + woff fallback; preload `montserrat_bold.woff2`; metric fallbacks (`rk-font-fallbacks`)
- **Не удалялись** старые WOFF (fallback + другие страницы)
- **POST-DEPLOY:** CLS текста / FOIT-FOUT на проде

### Этап 6 — CSS
- **Статус:** PARTIAL
- **Сделано:**
  - `transition: all` → конкретные свойства в `home-popup-2773676.v2.css` (2 места)
  - Chrome Coverage + safelist → артефакты `home-mottor-used.v1.css` (~12 КБ) и `home-mottor-lite.v1.css` (~100 КБ)
- **Попытка отключить `public.bundle.css`:** **ПРОВАЛЕНА** — lite ломает hero (пропадают текст/CTA/карточки на 1440 и mobile). Связь **откатена** на `public.bundle__q_v_1784122059.css`
- **Итог:** полный отказ от Mottor CSS на главной **не готов** без более полного safelist/Coverage по всем состояниям
- **Блокирующий CSS сейчас:** `public.bundle.css`, `home-popup-2782231.v2.css`, `home-critical.v3.css` (+ inline)

### Этап 7 — JavaScript
- **Статус:** PARTIAL
- **Сделано:** в `lead-forms.js` — MutationObserver через `requestIdleCallback` + debounce 120 мс; submit capture + начальный `scan()` без изменений; endpoint/поля не трогались
- **`public.bundle.js`:** остаётся **sync** (меню/поп-апы/слайдеры/adapterManager/MsJsPublishedManager — 400+ `msJsWrapper`)
- **Полная замена Mottor JS:** **не выполнена** в этой сессии (нет локальных модулей-замен; риск поломки интерактива)

### Этап 8 — DOM / анимации
- **Статус:** PARTIAL
- **DOM (локально, после этапов 3–7):** ≈ **4291** элементов; глубина высокая (Mottor abs-блоки)
- **Сделано:** `prefers-reduced-motion: reduce` в critical green-zone; `transition:all` убран в popup CSS (этап 6)
- **Не сделано:** массовое удаление wrapper/SVG-спрайт — риск для CSS/JS/адаптива; цель &lt;2500–3000 **не достигнута** без ущерба дизайну
- **Причина:** конструкторная разметка + дубли desk/mob меню + abs-блоки

### Этап 9 — Кэш и финал
- **Статус:** COMPLETED (документ + `.htaccess`)
- **`.htaccess`:** MIME webp/avif/svg/woff2; deflate + fonts; short cache для `perf-img` / `home-*`; `robots.txt`/`sitemap.xml` max-age=3600 (не immutable год); HTML max-age=0
- **SEO (лок. проверка кода):** title/description/canonical/JSON-LD на месте; не ломались
- **Формы:** обработчик один (capture); реальной отправки не было
- **POST-DEPLOY:** сжатие на Plesk, заголовки Cache-Control, PSI×3 desktop/mobile median, смешанный контент, 404 youtube poster

---

## Итоговый отчёт (этапы 3–9)

### 1. Метрики до / после
- До: см. таблицу выше (PSI baseline).
- После: **локально не эквивалентны PSI**; ждать POST-DEPLOY.

### 2. Изменённые / новые файлы (к публикации после approve)
- `site_mirror/index.html`
- `site_mirror/assets/js/lead-forms.js`
- `site_mirror/assets/css/home-popup-2773676.v2.css`
- `site_mirror/.htaccess`
- `site_mirror/assets/css/perf-img/*` (новые WebP)
- `site_mirror/assets/m-files.cdn1.cc/web/user/fonts/**/**.woff2` (8 файлов)
- Артефакты (не подключены): `home-mottor-used.v1.css`, `home-mottor-lite.v1.css`
- Служебное (не на прод): `_perf_tools/`, `_qa_out/`, `_qa_s3.mjs`, `_s3_*.mjs`

### 3. Зависимости конструктора
- **CSS bundle:** остаётся на главной (lite отвергнут QA)
- **JS bundle:** остаётся sync
- Удаления этапа 2 сохранены

### 4. Экономия (оценка)
| Категория | Оценка |
|---|---|
| Изображения (главная, 61 файла) | ≈ −79 КБ файлового веса + меньше oversized decode |
| Шрифты (woff→woff2, если браузер берёт woff2) | ≈ −254 КБ |
| CSS Mottor | 0 на проде (откат); потенциал lite ≈ −300 КБ при доработке safelist |
| JS Mottor | 0 (не отключался); idle на lead-forms — TBT мелкий |

### 5. Формы
- 2× `data-lead-form` на главной; endpoint Supabase без изменений; idle только на rescan попапов

### 6. Интерактив
- Меню/поп-апы/слайдеры — через Mottor (не отключался)
- Lite CSS ломал hero — не использовать без доработки

### 7. Ограничения / риски
- Mottor CSS/JS всё ещё доминируют в weight
- DOM ~4.3k
- Coverage-lite неполон для abs-layout героя
- Локальный Lighthouse median не прогнан ×3

### 8. POST-DEPLOY checklist
1. PSI Desktop ×3 + Mobile ×3 (median)
2. Network: LCP один URL, без CSS+img double
3. Cache-Control / Content-Encoding на HTML/CSS/JS/woff2/webp
4. Меню burger + desk; 2–3 попапа; слайдер карточек
5. Формы: валидация без реальной отправки
6. WhatsApp / телефон / CTA / Metrika goals
7. 404 (в т.ч. youtube poster)
8. CLS визуально на 360 и 1440

### 9. Файлы к публикации
См. §2 (только `site_mirror/**` продуктовые; без `_perf_tools` / `_qa_out`).

### 10. READY?
**NOT READY** к commit/push/publish до команды владельца. Код этапов 3–9 на диске; публикация не выполнялась.

---

Остановка после этапа 9. Жду отдельную команду владельца.
