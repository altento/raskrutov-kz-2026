$ErrorActionPreference = "Stop"

$script:LockBranch = "cursor-lock/site-write"
$script:LockRef = "refs/heads/$($script:LockBranch)"
$script:ExpectedRepoFragment = "raskrutovstudio-collab/raskrutov-kz-2026"
$script:EmptyTreeSha = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

# пределяем корень репозитория средствами PowerShell.
# то избегает проблем Windows PowerShell 5.1 с кириллицей
# в выводе `git rev-parse --show-toplevel`.
$script:SingleWriterRepoRoot = [System.IO.Path]::GetFullPath(
    (Join-Path $PSScriptRoot "..")
)

function Get-RepoRoot {
    $root = (Resolve-Path -LiteralPath $script:SingleWriterRepoRoot).Path

    if (-not (Test-Path -LiteralPath (Join-Path $root ".git"))) {
        throw "е удалось определить корень Git-репозитория."
    }

    return $root
}

function Write-LockLog {
    param(
        [Parameter(Mandatory=$true)][string]$RepoRoot,
        [Parameter(Mandatory=$true)][string]$Message
    )
    $logPath = Join-Path $RepoRoot ".git\cursor-lock.log"
    $line = "{0} {1}" -f ([DateTime]::UtcNow.ToString("o")), $Message
    Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
}

function Get-MachineConfig {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)

    $path = Join-Path $RepoRoot ".git\cursor-machine-id.json"
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Не настроен machine ID. Один раз запустите: .\scripts\setup-single-writer.ps1 -MachineName PC1 (или PC2)."
    }

    try {
        $cfg = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        throw "Повреждён файл .git/cursor-machine-id.json. Повторите setup-single-writer.ps1."
    }

    if ([string]::IsNullOrWhiteSpace($cfg.machine_id) -or [string]::IsNullOrWhiteSpace($cfg.machine_name)) {
        throw "В machine config отсутствует machine_id или machine_name."
    }

    return $cfg
}

function Assert-CorrectRepository {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)

    $remoteUrl = (& git -C $RepoRoot remote get-url origin 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($remoteUrl)) {
        throw "Remote origin не настроен."
    }

    $normalized = $remoteUrl.Trim().ToLowerInvariant()
    if (-not $normalized.Contains($script:ExpectedRepoFragment)) {
        throw "Lock-пакет предназначен для $($script:ExpectedRepoFragment), а origin = $($remoteUrl.Trim())."
    }

    return $remoteUrl.Trim()
}

function Invoke-GitFetch {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)

    $out = (& git -C $RepoRoot fetch origin --prune 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "git fetch origin --prune завершился ошибкой: $($out -join ' ')"
    }
}

function Get-RemoteLock {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)

    $ls = (& git -C $RepoRoot ls-remote --heads origin $script:LockRef 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось проверить remote lock: $($ls -join ' ')"
    }

    $text = ($ls -join "`n").Trim()
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $null
    }

    $sha = ($text -split "\s+")[0].Trim()
    if ([string]::IsNullOrWhiteSpace($sha)) {
        throw "Не удалось определить SHA remote lock."
    }

    $fetchSpec = "+$($script:LockRef):refs/cursor-lock/remote"
    $fetchOut = (& git -C $RepoRoot fetch --quiet origin $fetchSpec 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось загрузить содержимое remote lock: $($fetchOut -join ' ')"
    }

    $message = (& git -C $RepoRoot show -s --format=%B refs/cursor-lock/remote 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось прочитать lock commit."
    }

    $data = @{}
    foreach ($line in $message) {
        if ($line -match "^([^=]+)=(.*)$") {
            $data[$matches[1].Trim()] = $matches[2].Trim()
        }
    }

    return [PSCustomObject]@{
        sha           = $sha
        machine_id    = $data["machine_id"]
        machine_name  = $data["machine_name"]
        computer_name = $data["computer_name"]
        windows_user  = $data["windows_user"]
        started_at    = $data["started_at"]
        repo           = $data["repo"]
    }
}

function Save-LocalLockOwner {
    param(
        [Parameter(Mandatory=$true)][string]$RepoRoot,
        [Parameter(Mandatory=$true)]$MachineConfig,
        [Parameter(Mandatory=$true)][string]$Sha
    )

    $path = Join-Path $RepoRoot ".git\cursor-lock-owner.json"
    [PSCustomObject]@{
        machine_id   = $MachineConfig.machine_id
        machine_name = $MachineConfig.machine_name
        lock_sha     = $Sha
        recorded_at  = [DateTime]::UtcNow.ToString("o")
    } | ConvertTo-Json | Set-Content -LiteralPath $path -Encoding UTF8
}

function Remove-LocalLockOwner {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)
    $path = Join-Path $RepoRoot ".git\cursor-lock-owner.json"
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
    }
}

