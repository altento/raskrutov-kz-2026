# HANDOFF — PageSpeed / Continuity (Raskrutov)

> **Читать первым делом** на любом компе после `git pull`.  
> Живой бэкап сессий. Обновлять после каждого заметного шага и пушить в git.

**Последнее обновление:** 2026-08-04 — SEO EXCLUDED из perf-трека; active scope **57**  
**Рабочая ветка:** `performance/pagespeed-raskrutov`  
**Прод-ветка:** `plesk` → https://raskrutov.kz/  
**Репо:** https://github.com/raskrutovstudio-collab/raskrutov-kz-2026

> **Geo perf scope:** hubs + sozdanie + dizayn = **57**.  
> **`/web-studiya/seo-prodvizhenie/**` = EXCLUDED / OWNED BY ANOTHER EMPLOYEE** (не трогать, не PSI).

> **Важно:** живая главная = **clean rebuild** (`rk-clean`, `home-clean-*.css`), не старый Mottor `index.html`.  
> Mottor-копия сохранена как `site_mirror/index.mottor-legacy.html`.

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
| Mobile PSI Performance → **к 100** | Homepage **99**. Sozdanie peak **86** (CLS pass); menu-lite откатили после просадки lab |
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
- [x] Прогнать PSI mobile после деплоя critical CSS — **99** (2026-08-03)
- [ ] Ещё 1–2 прогона для стабильности (лаб гуляет ±1–2)
- [ ] Глазами: hero/ecosystem/меню на мобилке без FOUC
- [ ] Решить: долбим до ровной 100 или стоп
- [x] **Sozdanie mobile:** hotfix `9e68614b` — с **53 → 86** (было из‑за width=1920)
- [ ] Решить: clean-rebuild sozdanie (как home) vs жить с Mottor-потолком ~80–90
- [x] **/web-studiya/ mobile POST-DEPLOY:** clean swap → **90+**, отдельный прогон дал 89 (2026-08-05, юзер)
- [ ] **ЗАВТРА (после сброса квоты PSI):** сказать агенту запустить `python _psi_studiya_median.py` — медиана из 5 прогонов
- [ ] Опционально, чтобы 429 больше не ловить: завести бесплатный **PSI API key** (Google Cloud Console → APIs → включить «PageSpeed Insights API» → Credentials → API key) и отдать агенту
- [ ] **/web-studiya/:** по медиане решить — добивать до 100 или стоп / следующий URL
- [ ] **/web-studiya/:** если пилим дальше — скинуть desktop + CWV (FCP/LCP/TBT/CLS)


#### C. Мультикомп / бэкап контекста
- [ ] На другом компе: `git checkout performance/pagespeed-raskrutov && git pull`
- [ ] Читать этот файл + `.cursor/rules/raskrutov-perf-continuity.mdc`
- [ ] После любого заметного шага — агент обновляет HANDOFF и пушит (требовать, если забыл)

#### D. Региональное размножение / geo perf (active scope **57**)
- Полный handoff: **`docs/HANDOFF-REGIONAL.md`**
- Карта: `docs/seo-regional/SEO-карта_Raskrutov_региональная_2026-07-27.xlsx` + CSV
- **SEO-направление (`/web-studiya/seo-prodvizhenie/**`) — EXCLUDED / OWNED BY ANOTHER EMPLOYEE**  
  Не оптимизировать, не QA, не PSI. Опубликованный SEO-код **не откатывать**.
