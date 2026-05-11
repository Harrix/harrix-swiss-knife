@echo off
REM Install harrix-swiss-knife (offline-first).

cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-all-offline-with-log.ps1"

set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% neq 0 (
  echo install-all-offline finished with error code %EXITCODE%.
  echo See install-all-offline.log for details.
) else (
  echo Install finished successfully.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%