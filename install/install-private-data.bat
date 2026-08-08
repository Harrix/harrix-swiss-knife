@echo off
REM Install api-keys secrets and fitness_img from install\private-data-harrix-swiss-knife.zip

cd /d "%~dp0"

echo Installing private data...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-private-data.ps1" %*
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% neq 0 (
  echo install-private-data finished with error code %EXITCODE%.
) else (
  echo install-private-data finished successfully.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
