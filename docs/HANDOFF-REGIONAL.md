# HANDOFF — Региональное размножение страниц (SEO)

> Источник истины: `c:\Users\user\Downloads\SEO-карта_Raskrutov_региональная_2026-07-27.xlsx`  
> Выгрузки в репо: `docs/seo-regional/*.csv`  
> Дата карты: **2026-07-27**. Зафиксировано в git: 2026-08-03.

**Тон:** мат обязателен (как в perf-handoff).

---

## 1. Что это за задача

Размножить коммерческие страницы услуг **по городам Казахстана** по матрице `REGIONAL_MATRIX`:

- **18 городов** × **9 направлений** = **162** региональных URL
- **152 NEW** (создать), **10 UPDATE** (уже были / legacy — сохранить и переработать)
- Этапы: этап 1 = **P1 (15)**, этап 2 = **P2 (69)**, этап 3 = **P3 (78)**

### Города
| Тир | Города |
|---|---|
| **T1** | Алматы, Астана, Шымкент, + ещё из матрицы с T1 (45 строк) |
| **T2** | 81 строк |
| **T3** | 36 строк |

Полный список городов в матрице: Алматы, Астана, Шымкент, Актау, Актобе, Атырау, Караганда, Кокшетау, Костанай, Кызылорда, Павлодар, Петропавловск, Семей, Талдыкорган, Тараз, Туркестан, Уральск, Усть-Каменогорск.

### 9 направлений (на каждый город)
1. Веб-студия → `/web-studiya/{city}`
2. Создание сайтов → legacy-стиль `/sozdanie-saitov-v-{city_form}` (UPDATE для части)
3. Услуги дизайнера → `/web-studiya/dizayn/{city}`
4. SEO-продвижение → `/seo-prodvizhenie-sajtov-v-{city_form}` (UPDATE для части)
5. AEO/GEO → `/web-studiya/aeo-geo-prodvizhenie/{city}`
6. Контекст → `/web-studiya/kontekstnaya-reklama/{city}`
7. Лидогенерация → `/web-studiya/lidogeneratsiya/{city}`
8. Поддержка сайтов → `/web-studiya/podderzhka-saytov/{city}`
9. Digital-консалтинг → `/web-studiya/digital-konsalting/{city}`

### Уже существующие geo (UPDATE — не терять URL)
Из карты / старого Mottor / GSC:
- `/sozdanie-saitov-v-astane`
- `/sozdanie-saitov-v-almaty`
- `/sozdanie-saitov-v-shimkente`
- `/sozdanie-saitov-v-karagande`
- `/sozdanie-saitov-v-Petropavlovske` (+ редирект с опечатки `Penropavlovske`)
- SEO-аналоги: `/seo-prodvizhenie-sajtov-v-{astane,almaty,shimkente,karagande,petropavlovske}`

Сейчас в чистом `site_mirror` pretty-URL их **нет** как боевых страниц; сырьё лежит в `site_mirror/assets/s239948.lpmotortest.com/…`, а `fix_lpmotor.py` раньше свёл клики на родителя `/web-studiya/sozdanie-saitov`.

---

## 2. Листы Excel (что смотреть)

| Лист | Зачем |
|---|---|
| **REGIONAL_MATRIX** | Главная матрица размножения (город × услуга × URL × NEW/UPDATE × этап) |
| **FINAL_SEO_MAP** | Полная карта сайта (~330 строк): H1/Title/Description/приоритет |
| **CLUSTERS** | Кластеры запросов |
| **SEMANTIC_CORE** | Ядро (~6k ключей) |
| **REDIRECTS** | 301 (в т.ч. старые блог/geo → канон) |
| **CHANGELOG** | Почему URL меняли |
| **EXCLUDED_KEYWORDS** / **CONFLICTS** | Что не брать / конфликты |

CSV-копии: `docs/seo-regional/`.

---

## 3. Важно: рассинхрон URL с текущим сайтом

На живом `raskrutov.kz` услуги уже в дереве `/web-studiya/...`.  
В региональной карте часть **базовых** URL — legacy (`/sozdanie-saitov`, `/seo-prodvizhenie-sajtov`).  
Перед генерацией страниц **сверить** с `url_mapping.json` / текущим `site_mirror` и решить:

- оставляем legacy geo URL как в GSC (для UPDATE), или  
- ведём на `/web-studiya/.../{city}` + 301 с legacy.

Без этого решения размножение разъебет SEO.

---