- Active: 18 hubs + 18 sozdanie + 18 dizayn + 3 parents = **57**
- [x] Старт: sozdanie + хабы + dizayn (pretty) — задеплоены; SEO тоже на проде, но **вне этого perf-трека**
- [x] Visual QA representatives (hub/sozdanie/dizayn) — см. `reports/geo-pages-performance-final.md`
- [x] Mobile H1 hub FIXED; SEO H1 fix на проде — чужая зона
- [x] Commit/push/deploy CSS-extract — feature `193f7e04`, plesk `a424184b`
- [ ] PSI mobile/desktop — **QUOTA BLOCKED** (429 на anonymous API 2026-08-04); ручной замер через pagespeed.web.dev — см. `reports/geo-pages-performance-final.md`; **без seo-prodvizhenie**
- [ ] Дальше P2 регионалки — по `HANDOFF-REGIONAL.md` (SEO-страницы пишет другой сотрудник)
- [ ] ~~Astana hub orange 2026-08-06~~ — **отменено** (не в стиле хаба)
- [ ] **Astana hub purple/hub-aligned 2026-08-06:** глазами `http://127.0.0.1:8771/web-studiya/astana/` на 390/768/1440 → approve → commit/push/plesk (v4: карточки/hero как у хаба; самодельная каша убрана)
- [ ] После отдельного ОК: точечный deploy Astana/Almaty HTML + hub-city-clean.css, затем PSI mobile медианой (без SEO geo)
- [x] **Almaty hub CLEAN 2026-08-06:** глазами http://127.0.0.1:8771/web-studiya/almaty/ 390/768/1440 → approve → commit/push/plesk
- [x] **All 18 clean city hubs DEPLOY 2026-08-06:** юзер «зааливай» → feature + точечный plesk; глазами sample на https://raskrutov.kz/web-studiya/{city}/
#### E. По желанию / позже
- [ ] Plesk: Cache-Control для `home-*.css` (сейчас nginx может держать длинный max-age)
- [ ] Не заливать на Plesk ветку `deploy` / `site_deploy` (там GH prefix)
- [ ] Не коммитить мусорные untracked `lpfile/` и одноразовые `_psi_check_*.py` без нужды


#### F. CLEAN `/web-studiya/` index-clean (2026-08-05, локально, без swap)
- [ ] Глазами сверить index-clean vs donor (1440/390) — reports/web-studiya-clean/
- [ ] Approve swap: index.html ← index-clean.html (+ rename mottor → index.mottor-legacy.html)
- [ ] После approve: commit/push feature + точечный plesk deploy /web-studiya/
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
| `site_mirror/index.html` | Главная |
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

### 2026-08-03 — региональная SEO-карта подключена к continuity
- Источник: Downloads `SEO-карта_Raskrutov_региональная_2026-07-27.xlsx`
- Выгрузка + handoff: `docs/seo-regional/`, `docs/HANDOFF-REGIONAL.md`
- Масштаб: 18 городов × 9 направлений, 152 NEW / 10 UPDATE
- Следующее от юзера: подтвердить этап 1 + политику URL (см. §5.1 D)

### 2026-08-03 — geo «Создание сайтов» pretty (локально)
- 18 URL `/web-studiya/sozdanie-saitov/{city}` + 301 с legacy
- Ждём проверку глазами и ОК на plesk (см. `HANDOFF-REGIONAL.md`)

### 2026-08-03 — деплой geo + UI на plesk
- Push `plesk` `b11c88ce` (после rebase на remote hero/clean homepage)
- Live smoke: Astana/parent, rk-cities, 301 legacy, case URLs

### 2026-08-03 — PageSpeed: clean homepage baseline + critical split
- Live homepage = **clean** (`home-clean.css`), не Mottor. Baseline mobile PSI **73** (LCP 4.8, FCP 3.3, TBT 0)
- Главный аудит: render-blocking `home-clean.css` (~1.8s) + fonts Inter/Open Sans в критическом пути + ecosystem `fetchpriority=high`
- Сделано: `home-clean-critical.v1.css` (~14 KiB) + `home-clean-deferred.v1.css` (print/onload); lead-forms.css deferred; Metrika после `load`+idle; ecosystem `fetchpriority=low` + mobile webp; scroll rAF
- Mottor index → `site_mirror/index.mottor-legacy.html`; clean index синкнут в `site_mirror/`
- Деплой `plesk` `15cfcd90` + feature `d16cd0de`
- **PSI mobile после деплоя: Performance 99** (FCP 1.0 / LCP 2.0 / TBT 10 / CLS 0.001). Ссылка: https://pagespeed.web.dev/analysis/https-raskrutov-kz/0rvrfexh7h?form_factor=mobile
- Дальше: дожать до 100 (мелочи image delivery / font) или стоп по команде юзера

