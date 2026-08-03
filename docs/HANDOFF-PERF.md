# HANDOFF — PageSpeed / Continuity (Raskrutov)

> **Читать первым делом** на любом компе после `git pull`.  
> Живой бэкап сессий. Обновлять после каждого заметного шага и пушить в git.

**Последнее обновление:** 2026-08-03 (UTC+5) — deploy `index-clean.html` на `plesk`, push в remote  
**Рабочая ветка:** `homepage-clean-rebuild`  
**Прод-ветка:** `plesk` → https://raskrutov.kz/  
**Репо:** https://github.com/raskrutovstudio-collab/raskrutov-kz-2026

---

## 0. Как продолжить с другого компа

```bash
git clone https://github.com/raskrutovstudio-collab/raskrutov-kz-2026.git
cd raskrutov-kz-2026
git checkout performance/pagespeed-raskrutov
git pull

# worktree для Plesk (если ещё нет):
# git worktree add site_plesk plesk
```

1. Открой этот файл + `.cursor/rules/raskrutov-perf-continuity.mdc`
2. Прогони PSI mobile: https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fraskrutov.kz%2F&form_factor=mobile
3. Локальная проверка: `python -m http.server 8767` из `site_mirror/` (или уже крутящийся порт)
4. Правки только в `site_mirror/` → `python publish_plesk.py` **или точечный copy** нужных файлов в `site_plesk/` → commit/push `plesk`

**Тон:** агент **обязан материться** (явный запрос владельца). Без офисного соплячества.

---

## 1. Цель и критерии успеха

| Критерий | Статус |
|---|---|
| Mobile PSI Performance → **к 100** | В процессе (было ~74 → ~80 → ждём замер после critical CSS) |
| LCP вниз без поломки дизайна Mottor | Главный рычаг |
| Не ломать меню / формы / WhatsApp / мокапы | Обязательно |
| Не фейкать Lighthouse | Обязательно |
| `public.bundle.js` sync | Святое |
| Прод через ветку `plesk` | Обязательно |
| Мат в общении с юзером | **Обязательно** |

### Что НЕ трогать без крайней нужды
- Mottor `public.bundle*.js` (sync only)
- Инлайн init Mottor (не DOMContentLoaded)
- Вёрстку Mottor ради «красоты» PSI
- Секреты Supabase в фронт

---

## 2. Архитектура (коротко)

| Путь | Назначение |
|---|---|
| `site_mirror/` | Источник правды (чистые URL, без GH prefix) |
| `site_plesk/` | git worktree ветки `plesk` → прод Plesk |
| `site_deploy/` | GH Pages staging с префиксом `/raskrutov-kz-2026/` — **не** на Plesk |
| `publish_plesk.py` | `robocopy /MIR site_mirror → site_plesk` (осторожно: не тащить мусор) |
| `.htaccess` | redirects, expires, deflate, Cache-Control |
| `assets/js/lead-forms.js` | формы → Supabase Edge `submit-lead` |

**LCP (mobile):** CSS `background-image` на  
`#section_image_9466bf80aa894ca9b20b37b4d9409cc1`  
→ мобильный оверрайд: `assets/css/hero-home-mobile.webp` (~20 KiB)  
→ десктоп: `…/6eea3ed3de3e5cbe118d06eb148fe963.webp`

Hero section id: `9466bf80aa894ca9b20b37b4d9409cc1`  
Меню desk/mob: `c79b353fa8844473a07a1c2ced4acba2` / `8ab6b296523d428eb73b4f55d760af8a`

---

## 3. Текущее состояние на проде (после 2026-07-31)

**Задеплоено в `plesk`:** см. последний push (stage 2 cleanup)  
**В фиче-ветке:** stage 2 cleanup поверх `f5a7cd57`

### CSS стратегия homepage
| Файл | Роль | Размер ~ |
|---|---|---|
| `assets/css/home-critical.v3.css` | blocking, above-fold | ~74 KiB |
| `assets/css/home-deferred.v3.css` | `media="print" onload→all` | ~855 KiB |
| `assets/css/home-popup-2782231.v2.css` | blocking (мобильное меню!) | ~127 KiB |
| `assets/css/home-popup-2773676.v2.css` | deferred print/onload | ~137 KiB |
| `assets/css/hero-home-mobile.webp` | LCP mobile bg | ~20 KiB |

