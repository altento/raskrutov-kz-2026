# Raskrutov Agent Skills — стартовый пакет

Готовый набор из 11 навыков для связки **ChatGPT + Cursor + GitHub + Cursor Agents**.

## Состав

### Общий аудит
- `web-quality-audit`

### Frontend и качество
- `performance`
- `core-web-vitals`
- `accessibility`
- `frontend-design-review`
- `webapp-testing`

### SEO
- `seo`
- `seo-audit`
- `schema`
- `site-architecture`
- `programmatic-seo`

## Установка

1. Распакуйте архив в корень репозитория сайта.
2. После распаковки путь должен выглядеть так:

```text
ваш-проект/
├── .agents/
│   └── skills/
│       ├── web-quality-audit/
│       ├── performance/
│       └── ...
├── index.html
└── ...
```

3. Добавьте файлы в Git:

```bash
git add .agents/skills README_SKILLS_RU.md SOURCES_AND_LICENSES.md
git commit -m "Add project agent skills"
git push
```

4. Полностью перезапустите Cursor или перезагрузите окно проекта.
5. Проверьте обнаружение skills в настройках Cursor.

## Рекомендуемое распределение

### Основной Cursor Agent
- `web-quality-audit`
- `site-architecture`

### SEO Agent
- `seo`
- `seo-audit`
- `schema`
- `site-architecture`
- `programmatic-seo`

### Frontend Agent
- `performance`
- `core-web-vitals`
- `accessibility`
- `frontend-design-review`

### QA Agent
- `webapp-testing`
- `web-quality-audit`
- `core-web-vitals`
- `accessibility`

## Пример задачи Cursor

```text
Проведи аудит страницы /web-studiya/sozdanie-saitov/.
Используй project skills:
- web-quality-audit
- seo-audit
- core-web-vitals
- accessibility

Сначала составь отчёт с приоритетами P0–P3. Код пока не меняй.
Отдельно перечисли защищённые интеграции и возможные риски регрессии.
```

## Важно

Этот архив — адаптированный безопасный стартовый набор. В нём нет автоматически исполняемых shell/Python-скриптов и нет внешних зависимостей. Навык `webapp-testing` описывает процесс Playwright, но ничего самостоятельно не устанавливает.

Следующий логичный этап — добавить ваши собственные навыки:

- `forms-standard`;
- `clean-site-migration`;
- `protected-integrations-and-release`.
