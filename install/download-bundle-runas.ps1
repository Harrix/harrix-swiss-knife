#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet("Binaries", "Installers")]
    [string] $Kind
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$worker = Join-Path $PSScriptRoot "download-bundle-elevated.ps1"
if (-not (Test-Path -LiteralPath $worker)) {
    throw "Missing worker script: $worker"
}

$logName = if ($Kind -eq "Binaries") { "download-bundle-binaries.log" } else { "download-bundle-installers.log" }
$logPath = Join-Path (Join-Path $PSScriptRoot "dependencies") $logName

Write-Host "Starting elevated bundle download ($Kind). UAC prompt may appear."
Write-Host ("Log file: {0}" -f $logPath)
Write-Host "If GitHub returns HTTP 403 (rate limit), set user env var GITHUB_TOKEN and retry."
Write-Host ""

$p = Start-Process `
    -FilePath powershell.exe `
    -Verb RunAs `
    -Wait `
    -PassThru `
    -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $worker,
        "-Kind",
        $Kind
    )

exit $(if ($null -ne $p.ExitCode) { $p.ExitCode } else { 1 })
