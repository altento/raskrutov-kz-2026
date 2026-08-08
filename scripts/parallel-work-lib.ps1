$ErrorActionPreference = "Stop"

$script:ExpectedRepoFragment = "raskrutovstudio-collab/raskrutov-kz-2026"
$script:RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))

function Get-ParallelRepoRoot {
    if (-not (Test-Path -LiteralPath (Join-Path $script:RepoRoot ".git"))) {
        throw "Не найден Git-репозиторий."
    }
    return $script:RepoRoot
}

function Get-ParallelMachineConfig {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)
    $path = Join-Path $RepoRoot ".git\cursor-machine-id.json"
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Не настроен machine ID. Запустите scripts/setup-parallel-work.ps1 -MachineName PC1 или PC2."
    }
    $cfg = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($cfg.machine_name -notin @("PC1","PC2")) {
        throw "Неизвестный machine_name: $($cfg.machine_name)"
    }
    return $cfg
}

function Get-ExpectedWorkBranch {
    param([Parameter(Mandatory=$true)]$MachineConfig)
    if ($MachineConfig.machine_name -eq "PC1") { return "work/pc1" }
    return "work/pc2"
}

function Assert-ParallelRepository {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)
    $remote = (& git -C $RepoRoot remote get-url origin 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($remote)) {
        throw "origin не настроен."
    }
    if (-not $remote.Trim().ToLowerInvariant().Contains($script:ExpectedRepoFragment)) {
        throw "Неверный origin: $($remote.Trim())"
    }
}

function Test-WorkingTreeClean {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)
    $lines = @(& git -C $RepoRoot status --porcelain)
    return -not ($lines.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace(($lines -join "")))
}

function Invoke-ParallelFetch {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)
    & git -C $RepoRoot fetch origin --prune | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "git fetch origin --prune завершился ошибкой." }
}

function Sync-WorkBranchToMain {
    param(
        [Parameter(Mandatory=$true)][string]$RepoRoot,
        [Parameter(Mandatory=$true)][string]$WorkBranch
    )

    Invoke-ParallelFetch -RepoRoot $RepoRoot

    $current = (& git -C $RepoRoot branch --show-current).Trim()
    if ($current -ne $WorkBranch) {
        throw "Ожидалась ветка $WorkBranch, текущая ветка: $current"
    }

    if (-not (Test-WorkingTreeClean -RepoRoot $RepoRoot)) {
        throw "Есть незакоммиченные изменения. Автосинхронизация не выполняется."
    }

    & git -C $RepoRoot merge-base --is-ancestor HEAD origin/main 2>$null
    if ($LASTEXITCODE -eq 0) {
        & git -C $RepoRoot merge --ff-only origin/main | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Fast-forward рабочей ветки до origin/main не удался." }
        return "synced"
    }

    & git -C $RepoRoot merge-base --is-ancestor HEAD "origin/$WorkBranch" 2>$null
    $remoteContainsHead = ($LASTEXITCODE -eq 0)

    $ahead = (& git -C $RepoRoot rev-list --count "origin/main..HEAD").Trim()
    if ([int]$ahead -gt 0) {
        throw "Предыдущая работа из $WorkBranch ещё не вошла в main. Дождитесь интеграции GitHub Actions и повторите промт."
    }

    if (-not $remoteContainsHead) {
        throw "Локальная и удалённая рабочие ветки расходятся. Нужна ручная проверка."
    }

    throw "Рабочую ветку нельзя безопасно синхронизировать с main автоматически."
}

function New-ParallelSessionMarker {
    param(
        [Parameter(Mandatory=$true)][string]$RepoRoot,
        [Parameter(Mandatory=$true)]$MachineConfig,
        [Parameter(Mandatory=$true)][string]$WorkBranch
    )
    $path = Join-Path $RepoRoot ".git\cursor-parallel-session.json"
    [PSCustomObject]@{
        machine_name = $MachineConfig.machine_name
        machine_id = $MachineConfig.machine_id
        branch = $WorkBranch
        start_head = (& git -C $RepoRoot rev-parse HEAD).Trim()
        started_at = [DateTime]::UtcNow.ToString("o")
    } | ConvertTo-Json | Set-Content -LiteralPath $path -Encoding UTF8
}

function Remove-ParallelSessionMarker {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)
    $path = Join-Path $RepoRoot ".git\cursor-parallel-session.json"
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
}

function Test-ParallelSessionMarker {
    param(
        [Parameter(Mandatory=$true)][string]$RepoRoot,
        [Parameter(Mandatory=$true)]$MachineConfig,
        [Parameter(Mandatory=$true)][string]$WorkBranch
    )
    $path = Join-Path $RepoRoot ".git\cursor-parallel-session.json"
    if (-not (Test-Path -LiteralPath $path)) { return $false }
    try {
        $m = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
        return ($m.machine_id -eq $MachineConfig.machine_id -and $m.branch -eq $WorkBranch)
    } catch { return $false }
}

function Assert-OwnWorkBranch {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)
    $cfg = Get-ParallelMachineConfig -RepoRoot $RepoRoot
    $expected = Get-ExpectedWorkBranch -MachineConfig $cfg
    $current = (& git -C $RepoRoot branch --show-current).Trim()
    if ($current -ne $expected) {
        throw "На $($cfg.machine_name) разрешена рабочая ветка $expected. Текущая: $current"
    }
    return [PSCustomObject]@{ machine = $cfg; branch = $expected }
}