function Acquire-ProjectLock {
    param(
        [Parameter(Mandatory=$true)][string]$RepoRoot,
        [Parameter(Mandatory=$true)]$MachineConfig
    )

    Assert-CorrectRepository -RepoRoot $RepoRoot | Out-Null

    $existing = Get-RemoteLock -RepoRoot $RepoRoot
    if ($null -ne $existing) {
        if ($existing.machine_id -eq $MachineConfig.machine_id) {
            Save-LocalLockOwner -RepoRoot $RepoRoot -MachineConfig $MachineConfig -Sha $existing.sha
            Write-LockLog -RepoRoot $RepoRoot -Message "LOCK already owned by $($MachineConfig.machine_name), sha=$($existing.sha)"
            return [PSCustomObject]@{
                owned = $true
                acquired_now = $false
                lock = $existing
            }
        }

        return [PSCustomObject]@{
            owned = $false
            acquired_now = $false
            lock = $existing
        }
    }

    $repoUrl = (& git -C $RepoRoot remote get-url origin).Trim()
    $started = [DateTime]::UtcNow.ToString("o")
    $message = @"
CURSOR_PROJECT_LOCK
machine_id=$($MachineConfig.machine_id)
machine_name=$($MachineConfig.machine_name)
computer_name=$env:COMPUTERNAME
windows_user=$env:USERNAME
started_at=$started
repo=$repoUrl
"@

    $commitOut = ($message | & git -C $RepoRoot commit-tree $script:EmptyTreeSha -F - 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось создать lock commit. Проверьте git user.name/user.email. $($commitOut -join ' ')"
    }

    $commitSha = ($commitOut -join "").Trim()
    if ([string]::IsNullOrWhiteSpace($commitSha)) {
        throw "git commit-tree не вернул SHA."
    }

    $refspec = "$commitSha`:$($script:LockRef)"
    $lease = "--force-with-lease=$($script:LockRef):"

    $oldInternal = $env:CURSOR_PROJECT_LOCK_INTERNAL
    $env:CURSOR_PROJECT_LOCK_INTERNAL = "1"
    try {
        $pushOut = (& git -C $RepoRoot push --quiet origin $refspec $lease 2>$null)
        $pushCode = $LASTEXITCODE
    } finally {
        if ($null -eq $oldInternal) {
            Remove-Item Env:CURSOR_PROJECT_LOCK_INTERNAL -ErrorAction SilentlyContinue
        } else {
            $env:CURSOR_PROJECT_LOCK_INTERNAL = $oldInternal
        }
    }

    if ($pushCode -eq 0) {
        $newLock = [PSCustomObject]@{
            sha = $commitSha
            machine_id = $MachineConfig.machine_id
            machine_name = $MachineConfig.machine_name
            computer_name = $env:COMPUTERNAME
            windows_user = $env:USERNAME
            started_at = $started
            repo = $repoUrl
        }
        Save-LocalLockOwner -RepoRoot $RepoRoot -MachineConfig $MachineConfig -Sha $commitSha
        Write-LockLog -RepoRoot $RepoRoot -Message "LOCK acquired by $($MachineConfig.machine_name), sha=$commitSha"
        return [PSCustomObject]@{
            owned = $true
            acquired_now = $true
            lock = $newLock
        }
    }

    # Возможна гонка: другой ПК успел создать lock после нашей проверки.
    Start-Sleep -Milliseconds 200
    $raceLock = Get-RemoteLock -RepoRoot $RepoRoot
    if ($null -ne $raceLock -and $raceLock.machine_id -eq $MachineConfig.machine_id) {
        Save-LocalLockOwner -RepoRoot $RepoRoot -MachineConfig $MachineConfig -Sha $raceLock.sha
        return [PSCustomObject]@{
            owned = $true
            acquired_now = $false
            lock = $raceLock
        }
    }

    if ($null -ne $raceLock) {
        return [PSCustomObject]@{
            owned = $false
            acquired_now = $false
            lock = $raceLock
        }
    }

    throw "Не удалось получить GitHub lock: $($pushOut -join ' ')"
}

function Release-ProjectLock {
    param(
        [Parameter(Mandatory=$true)][string]$RepoRoot,
        [Parameter(Mandatory=$true)]$MachineConfig,
        [switch]$Force
    )

    $existing = Get-RemoteLock -RepoRoot $RepoRoot
    if ($null -eq $existing) {
        Remove-LocalLockOwner -RepoRoot $RepoRoot
        return [PSCustomObject]@{ released = $true; reason = "already-free" }
    }

    if (-not $Force -and $existing.machine_id -ne $MachineConfig.machine_id) {
        return [PSCustomObject]@{
            released = $false
            reason = "owned-by-other"
            lock = $existing
        }
    }

    $deleteRefspec = ":$($script:LockRef)"
    $lease = "--force-with-lease=$($script:LockRef):$($existing.sha)"
    $oldInternal = $env:CURSOR_PROJECT_LOCK_INTERNAL
    $env:CURSOR_PROJECT_LOCK_INTERNAL = "1"
    try {
        $out = (& git -C $RepoRoot push --quiet origin $deleteRefspec $lease 2>$null)
        $deleteCode = $LASTEXITCODE
    } finally {
        if ($null -eq $oldInternal) {
            Remove-Item Env:CURSOR_PROJECT_LOCK_INTERNAL -ErrorAction SilentlyContinue
        } else {
            $env:CURSOR_PROJECT_LOCK_INTERNAL = $oldInternal
        }
    }

    if ($deleteCode -ne 0) {
        return [PSCustomObject]@{
            released = $false
            reason = "delete-failed"
            message = ($out -join " ")
            lock = $existing
        }
    }

    Remove-LocalLockOwner -RepoRoot $RepoRoot
    try {
        & git -C $RepoRoot update-ref -d refs/cursor-lock/remote 2>$null | Out-Null
    } catch {}

    Write-LockLog -RepoRoot $RepoRoot -Message "LOCK released; previous owner=$($existing.machine_name), sha=$($existing.sha)"
    return [PSCustomObject]@{ released = $true; reason = "released"; lock = $existing }
}

