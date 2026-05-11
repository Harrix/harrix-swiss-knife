#Requires -Version 5.1
# Run download-bundle.ps1 as admin and write log to install\dependencies\.
# Note: $ErrorActionPreference is kept as "Continue" so pipeline output via Tee-Object does not interfere with capturing $LASTEXITCODE.
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet("Binaries", "Installers")]
    [string] $Kind
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

Set-Location -LiteralPath $PSScriptRoot

$bundleScript = Join-Path $PSScriptRoot "download-bundle.ps1"
if (-not (Test-Path -LiteralPath $bundleScript)) {
    Write-Host ("Not found: {0}" -f $bundleScript) -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

$deps = Join-Path $PSScriptRoot "dependencies"
if (-not (Test-Path -LiteralPath $deps)) {
    New-Item -ItemType Directory -Path $deps -Force | Out-Null
}

$logName = if ($Kind -eq "Binaries") { "download-bundle-binaries.log" } else { "download-bundle-installers.log" }
$logPath = Join-Path $deps $logName

$exitCode = 0
try {
    if ($Kind -eq "Binaries") {
        & $bundleScript -Force -OnlyBinaries *>&1 | Tee-Object -FilePath $logPath
    }
    else {
        & $bundleScript -Force -SkipBinaries -SkipRepos -SkipUvCache *>&1 | Tee-Object -FilePath $logPath
    }
    $lastExitCodeVar = Get-Variable -Name "LASTEXITCODE" -Scope Global -ErrorAction SilentlyContinue
    if ($null -ne $lastExitCodeVar) {
        $exitCode = [int]$lastExitCodeVar.Value
    }
    else {
        $exitCode = 0
    }
}
catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    $exitCode = 1
}

if ($null -eq $exitCode) {
    $exitCode = 0
}

Write-Host ""
Write-Host ("Elevated download finished (exit code {0}). Log: {1}" -f $exitCode, $logPath) -ForegroundColor Cyan
Write-Host "Press Enter to close this elevated window..." -ForegroundColor Yellow
Read-Host | Out-Null

exit $exitCode
