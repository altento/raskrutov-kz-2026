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

## 4. Чеклист ЮЗЕРА

- [x] Подтвердить: стартуем с направления **«Создание сайтов»**
- [x] Подтвердить политику URL: **pretty** `/web-studiya/sozdanie-saitov/{city}`
- [ ] Глазами проверить 2–3 города (Алматы / Астана / Петропавловск) на проде или локально
- [ ] Подтвердить деплой на `plesk` этого пакета
- [ ] Дальше: следующее направление (SEO / веб-студия / …) или уникализация контента глубже (не только H1/Title/Desc)

## 5. Чеклист АГЕНТА

- [x] Скопировать xlsx в `docs/seo-regional/` + CSV
- [x] Решение pretty зафиксировано: `/web-studiya/sozdanie-saitov/{slug}`
- [x] Сгенерировать 18 geo-страниц «Создание сайтов» (`generate_regional_sozdanie.py`)
- [x] 301 legacy `/sozdanie-saitov-v-*` → pretty в `.htaccess` + pages stubs + `url_mapping.json` + sitemap
- [x] Прогнать wire_lead_forms / breadcrumbs / schema / green_zone / fix_site_errors
- [ ] Перелинковка с родителя `/web-studiya/sozdanie-saitov` на города (блок ссылок)
- [ ] Деплой `plesk` после ОК юзера
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
- **Не задеплоено на plesk** — ждём ОК / проверку глазами