function Invoke-ProjectPreflight {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)

    Assert-CorrectRepository -RepoRoot $RepoRoot | Out-Null
    Invoke-GitFetch -RepoRoot $RepoRoot

    $branch = (& git -C $RepoRoot branch --show-current).Trim()
    $statusLines = @(& git -C $RepoRoot status --porcelain)
    $dirty = $statusLines.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace(($statusLines -join ""))

    $head = (& git -C $RepoRoot rev-parse HEAD).Trim()
    $originMain = (& git -C $RepoRoot rev-parse origin/main 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($originMain)) {
        throw "origin/main не найден."
    }
    $originMain = $originMain.Trim()

    $action = "none"

    if ($branch -eq "main" -and -not $dirty) {
        $countsRaw = (& git -C $RepoRoot rev-list --left-right --count "HEAD...origin/main").Trim()
        $parts = $countsRaw -split "\s+"
        if ($parts.Count -ge 2) {
            $ahead = [int]$parts[0]
            $behind = [int]$parts[1]

            if ($ahead -eq 0 -and $behind -gt 0) {
                $pullOut = (& git -C $RepoRoot pull --ff-only origin main 2>$null)
                if ($LASTEXITCODE -ne 0) {
                    throw "Безопасный fast-forward main не удался: $($pullOut -join ' ')"
                }
                $action = "fast-forwarded-main"
                $head = (& git -C $RepoRoot rev-parse HEAD).Trim()
            } elseif ($ahead -gt 0 -and $behind -gt 0) {
                $action = "main-diverged-no-auto-merge"
            } elseif ($ahead -gt 0) {
                $action = "main-ahead-local-commits"
            }
        }
    } elseif ($dirty) {
        $action = "dirty-working-tree-protected"
    }

    return [PSCustomObject]@{
        branch = $branch
        dirty = $dirty
        head = $head
        origin_main = $originMain
        action = $action
    }
}

function Test-BranchFullyPushed {
    param([Parameter(Mandatory=$true)][string]$RepoRoot)

    $statusLines = @(& git -C $RepoRoot status --porcelain)
    $dirty = $statusLines.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace(($statusLines -join ""))
    if ($dirty) {
        return [PSCustomObject]@{ safe = $false; reason = "working-tree-dirty" }
    }

    Invoke-GitFetch -RepoRoot $RepoRoot

    $branch = (& git -C $RepoRoot branch --show-current).Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) {
        return [PSCustomObject]@{ safe = $false; reason = "detached-head" }
    }

    $upstream = (& git -C $RepoRoot rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($upstream)) {
        return [PSCustomObject]@{ safe = $false; reason = "no-upstream" }
    }
    $upstream = $upstream.Trim()

    $countsRaw = (& git -C $RepoRoot rev-list --left-right --count "HEAD...$upstream").Trim()
    $parts = $countsRaw -split "\s+"
    if ($parts.Count -lt 2) {
        return [PSCustomObject]@{ safe = $false; reason = "cannot-compare-upstream" }
    }

    $ahead = [int]$parts[0]
    $behind = [int]$parts[1]

    # Для HEAD...upstream: left = только HEAD (ahead), right = только upstream (behind)
    if ($ahead -eq 0 -and $behind -eq 0) {
        return [PSCustomObject]@{
            safe = $true
            reason = "clean-and-synchronized"
            branch = $branch
            upstream = $upstream
        }
    }

    return [PSCustomObject]@{
        safe = $false
        reason = "branch-not-synchronized"
        branch = $branch
        upstream = $upstream
        ahead = $ahead
        behind = $behind
    }
}

function Test-LocalLockMarker {
    param(
        [Parameter(Mandatory=$true)][string]$RepoRoot,
        [Parameter(Mandatory=$true)]$MachineConfig
    )

    $path = Join-Path $RepoRoot ".git\cursor-lock-owner.json"
    if (-not (Test-Path -LiteralPath $path)) {
        return $false
    }

    try {
        $owner = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
        return $owner.machine_id -eq $MachineConfig.machine_id
    } catch {
        return $false
    }
}
