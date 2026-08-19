#Requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet("Auto", "Online", "Offline")]
    [string] $Mode = "Auto",
    [switch] $SkipPrerequisites,
    [switch] $SkipGit,
    [switch] $SkipUv,
    [switch] $SkipVsCode,
    [switch] $SkipPython,
    [switch] $PrerequisitesChosen,
    [switch] $NonInteractive
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-IsAdministrator {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($id)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Convert-PrerequisiteEmit {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [object[]] $Lines
    )
    $plan = @{
        Git         = $true
        Uv          = $true
        VsCode      = $true
        Python      = $true
        NeedElevate = $false
    }
    foreach ($line in $Lines) {
        $text = [string]$line
        if ($text -match '^HSK_PREREQ_GIT=(\d)') { $plan.Git = $Matches[1] -eq "1" }
        elseif ($text -match '^HSK_PREREQ_UV=(\d)') { $plan.Uv = $Matches[1] -eq "1" }
        elseif ($text -match '^HSK_PREREQ_VSCODE=(\d)') { $plan.VsCode = $Matches[1] -eq "1" }
        elseif ($text -match '^HSK_PREREQ_PYTHON=(\d)') { $plan.Python = $Matches[1] -eq "1" }
        elseif ($text -match '^HSK_PREREQ_NEED_ELEVATE=(\d)') { $plan.NeedElevate = $Matches[1] -eq "1" }
    }
    return $plan
}

$script = Join-Path $PSScriptRoot "harrix-swiss-knife.ps1"
$log = Join-Path $PSScriptRoot "install.log"
if (-not (Test-Path -LiteralPath $script)) {
    Write-Error "Not found: $script"
    exit 1
}

$plan = @{
    Git         = $true
    Uv          = $true
    VsCode      = $true
    Python      = $true
    NeedElevate = $false
}
if ($SkipPrerequisites) {
    $plan.Git = $false
    $plan.Uv = $false
    $plan.VsCode = $false
    $plan.Python = $false
}
elseif ($PrerequisitesChosen) {
    $plan.Git = -not $SkipGit
    $plan.Uv = -not $SkipUv
    $plan.VsCode = -not $SkipVsCode
    $plan.Python = -not $SkipPython
    $plan.NeedElevate = $plan.Git -or $plan.VsCode
}
else {
    $emitArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $script, "-EmitPrerequisiteChoices")
    if ($NonInteractive) { $emitArgs += "-NonInteractive" }
    if ($SkipGit) { $emitArgs += "-SkipGit" }
    if ($SkipUv) { $emitArgs += "-SkipUv" }
    if ($SkipVsCode) { $emitArgs += "-SkipVsCode" }
    if ($SkipPython) { $emitArgs += "-SkipPython" }
    $emitOutput = & powershell.exe @emitArgs
    $emitCode = $LASTEXITCODE
    if ($null -eq $emitCode) { $emitCode = 0 }
    if ($emitCode -ne 0) {
        Write-Error "Prerequisite menu failed (exit $emitCode)."
        exit $emitCode
    }
    $plan = Convert-PrerequisiteEmit -Lines @($emitOutput)
}

$runner = Join-Path $env:TEMP ("harrix-swiss-knife-install-{0}.ps1" -f ([guid]::NewGuid().ToString("N")))
$scriptLiteral = "'" + $script.Replace("'", "''") + "'"
$logLiteral = "'" + $log.Replace("'", "''") + "'"
$modeLiteral = "'" + $Mode.Replace("'", "''") + "'"
$extraSwitches = " -PrerequisitesChosen"
if ($SkipPrerequisites) { $extraSwitches += " -SkipPrerequisites" }
if ($NonInteractive) { $extraSwitches += " -NonInteractive" }
if (-not $plan.Git) { $extraSwitches += " -SkipGit" }
if (-not $plan.Uv) { $extraSwitches += " -SkipUv" }
if (-not $plan.VsCode) { $extraSwitches += " -SkipVsCode" }
if (-not $plan.Python) { $extraSwitches += " -SkipPython" }
$runnerContent = @(
    '$ErrorActionPreference = "Continue"',
    '$ScriptPath = ' + $scriptLiteral,
    '$LogPath = ' + $logLiteral,
    '$Mode = ' + $modeLiteral,
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
    '    & $ScriptPath -Mode $Mode -NoPauseOnError' + $extraSwitches,
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
$runnerArgs = @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $runner
)
try {
    $needElevate = [bool]$plan.NeedElevate
    $alreadyAdmin = Test-IsAdministrator
    if ($needElevate -and -not $alreadyAdmin) {
        Write-Host "Requesting Administrator once (Git / VS Code install)." -ForegroundColor DarkGray
        $process = Start-Process -FilePath powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList $runnerArgs
    }
    else {
        if ($needElevate -and $alreadyAdmin) {
            Write-Host "Already running as Administrator; continuing without a second UAC prompt." -ForegroundColor DarkGray
        }
        $process = Start-Process -FilePath powershell.exe -Wait -PassThru -NoNewWindow -ArgumentList $runnerArgs
    }
    $exitCode = if ($null -ne $process -and $null -ne $process.ExitCode) { $process.ExitCode } else { 1 }
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
