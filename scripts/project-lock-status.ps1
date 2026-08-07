$ErrorActionPreference = "Stop"

$lib = Join-Path $PSScriptRoot "project-lock-lib.ps1"
. (Resolve-Path $lib)

$root = Get-RepoRoot
Assert-CorrectRepository -RepoRoot $root | Out-Null
$machine = Get-MachineConfig -RepoRoot $root
$lock = Get-RemoteLock -RepoRoot $root

Write-Host "=== PROJECT LOCK STATUS ==="
Write-Host "This machine: $($machine.machine_name) / $($machine.machine_id)"

if ($null -eq $lock) {
    Write-Host "Remote lock: FREE"
    exit 0
}

Write-Host "Remote lock: BUSY"
Write-Host "Owner machine:  $($lock.machine_name)"
Write-Host "Computer name:  $($lock.computer_name)"
Write-Host "Windows user:   $($lock.windows_user)"
Write-Host "Started UTC:    $($lock.started_at)"
Write-Host "Lock SHA:       $($lock.sha)"

if ($lock.machine_id -eq $machine.machine_id) {
    Write-Host "Ownership: THIS COMPUTER"
    exit 0
}

Write-Host "Ownership: OTHER COMPUTER"
exit 2
