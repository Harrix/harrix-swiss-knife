@echo off
REM Install harrix-swiss-knife (online or offline; mode Auto unless overridden).
REM Examples:
REM   install.bat
REM   install.bat -Mode Offline
REM   install.bat -Mode Online
REM   install.bat -SkipPrerequisites
REM The first window asks [A] all missing / [C] choose / [S] skip.
REM UAC appears at most once, and only if Git or VS Code will actually be installed.

cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-with-log.ps1" %*

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
