@echo off
REM Runs deploy-harrix-swiss-knife.ps1 in elevated PowerShell (UAC prompt).
REM Use when symlink step fails without Windows Developer Mode.
REM Extra switches (-InstallRoot, etc.) are not passed; run the .ps1 from an elevated shell if you need them.

cd /d "%~dp0"
echo Starting elevated deploy (UAC prompt may appear)...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$script = (Resolve-Path -LiteralPath (Join-Path (Get-Location) 'deploy-harrix-swiss-knife.ps1')).Path; if (-not (Test-Path -LiteralPath $script)) { Write-Error ('Not found: ' + $script); exit 1 }; $p = Start-Process -FilePath powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',$script; exit $(if ($null -ne $p.ExitCode) { $p.ExitCode } else { 1 })"
set EXITCODE=%ERRORLEVEL%
echo.
if %EXITCODE% neq 0 (
  echo Launcher finished with error code %EXITCODE%.
  echo If you saw a separate elevated window, read the message there and fix prerequisites ^(often install App Installer / winget from Microsoft Store^).
)
pause
