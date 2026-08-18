@echo off
REM Build online/offline distributable zip archives.

cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build-install-zips.ps1"

set EXITCODE=%ERRORLEVEL%
echo.
if %EXITCODE% neq 0 (
  echo build-install-zips finished with error code %EXITCODE%.
) else (
  echo build-install-zips finished successfully.
)
echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%

