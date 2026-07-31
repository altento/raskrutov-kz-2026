# PERFORMANCE STATUS — RASKRUTOV.KZ

## Текущая контрольная точка
- Ветка: `performance/pagespeed-raskrutov` @ `8baa61f8` (синхрон с origin)
- Git status: clean по коду этапов 1–2; untracked: `PERFORMANCE_OPTIMIZATION_PLAN.md`
- Незакоммиченные изменения этапов 1–2: нет (уже в `8baa61f8` / `plesk` `0ed5d67f`)
- Дата локальной проверки: 2026-07-31
- Доступность локального Lighthouse: Chrome headless доступен; внешний PSI — POST-DEPLOY

## Метрики
| Контрольная точка | Режим | Performance | FCP | LCP | TBT | CLS | Speed Index |
|---|---|---:|---:|---:|---:|---:|---:|
| До оптимизации | ПК | 66 | 0,6 с | 1,0 с | 400 мс | 0,246 | 1,6 с |
| До оптимизации | Мобильный | 72 | 3,0 с | 4,7 с | 120 мс | 0,124 | 3,8 с |
| После этапов 1–2 | ПК | — | — | — | — | — | — |
| После этапов 1–2 | Мобильный | — | — | — | — | — | — |

> После 1–2: PSI не замерялся заново (нужна опубликованная версия / локальный Lighthouse на этапе 3+).

## Статусы этапов
- Этап 1 — COMPLETED ранее (аудит)
- Этап 2 — COMPLETED ранее, изменения применены и запушены (`plesk` / feature)
- Этап 3 — IN PROGRESS
- Этап 4 — PENDING
- Этап 5 — PENDING
- Этап 6 — PENDING
- Этап 7 — PENDING
- Этап 8 — PENDING
- Этап 9 — PENDING

## Уже изменённые файлы (этапы 1–2)
### Этап 2 (в git)
- `site_mirror/index.html` — убраны preload `public.bundle.css`, пустые `#head-blocks-style` / `#site_style_text`, мёртвый gtag/ga sniffer
- Удалены: `home-all-blocks.css`, `home-all-blocks.v2.css`, `home-popup-2773676.css`, `home-popup-2782231.css` (без v2), `*.motortest.bak`
- Сохранены: sync `public.bundle*.js/css` stylesheet, `lead-forms.js`, home-critical/deferred/popup v2

## План этапов 3–9 (кратко)
3. LCP/CLS первого экрана (img/picture или preload + reserve)
4. Оптимизация изображений под контейнеры
5. Шрифты WOFF2 / subset / CLS
6. Вырезание неиспользуемого CSS / отвязка bundle CSS
7. Замена Mottor JS локальными модулями
8. DOM + анимации (transform/opacity)
9. Кэш + финальная проверка + итоговый отчёт

## Журнал этапов
### Этап 1
- Статус: COMPLETED
- Что сделано: полный аудит главной, зависимости bundle, P1–P3

### Этап 2
- Статус: COMPLETED
- Что сделано: удаление подтверждённого мусора; QA 195/195 assets; push `plesk`/`feature`

### Этап 3
- Статус: IN PROGRESS
- Изменённые файлы: —
- Что сделано: —
- Что проверено: —
- Метрики: —
- Риски/ограничения: —
- POST-DEPLOY проверки: —
