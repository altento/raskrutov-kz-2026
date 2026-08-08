$ErrorActionPreference = "Stop"

function Emit-Result {
    param([bool]$Continue, [string]$Message = "")
    $obj = [ordered]@{ continue = $Continue }
    if ($Message) { $obj["user_message"] = $Message }
    [Console]::Out.WriteLine(($obj | ConvertTo-Json -Compress))
    [Console]::Out.Flush()
}

try {
    $null = [Console]::In.ReadToEnd()
    $lib = Join-Path $PSScriptRoot "..\..\scripts\parallel-work-lib.ps1"
    . (Resolve-Path $lib)

    $root = Get-ParallelRepoRoot
    Assert-ParallelRepository -RepoRoot $root
    $ctx = Assert-OwnWorkBranch -RepoRoot $root

    if (-not (Test-WorkingTreeClean -RepoRoot $root)) {
        Emit-Result -Continue $false -Message "PARALLEL WORK BLOCKED: рабочее дерево содержит незавершённые изменения. Сначала завершите или сохраните предыдущую задачу."
        exit 0
    }

    $sync = Sync-WorkBranchToMain -RepoRoot $root -WorkBranch $ctx.branch
    New-ParallelSessionMarker -RepoRoot $root -MachineConfig $ctx.machine -WorkBranch $ctx.branch

    Emit-Result -Continue $true -Message "PARALLEL WORK: $($ctx.machine.machine_name) / $($ctx.branch) синхронизирован с main. Можно работать."
    exit 0
}
catch {
    Emit-Result -Continue $false -Message "PARALLEL WORK BLOCKED: $($_.Exception.Message)"
    exit 0
}