### 2026-08-03 — sozdanie + 18 geo: Mottor CSS extract (как на home)
- Baseline parent mobile PSI **66** (LCP 7.8 / FCP 2.6 / CLS 0.124)
- HEAD был ~566 KiB inline CSS → вынесено: `sozdanie-critical.v1.css` (~48 KiB) + deferred/extra/popup; HEAD ~10 KiB
- LCP preload починен на реальный hero bg `00e5f308…webp`; video players → lazy; `public.bundle.js` sync
- Применено к parent + 18 geo; деплой `plesk` `0bcb2ee9`
- Скрипты: `_psi_opt_sozdanie.py`, `_psi_fix_sozdanie_perf.py`
- **PSI mobile после деплоя: 82** (FCP 1.7 / LCP 2.3 / TBT 250 / CLS 0.218). Было 66 / LCP 7.8
- Ссылка: https://pagespeed.web.dev/analysis/https-raskrutov-kz-web-studiya-sozdanie-saitov/aa0x6tppqr?form_factor=mobile
- Дальше: CLS (hero reserve / dims), image delivery; TBT упирается в sync `public.bundle.js`


### 2026-08-03 — sozdanie CLS pass 2
- width/height на img; hero min-height 640 mobile; Montserrat+fallback в critical; rk-cities jpeg сжаты
- Mottor CDN src recipes не ломать (scale/x3/1920 обязателен)
- plesk 869edcd1


### 2026-08-03 — sozdanie menu-lite split
- Blocking popup-menu 110KiB → menu-lite ~58KiB + deferred heavy; plesk e43a0cbc


### 2026-08-03 — sozdanie: menu-lite FAIL → revert
- menu-lite дал lab **59** (LCP 10.8) — откат на full popup-menu blocking `f81563e1`
- Рабочий пик: **86** после CLS dims/hero/cities (869edcd1)
- Потолок без clean-rebuild / без defer Mottor JS: TBT+bundle

### 2026-08-03 — sozdanie hotfix после регрессии ~53
- Юзер: mobile PSI **53** на `/web-studiya/sozdanie-saitov/`
- Причина: pass2 повесил `width="1920" height="1152"` на галерею; при deferred CSS браузер рисовал гигантский layout → LCP/CLS в жопу
- Фикс: сняли все img width/height; hero reserve 280/360 вместо 520/640; parent+18 geo
- `plesk` **`9e68614b`** (live: `w1920=0`, soft reserve ок)
- **PSI mobile после hotfix: 86** (FCP 2.5 / LCP 3.1 / TBT 20 / CLS 0.11)
- Ссылка: https://pagespeed.web.dev/analysis/https-raskrutov-kz-web-studiya-sozdanie-saitov/r1gftbmx9y?form_factor=mobile
- Дальше: к ~100 нужен **clean sozdanie** как home; Mottor потолок ~80–90 (CLS 0.11 ещё кусает)

### 2026-08-03 — sozdanie CTA: убрать «Написать» + починить попап
- «Написать» (`eb58a54c…`, sectionScroll) выпилен с parent+18 geo
- «Получить консультацию»: Mottor `msJsWrapper(...,'showPopup')` → `ReferenceError: showPopup is not defined`; переведено на `showSectionPopup(popupId)` (8 кнопок/страница)
- `plesk` **`670e6a92`**; live smoke: Napisat gone, popup `open`

### 2026-08-03 — регионалка: пакет SEO geo (локально)
- 18× `/web-studiya/seo-prodvizhenie/{city}` + 301 legacy `seo-prodvizhenie-sajtov-v-*`
- См. `HANDOFF-REGIONAL.md`; ждём QA глазками → деплой plesk

### 2026-08-03 — регионалка: хабы `/web-studiya/{city}`
- 18 хабов + parent cities grid; `generate_regional_hubs.py` + `_pipeline_hubs_geo.py`
- Точечный деплой на `plesk` (хабы + parent + sitemap)
- Детали: `HANDOFF-REGIONAL.md`. Дальше P2 (dizayn/PPC…) или QA глазками

### 2026-08-03 — регионалка: дизайн `/web-studiya/dizayn/{city}`
- 18 geo + parent cities; hubs wired на geo; `generate_regional_dizayn.py`
- Деплой `plesk` точечно. Дальше: контекст/лидоген/…

