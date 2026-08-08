$ErrorActionPreference = "Stop"

function Emit-Allow {
    [Console]::Out.WriteLine('{"permission":"allow"}')
    [Console]::Out.Flush()
}

function Emit-Deny([string]$Message) {
    $obj = [ordered]@{ permission = "deny"; user_message = $Message; agent_message = $Message }
    [Console]::Out.WriteLine(($obj | ConvertTo-Json -Compress))
    [Console]::Out.Flush()
}

try {
    $null = [Console]::In.ReadToEnd()
    $lib = Join-Path $PSScriptRoot "..\..\scripts\parallel-work-lib.ps1"
    . (Resolve-Path $lib)

    $root = Get-ParallelRepoRoot
    $ctx = Assert-OwnWorkBranch -RepoRoot $root

    if (-not (Test-ParallelSessionMarker -RepoRoot $root -MachineConfig $ctx.machine -WorkBranch $ctx.branch)) {
        Emit-Deny "Изменение заблокировано: нет активной безопасной Cursor-сессии для $($ctx.branch). Повторно отправьте промт."
        exit 0
    }

    Emit-Allow
    exit 0
}
catch {
    Emit-Deny "Изменение заблокировано parallel-work safety: $($_.Exception.Message)"
    exit 0
}
