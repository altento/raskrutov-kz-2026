$ErrorActionPreference = "SilentlyContinue"

try {
    $null = [Console]::In.ReadToEnd()

    $lib = Join-Path $PSScriptRoot "..\..\scripts\project-lock-lib.ps1"
    . (Resolve-Path $lib)

    $root = Get-RepoRoot
    $machine = Get-MachineConfig -RepoRoot $root
    $remoteLock = Get-RemoteLock -RepoRoot $root

    if ($null -eq $remoteLock) {
        Remove-LocalLockOwner -RepoRoot $root
        [Console]::Out.WriteLine("{}")
        exit 0
    }

    if ($remoteLock.machine_id -ne $machine.machine_id) {
        Remove-LocalLockOwner -RepoRoot $root
        [Console]::Out.WriteLine("{}")
        exit 0
    }

    $safe = Test-BranchFullyPushed -RepoRoot $root

    if ($safe.safe) {
        $release = Release-ProjectLock -RepoRoot $root -MachineConfig $machine
        Write-LockLog -RepoRoot $root -Message "AFTER_RESPONSE auto-release result=$($release.released) reason=$($release.reason)"
    } else {
        Write-LockLog -RepoRoot $root -Message "AFTER_RESPONSE lock retained reason=$($safe.reason)"
    }

    [Console]::Out.WriteLine("{}")
    [Console]::Out.Flush()
    Start-Sleep -Milliseconds 60
}
catch {
    # Fail-safe: ошибка after-response НЕ должна удалять lock.
    try {
        $root = (& git rev-parse --show-toplevel 2>$null).Trim()
        if ($root) {
            Add-Content -LiteralPath (Join-Path $root ".git\cursor-lock.log") -Value ("{0} AFTER_RESPONSE ERROR {1}" -f ([DateTime]::UtcNow.ToString("o")), $_.Exception.Message) -Encoding UTF8
        }
    } catch {}
    [Console]::Out.WriteLine("{}")
    exit 0
}
