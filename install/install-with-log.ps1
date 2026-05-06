#Requires -Version 5.1
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script = Join-Path $PSScriptRoot "harrix-swiss-knife.ps1"
$log = Join-Path $PSScriptRoot "install.log"
if (-not (Test-Path -LiteralPath $script)) {
    Write-Error "Not found: $script"
    exit 1
}

$header = @(
    "=== Harrix Swiss Knife install log ===",
    "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "Working directory: $PSScriptRoot",
    ""
)
$header | Set-Content -LiteralPath $log -Encoding UTF8

$runner = Join-Path $env:TEMP ("harrix-swiss-knife-install-{0}.ps1" -f ([guid]::NewGuid().ToString("N")))
$runnerContent = @"
`$ErrorActionPreference = "Continue"
try {
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding(`$false)
    `$OutputEncoding = [Console]::OutputEncoding
}
catch { }

& "$script" -NoPauseOnError *>&1 | ForEach-Object {
    `$line = `$_.ToString()
    `$line | Out-File -LiteralPath "$log" -Append -Encoding UTF8
}

exit 0
"@

$runnerContent | Set-Content -LiteralPath $runner -Encoding UTF8
try {
    $process = Start-Process -FilePath powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $runner
    )
    $exitCode = if ($null -ne $process.ExitCode) { $process.ExitCode } else { 1 }
}
finally {
    Remove-Item -LiteralPath $runner -Force -ErrorAction SilentlyContinue
}

@(
    "",
    "Finished: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "Exit code: $exitCode"
) | Out-File -LiteralPath $log -Append -Encoding UTF8

Start-Process -FilePath notepad.exe -ArgumentList ('"' + $log + '"') | Out-Null
Write-Host "Install log: $log"
exit $exitCode
