УСТАНОВКА

1. Распакуйте содержимое ZIP в корень репозитория raskrutov-kz-2026.
   После распаковки должен существовать путь:
   .agents/skills/accessibility/SKILL.md

2. Запустите INSTALL_SKILLS.ps1 из PowerShell:
   .\INSTALL_SKILLS.ps1

Скрипт:
- проверит наличие 13 SKILL.md;
- проверит 4 reference-файла;
- добавит только .agents/skills;
- создаст коммит;
- отправит его в origin/main.

Папка site_plesk и другие несвязанные файлы в коммит не попадут.