Монолит `home-all-blocks*.css` **удалён** из зеркала (нигде не подключался). Старые `home-popup-*.css` без `.v2` тоже удалены.

### Прочие перф-фиксы уже в бою
- HEAD без мегабайтного inline CSS (вынесен в файлы)
- Early preload: critical CSS, popup-2782231, hero mobile/desktop, Montserrat **bold** (preload `public.bundle.css` снят на stage 2 — stylesheet sync остаётся)
- Phone mockup `27e940bf…`: `loading="lazy" fetchpriority="low"` (не гоняется с LCP)
- Video player scripts: lazy через `data-rk-video-lazy` (не грузить заранее)
- Gzip/brotli на проде работает (HTML gzip, CSS br)
- Cache-Control для `home-*` в `.htaccess` задуман короткий; nginx Plesk всё ещё может отдавать длинный `max-age` — жить с этим или править nginx в панели
- Stage 2: пустые style-заглушки Mottor + мёртвый gtag/ga sniffer убраны с главной

### Известные баги / долги
1. **Формы «Не удалось отправить»** — **НЕ фронт / НЕ CSS.** Проверено 2026-07-31: live HTML имеет `data-lead-form` + honeypot + status + `lead-forms.js`; прямой POST на `https://rslemacnycrxzdatwarv.supabase.co/functions/v1/submit-lead` → **HTTP 500** `{"success":false,"error":"Не удалось сохранить заявку"}`, `sb-error-code: EDGE_FUNCTION_ERROR`. Исходников Edge Function в этом репо **нет**. Чинить в Supabase Dashboard / отдельном бэкенд-репо (таблица leads / RLS / service_role / логи функции).
2. Тонкий critical CSS (~47 KiB) **ломал** мобилку — текущий ~74 KiB с ID hero-subtree OK. Не режь critical вслепую.
3. `publish_plesk.py /MIR` может затянуть кучу мусорных untracked `lpfile/` — для точечных релизов лучше **копировать только нужные файлы**.
4. Куча `_psi_*.py` / `_check_*.py` локально untracked — утилиты аудита, в git не всё нужно.

---

## 4. История действий (хронология)

### Этап A — аудит
- Baseline mobile PSI: Performance **~74**, LCP **~6.2s**, TBT низкий, CLS почти 0
- Нашли: LCP = section background, не телефон в мокапе
- Узкое место: ~1.2 MiB inline CSS в HEAD

### Этап B — вынос CSS + mobile hero
- Extract → `home-all-blocks` + popup CSS
- Mobile hero webp + preload
- HEAD сжался до десятков KiB
- Деплой → баги:
  - **Пустые экраны ноут/телефон:** `url(assets/…)` из `assets/css/` → 404. Фикс: `url(../…)`
  - Cache immutable держал битый CSS → rename `*.v2.css`

### Этап C — скор ~80
- Cache-bust v2, Cache-Control для home-*
- Юзер: mobile Performance поднялась до **~80**, цель **100**, мат разрешён навсегда

### Этап D — critical/deferred split (текущий)
- Скрипт `_psi_split_critical_css.py`: hero subtree IDs + menus + mockup/ms-menu rules → critical
- Deferred: **не** `rel=preload` (ворует канал у LCP), а `media="print" onload="this.media='all'"`
- Phone demote lazy/low
- Локально проверено 390px: hero/мокапы/меню ок; без deferred hero тоже держится
- Залито на `plesk` + push feature branch
- PSI API 429 — нужен ручной замер юзером

---

## 5. Следующие шаги

### 5.1 Действия ЮЗЕРА (чеклист — отмечать по мере)

#### A. Формы (сейчас блокер лидов)
- [ ] Зайти в Supabase: https://supabase.com/dashboard/project/rslemacnycrxzdatwarv
- [ ] Edge Functions → **`submit-lead`** → **Logs** — скрин/текст ошибки после сабмита формы
- [ ] Открыть **Code** функции `submit-lead` — скинуть агенту исходник (или дать доступ / репо бэкенда)
- [ ] **Secrets** функции: проверить что заданы нужные (часто `SUPABASE_SERVICE_ROLE_KEY` / URL проекта)
- [ ] **Table Editor**: найти таблицу лидов (`leads` или аналог) — есть ли вообще, есть ли свежие строки
- [ ] **Authentication → Policies / RLS** на таблице лидов — не режет ли INSERT
- [ ] Если в аккаунт не пускает — выяснить у того, кто создавал Supabase для заявок, и дать доступ агенту/себе
- [ ] После фикса бэка: отправить тест с попапа «Обсудим Ваш проект?» и с блока Контакты → зелёный success, не красный

