#Requires -Version 5.1
# Remove *.log files from install\ and install\dependencies\ only (top level per folder).
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$installDir = $PSScriptRoot
Write-Host ""
Write-Host ("Install dir: {0}" -f $installDir) -ForegroundColor Green

$removedFiles = 0

foreach ($logRoot in @($installDir, (Join-Path $installDir "dependencies"))) {
    if (-not (Test-Path -LiteralPath $logRoot)) { continue }
    foreach ($log in @(Get-ChildItem -LiteralPath $logRoot -File -Filter "*.log" -Force -ErrorAction SilentlyContinue)) {
        Remove-Item -LiteralPath $log.FullName -Force -ErrorAction Stop
        $removedFiles++
        Write-Host ("    Removed: {0}" -f $log.FullName) -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host ("Done. Removed {0} log file(s)." -f $removedFiles) -ForegroundColor Green
