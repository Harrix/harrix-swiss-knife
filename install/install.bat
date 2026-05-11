@echo off
REM Install harrix-swiss-knife (online).

cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-with-log.ps1"

set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% neq 0 (
  echo install finished with error code %EXITCODE%.
  echo See install.log for details. If you saw a separate elevated window, fix prerequisites
  echo ^(often install App Installer / winget from Microsoft Store^) and re-run install.bat.
) else (
  echo Install finished successfully.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
