@echo off
REM Remove *.log files from install\ and install\dependencies\ only.

cd /d "%~dp0"

echo Cleaning log files...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0clean-logs.ps1"
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% neq 0 (
  echo clean-logs finished with error code %EXITCODE%.
) else (
  echo clean-logs finished successfully.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
