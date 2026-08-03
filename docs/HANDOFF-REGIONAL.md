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

- [ ] Подтвердить: стартуем с **этапа 1 (P1, 15 страниц)** или сразу шире
- [ ] Подтвердить политику URL: legacy geo (`/sozdanie-saitov-v-astane`) vs pretty (`/web-studiya/sozdanie-saitov/astana`)
- [ ] Дать/подтвердить список уникализации контента (город в H1/Title/тексте/кейсах/адресе — что обязательно уникально)
- [ ] Скинуть доступы/материалы по городам (телефон, адрес, 2ГИС), если нужны локальные NAP
- [ ] После генерации этапа 1 — проверить 2–3 URL глазами + Search Console

## 5. Чеклист АГЕНТА

- [ ] Скопировать xlsx в `docs/seo-regional/` (бэкап) + держать CSV актуальными
- [ ] Свести REGIONAL_MATRIX этап 1 → конкретный список URL vs файлы в `site_mirror`
- [ ] Не плодить thin-дубли: уникальные H1/Title/Description + локальные блоки
- [ ] Прогнать пайплайн из `raskrutov-site-pipeline.mdc` (schema, breadcrumbs, alts, audit)
- [ ] Редиректы из листа REDIRECTS → `.htaccess`
- [ ] Деплой через `plesk`, обновить этот handoff + `docs/HANDOFF-PERF.md` §5

---

## 6. Журнал

### 2026-08-03
- Юзер указал на xlsx региональной SEO-карты
- Распарсили листы, выгрузили CSV в `docs/seo-regional/`
- Зафиксировали масштаб: 18 городов × 9 направлений, 152 NEW / 10 UPDATE
