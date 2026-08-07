$ErrorActionPreference = "Stop"

function Emit-Result {
    param(
        [Parameter(Mandatory=$true)][bool]$Continue,
        [string]$Message = ""
    )

    $obj = [ordered]@{ continue = $Continue }
    if (-not [string]::IsNullOrWhiteSpace($Message)) {
        $obj["user_message"] = $Message
    }

    [Console]::Out.WriteLine(($obj | ConvertTo-Json -Compress))
    [Console]::Out.Flush()
    Start-Sleep -Milliseconds 100
}

try {
    # Cursor передаёт JSON на stdin; здесь он нужен только чтобы гарантированно вычитать поток.
    $null = [Console]::In.ReadToEnd()

    $lib = Join-Path $PSScriptRoot "..\..\scripts\project-lock-lib.ps1"
    . (Resolve-Path $lib)

    $root = Get-RepoRoot
    $machine = Get-MachineConfig -RepoRoot $root

    $preflight = Invoke-ProjectPreflight -RepoRoot $root
    Write-LockLog -RepoRoot $root -Message "PREFLIGHT machine=$($machine.machine_name) branch=$($preflight.branch) dirty=$($preflight.dirty) action=$($preflight.action)"

    $result = Acquire-ProjectLock -RepoRoot $root -MachineConfig $machine

    if ($result.owned) {
        Emit-Result -Continue $true
        exit 0
    }

    $lock = $result.lock
    $owner = if ($lock.machine_name) { $lock.machine_name } else { "другой компьютер" }
    $started = if ($lock.started_at) { $lock.started_at } else { "время неизвестно" }

    Emit-Result -Continue $false -Message "PROJECT WRITE LOCK: задача не запущена. Проект сейчас занят компьютером '$owner' (lock с $started). Дождитесь завершения работы на этом ПК или проверьте lock через scripts/project-lock-status.ps1."
    exit 0
}
catch {
    Emit-Result -Continue $false -Message "GIT PREFLIGHT / PROJECT LOCK BLOCKED: $($_.Exception.Message)"
    exit 0
}
