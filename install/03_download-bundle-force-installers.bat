@echo off
REM Run download-bundle.ps1 elevated with -Force (installers only).

cd /d "%~dp0"

set "LOGFILE=%~dp0dependencies\download-bundle-installers.log"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download-bundle-runas.ps1" -Kind Installers

set EXITCODE=%ERRORLEVEL%
echo.
echo Elevated process exit code: %EXITCODE%
echo Full log: "%LOGFILE%"
if exist "%LOGFILE%" (
  if %EXITCODE% neq 0 (
    echo.
    echo Last lines from log:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-Content -LiteralPath '%LOGFILE%' -Tail 40 | ForEach-Object { Write-Host $_ }"
  )
) else (
  echo WARNING: Log file was not created - check UAC prompt was accepted.
)

echo.
if %EXITCODE% neq 0 (
  echo Bundle download (installers only) finished with error code %EXITCODE%.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
