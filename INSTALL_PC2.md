# Установка на ПК2

До завершения первичной синхронизации ПК1 не изменяйте файлы проекта на ПК2.

## 1. Убедиться, что на ПК2 нет нужных незакоммиченных изменений

В корне проекта:

```powershell
git status
```

Если есть важные локальные изменения — НЕ удаляйте их и НЕ делайте pull поверх них.
Сначала сохраните/сравните их отдельно.

Если working tree clean, продолжайте.

## 2. Получить актуальный GitHub

```powershell
git fetch origin --prune
git checkout main
git pull --ff-only origin main
```

После этого файлы single-writer пакета должны появиться автоматически из GitHub.

Проверьте наличие:

```text
.cursor/hooks.json
.cursor/rules/git-single-writer.mdc
.githooks/pre-commit
.githooks/pre-push
scripts/setup-single-writer.ps1
```

## 3. Включить систему на ПК2

В PowerShell:

```powershell
.\scripts\setup-single-writer.ps1 -MachineName PC2
```

Ожидаемый итог:

```text
SINGLE-WRITER SETUP OK
Machine: PC2
Hooks: .githooks
```

## 4. Проверка свободного состояния

```powershell
.\scripts\project-lock-status.ps1
```

## 5. Проверка блокировки ПК2

Сначала на ПК1 вручную получите lock:

```powershell
.\scripts\project-lock-acquire.ps1
```

Теперь на ПК2:

```powershell
.\scripts\project-lock-status.ps1
```

Должно показать:

```text
Remote lock: BUSY
Ownership: OTHER COMPUTER
Owner machine: PC1
```

Теперь в Cursor на ПК2 отправьте любой обычный промт, например:

```text
Проверь текущую структуру проекта.
```

Ожидаемое поведение:

Cursor НЕ должен начать Agent-задачу.
`beforeSubmitPrompt` должен показать, что проект занят PC1.

Это означает, что защита работает.

## 6. Проверка обратного направления

На ПК1:

```powershell
.\scripts\project-lock-release.ps1
```

На ПК2:

```powershell
.\scripts\project-lock-acquire.ps1
```

На ПК1 `project-lock-status.ps1` теперь должен показывать владельца PC2.

После теста на ПК2:

```powershell
.\scripts\project-lock-release.ps1
```

## 7. Обычная работа

После установки команды помнить не требуется.

Отправляете Cursor промт.

Cursor сам:

1. делает Git preflight;
2. проверяет актуальность;
3. получает GitHub lock;
4. начинает задачу только при успешном lock.

Если другой ПК занят — промт блокируется.
