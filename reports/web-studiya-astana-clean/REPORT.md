# Отчёт: clean regional hub Astana (пилот)

Дата: 2026-08-05  
Скиллы: `lp-motor-clean-migration`, `programmatic-seo`, `forms-standard`

## 1. Изменённые / созданные файлы

| Файл | Действие |
|---|---|
| `site_mirror/web-studiya/astana/index-clean.html` | создан (~59 KiB) |
| `site_mirror/assets/css/hub-city-clean.css` | создан |
| `docs/HANDOFF-PERF.md` | запись в журнал |
| `docs/HANDOFF-REGIONAL.md` | чеклист пилота |
| `_qa_astana_hub_clean.py` | локальный QA-скрипт |

**Не трогали:** `site_mirror/web-studiya/astana/index.html` (Mottor 385 KiB остаётся боевым до approve).  
**Не делали:** commit / push / plesk / swap / sitemap / .htaccess.

## 2. URL

- Целевой боевой: `/web-studiya/astana/`
- Preview сейчас: `/web-studiya/astana/index-clean.html`
- Локально: `http://127.0.0.1:8771/web-studiya/astana/index-clean.html`
- **Не создавали** `/web-studiya/sozdanie-saitov/astana/` (уже существует отдельно — не дублировали)

## 3. Метаданные

- **Title:** Веб-студия в Астане — сайты, SEO и digital-продвижение | Raskrutov
- **Description:** Веб-студия Raskrutov для бизнеса в Астане: создаём сайты, продвигаем в Google, настраиваем рекламу, CRM и digital-инструменты для роста заявок.
- **Canonical:** `https://raskrutov.kz/web-studiya/astana/`
- **H1 (один):** Веб-студия в Астане для роста бизнеса
- OG совпадает с Title/Description

## 4. Уникализированные блоки

- Hero-оффер + trust (сайты / SEO·AEO / контекст / CRM / заявки)
- Региональный prose «digital-система вместо разрозненных подрядчиков»
- Задачи бизнеса (6 карточек)
- Направления (9) с пользой + ссылкой
- Блоки: создание сайтов / SEO·AEO / реклама·лиды / CRM / консалтинг
- «Для кого», «Почему Raskrutov», этапы работы (8)
- FAQ × 8 (не копия родителя)
- Финальный CTA + контакты с честным remote
- Breadcrumbs: Главная → Веб-студия → Веб-студия в Астане

Общие брендовые компоненты сохранены: header, sticky Позвонить/WhatsApp, modal, soc-widget, home-clean/studio-clean токены.

## 5. Направления услуг

Все ссылки проверены на диск (`index.html` существует):

1. Создание сайтов → `/web-studiya/sozdanie-saitov/`
2. Дизайн → `/web-studiya/dizayn/`
3. SEO → `/web-studiya/seo-prodvizhenie/`
4. AEO → `/web-studiya/aeo-prodvizhenie/`
5. Контекст → `/web-studiya/kontekstnaya-reklama/`
6. Лидогенерация → `/web-studiya/lidogeneratsiya/`
7. Поддержка → `/web-studiya/podderzhka-saytov/`
8. Digital-консалтинг → `/web-studiya/digital-konsalting/`
9. CRM и автоматизация → **отдельного URL нет** → честно ведём на `/web-studiya/lidogeneratsiya/` (+ упоминание консалтинга)

## 6. Внутренние ссылки

- Хаб: `/web-studiya/`
- Услуги: список выше + подстраницы landing / google / yandex и т.д.
- Кейсы: `/keysy/` (отдельный кейс «производство в Астане» на диске **не найден** — не выдумывали URL)
- Анкоры разные: «услуги веб-студии», «разработка сайта», «SEO-продвижение», «продвижение в Google», «контекстная реклама», «поддержка сайта», «digital-консалтинг»

## 7. JSON-LD

`Organization`, `WebSite`, `WebPage`, `BreadcrumbList`, `ProfessionalService` (areaServed: Астана, Казахстан), `FAQPage` (8 видимых Q&A).

**Нет:** вымышленный офис в Астане, AggregateRating, отзывы, цены в schema.

Адрес Organization = Петропавловск (подтверждённый офис). На странице явно: работаем с Астаной дистанционно.

## 8. Мобильная версия

- Sticky CTA Позвонить / WhatsApp (из studio-clean)
- Адаптивные сетки hub-city-clean (1→2→3 колонки)
- Viewport meta, один DOM без desktop/mobile дублей
- Cursor browser к `127.0.0.1` из среды не достучался (chrome-error); HTTP smoke локально: **200**, ассеты head-check в том же прогоне

**Нужно глазами:** открыть preview у себя на 390/1440.

## 9. Формы и WhatsApp

- 2× `data-lead-form` + honeypot + `data-form-status`
- Имена: «Астана хаб — контакты — отправьте заявку» / «Астана хаб — попап — обсудить проект»
- `lead-forms.js` + `home-clean.js` (defer)
- `tel:+77000216900`, `https://wa.me/77000216900`
- Реальную отправку **не** гоняли (скилл)

## 10. Дубли / каннибализация

| URL | Интент |
|---|---|
| `/web-studiya/` | общий хаб студии (Казахстан) |
| `/web-studiya/astana/` | региональный хаб «веб-студия в Астане» |
| `/web-studiya/sozdanie-saitov/astana/` | услуга «создание сайтов» в городе |
| `/web-studiya/seo-prodvizhenie/*` | чужая зона / отдельный интент SEO |

Title/H1/Description **не** совпадают с родителем. Страница не doorway: есть самостоятельный prose, FAQ, процесс, направления с пользой. Риск средний только если массово клонировать без уникализации — пилот как раз против этого.

## 11. Перед следующими городами

1. Approve Astana: swap `index.html` ← `index-clean.html`, Mottor → `index.mottor-legacy.html`.
2. Вынести шаблон генератора (город / предложный падеж / meta из FINAL_SEO_MAP / FAQ).
3. Пилот ещё 2 города (Алматы, Шымкент) → QA → только потом остальные 15.
4. Не подставлять город в каждый абзац; не врать про офис; CRM без отдельного URL — честно линковать на лидоген.
5. SEO geo не трогать (чужой сотрудник).
6. После swap — точечный plesk (без `/MIR`), потом PSI медианой.

## Критерии готовности (скилл)

| Критерий | Статус |
|---|---|
| Изолированный preview без поломки боевого | ✅ |
| Нет Mottor bundle / lpmotor | ✅ |
| SEO meta + canonical + 1 H1 | ✅ |
| Формы по стандарту проекта | ✅ |
| Уникальность vs parent | ✅ (контент) |
| Swap / commit / publish | ❌ ждут команду |
| Визуал глазами владельца 1440/390 | ⏳ |
| Lighthouse median | ⏳ после swap/прод |

**Вывод:** страница готова к **ручной проверке владельцем** по preview. К swap и деплою — только после твоего «ок».
