# HANDOFF — Региональное размножение страниц (SEO)

> Источник истины: `c:\Users\user\Downloads\SEO-карта_Raskrutov_региональная_2026-07-27.xlsx`  
> Выгрузки в репо: `docs/seo-regional/*.csv`  
> Дата карты: **2026-07-27**. Зафиксировано в git: 2026-08-03.

**Тон:** мат обязателен (как в perf-handoff).

> **Perf-track (с 2026-08-04):** страницы `/web-studiya/seo-prodvizhenie/**` =  
> **EXCLUDED / OWNED BY ANOTHER EMPLOYEE**.  
> Performance-агент их не оптимизирует / не PSI / не откатывает.  
> Active perf-scope: **57** = hubs + sozdanie + dizayn (+ 3 parents).

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
- [ ] **PILOT clean Astana hub:** открыть `…/astana/index-clean.html` локально → approve swap на `index.html`
- [x] **Astana hub SWAP (2026-08-05):** clean → `index.html`, Mottor → `index.mottor-legacy.html` (approve «ок»)
- [ ] **Astana hub REDESIGN purple/mockup (2026-08-06):** глазами `127.0.0.1:8771/web-studiya/astana/` 390/768/1440; оранж отменён; commit/push/deploy только по отдельной команде
- [x] **Almaty hub CLEAN (2026-08-06):** deploy plesk глазами `127.0.0.1:8771/web-studiya/almaty/` 390/768/1440; Mottor → `index.mottor-legacy.html`; commit/push/deploy только по отдельной команде
- [x] Batch5 clean hubs (2026-08-06): shymkent/aktau/aktobe/atyrau/karaganda — локально → **deploy all 18**
- [x] **All 18 clean hubs DEPLOY (2026-08-06):** feature + точечный plesk; глазами 2–3 города на https://raskrutov.kz/web-studiya/{city}/
- [x] Следующее: **дизайн** `/web-studiya/dizayn/{city}`
- [x] **Parent `/web-studiya/dizayn/` CLEAN DEPLOY (2026-08-07)** — юзер «залей хаб»; geo 18 **не** деплоили, переработка отдельно
- [ ] Глазами live: https://raskrutov.kz/web-studiya/dizayn/
- [ ] Clean rebuild + deploy 18 geo `dizayn/{city}/` — по команде
- [x] Visual QA perf-представителей (Astana hub / Almaty sozdanie / Shymkent seo / Petropavlovsk dizayn × 360–1920) — локально после CSS-extract
- [x] Mobile H1 на hub/seo geo **FIXED**
- [x] Commit + deploy CSS-extract + H1 fix (feature `193f7e04`, plesk `a424184b`)
- [x] **SEO (`seo-prodvizhenie`) EXCLUDED из perf-трека** — owned by another employee; код на проде не откатывать
- [ ] PSI — только **57** (hub + sozdanie + dizayn); **без SEO**
- [ ] Следующее P2 регионалки (контекст / лидоген / …) — SEO пишет другой сотрудник

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
- sozdanie/dizayn не трогали

### 2026-08-04 — SEO OUT OF PERF TRACK
- `/web-studiya/seo-prodvizhenie/**` + `seo-*.v1.css` → **EXCLUDED / OWNED BY ANOTHER EMPLOYEE**
- Не править / не PSI / не QA в performance-сессиях
- Published SEO **не откатывать**
- Perf active: **57** (hubs + sozdanie + dizayn + 3 parents)

### 2026-08-06 — полный redesign `/web-studiya/astana/` (локально)

- DOM пересобран в 9 секций по концепции «Digital-партнёр для бизнеса в Астане».
- 4 направления вместо 9 карточек и повторяющихся отдельных сервисных секций.
- Уникальные regional prose, задачи, подход, кейс-категории, 6 этапов и FAQ×6.
- Только одно hero-изображение; HTML −23 KiB; `studio-clean.css` отключён на этой странице.
- QA: 6 контрольных ширин без overflow; 20/20 внутренних URL 200; JSON-LD валиден.
- `/web-studiya/seo-prodvizhenie/astana/` не создавался; другие города и parent не менялись.
- Commit / push / deploy не выполнялись.

### 2026-08-06 — Astana: выравнивание под хаб (v4, локально)

- Юзер: предыдущая версия «криво и ужасно».
- Пересобрано ближе к `/web-studiya/`: hero 1 lead + 3 trust; карточки услуг с `ul` + SVG `+`; adv + cta-panel; contacts/banner как у хаба.
- Убраны самодельные битые блоки (фейк-visual из hero-bg, текстовые «more» вместо кружка, перегруженные task/why/include).
- Оставлены региональные: prose, cases→/keysy/, process×5, FAQ×8, remote note.
- CSS: `hub-city-clean.css?v=4` тонкий слой.
- Preview: `http://127.0.0.1:8771/web-studiya/astana/` — без commit/push.

### 2026-08-06 — Almaty hub CLEAN (локально, эталон Astana)

