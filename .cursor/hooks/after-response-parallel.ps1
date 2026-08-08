$ErrorActionPreference = "SilentlyContinue"

function Emit([string]$Message) {
    $obj = [ordered]@{}
    if ($Message) { $obj["user_message"] = $Message }
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
        Emit ""
        exit 0
    }

    $changes = @(& git -C $root status --porcelain)
    $dirty = $changes.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace(($changes -join ""))

    if (-not $dirty) {
        Remove-ParallelSessionMarker -RepoRoot $root
        Emit "PARALLEL WORK: изменений нет."
        exit 0
    }

    Push-Location $root
    try {
        & npm run quality:all
        $qualityCode = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    if ($qualityCode -ne 0) {
        Remove-ParallelSessionMarker -RepoRoot $root
        Emit "PARALLEL WORK: quality:all не пройден. Изменения сохранены локально, автоматический commit/push остановлен."
        exit 0
    }

    & git -C $root add -A
    if ($LASTEXITCODE -ne 0) { throw "git add завершился ошибкой." }

    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    $message = "auto($($ctx.machine.machine_name)): Cursor task $stamp"
    & git -C $root commit -m $message
    if ($LASTEXITCODE -ne 0) { throw "git commit завершился ошибкой." }

    & git -C $root push origin $ctx.branch
    if ($LASTEXITCODE -ne 0) { throw "git push завершился ошибкой." }

    Remove-ParallelSessionMarker -RepoRoot $root
    Emit "PARALLEL WORK: изменения проверены, закоммичены и отправлены в $($ctx.branch). GitHub интегрирует их в main автоматически."
    exit 0
}
catch {
    try {
        $root = Get-ParallelRepoRoot
        Remove-ParallelSessionMarker -RepoRoot $root
    } catch {}
    Emit "PARALLEL WORK AUTO-SYNC STOPPED: $($_.Exception.Message). Изменения не потеряны."
    exit 0
}
