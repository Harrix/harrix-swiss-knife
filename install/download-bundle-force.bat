@echo off
REM Run Download-Bundle.ps1 elevated with -Force.

cd /d "%~dp0"
echo Starting elevated bundle download (UAC prompt may appear)...

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$script = (Resolve-Path -LiteralPath (Join-Path (Get-Location) 'Download-Bundle.ps1')).Path; if (-not (Test-Path -LiteralPath $script)) { Write-Error ('Not found: ' + $script); exit 1 }; $p = Start-Process -FilePath powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',$script,'-Force'; exit $(if ($null -ne $p.ExitCode) { $p.ExitCode } else { 1 })"

set EXITCODE=%ERRORLEVEL%
echo.
if %EXITCODE% neq 0 (
  echo Bundle download finished with error code %EXITCODE%.
)
pause
