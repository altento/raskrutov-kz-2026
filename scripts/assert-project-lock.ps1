param(
    [ValidateSet("commit","push")]
    [string]$Mode = "commit"
)

$ErrorActionPreference = "Stop"

try {
    $lib = Join-Path $PSScriptRoot "project-lock-lib.ps1"
    . (Resolve-Path $lib)

    $root = Get-RepoRoot
    $machine = Get-MachineConfig -RepoRoot $root
    $lock = Get-RemoteLock -RepoRoot $root

    if ($null -eq $lock) {
        Write-Host ""
        Write-Host "BLOCKED: git $Mode запрещён — project write lock не занят."
        Write-Host "Обычный путь: отправьте задачу в Cursor Agent, lock получится автоматически."
        Write-Host "Для ручной работы: .\scripts\project-lock-acquire.ps1"
        exit 10
    }

    if ($lock.machine_id -ne $machine.machine_id) {
        Write-Host ""
        Write-Host "BLOCKED: git $Mode запрещён."
        Write-Host "Project lock принадлежит другому компьютеру: $($lock.machine_name)"
        Write-Host "Lock с: $($lock.started_at)"
        exit 11
    }

    Write-Host "Project lock OK: $($machine.machine_name)"
    exit 0
}
catch {
    Write-Host ""
    Write-Host "BLOCKED: single-writer safety check failed: $($_.Exception.Message)"
    exit 12
}
