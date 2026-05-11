@echo off
REM Run download-bundle.ps1 elevated with -Force (media binaries only).
REM Populates install\dependencies: copies repo-root exes if present, downloads fallback zips,
REM extracts avifenc/avifdec/ffmpeg into dependencies, then removes those zips when done.

cd /d "%~dp0"

set "LOGFILE=%~dp0dependencies\download-bundle-binaries.log"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download-bundle-runas.ps1" -Kind Binaries

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
  echo Bundle download (binaries only) finished with error code %EXITCODE%.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
