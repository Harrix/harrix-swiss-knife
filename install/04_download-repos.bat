@echo off
REM Snapshot working trees of sibling repos (git archive HEAD).

cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download-repos.ps1"

set EXITCODE=%ERRORLEVEL%
echo.
if %EXITCODE% neq 0 (
  echo download-repos finished with error code %EXITCODE%.
) else (
  echo download-repos finished successfully.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
