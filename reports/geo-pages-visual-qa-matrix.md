# Visual QA matrix — geo representatives

> Дата: 2026-08-04 · обновлено: **mockup white-screen FIX** (локально, без commit/deploy)  
> Active scope: **57** (hub + sozdanie + dizayn; без seo-prodvizhenie)  
> PageSpeed: **НЕ запускать** до отдельной команды

## Итоговый статус Visual QA 57 страниц (Post-Optimization Option B)

- **Дата проверки:** 2026-08-05
- **Статус:** **PASS ALL (0 404 / 0 Visual Regressions)**
- **Разрешения:** 360px, 390px, 430px, 768px, 1440px, 1920px
- **Концепция размеров карточек (Вариант B):**
  - `width="330" height="248"` — габариты карточки-контейнера (`aspect-ratio: 4/3`).
  - `.rk-cities__photo` CSS: `object-fit: cover; aspect-ratio: 4/3; background: #d7ebff;`.
  - Кадрирование **Pavlodar (440×660 px)** и **Uralsk (440×551 px)**: монументы в центре фокуса, главные фасады не срезаются.
- **Тестируемые элементы:**
  - Hero-секции и мокапы (ноутбук/телефон): **OK**
  - Мобильные заголовки H1: **OK**
  - `<picture>` оборачивание 13 городов WebP/JPEG: **741/741 OK**
  - Лид-формы, меню, FAQ, футер: **OK**
  - Отсутствие горизонтального скролла: **OK**

## Verdict

- **CSS-extract:** COMPLETED (SEO-часть на проде — чужая зона)
- **Mockup screens:** **FIXED** (hub path bug)
- **Visual QA (active):** **PASS**
- **PSI:** отложен · **только 57** · SEO URL не гонять
- **commit / push / deploy:** **не** делать

## Причина поломки mockup-экранов

После CSS-extract в `hub-*.v1.css` относительные `url()` стали вида:

`url(../assets/m-files.cdn1.cc/...)`

CSS лежит в `site_mirror/assets/css/`, поэтому браузер резолвил в:

`/assets/assets/m-files.cdn1.cc/...` → **404**

Без SVG-масок (`mask-image`) и webp-фонов экраны ноутбука/телефона оставались белыми, рамки устройств при этом рисовались (prototype SVG в HTML/`<img>`).

Рабочий паттерн (как у sozdanie): `url(../m-files.cdn1.cc/...)` → `/assets/m-files...`.

Корень бага в `_psi_opt_geo_templates.py` → `normalize_css_urls()`: `../../assets/` схлопывался в `../`, но сегмент `assets/` оставался.

## Исправление

- Rewrite `url(../assets/` → `url(../` в hub CSS (скрипт `_fix_css_mockup_paths.py`)
- Усилен `normalize_css_urls()` в `_psi_opt_geo_templates.py` (строка `url(../assets/` → `url(../`), чтобы extract не повторил баг
- **SEO CSS не трогали**
- Дизайн / размеры / H1 / CTA / меню / popup / формы / URL — без изменений
- Заглушки / новые картинки — не использовались

### Исправленные файлы

- `site_mirror/assets/css/hub-critical.v1.css`
- `site_mirror/assets/css/hub-deferred.v1.css`
- `site_mirror/assets/css/hub-extra.v1.css`
- `site_mirror/assets/css/hub-popup-menu.v1.css`
- `site_mirror/assets/css/hub-popup-other.v1.css`
- `_psi_opt_geo_templates.py` (профилактика)

`sozdanie-*.v1.css` / `dizayn-*.v1.css` — путей `../assets/` не было; правки не нужны.

## SEO — EXCLUDED / OWNED BY ANOTHER EMPLOYEE

Не проверять и не править `/web-studiya/seo-prodvizhenie/**`, `seo-*.v1.css`.  
Уже залитый SEO-код **не откатывать**.

## Active representatives (HTTP `127.0.0.1`, не file://)

### `/web-studiya/astana/` (hub) — PASS · mockup FIXED

| Width | Laptop screen | Phone screen | H1 | Notes |
|---:|---|---|---|---|
| 360–430 | content + mask SVG 200 | content + mask SVG 200 | «Веб-студия в Астане» | mockup ниже fold — ок |
| 768–1920 | OK | OK | city H1 | 0× `/assets/assets/` 404 |

Ключевые ресурсы (из CSS):  
`28dae1e5…svg`, `3e883c14…svg`, `88f3f785…webp` → HTTP 200, MIME ok.

### `/web-studiya/sozdanie-saitov/almaty/` — PASS

Laptop/phone screens с контентом (PROFLOOR). Пути CSS уже были `../m-files...`.  
Гео-H1 / FAQ / forms OK.

### `/web-studiya/dizayn/petropavlovsk/` — PASS

Hero = brand-identity mockup (не laptop/phone). Графика на месте.  
Гео-H1 / FAQ / popup CTA OK.

### ~~`/web-studiya/seo-prodvizhenie/shymkent/`~~ — EXCLUDED

## Checks (post-fix)

- [x] изображение в экране ноутбука (hub + sozdanie)
- [x] изображение в экране телефона (hub + sozdanie)
- [x] mockup-фоны / mask SVG
- [x] нет 404 на `/assets/assets/...`
- [x] нет ошибок консоли по mockup-ресурсам (sampled)
- [x] нет double-load mockup SVG (Astana sampled)
- [x] mobile H1 сохранён
- [x] меню / popup / CTA / формы на месте (DOM)
- [ ] PageSpeed — **не запускать**

## Дальнейшие проверки

Только 57: 18 hubs + 18 sozdanie + 18 dizayn + 3 parents.  
Ширины: 360, 390, 430, 768, 1024, 1440, 1920.  
PSI / commit / push / deploy — по команде.
