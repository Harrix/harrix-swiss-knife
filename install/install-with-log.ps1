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

$runner = Join-Path $env:TEMP ("harrix-swiss-knife-install-{0}.ps1" -f ([guid]::NewGuid().ToString("N")))
$scriptLiteral = "'" + $script.Replace("'", "''") + "'"
$logLiteral = "'" + $log.Replace("'", "''") + "'"
$runnerContent = @(
    '$ErrorActionPreference = "Continue"',
    '$ScriptPath = ' + $scriptLiteral,
    '$LogPath = ' + $logLiteral,
    '$TranscriptPath = $LogPath',
    'try {',
    '    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)',
    '    $OutputEncoding = [Console]::OutputEncoding',
    '}',
    'catch { }',
    '',
    '$exitCode = 0',
    'try {',
    '    Start-Transcript -LiteralPath $TranscriptPath -Force | Out-Null',
    '    & $ScriptPath -NoPauseOnError',
    '    if ($null -ne $global:LASTEXITCODE) { $exitCode = $global:LASTEXITCODE }',
    '}',
    'catch {',
    '    $exitCode = 1',
    '    Write-Host $_',
    '}',
    'finally {',
    '    try { Stop-Transcript | Out-Null } catch { }',
    '}',
    '',
    'exit $exitCode'
) -join [Environment]::NewLine

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
) | Out-File -LiteralPath $log -Append

Start-Process -FilePath notepad.exe -ArgumentList ('"' + $log + '"') | Out-Null
Write-Host "Install log: $log"
exit $exitCode
