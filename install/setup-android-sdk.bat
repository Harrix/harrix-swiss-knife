@echo off
REM Optional: install JDK 17 + Android SDK for the android\ module (not part of zip pipeline 01-06).

cd /d "%~dp0"

echo Setting up Android SDK / JDK for HSK Android...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-android-sdk.ps1"
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% neq 0 (
  echo setup-android-sdk finished with error code %EXITCODE%.
) else (
  echo setup-android-sdk finished successfully.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
