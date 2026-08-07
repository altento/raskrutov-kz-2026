# Установка на ПК1 — основной актуальный компьютер

ПК1 — компьютер, на котором сейчас находится наиболее свежая версия Raskrutov.kz.

## 0. Текущую задачу Cursor не прерывать

Если Cursor уже выполняет большой промт:

1. дайте ему полностью закончить;
2. не запускайте параллельную работу на ПК2;
3. после завершения переходите к установке.

## 1. Сначала сохранить актуальное состояние проекта

До первой синхронизации НЕ выполняйте:

- `git reset --hard`;
- `git clean -fd`;
- принудительный checkout старого `main`.

Сначала сравните локальный проект с GitHub и сохраните все актуальные страницы.

Цель первоначальной синхронизации:

- актуальные HTML;
- CSS;
- JS;
- изображения;
- `.cursor/rules`;
- skills;
- другие production-файлы;

должны оказаться в GitHub.

Если есть сомнения, сначала отправьте изменения в отдельную sync-ветку и только после проверки объединяйте её с рабочей основной веткой.

## 2. Разместить файлы пакета

Скопируйте содержимое архива В КОРЕНЬ репозитория.

После копирования должны существовать:

```text
.cursor/hooks.json
.cursor/hooks/before-submit-lock.ps1
.cursor/hooks/pre-tool-lock.ps1
.cursor/hooks/after-response-unlock.ps1
.cursor/rules/git-single-writer.mdc

.githooks/pre-commit
.githooks/pre-push

scripts/project-lock-lib.ps1
scripts/setup-single-writer.ps1
scripts/project-lock-status.ps1
scripts/project-lock-acquire.ps1
scripts/project-lock-release.ps1
scripts/assert-project-lock.ps1
```

## 3. Эти файлы должны попасть в GitHub

Добавьте пакет в commit вместе с актуальным состоянием проекта либо отдельным commit.

Важно: `setup-single-writer.ps1` пока можно ещё не запускать, поэтому новые Git hooks не помешают первому commit пакета.

## 4. Отправить пакет в GitHub

После commit/push убедитесь, что новые файлы реально присутствуют в remote.

## 5. Включить систему на ПК1

Откройте PowerShell в корне проекта:

```powershell
.\scripts\setup-single-writer.ps1 -MachineName PC1
```

Ожидаемый итог:

```text
SINGLE-WRITER SETUP OK
Machine: PC1
Hooks: .githooks
```

## 6. Проверить

```powershell
.\scripts\project-lock-status.ps1
```

До начала новой Cursor-задачи должно быть:

```text
Remote lock: FREE
```

## 7. Тест без изменения сайта

В PowerShell:

```powershell
.\scripts\project-lock-acquire.ps1
```

Проверьте:

```powershell
.\scripts\project-lock-status.ps1
```

Должно показать:

```text
Remote lock: BUSY
Ownership: THIS COMPUTER
Owner machine: PC1
```

Пока этот lock удерживается, переходите к тесту на ПК2.

После успешного теста ПК2 вернитесь на ПК1 и выполните:

```powershell
.\scripts\project-lock-release.ps1
```

## 8. Дальше вручную ничего запускать не нужно

При обычной работе просто отправляйте Cursor задания.

Lock будет получаться автоматически при отправке промта.
