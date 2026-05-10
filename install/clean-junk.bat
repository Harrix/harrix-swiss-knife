@echo off
REM Remove common junk/cache folders and Python bytecode under repo root (skips .git).

cd /d "%~dp0"

echo Cleaning junk under repository...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0clean-junk.ps1"
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% neq 0 (
  echo clean-junk finished with error code %EXITCODE%.
) else (
  echo clean-junk finished successfully.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
