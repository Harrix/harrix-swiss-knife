@echo off
REM Offline-first installer entrypoint.
REM Assumes you have already prepared install\dependencies\ (including uv-cache) on this machine.
REM Runs harrix-swiss-knife.ps1 elevated and captures output to install-all-offline.log.

cd /d "%~dp0"
echo Starting elevated offline deploy (UAC prompt may appear)...

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$runner = (Resolve-Path -LiteralPath (Join-Path (Get-Location) 'install-all-offline-with-log.ps1')).Path; & $runner; exit $LASTEXITCODE"

set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% neq 0 (
  echo Launcher finished with error code %EXITCODE%.
  echo See install-all-offline.log for details.
  echo.
  pause
) else (
  echo Install finished successfully.
  echo Log opened in Notepad. This window will close automatically.
  timeout /t 3 /nobreak > nul
)

