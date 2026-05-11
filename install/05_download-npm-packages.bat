@echo off
setlocal

REM Download (pack) pinned npm global packages into install\dependencies\npm-packages
REM Uses npm.cmd to avoid PowerShell ExecutionPolicy issues with npm.ps1.

set "SCRIPT_DIR=%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%download-npm-packages.ps1"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo ERROR: download-npm-packages.ps1 failed with exit code %RC%
  pause
  exit /b %RC%
)

echo.
echo OK
pause
exit /b 0

