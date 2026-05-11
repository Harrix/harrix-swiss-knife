@echo off
REM Populate only install\dependencies\uv-cache\ using uv sync.

cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download-uv-cache.ps1"

set EXITCODE=%ERRORLEVEL%
echo.
if %EXITCODE% neq 0 (
  echo download-uv-cache finished with error code %EXITCODE%.
) else (
  echo download-uv-cache finished successfully.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
