$ErrorActionPreference = "Continue"

function Section([string]$Title) {
    Write-Host ""
    Write-Host "=== $Title ==="
}

function Run-Git([string[]]$Args) {
    try {
        $out = & git @Args 2>&1
        $code = $LASTEXITCODE
        if ($null -ne $out) { $out | ForEach-Object { Write-Host $_ } }
        Write-Host "[exit=$code]"
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)"
    }
}

Write-Host "PARALLEL WORK DIAGNOSTIC"
Write-Host ("Time: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss K"))
Write-Host ("Computer: {0}" -f $env:COMPUTERNAME)
Write-Host ("Windows user: {0}" -f $env:USERNAME)
Write-Host ("PowerShell: {0}" -f $PSVersionTable.PSVersion)
Write-Host ("PWD: {0}" -f (Get-Location).Path)

Section "REPOSITORY"
Run-Git @("rev-parse", "--show-toplevel")
Run-Git @("remote", "-v")
Run-Git @("branch", "--show-current")
Run-Git @("status", "--short", "--branch")
Run-Git @("log", "-1", "--oneline")

Section "FETCH"
Run-Git @("fetch", "origin", "--prune")

Section "REMOTE REFS"
foreach ($ref in @("origin/main", "origin/work/pc1", "origin/work/pc2")) {
    Write-Host ("-- {0}" -f $ref)
    Run-Git @("rev-parse", "--verify", $ref)
}

Section "REQUIRED FILES"
$paths = @(
    "scripts/setup-parallel-work.ps1",
    "scripts/parallel-work-lib.ps1",
    "scripts/assert-parallel-work.ps1",
    ".cursor/hooks.json",
    ".cursor/hooks/before-submit-parallel.ps1",
    ".cursor/hooks/pre-tool-parallel.ps1",
    ".cursor/hooks/after-response-parallel.ps1",
    ".githooks/pre-commit",
    ".githooks/pre-push"
)
foreach ($path in $paths) {
    $exists = Test-Path -LiteralPath $path
    Write-Host ("{0} : {1}" -f $path, $exists)
}

Section "MACHINE CONFIG"
$config = ".git/cursor-machine-id.json"
if (Test-Path -LiteralPath $config) {
    try {
        $cfg = Get-Content -LiteralPath $config -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host ("machine_name: {0}" -f $cfg.machine_name)
        Write-Host ("machine_id present: {0}" -f (-not [string]::IsNullOrWhiteSpace([string]$cfg.machine_id)))
        Write-Host ("computer_name: {0}" -f $cfg.computer_name)
        Write-Host ("windows_user: {0}" -f $cfg.windows_user)
    } catch {
        Write-Host "CONFIG ERROR: $($_.Exception.Message)"
    }
} else {
    Write-Host "NO MACHINE CONFIG"
}

Section "GIT CONFIG"
Run-Git @("config", "--get", "core.hooksPath")
Run-Git @("config", "--get", "fetch.prune")
Run-Git @("config", "--get", "pull.ff")

Section "SETUP SCRIPT PARSE"
$setup = "scripts/setup-parallel-work.ps1"
if (Test-Path -LiteralPath $setup) {
    try {
        $tokens = $null
        $errors = $null
        [void][System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $setup).Path, [ref]$tokens, [ref]$errors)
        if ($errors.Count -eq 0) {
            Write-Host "setup-parallel-work.ps1 parse: OK"
        } else {
            Write-Host "setup-parallel-work.ps1 parse errors:"
            $errors | ForEach-Object { Write-Host $_.Message }
        }
    } catch {
        Write-Host "PARSE ERROR: $($_.Exception.Message)"
    }
} else {
    Write-Host "setup-parallel-work.ps1 missing"
}

Section "EXECUTION POLICY"
try {
    Get-ExecutionPolicy -List | Format-Table -AutoSize | Out-String | Write-Host
} catch {
    Write-Host "EXECUTION POLICY ERROR: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "=== DIAGNOSTIC COMPLETE ==="
