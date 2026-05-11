#Requires -Version 5.1
# Populate install\dependencies\uv-cache\ via download-bundle.ps1 and write log.
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

$logPath = Join-Path $PSScriptRoot "download-uv-cache.log"
Write-Host ("Writing log to: {0}" -f $logPath) -ForegroundColor DarkGray
Write-Host ""

$script = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "download-bundle.ps1")).Path
& $script -OnlyUvCache *>&1 | Tee-Object -FilePath $logPath -Append | Out-Host
exit $LASTEXITCODE