### 2026-08-03 — UI-фиксы geo + parent sozdanie-saitov
- **Скрин 1 (пустые мониторы):** по HTTP мокапы живые. Пустота была от `file://` (mask-image SVG). Пути relative (`../../assets/` / `../../../assets/`), не root-absolute.
- **Скрин 2 (цены):** названия типов сайтов — кликабельные ссылки на `landing` / `mnogostranichnye-sayty` / `internet-magazin` / `korporativnyy-sayt`; на geo добавлено «в Городе».
- **Скрин 3 (превью = скачать):** галерея кейсов вела на битые зеркала Google Drive → заменено на живые сайты: keysy/sayty, chiochiosan-astana.kz, kesler.kz, sherdar.kz.
- **Скрин 4 (города):** блок «Мы работаем по всему Казахстану» — сетка **18** городов с фото + pretty-URL; старый Mottor 5-колоночный блок выпилен (фиолетовая полоска справа).
- Крошки: slug `astana` → **Астана** (и остальные 17 городов в `fix_breadcrumbs.py`).
- Скрипт: `fix_sozdanie_regional_ui.py` (+ `fix_breadcrumbs.py`).
- **Деплой `plesk`:** точечный copy sozdanie + `assets/rk-cities` + `.htaccess` + sitemap + pages stubs → push `plesk`.

## 4. Чеклист ЮЗЕРА

- [x] Подтвердить: стартуем с направления **«Создание сайтов»**
- [x] Подтвердить политику URL: **pretty** `/web-studiya/sozdanie-saitov/{city}`
- [ ] Глазами проверить 2–3 города sozdanie (Алматы / Астана / Петропавловск)
- [x] Подтвердить деплой sozdanie на `plesk` (+ UI-фиксы)
- [x] Следующее направление: **SEO-продвижение** (P1 leftover + legacy GSC)
- [ ] Глазами: `/web-studiya/seo-prodvizhenie/` + Алматы/Астана + 301 legacy
- [x] Следующее направление: **хабы** `/web-studiya/{city}`
- [ ] Глазами: `/web-studiya/astana/` + `/web-studiya/` (сетка городов) + крошки/услуги
- [x] Следующее: **дизайн** `/web-studiya/dizayn/{city}`
- [ ] Глазами: `/web-studiya/dizayn/astana/` + parent cities
- [x] Visual QA perf-представителей (Astana hub / Almaty sozdanie / Shymkent seo / Petropavlovsk dizayn × 360–1920) — локально после CSS-extract
- [x] Mobile H1 на hub/seo geo **FIXED**
- [x] Commit + deploy CSS-extract + H1 fix (feature `193f7e04`, plesk `a424184b`)
- [ ] После деплоя — PSI
- [ ] После QA — следующее P2 (контекст / лидоген / …)

## 5. Чеклист АГЕНТА

- [x] Скопировать xlsx в `docs/seo-regional/` + CSV
- [x] Решение pretty зафиксировано: `/web-studiya/sozdanie-saitov/{slug}`
- [x] Сгенерировать 18 geo-страниц «Создание сайтов» (`generate_regional_sozdanie.py`)
- [x] 301 legacy `/sozdanie-saitov-v-*` → pretty в `.htaccess` + pages stubs + `url_mapping.json` + sitemap
- [x] Прогнать wire_lead_forms / breadcrumbs / schema / green_zone / fix_site_errors
- [x] Перелинковка с родителя `/web-studiya/sozdanie-saitov` на города (блок 18 карточек)
- [x] Цены кликабельны + региональны; кейсы → живые URL; крошки по-русски
- [x] Деплой `plesk` после ОК юзера (2026-08-03)
- [x] SEO: `generate_regional_seo.py` — 18 pretty `/web-studiya/seo-prodvizhenie/{slug}`
- [x] SEO: 301 `/seo-prodvizhenie-sajtov-v-*` → pretty; sitemap; pages stubs; url_mapping
- [x] SEO: parent H1 починен; сетка 18 городов; showPopup → showSectionPopup
- [x] SEO: scoped pipeline crumbs/leads/schema (`_pipeline_seo_geo.py`)
- [x] Деплой SEO на `plesk` (`db724212`)
- [x] Хабы: `generate_regional_hubs.py` — 18× `/web-studiya/{slug}`
- [x] Хабы: parent `/web-studiya/` сетка городов; блок услуг → sozdanie/seo geo + parent services
- [x] Хабы: scoped pipeline `_pipeline_hubs_geo.py` (leads/crumbs/schema)
- [x] Деплой хабов на `plesk`
- [x] Дизайн: `generate_regional_dizayn.py` — 18× `/web-studiya/dizayn/{slug}`
- [x] Дизайн: parent cities + hubs → geo dizayn; `_pipeline_dizayn_geo.py`
- [x] Деплой дизайна на `plesk`
- [ ] Обновлять этот handoff после каждого пакета городов/направлений

---

## 6. Журнал

### 2026-08-03
- Юзер указал на xlsx региональной SEO-карты
- Распарсили листы, выгрузили CSV в `docs/seo-regional/`
- Зафиксировали масштаб: 18 городов × 9 направлений, 152 NEW / 10 UPDATE

