# HANDOFF — PageSpeed / Continuity (Raskrutov)

> **Читать первым делом** на любом компе после `git pull`.  
> Живой бэкап сессий. Обновлять после каждого заметного шага и пушить в git.

**Последнее обновление:** 2026-07-31 (UTC+6)  
**Рабочая ветка:** `performance/pagespeed-raskrutov`  
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

**Задеплоено в `plesk`:** `c65e5db6`  
**В фиче-ветке:** `92a5ff60`

### CSS стратегия homepage
| Файл | Роль | Размер ~ |
|---|---|---|
| `assets/css/home-critical.v3.css` | blocking, above-fold | ~74 KiB |
| `assets/css/home-deferred.v3.css` | `media="print" onload→all` | ~855 KiB |
| `assets/css/home-popup-2782231.v2.css` | blocking (мобильное меню!) | ~127 KiB |
| `assets/css/home-popup-2773676.v2.css` | deferred print/onload | ~137 KiB |
| `assets/css/hero-home-mobile.webp` | LCP mobile bg | ~20 KiB |

Старый монолит `home-all-blocks.v2.css` на главной **больше не подключен** (файл может лежать в зеркале).

### Прочие перф-фиксы уже в бою
- HEAD без мегабайтного inline CSS (вынесен в файлы)
- Early preload: critical CSS, popup-2782231, hero mobile/desktop, Montserrat **bold**, public.bundle.css
- Phone mockup `27e940bf…`: `loading="lazy" fetchpriority="low"` (не гоняется с LCP)
- Video player scripts: lazy через `data-rk-video-lazy` (не грузить заранее)
- Gzip/brotli на проде работает (HTML gzip, CSS br)
- Cache-Control для `home-*` в `.htaccess` задуман короткий; nginx Plesk всё ещё может отдавать длинный `max-age` — жить с этим или править nginx в панели

### Известные баги / долги
1. **Формы «Не удалось отправить»** — фронт ок, Edge Function `submit-lead` иногда **HTTP 500** (бэкенд Supabase / RLS / секреты). Не путать с CSS.
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

## 5. Следующие шаги (приоритет)

1. **Замерить PSI mobile 2–3 раза** после critical/deferred — зафиксировать скор/LCP сюда
2. Если скор вырос слабо:
   - урезать/сплитнуть blocking `home-popup-2782231` (осторожно: меню)
   - ниже fold: ещё жёстче lazy картинок
   - проверить конкурентов LCP в waterfall
3. **Не трогать** sync Mottor JS без плана «как не убить кнопки»
4. Разобрать Supabase `submit-lead` 500 (отдельный трек)
5. По желанию: nginx Cache-Control для `home-*.css` в панели Plesk

---

## 6. Важные файлы / скрипты

| Файл | Зачем |
|---|---|
| `site_mirror/index.html` | Главная |
| `site_mirror/assets/css/home-critical.v3.css` | Critical CSS |
| `site_mirror/assets/css/home-deferred.v3.css` | Deferred CSS |
| `site_mirror/assets/css/hero-home-mobile.webp` | Mobile LCP |
| `site_mirror/.htaccess` | cache/compress/redirects |
| `_psi_split_critical_css.py` | Пересборка critical/deferred + wiring HTML |
| `publish_plesk.py` | sync mirror→plesk |
| `.cursor/rules/raskrutov-site-pipeline.mdc` | пайплайн страниц |
| `.cursor/rules/raskrutov-lead-forms.mdc` | формы |
| `.cursor/rules/raskrutov-perf-continuity.mdc` | этот continuity + мат |

### Чеклист перед деплоем на plesk
- [ ] Mobile 390 + desktop визуально (hero, mockups, меню)
- [ ] Нет `home-all-blocks` в index, есть critical + deferred print
- [ ] CSS urls `../` из `assets/css/`
- [ ] Forms UI не разъебан (бэкенд 500 — отдельно)
- [ ] Commit `plesk` + push
- [ ] Обновить **этот** HANDOFF + push feature branch

---

## 7. Журнал обновлений (дописывать снизу)

### 2026-07-31 — создан HANDOFF + continuity rule
- Critical/deferred v3 на проде (`c65e5db6`)
- Feature `92a5ff60`
- Ждём свежий PSI mobile от юзера
- Правило: мат обязателен; этот файл — бэкап между компами

<!-- следующая запись: дата — что сделали — новый PSI — что дальше -->