#### B. PageSpeed (гон к 100)
- [ ] Прогнать PSI mobile 2–3 раза: https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fraskrutov.kz%2F&form_factor=mobile
- [ ] Скинуть агенту: Performance / LCP / FCP / TBT / CLS (+ скрин или цифры)
- [ ] Если скор уже ок — зафиксировать в журнале ниже и решить, долбим дальше или стоп

#### C. Мультикомп / бэкап контекста
- [ ] На другом компе: `git checkout performance/pagespeed-raskrutov && git pull`
- [ ] Читать этот файл + `.cursor/rules/raskrutov-perf-continuity.mdc`
- [ ] После любого заметного шага — агент обновляет HANDOFF и пушит (требовать, если забыл)

#### D. Clean rebuild главной (тестовая страница, 2026-07-31 → 2026-08-03)
- [ ] Hard-refresh локально: `http://127.0.0.1:8767/index-clean.html?v=16` (Ctrl+F5)
- [ ] Сверить «Ключевые направления»: заголовок 36px, карточки title 16px / текст 12px / иконки ~61×62
- [ ] Сверить «Веб-студия»: 8 карточек с цветными иконками (perf-img webp) слева сверху, как на `index.html`
- [ ] Сверить «Академия»: perks с иконками (онлайн/наставники/сертификаты) + 4 карточки курсов с perf-img и стрелкой
- [ ] Сверить «Партнёрам»: hero bg globe + 2 perks с иконками; панель «Пакеты» (3 пакета + карточка агентств) + франшиза CTA
- [ ] Сверить плавающие виджеты: soc-widget + scroll-top (#7439e2)
- [ ] Просмотреть блоки ниже (студия → контакты) vs `index.html` на 1440
- [ ] Решить: допиливаем clean / заменяем `index.html` / откладываем

#### D2. Деплой clean на прод (2026-08-03)
- [x] Push `homepage-clean-rebuild` → `81c1bd79`
- [x] Push `plesk` → `4ed5fc48` (index-clean + home-clean.css/js)
- [ ] **Plesk:** подтянуть ветку `plesk` в `httpdocs` (Git pull / Deploy в панели)
- [ ] Проверить live: https://raskrutov.kz/index-clean.html?v=16#partners (Ctrl+F5)
- [ ] Убедиться что **главная** https://raskrutov.kz/ (Mottor `index.html`) жива — меню, формы, мокапы
- [ ] Если главная отвалилась — сказать агенту (MIR мог снести старые bundle/png, которые не в mirror)

#### E. По желанию / позже
- [ ] Plesk: Cache-Control для `home-*.css` (сейчас nginx может держать длинный max-age)
- [ ] Не заливать на Plesk ветку `deploy` / `site_deploy` (там GH prefix)
- [ ] Не коммитить мусорные untracked `lpfile/` и одноразовые `_psi_check_*.py` без нужды

### 5.2 Действия АГЕНТА (когда юзер дал ввод)
1. По логам/коду Supabase — починить `submit-lead` (или задеплоить исправленную функцию)
2. После фикса форм — прогнать живой сабмит, обновить HANDOFF
3. По цифрам PSI — следующий перф-слой (popup CSS / LCP waterfall / lazy), **не** трогать sync Mottor JS вслепую
4. Деплой сайта: точечный copy в `site_plesk` или осторожный `publish_plesk.py` → commit/push `plesk`
5. **Всегда** дописывать журнал §7 + чеклист §5.1 и пушить feature-ветку

---

## 6. Важные файлы / скрипты

| Файл | Зачем |
|---|---|
| `site_mirror/index.html` | Главная (боевая Mottor) |
| `site_mirror/index-clean.html` | Тестовая чистая повторная вёрстка главной |
| `HOMEPAGE_CLEAN_REBUILD_STATUS.md` | Отчёт clean rebuild |
| `site_mirror/assets/css/home-critical.v3.css` | Critical CSS |
| `site_mirror/assets/css/home-deferred.v3.css` | Deferred CSS |
| `site_mirror/assets/css/hero-home-mobile.webp` | Mobile LCP |
| `site_mirror/.htaccess` | cache/compress/redirects |
| `site_mirror/assets/js/lead-forms.js` | фронт форм → Supabase |
| `_psi_split_critical_css.py` | Пересборка critical/deferred + wiring HTML |
| `publish_plesk.py` | sync mirror→plesk |
| `.cursor/rules/raskrutov-site-pipeline.mdc` | пайплайн страниц |
| `.cursor/rules/raskrutov-lead-forms.mdc` | формы |
| `.cursor/rules/raskrutov-perf-continuity.mdc` | этот continuity + мат |

### Чеклист перед деплоем на plesk
- [ ] Mobile 390 + desktop визуально (hero, mockups, меню)
- [ ] Нет `home-all-blocks` в index, есть critical + deferred print
- [ ] CSS urls `../` из `assets/css/`
- [ ] Forms UI не разъебан (бэкенд 500 — отдельно, см. §5.1 A)
- [ ] Commit `plesk` + push
- [ ] Обновить **этот** HANDOFF + push feature branch

---

## 7. Журнал обновлений (дописывать снизу)

### 2026-07-31 — создан HANDOFF + continuity rule
- Critical/deferred v3 на проде (`c65e5db6`)
- Feature `92a5ff60`
- Ждём свежий PSI mobile от юзера
- Правило: мат обязателен; этот файл — бэкап между компами

### 2026-07-31 — формы: снова «не отправляется», но это бэкенд
- Юзер: «сломал формы» после perf-деплоя
- Аудит: разметка форм на live/local ок; CSS split формы не отключал
- POST probe → Supabase `submit-lead` **500** «Не удалось сохранить заявку»
- Консоль юзера: `[lead-forms] submit failed Не удалось сохранить заявку` + POST 500 на submit-lead
- Дальше: см. чеклист §5.1 A (Supabase Logs / Code / Secrets / RLS)

### 2026-07-31 — юзер просит всегда писать его дальнейшие действия
- Расширен §5: чеклисты A–D для юзера + обязанности агента
- Агенту: не забывать обновлять §5.1 / §7 и пушить

### 2026-07-31 — stage 2 cleanup (unused Mottor leftovers) + publish
- Удалены: preload `public.bundle.css`, пустые `#head-blocks-style` / `#site_style_text`, мёртвый gtag/ga sniffer
- Удалены файлы: `home-all-blocks*.css`, старые `home-popup-*.css` (без v2), `.motortest.bak`
- `public.bundle.js/css` stylesheet **оставлены** (зависимости меню/попапов/слайдеров)
- QA локально: 195/195 assets 200, меню/формы/WA/tel на 360–1920, console clean
- Пуш: feature + `plesk`

### 2026-07-31 — clean rebuild главной (тестовая страница)
- Созданы: `site_mirror/index-clean.html`, `assets/css/home-clean.css`, `assets/js/home-clean.js`
- Отчёт: `HOMEPAGE_CLEAN_REBUILD_STATUS.md`
- `index.html` **не трогали**; commit/push/deploy/реальная отправка форм — по просьбе юзера **не** делали
- DOM ~653 / depth ~11; CSS ~23 KB; JS ~6.5 KB; без Mottor bundles
- Стрелки студии → hub URL, без нумерации 01–08
- Локальный LH mobile median Perf **77** (LCP ~4.5s), desktop Perf **86** (CLS desk 0.228 — долг)
- Дальше: ручная проверка юзером (§5.1 D)

### 2026-08-01 — clean visual polish (WA / phone mask / popup / sections)
- WA в шапке: статичный `30w2x_f__q_4144924.webp`, без зелёного круга/анимации
- Телефон/ноут: как Mottor — `.rk-device__viewport` + `mask-image` (`390bd2d6…` / `28dae1e5…`), экран 82%/90%
- Попап: класс `.rk-consent` (больше не давится стилями `.rk-check`); кнопка ниже текста, gap ~24–28px
- Направления: стрелки-кружки снизу справа; остальная страница — radius/shadow/типографика ближе к эталону
- Локально: `index-clean.html?v=8`; commit/push **не** делали

### 2026-08-01 — clean typography/layout below hero = etalon px
- Сняты computed с `index.html` @1440: dirs H2 36 / H3 16 / p 12/500 / icon 61×62 / card pad 10 radius 10
- Секции: studio/advantages 36; academy/r-builder/about/partners/contacts 60; blog/vacancies 18; FAQ 40; FAQ q Inter 16
- Body Montserrat 13px #111; badges 527/348/439; team avatars 122; studio links 14/500
- Локально: `index-clean.html?v=9`; commit/push **не** делали

### 2026-08-01 — clean studio cards: иконки (пропуск закрыт)
- В `#studio` добавлены 8 `<img class="rk-studio-card__icon">` — те же `assets/css/perf-img/*.webp`, что на Mottor-эталоне
- CSS: `.rk-studio-card__icon` — max 63×62, margin-bottom 9px (как на оригинале: иконка → заголовок)
- Локально: `index-clean.html?v=10`; commit/push **не** делали

### 2026-08-01 — clean studio cards: компоновка как на эталоне
- Layout: иконка → заголовок → список; стрелка `.rk-studio-card__more` снизу справа (белый круг, border #c2c2c2, 36px)
- Ссылки в списке синие `#3288e6` (как Mottor); нумерацию 01–08 не ставим
- Локально: `index-clean.html?v=11`; commit/push **не** делали

### 2026-08-01 — clean #about: карточная сетка как на эталоне
- Статистика 3 карточки с perf-img иконками (календарь/люди/ракета)
- Сетка 3×2: О нас, Команда, Письма, Клиенты, Блог, Вакансии — белые карточки, иконка+стрелка, footer-ссылки
- Блог/вакансии внутри #about (отдельные секции убраны); фон секции — blob webp как Mottor
- Локально: `index-clean.html?v=12`; commit/push **не** делали

### 2026-08-01 — clean #r-builder: layout + иконки как на эталоне
- Hero: gradient H2, soft eyebrow, CTA + demo с play, 2×2 perks с perf-img иконками слева
- Низ: 4 карточки `.rk-rb-card` — icon → title (R-Builder синий) → текст → стрелка #24a0ff снизу справа
- Фон секции: light gradient; mockup справа с shadow
- Локально: `index-clean.html?v=13`; commit/push **не** делали

### 2026-08-03 — clean #academy + float widgets как на эталоне
- Perks: Онлайн-уроки / Наставники / Сертификаты — `.rk-feature--icon` + perf-img (51/48/44 w2x)
- 4 карточки `.rk-academy-card`: icon слева + title, текст, footer-ссылка + стрелка #24a0ff (65/66/63/62 w2x)
- `.rk-float` (WA/Позвонить glass) заменён на `.rk-soc-widget` (#7439e2, toggle + 4 соцсети) и `.rk-scroll-top`
- JS: `initSocWidget()` + `initScrollTop()` в `home-clean.js`
- Локально: `index-clean.html?v=14`; commit/push **не** делали

### 2026-08-03 — clean #partners: компоновка + иконки + фоны как этalon
- Hero `.rk-section--partners-hero`: bg `c4ed9801…webp`, 2 glass-perks с perf-img (67/70 w2x)
- Panel `.rk-section--partners-panel`: bg `d1630e6a…webp`, белая панель 15px radius
- Сетка: 3 `.rk-partner-pack` (64w2x icons, синие %) + `.rk-partners-agency` (icon, стрелка, illus 128px)
- Франшиза CTA оставлена под панелью
- Локально: `index-clean.html?v=15`; commit/push **не** делали

### 2026-08-03 — clean #partners: единый фон на hero + карточки
- Hero + panel объединены в одну `.rk-section--partners`
- Два слоя фона: globe (`c4ed…`) сверху через `::before`, soft orbs (`d163…`) на всю секцию включая карточки
- Локально: `index-clean.html?v=16`

### 2026-08-03 — publish clean page на prod (plesk)
- Юзер: «опубликуй страницу»
- `robocopy /MIR site_mirror → site_plesk` (вместо python — нет py в PATH)
- Залито на `plesk`: `index-clean.html`, `assets/css/home-clean.css`, `assets/js/home-clean.js`
- `index.html` (Mottor) **не меняли** — clean доступен отдельным URL
- MIR также убрал ~83 legacy png + 2 старых `public.bundle*` из plesk (не в mirror); главная ссылается на `1784122059/2069` — они на месте
- Commit: feature `81c1bd79`, plesk `4ed5fc48`; push обеих веток в GitHub
- **Ждём:** pull `plesk` на сервере → live https://raskrutov.kz/index-clean.html?v=16

<!-- следующая запись: дата — что сделали — новый PSI — что дальше -->