### 2026-08-03 — geo perf: CSS-extract hub/seo/dizayn + visual QA (локально, без commit)
- Extract critical/deferred/popup/extra на **57** страниц (19 hub + 19 seo + 19 dizayn); sozdanie уже было
- HTML: hub/seo ~379 KiB HEAD ~9; dizayn ~420 / ~9; `public.bundle.js` sync
- Visual QA: Astana hub / Almaty sozdanie / Shymkent seo / Petropavlovsk dizayn × 360–1920
- Вердикт: **PASS WITH WARN** — на hub+seo mobile H1 `display:none`, виден Mottor «полного цикла…» (контент, не CSS)
- Popup/меню/формы/FAQ/0×404 sampled — ок; CLS формальный → Lighthouse
- Отчёты: `reports/geo-pages-performance-final.md`, `geo-pages-visual-qa-matrix.md`
- **PSI = POST-DEPLOY**; commit/push/deploy **не** делали (ждём команду юзера)

### 2026-08-04 — mobile H1 FIXED (hub + seo geo)
- Причина: Mottor `@media(max-width:500px)` — `.blk-data--pc` hide / `.blk-data--mobile370` show
- Фикс: `<style data-rk-mobile-h1-fix>` на 18 hub + 18 seo cities (блок `b-aa35398c…`); CSS-extract не трогали
- QA: Astana + Shymkent @360/390/430 — гео-H1 visible, дубль hidden; sozdanie/dizayn не трогали
- Скрипт: `_fix_mobile_h1_geo.py`; отчёты обновлены → **PASS / FIXED**

### 2026-08-04 — COMMIT + DEPLOY geo CSS-extract + mobile H1
- Feature `performance/pagespeed-raskrutov` **`193f7e04`**: 87 files (57 HTML + 15 CSS + reports/scripts/HANDOFF)
- Plesk **`a424184b`**: точечный copy 72 site files (без akademiya/crm MIR)
- Live: Astana / sozdanie Almaty / seo Shymkent / dizayn Petropavlovsk → **HTTP 200**; critical CSS на проде; hub+seo `data-rk-mobile-h1-fix` live
- Дальше: **PSI POST-DEPLOY**

### 2026-08-04 — SEO EXCLUDED из performance-трека
- Юзер: SEO (`/web-studiya/seo-prodvizhenie/**` + seo-*.css) передан **другому сотруднику**
- Статус: **EXCLUDED / OWNED BY ANOTHER EMPLOYEE**
- Не менять / не оптимизировать / не PSI / не visual QA SEO
- Уже залитый SEO-код **не откатывать**
- Active perf-scope: **57** = hubs 18 + sozdanie 18 + dizayn 18 + parents 3
- Отчёты обновлены: `geo-pages-performance-final.md`, visual-qa-matrix; commit/push/deploy **не** делать

### 2026-08-04 — FIX mockup white screens (hub CSS paths)
- Симптом: `/web-studiya/astana/` — рамки ноут/телефона есть, экраны белые после CSS-extract
- Причина: в `hub-*.v1.css` `url(../assets/m-files...)` → резолв в `/assets/assets/...` → 404 на mask SVG/webp
- Фикс: `url(../assets/` → `url(../` в hub CSS; `normalize_css_urls()` в `_psi_opt_geo_templates.py` усилен
- sozdanie/dizayn путей `../assets/` не имели; SEO не трогали
- QA HTTP: Astana / sozdanie Almaty / dizayn Petropavlovsk — экраны/графика ок; PSI **не** гоняли
- Отчёт: `reports/geo-pages-visual-qa-matrix.md`; commit/push/deploy **не** делать

### 2026-08-04 — PSI POST-DEPLOY: smoke-check PASS / API QUOTA BLOCKED

- **Smoke-check (4 representative):** HTTP 200 на всех; critical CSS ✅; H1 ✅; canonical ✅; lead_form ✅; mobile H1 fix на hubs ✅; webp-ссылки ✅
- **PSI API:** HTTP 429 на первом же запросе — anonymous quota исчерпана
- Затронутые URL: astana hub / almaty sozdanie / petropavlovsk dizayn / web-studiya parent — все QUOTA BLOCKED
- Остальные 53 URL — NOT RUN
- **Показатели не выдуманы** — таблица PSI PENDING
- Ручной замер: pagespeed.web.dev — см. `reports/geo-pages-performance-final.md` (ссылки + инструкция)
- Отчёт обновлён: `reports/geo-pages-performance-final.md`
- Commit/push/deploy — не выполнялись

