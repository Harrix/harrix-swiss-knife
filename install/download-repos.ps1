#Requires -Version 5.1
# Snapshot sibling repos (git archive HEAD) via download-bundle.ps1 and write log.
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

$logPath = Join-Path $PSScriptRoot "download-repos.log"
Write-Host ("Writing log to: {0}" -f $logPath) -ForegroundColor DarkGray
Write-Host ""

$script = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "download-bundle.ps1")).Path
& $script -OnlyRepos *>&1 | Tee-Object -FilePath $logPath -Append | Out-Host
exit $LASTEXITCODE
