@echo off
REM Runs harrix-swiss-knife.ps1 in elevated PowerShell (UAC prompt).
REM Captures full output to install.log and opens it in Notepad afterwards.

cd /d "%~dp0"
echo Starting elevated deploy (UAC prompt may appear)...

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$runner = (Resolve-Path -LiteralPath (Join-Path (Get-Location) 'install-with-log.ps1')).Path; & $runner; exit $LASTEXITCODE"

set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% neq 0 (
  echo Launcher finished with error code %EXITCODE%.
  echo See install.log for details. If you saw a separate elevated window, fix prerequisites
  echo ^(often install App Installer / winget from Microsoft Store^) and re-run install.bat.
  echo.
  pause
) else (
  echo Install finished successfully.
  echo Log opened in Notepad. This window will close automatically.
  timeout /t 3 /nobreak > nul
)
