$ErrorActionPreference = "Stop"

$lib = Join-Path $PSScriptRoot "project-lock-lib.ps1"
. (Resolve-Path $lib)

$root = Get-RepoRoot
$machine = Get-MachineConfig -RepoRoot $root
$null = Invoke-ProjectPreflight -RepoRoot $root
$result = Acquire-ProjectLock -RepoRoot $root -MachineConfig $machine

if ($result.owned) {
    Write-Host "LOCK OWNED: $($machine.machine_name)"
    Write-Host "SHA: $($result.lock.sha)"
    exit 0
}

Write-Host "LOCK BUSY"
Write-Host "Owner: $($result.lock.machine_name)"
Write-Host "Started: $($result.lock.started_at)"
exit 2