### 2026-08-05 — ДЕПЛОЙ 8e992322 ВЫПОЛНЕН / КОНТРОЛЬНЫЙ PSI CHECK (API 429)

- **Commit:** `8e992322` на ветке `plesk` (точечно 57 HTML, 13 WebP, 1 CSS).
- **Production QA:** 4 репрезентативные страницы проверены на проде — **104 / 104 ассетов HTTP 200 OK, 0 ошибок 404**.
- **PSI API статус:** **HTTP 429 (QUOTA BLOCKED)**. Автоматические запросы остановлены.
- **Дальше:** Ручной 3-кратный замер (Mobile & Desktop, 20–30 с интервал) в интерфейсе `pagespeed.web.dev` по подготовленным ссылкам.
- **Не затронуто:** Новые коммиты, деплои и изменения кода не выполнялись. SEO-ветка не затрагивалась.

### 2026-08-05 — CLEAN /web-studiya/ index-clean (локально, без swap)

- SOURCE: https://m65176a2c628d6.lpmotortest.com/web-studiya
- TARGET preview: site_mirror/web-studiya/index-clean.html (Mottor index.html НЕ трогали)
- CSS: assets/css/studio-clean.css + reuse home-clean-critical/deferred
- JS: home-clean.js + lead-forms.js
- Cities: 18 webp from RAR → assets/img/cities/
- Studio assets: assets/img/studio/ (hero-bg, hero-laptop, adv-01..04)
- Header / nav / sticky CTA (Позвонить+WhatsApp) / soc-widget — с главной
- Forms: data-lead-form, names «Студия — контакты…» / «Студия — попап…»
- Screenshots: reports/web-studiya-clean/donor-*.png, local-*.png
- LH mobile median lab: Perf 29 / FCP 4.5s / LCP 6.9s / TBT ~14s / CLS 0.026 (локальный simulate; не прод; TBT раздут home-deferred+third-party — не фейк 90+)
- Diagnosis: reports/web-studiya-clean/lh-diagnosis.md (from lh-mobile-2.json)
- Commit/push/deploy/swap index → НЕ делали (ждём approve юзера)

### 2026-08-05 — SWAP + DEPLOY clean /web-studiya/ (approve юзера получен)

- Юзер сказал «делай как надо» → выполнен swap боевой страницы.
- Swap в `site_mirror/web-studiya/`: `index.html` (Mottor 391 KiB) → `index.mottor-legacy.html`; clean 50 KiB → `index.html` (через `git mv`, история сохранена).
- URL `/web-studiya/` не меняется → sitemap/redirect/.htaccess/canonical трогать не нужно.
- Feature `performance/pagespeed-raskrutov`: коммит swap поверх `a7a901fb`.
- Plesk: точечный copy (index.html + index.mottor-legacy.html + studio-clean.css + img/cities + img/studio) в `site_plesk`, commit/push ветку `plesk`. **Без** `/MIR` (чтобы не тащить untracked geo-мусор).
- Plesk-пуш выполнен шелл-агентом: коммит `01f8e6ec` (26 файлов: index.html + studio-clean.css + 18 cities + 6 studio), rebase поверх Astana `e02fd250`, push `e02fd250..01f8e6ec`.
- Prod smoke `https://raskrutov.kz/web-studiya/`: HTTP 200, отдаётся clean (rk-clean, studio-clean.css, без public.bundle/GH-префикса). **42/42 картинки грузятся, 0 битых, 18/18 городов ок** (был кратковременный лаг пропагации бинарников — прошёл). Sticky Позвонить/WhatsApp, крошки, hero-laptop, формы на месте.
- PSI: POST-DEPLOY, мерить руками на живом URL (API ранее 429). Lab-число Perf 29 было раздуто локальной машиной (8×http.server+node+chrome) — не показатель прода.

### 2026-08-05 — PSI mobile /web-studiya/ POST-DEPLOY: стабильно 90+

