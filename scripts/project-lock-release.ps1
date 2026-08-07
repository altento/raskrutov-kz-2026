param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$lib = Join-Path $PSScriptRoot "project-lock-lib.ps1"
. (Resolve-Path $lib)

$root = Get-RepoRoot
$machine = Get-MachineConfig -RepoRoot $root
$lock = Get-RemoteLock -RepoRoot $root

if ($null -eq $lock) {
    Write-Host "Lock уже свободен."
    Remove-LocalLockOwner -RepoRoot $root
    exit 0
}

if ($lock.machine_id -ne $machine.machine_id -and -not $Force) {
    Write-Host "ОТКАЗ: lock принадлежит другому компьютеру: $($lock.machine_name)"
    Write-Host "Для аварийного снятия после проверки используйте:"
    Write-Host "  .\scripts\project-lock-release.ps1 -Force"
    exit 2
}

if ($lock.machine_id -ne $machine.machine_id -and $Force) {
    Write-Host "ВНИМАНИЕ: lock принадлежит '$($lock.machine_name)' с $($lock.started_at)."
    Write-Host "Force-release допустим только если вы уверены, что тот компьютер больше НЕ работает."
    $confirm = Read-Host "Введите RELEASE для подтверждения"
    if ($confirm -ne "RELEASE") {
        Write-Host "Отменено."
        exit 3
    }
}

$result = Release-ProjectLock -RepoRoot $root -MachineConfig $machine -Force:$Force

if ($result.released) {
    Write-Host "LOCK RELEASED"
    exit 0
}

Write-Host "LOCK NOT RELEASED: $($result.reason)"
if ($result.message) {
    Write-Host $result.message
}
exit 4