- Mottor `/web-studiya/almaty/index.html` → `index.mottor-legacy.html`.
- Clean rebuild по структуре Astana: header/menu, hero, regional, 6 направлений, adv+CTA, cases→/keysy/, process×5, FAQ×9, contacts+modal, sticky WA/tel.
- Уникальные тексты/FAQ/JSON-LD под Алматы; remote note без офиса в городе; `service=Веб-студия — Алматы`.
- CSS: `hub-city-clean.css?v=9` — алиас `.rk-almaty-page` + сетка 3×2 для 6 карточек.
- QA: 390 без overflow; modal lead открывается; assets OK; Astana HTML не трогали; sitemap URL уже был.
- Preview: `http://127.0.0.1:8771/web-studiya/almaty/` — **без commit/push/deploy**.

### 2026-08-06 — Almaty hub DEPLOY

- Clean /web-studiya/almaty/ + hub-city-clean.css → feature + точечный plesk.
- Live: https://raskrutov.kz/web-studiya/almaty/

### 2026-08-06 — Batch5 clean hubs (локально)

- Города: Шымкент, Актау, Актобе, Атырау, Караганда.
- Mottor → `index.mottor-legacy.html`; clean по эталону Алматы: devices hero + `cities/{slug}.webp`, FAQ×9, ProfessionalService areaServed, remote note.
- CSS: `hub-city-clean.css` + класс `.rk-hub-city-page` (?v=11).
- Preview: `http://127.0.0.1:8771/web-studiya/{slug}/` — commit/push/deploy по отдельной команде.

### 2026-08-06 — Rest clean hubs (локально): все 18

- Добиты Mottor-остатки: kokshetau, kostanay, kyzylorda, pavlodar, petropavlovsk, semey, taldykorgan, taraz, turkestan, uralsk, ust-kamenogorsk.
- У каждого: `index.mottor-legacy.html`, clean по эталону Алматы, `cities/{slug}.webp`, devices hero, FAQ×9, JSON-LD, уникальные тексты.
- Петропавловск (HQ): без формулировки «местного адреса нет»; офис в городе + очно/онлайн.
- CSS: `.rk-hub-city-page`, `hub-city-clean.css?v=12`.
- QA `_qa_hub_all18.py`: 18/18 OK, уникальные H1.

### 2026-08-06 — DEPLOY all 18 clean city hubs

- Юзер: «зааливай все на сервер».
- Feature + точечный plesk (без `/MIR`): 18× `web-studiya/{city}/index.html` (+ mottor-legacy), `hub-city-clean.css`, city/studio webp.
- Commits: feature **`1dc8b067`**, plesk **`4f905053`**.
- Live smoke: astana/almaty/shymkent/petropavlovsk/ust-kamenogorsk/aktau — HTTP 200, clean, без Mottor bundle.
- SEO uniqueness: Title/Desc/H1/regional unique; FAQ-вопросы шаблонные — ок для услуги.

### 2026-08-06 — FIX: вернули 8 направлений на city hubs

- На Almaty + 16 batch было 6 карточек (слияние SEO/AEO, без Лидогенерации). Юзер: «потерял по 2».
- Восстановлен полный набор как у parent/Astana: 01–08 (+ AEO/GEO, Лидогенерация).
- Попутно: починены `class=\"…\"` в `#services` у batch-генератора; CSS сетка 4×2 (`hub-city-clean.css?v=13`).
- Deploy: feature + точечный plesk.

### 2026-08-06 — CLEAN rebuild parent `/web-studiya/dizayn/` (локально, только clean, без деплоя)

- Задача: чистый ребилд родительской страницы «Услуги дизайнера» отдельно от gео-страниц.
- Создан `web-studiya/dizayn/index-clean.html` + `assets/css/dizayn-parent-clean.css`; живой Mottor `index.html` не тронут.
- Cities-блок на parent: заголовок и лейблы переведены с «Дизайн в {город}» на **«Услуги дизайнера в {город}»** (programmatic-seo requirement), 18 ссылок на существующие `dizayn/{slug}/` не менялись.
- Geo-страницы `web-studiya/dizayn/{city}/` (18 шт.) — тогда ещё без gap-fix (см. 2026-08-07).
- Commit/push/deploy не выполнялись — ждём глазами-ОК юзера на swap (см. `HANDOFF-PERF.md` §5.1 G).

### 2026-08-07 — Dizayn Mottor geo: гигантский отступ + rename cities

- Юзер: «на региональных тоже этот отступ гигантский».
- Причина = `data-dizayn-hero-reserve` 280/320px на пустом hero `section_image` (тот же паттерн, что у parent).
- Фикс локально: parent Mottor + 18 geo — выпилен reserve; cities/crumbs «Дизайн» → «Услуги дизайнера».
- Локально: `http://127.0.0.1:8772/web-studiya/dizayn/astana/` — gap ~67px.

### 2026-08-07 — DEPLOY только parent dizayn hub

- Юзер: хаб залить, региональные оставить — будем перерабатывать.
- Прод: clean `/web-studiya/dizayn/`; geo Mottor на https://raskrutov.kz/web-studiya/dizayn/{city}/ без изменений.