- Юзер прогнал живой `https://raskrutov.kz/web-studiya/` на mobile PageSpeed — **Performance стабильно 90+**.
- Подтверждает: clean-rebuild (без Mottor `public.bundle`) работает на проде; локальный lab Perf 29 был мусором.
- Desktop / точные CWV (FCP/LCP/TBT/CLS) юзер не скинул — при необходимости дозамерить.
- Дальше: решить, долбим до ровной 100 на студии или стоп / следующий URL.

### 2026-08-05 — PSI 89 vs 90+: это шум, замер медианы ОТЛОЖЕН (квота 429)

- Юзер: следующий прогон дал **89** после 90+. Это **не регресс** — разброс лаборатории.
- Причины качелей: PSI крутится на общих гугловых раннерах с плавающим CPU (±3–5 баллов норма); балл округляется (89.5→90); веса TBT 30% / LCP 25% / CLS 25% — дёрнулся TBT на ~150 мс, уехало несколько баллов.
- Главный источник разброса на этой странице: **Яндекс.Метрика с `webvisor: true`**. Уже отложена по-человечески (`requestIdleCallback` после `load`, timeout 4000 мс, см. `site_mirror/web-studiya/index.html`), но на медленном эмулированном CPU таймаут иногда влезает **внутрь** окна замера → TBT скачет → 89 vs 92.
- Решение юзера: мерить **медиану из 5 прогонов**, а не верить одиночному числу.
- **БЛОКЕР:** PSI API отдаёт `HTTP 429 Quota exceeded ... 'Queries per day'` на анонимной квоте → автозамер невозможен. Веб-морда `pagespeed.web.dev` при этом работает (жрёт другую квоту).
- Юзер выбрал: **ждать сброса суточной квоты**, замерить позже.
- Готово к запуску: `_psi_studiya_median.py` — 5 прогонов mobile по `https://raskrutov.kz/web-studiya/`, считает медиану score + FCP/LCP/TBT/CLS/SI, пишет `reports/web-studiya-clean/psi-mobile-median.json`. Провалившиеся прогоны не выдумывает.
- Варианты «навсегда убрать 429» (юзер пока не выбрал): бесплатный PSI API key в Google Cloud → подставить в скрипт.
- Оптимизации под балл **не делали** — сначала честные цифры, потом резать.

### 2026-08-05 — PILOT clean hub Astana (index-clean, без swap)

- Задача: programmatic SEO + clean migration для регионального хаба `/web-studiya/astana/`.
- SOURCE/донор визуала: clean parent `/web-studiya/` (+ токены home-clean). Mottor `astana/index.html` **не трогали**.
- Preview: `site_mirror/web-studiya/astana/index-clean.html` (~59 KiB, без `public.bundle`).
- CSS: `assets/css/hub-city-clean.css` + reuse studio-clean / home-clean / lead-forms.
- Уникально: Title/Description/H1 из ТЗ; региональный prose; направления с проверенными URL; FAQ×8 + FAQPage; areaServed Астана; честный remote (офис = Петропавловск).
- Формы: `data-lead-form` «Астана хаб — контакты…» / «Астана хаб — попап…».
- Swap / commit / push / plesk — **НЕ** делали (скилл + ждать approve).
- Локальный preview: `http://127.0.0.1:8771/web-studiya/astana/index-clean.html`
- Дальше: глазами сверить → approve swap → шаблон для Алматы/Шымкент.

### 2026-08-05 — SWAP + DEPLOY clean hub Astana (approve «ок»)

- Swap: `astana/index.html` (Mottor ~394 KiB) → `index.mottor-legacy.html`; clean ~59 KiB → `index.html`.
- CSS: `assets/css/hub-city-clean.css` (новый).
- Feature commit + точечный plesk: `web-studiya/astana/index.html` + hub-city-clean.css (+ legacy не обязателен на прод).
- URL `/web-studiya/astana/` без смены → sitemap/301 не трогали.
- Живой смоук `https://raskrutov.kz/web-studiya/astana/`: HTTP 200, `rk-hub-city`, H1 «Веб-студия в Астане для роста бизнеса», без `public.bundle`, `hub-city-clean.css` 200.
- Feature `323ce2cf`; plesk `9976d73e` (`01f8e6ec..9976d73e`).
- Дальше: пилот Алматы / Шымкент по тому же шаблону (не массово 18).

### 2026-08-06 — REDESIGN clean hub Astana (локально, без deploy)

