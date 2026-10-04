# Auto commit and push when the working tree has changes (run by the Stop hook).
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

git add -A
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) { exit 0 }

$msg = "Auto commit " + (Get-Date -Format 'yyyy-MM-dd HH:mm')
git commit -m $msg
git push origin HEAD
