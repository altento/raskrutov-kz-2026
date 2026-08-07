$ErrorActionPreference = "Stop"

function Emit-Allow {
    [Console]::Out.WriteLine('{"permission":"allow"}')
    [Console]::Out.Flush()
    Start-Sleep -Milliseconds 80
}

function Emit-Deny {
    param([Parameter(Mandatory=$true)][string]$Message)
    $obj = [ordered]@{
        permission = "deny"
        user_message = $Message
        agent_message = $Message
    }
    [Console]::Out.WriteLine(($obj | ConvertTo-Json -Compress))
    [Console]::Out.Flush()
    Start-Sleep -Milliseconds 100
}

try {
    $null = [Console]::In.ReadToEnd()

    $lib = Join-Path $PSScriptRoot "..\..\scripts\project-lock-lib.ps1"
    . (Resolve-Path $lib)

    $root = Get-RepoRoot
    $machine = Get-MachineConfig -RepoRoot $root

    if (Test-LocalLockMarker -RepoRoot $root -MachineConfig $machine) {
        Emit-Allow
        exit 0
    }

    Emit-Deny -Message "Изменение заблокировано: текущая Cursor-сессия не имеет локального подтверждения project write lock. Повторно отправьте промт; beforeSubmitPrompt должен получить GitHub lock."
    exit 0
}
catch {
    Emit-Deny -Message "Изменение заблокировано системой single-writer: $($_.Exception.Message)"
    exit 0
}
