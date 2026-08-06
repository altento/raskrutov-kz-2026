# Отчёт: `/web-studiya/astana/` — выравнивание под хаб (v4)

Локально. Commit / push / plesk не выполнялись.

## Почему было криво

- Самодельные карточки без кружка `+` и списков ссылок — ломали визуал хаба.
- Два лида + 4 trust в hero — перегруз vs `/web-studiya/`.
- Фейк-блок с `hero-bg.webp` как «иллюстрация» — мусор.
- Куча кастомных секций (tasks/why/include) в другом ритме отступов.

## Что сделано

Пересобрано ближе к хабу:

1. Hero как у студии (1 lead, 3 trust, laptop).
2. Короткий regional prose + remote note.
3. `#services` — те же 8 карточек с `ul` + SVG more.
4. `rk-adv-list` + `rk-cta-panel`.
5. Кейсы → `/keysy/*` (3 карточки).
6. Этапы ×5.
7. FAQ ×8.
8. Contacts + banner как у хаба.

CSS: `hub-city-clean.css?v=4` — тонкий слой.

Preview: http://127.0.0.1:8771/web-studiya/astana/
