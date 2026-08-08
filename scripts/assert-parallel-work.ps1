param(
    [ValidateSet("commit","push")]
    [string]$Mode = "commit"
)

$ErrorActionPreference = "Stop"

try {
    $lib = Join-Path $PSScriptRoot "parallel-work-lib.ps1"
    . (Resolve-Path $lib)

    $root = Get-ParallelRepoRoot
    Assert-ParallelRepository -RepoRoot $root
    $ctx = Assert-OwnWorkBranch -RepoRoot $root

    if ($Mode -eq "push") {
        $branch = (& git -C $root branch --show-current).Trim()
        if ($branch -ne $ctx.branch) {
            throw "Push разрешён только в $($ctx.branch)."
        }
    }

    Write-Host "Parallel work OK: $($ctx.machine.machine_name) / $($ctx.branch)"
    exit 0
}
catch {
    Write-Host ""
    Write-Host "BLOCKED: parallel-work $Mode safety check failed: $($_.Exception.Message)"
    exit 12
}
