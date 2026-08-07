$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$skillFiles = Get-ChildItem ".agents\skills" -Recurse -Filter "SKILL.md" -File
$referenceFiles = Get-ChildItem ".agents\skills" -Recurse -File |
    Where-Object { $_.FullName -match "\\references\\" }

if ($skillFiles.Count -ne 13) {
    throw "Ожидалось 13 SKILL.md, найдено: $($skillFiles.Count)"
}

if ($referenceFiles.Count -ne 4) {
    throw "Ожидалось 4 reference-файла, найдено: $($referenceFiles.Count)"
}

git add -- .agents/skills
git commit -m "feat: add complete project agent skills bundle"
git push origin main

Write-Host ""
Write-Host "Готово: опубликовано 13 навыков и 4 reference-файла." -ForegroundColor Green
Write-Host "Проверка: (Get-ChildItem .agents\skills -Recurse -Filter SKILL.md).Count"