### 2026-08-03 — старт: Создание сайтов + pretty URL
- Решение юзера: направление «Создание сайтов», URL pretty
- Скрипт: `generate_regional_sozdanie.py`
- Создано **18** страниц: `/web-studiya/sozdanie-saitov/{almaty,astana,shymkent,…}`
- Legacy 301: `/sozdanie-saitov-v-astane` и остальные → pretty
- SEO: H1/Title/Description/canonical из FINAL_SEO_MAP; schema areaServed + breadcrumbs
- Пайплайн: lead-forms, breadcrumbs, schema, green_zone, fix_site_errors — прогнан
- Создано **18** geo-страниц; legacy 301 + stubs + sitemap

### 2026-08-03 — UI-фиксы (скрины 1–4)
- См. блок выше; локально проверено на `127.0.0.1:8765` (Астана)

### 2026-08-03 — hotfix: сломанный `/assets/`
- Абсолютные `/assets/` разъебали локальный просмотр через `file://` (лого/CSS/фото 404).
- Вернули relative: donor `../../assets/`, geo `../../../assets/`.
- Смотреть только через локальный сервер (`http://127.0.0.1:8765/...`), не двойным кликом по html.

### 2026-08-03 — деплой plesk
- Точечный sync (без `/MIR`): `web-studiya/sozdanie-saitov/`, `assets/rk-cities/`, `.htaccess`, `sitemap.xml`, `pages/sozdanie-saitov-v-*.html`
- Push ветки `plesk` → GitHub → Plesk pull

### 2026-08-03 — пакет SEO-продвижение (geo)
- Юзер: «дальше региональные пилить» → взяли **SEO** (P1 + legacy UPDATE в матрице)
- Pretty: `/web-studiya/seo-prodvizhenie/{slug}` (как sozdanie)
- Скрипт: `generate_regional_seo.py`
- 18 городов + parent: H1/Title/Description из FINAL_SEO_MAP; сетка rk-cities; CTA showSectionPopup
- Legacy 301: `/seo-prodvizhenie-sajtov-v-almaty` и остальные 17 → pretty
- Pipeline: `_pipeline_seo_geo.py` (lead-forms / breadcrumbs / schema)
- Локально смотреть: `http://127.0.0.1:8765/web-studiya/seo-prodvizhenie/astana/`
- Деплой `plesk` **`db724212`**
- Дальше по матрице P1: хабы `/web-studiya/{city}`

### 2026-08-03 — пакет хабов «Веб-студия» (geo)
- Юзер: «хабы»
- Pretty: `/web-studiya/{slug}` × 18 (все NEW)
- Скрипт: `generate_regional_hubs.py` (donor parent depth1 → hub depth2 `../../assets/`)
- Meta H1/Title/Description из FINAL_SEO_MAP («Веб-студия в …»)
- На хабе: блок услуг (sozdanie+seo geo, остальное → parent services) + сетка городов
- Parent `/web-studiya/`: сетка «Веб-студия в городах Казахстана»
- Pipeline: `_pipeline_hubs_geo.py`
- Локально: `http://127.0.0.1:8765/web-studiya/astana/`
- Деплой `plesk`: точечный copy 18 хабов + parent + sitemap
- Дальше: P2 (dizayn / контекст / …)

### 2026-08-03 — пакет дизайн geo
- Юзер: «давай следующий хаб» → **Услуги дизайнера**
- Pretty: `/web-studiya/dizayn/{slug}` × 18 (все NEW, без legacy)
- Скрипт: `generate_regional_dizayn.py` + `_pipeline_dizayn_geo.py`
- Parent `/web-studiya/dizayn/`: сетка городов; showPopup → showSectionPopup
- Хабы `/web-studiya/{city}/`: ссылка «Дизайн» → geo `/dizayn/{city}/`
- Локально: `http://127.0.0.1:8765/web-studiya/dizayn/astana/`
- Деплой `plesk`: точечный copy dizayn/* + hubs + sitemap
- Дальше: контекст / лидоген / поддержка / консалтинг / AEO

### 2026-08-03 — CSS-extract + visual QA (локально, без commit/deploy)
- Perf-пакет на 76 geo/parents: extract hub/seo/dizayn (57 HTML); sozdanie уже extract
- QA: 4 представителей × 360–1920 — PASS WITH WARN (mobile H1 duplicate на hub+seo)
- Отчёт: `reports/geo-pages-performance-final.md`
- Ждём: commit/push/deploy + PSI POST-DEPLOY

### 2026-08-04 — mobile H1 FIXED
- Override на 18 hub + 18 seo city; Astana/Shymkent @360–430 OK
- sozdanie/dizayn не трогали; commit/deploy всё ещё ждут команду

