param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("PC1","PC2")]
    [string]$MachineName
)

$ErrorActionPreference = "Stop"

$root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
if (-not (Test-Path -LiteralPath (Join-Path $root ".git"))) {
    throw "Не найден Git-репозиторий: $root"
}

$remote = (& git -C $root remote get-url origin).Trim()
if (-not $remote.ToLowerInvariant().Contains("raskrutovstudio-collab/raskrutov-kz-2026")) {
    throw "Неверный origin: $remote"
}

$configPath = Join-Path $root ".git\cursor-machine-id.json"
if (-not (Test-Path -LiteralPath $configPath)) {
    $cfg = [PSCustomObject]@{
        machine_name = $MachineName
        machine_id = [Guid]::NewGuid().ToString()
        computer_name = $env:COMPUTERNAME
        windows_user = $env:USERNAME
        created_at = [DateTime]::UtcNow.ToString("o")
    }
    $cfg | ConvertTo-Json | Set-Content -LiteralPath $configPath -Encoding UTF8
} else {
    $cfg = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($cfg.machine_name -ne $MachineName) {
        throw "Этот checkout уже настроен как $($cfg.machine_name)."
    }
}

$branch = if ($MachineName -eq "PC1") { "work/pc1" } else { "work/pc2" }

& git -C $root fetch origin --prune
if ($LASTEXITCODE -ne 0) { throw "git fetch завершился ошибкой." }

$status = @(& git -C $root status --porcelain)
if ($status.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace(($status -join ""))) {
    throw "Рабочее дерево не чистое. Сначала сохраните текущие изменения."
}

$current = (& git -C $root branch --show-current).Trim()
if ($current -eq "main") {
    & git -C $root merge --ff-only origin/main
    if ($LASTEXITCODE -ne 0) { throw "Не удалось синхронизировать main." }
}

& git -C $root switch -C $branch "origin/$branch"
if ($LASTEXITCODE -ne 0) { throw "Не удалось переключиться на $branch." }

& git -C $root config core.hooksPath .githooks
& git -C $root config fetch.prune true
& git -C $root config pull.ff only

Write-Host ""
Write-Host "=== PARALLEL WORK SETUP OK ==="
Write-Host "Machine: $MachineName"
Write-Host "Branch:  $branch"
Write-Host "Repo:    $root"
Write-Host ""
Write-Host "Cursor теперь работает параллельно через отдельную ветку этого ПК."
