@echo off
REM Pack api-keys secrets and fitness_img into install\private-data-harrix-swiss-knife.zip

cd /d "%~dp0"

echo Packing private data...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0pack-private-data.ps1" %*
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% neq 0 (
  echo pack-private-data finished with error code %EXITCODE%.
) else (
  echo pack-private-data finished successfully.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
