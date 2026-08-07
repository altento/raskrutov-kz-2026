param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("PC1","PC2")]
    [string]$MachineName,

    [switch]$ResetIdentity
)

$ErrorActionPreference = "Stop"

$lib = Join-Path $PSScriptRoot "project-lock-lib.ps1"
. (Resolve-Path $lib)

$root = Get-RepoRoot
Assert-CorrectRepository -RepoRoot $root | Out-Null

$configPath = Join-Path $root ".git\cursor-machine-id.json"

if ((Test-Path -LiteralPath $configPath) -and -not $ResetIdentity) {
    $existing = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json

    if ($existing.machine_name -ne $MachineName) {
        throw "На этом checkout уже настроен identity '$($existing.machine_name)'. Для преднамеренной замены используйте -ResetIdentity."
    }

    Write-Host "Machine identity уже существует: $($existing.machine_name) / $($existing.machine_id)"
} else {
    $cfg = [PSCustomObject]@{
        machine_name = $MachineName
        machine_id = [Guid]::NewGuid().ToString()
        computer_name = $env:COMPUTERNAME
        windows_user = $env:USERNAME
        created_at = [DateTime]::UtcNow.ToString("o")
    }

    $cfg | ConvertTo-Json | Set-Content -LiteralPath $configPath -Encoding UTF8
    Write-Host "Создан machine identity: $($cfg.machine_name) / $($cfg.machine_id)"
}

& git -C $root config core.hooksPath .githooks
if ($LASTEXITCODE -ne 0) {
    throw "Не удалось установить core.hooksPath=.githooks"
}

& git -C $root config fetch.prune true
& git -C $root config --get core.hooksPath

$hooksJson = Join-Path $root ".cursor\hooks.json"
if (-not (Test-Path -LiteralPath $hooksJson)) {
    throw "Не найден .cursor/hooks.json"
}

$preCommit = Join-Path $root ".githooks\pre-commit"
$prePush = Join-Path $root ".githooks\pre-push"
if (-not (Test-Path -LiteralPath $preCommit) -or -not (Test-Path -LiteralPath $prePush)) {
    throw "Не найдены versioned Git hooks в .githooks"
}

Write-Host ""
Write-Host "=== SINGLE-WRITER SETUP OK ==="
Write-Host "Machine: $MachineName"
Write-Host "Repo:    $root"
Write-Host "Hooks:   .githooks"
Write-Host ""
Write-Host "Проверка lock:"
Write-Host "  .\scripts\project-lock-status.ps1"
Write-Host ""
Write-Host "В обычной работе вручную acquire/release выполнять НЕ нужно."
