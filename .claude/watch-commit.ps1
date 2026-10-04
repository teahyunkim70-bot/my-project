# Watch the project folder; commit and push 3 seconds after the last file change.
$root = Split-Path -Parent $PSScriptRoot
$script = Join-Path $PSScriptRoot 'auto-commit.ps1'
$log = Join-Path $PSScriptRoot 'watch-commit.log'

$w = New-Object System.IO.FileSystemWatcher $root
$w.IncludeSubdirectories = $true
$w.NotifyFilter = [System.IO.NotifyFilters]'FileName, DirectoryName, LastWrite'

$pending = $false
$last = Get-Date
while ($true) {
    $r = $w.WaitForChanged([System.IO.WatcherChangeTypes]::All, 1000)
    if (-not $r.TimedOut) {
        $n = $r.Name
        if ($n -notmatch '(^|\\)(\.git|node_modules)(\\|$)' -and $n -ne '.claude\watch-commit.log') {
            $pending = $true
            $last = Get-Date
        }
    }
    if ($pending -and ((Get-Date) - $last).TotalSeconds -ge 3) {
        $pending = $false
        try {
            $out = & powershell -NoProfile -ExecutionPolicy Bypass -File $script 2>&1 | Out-String
            Add-Content -Path $log -Value ("[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $out.Trim())
        } catch {
            Add-Content -Path $log -Value ("[{0}] ERROR {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $_)
        }
    }
}