- Полностью пересобран `site_mirror/web-studiya/astana/index.html`: 14 → 9 секций, H2 15 → 8, H3 23 → 12.
- Hero: два изображения → одно; HTML 57 953 → 34 897 bytes; CSS-файлы 5 → 4; новых JS/библиотек нет.
- Новый page-specific визуал: black / white / `#FE780A`; глобальные токены и `/web-studiya/` не менялись.
- SEO: утверждённые Title/Description/H1/canonical, Service areaServed Astana, FAQ×6, breadcrumbs.
- QA: 320/375/430/768/1024/1440 без horizontal overflow; CTA виден на mobile; 20/20 внутренних URL 200; runtime errors 0; menu PASS.
- Форма: один global `data-lead-form`, Supabase endpoint/UTM/analytics сохранены; реальный submit не выполнялся.
- Lighthouse CLI завис на загрузке пакета и остановлен; score не выдумывался. PSI — после разрешённого deploy.
- Отчёт: `reports/web-studiya-astana-clean/REPORT.md`.
- Commit / push / plesk **не выполнялись** по прямому запрету пользователя.

### 2026-08-06 — Astana hub: откат оранжа → стиль хаба + макет (локально)

- Юзер отклонил orange/black: страница должна быть как `/web-studiya/` + макет (светлый, purple/blue).
- Переписаны `astana/index.html` + `hub-city-clean.css?v=3`; подключены `studio-clean.css` + home-clean.
- ~11 смысловых секций; 6 направлений; FAQ×8; ProfessionalService areaServed Астана; офис только Петропавловск + remote.
- QA `_qa_astana_hub_v3.py`: 1 H1, miss links 0, без `public.bundle`/оранжа; preview `127.0.0.1:8771` HTTP 200 `rk-astana-page`.
- Browser mobile: hero/CTA/sticky в hub-стиле.
- Commit / push / plesk **снова запрещены** пользователем.
- Отчёт: `reports/web-studiya-astana-clean/REPORT.md`.

### 2026-08-06 — Almaty hub CLEAN (локально, эталон Astana)

- Mottor `web-studiya/almaty/index.html` → `index.mottor-legacy.html`; clean rebuild ~53 KiB.
- Структура/визуал/JS как Astana; тексты/FAQ×9/JSON-LD уникальны под Алматы; remote без офиса в городе.
- CSS `hub-city-clean.css?v=9`: `.rk-almaty-page` + сетка 3×2; Astana HTML не меняли.
- Preview `http://127.0.0.1:8771/web-studiya/almaty/`: 200, 1 H1, modal lead OK, WA/tel OK, overflow@390 нет.
- Commit / push / plesk **не выполнялись** (запрет в ТЗ).

<!-- следующая запись: дата — что сделали — новый PSI — что дальше -->

### 2026-08-06 — Almaty hub CLEAN deploy

- Feature + plesk: web-studiya/almaty/index.html (+ mottor-legacy), hub-city-clean.css, Astana CSS ?v=10.
- Live: https://raskrutov.kz/web-studiya/almaty/

### 2026-08-06 — Batch5 clean hubs (локально)

- 5 хабов: shymkent/aktau/aktobe/atyrau/karaganda; CSS `rk-hub-city-page` v11.
- Commit/push/plesk не делались — ждать «заливай».

### 2026-08-06 — Rest clean hubs: все 18 city hubs (локально)

- Закрыт полный комплект `/web-studiya/{city}/` clean (18). Mottor → legacy.

### 2026-08-06 — DEPLOY all 18 clean city hubs

- Юзер: «зааливай все на сервер».
- Feature + точечный plesk (без `/MIR`): 18× index.html (+ mottor-legacy), `hub-city-clean.css`, img/cities + hero-devices.
- Feature **`1dc8b067`**, plesk **`4f905053`** (`e5eceb45..4f905053`).
- Не тащили akademiya/faq/crm dirty tree и untracked lpfile.
- Live smoke sample: clean markers, без Mottor `public.bundle`.

### 2026-08-06 — FIX 8 направлений на city hubs

- Вернули AEO/GEO + Лидогенерация (было 6, стало 8 как parent/Astana).
- `hub-city-clean.css?v=13`, сетка 4×2; фикс escaped attrs `#services`.
