@echo off
REM Runs harrix-swiss-knife.ps1 in elevated PowerShell (UAC prompt).
REM Captures full output to install.log and opens it in Notepad afterwards.

cd /d "%~dp0"
echo Starting elevated deploy (UAC prompt may appear)...

set "LOGFILE=%~dp0install.log"
REM Reset log between runs so user always sees the latest run.
> "%LOGFILE%" echo === Harrix Swiss Knife install log ===
>> "%LOGFILE%" echo Started: %DATE% %TIME%
>> "%LOGFILE%" echo Working directory: %~dp0
>> "%LOGFILE%" echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$script = (Resolve-Path -LiteralPath (Join-Path (Get-Location) 'harrix-swiss-knife.ps1')).Path; if (-not (Test-Path -LiteralPath $script)) { Write-Error ('Not found: ' + $script); exit 1 }; $log = (Join-Path (Get-Location) 'install.log'); $cmd = ('& ' + [char]34 + $script + [char]34 + ' *>> ' + [char]34 + $log + [char]34); $p = Start-Process -FilePath powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-Command',$cmd; exit $(if ($null -ne $p.ExitCode) { $p.ExitCode } else { 1 })"

set EXITCODE=%ERRORLEVEL%
>> "%LOGFILE%" echo.
>> "%LOGFILE%" echo Finished: %DATE% %TIME%
>> "%LOGFILE%" echo Exit code: %EXITCODE%

echo.
echo Install log: %LOGFILE%
if %EXITCODE% neq 0 (
  echo Launcher finished with error code %EXITCODE%.
  echo See the log for details. If you saw a separate elevated window, fix prerequisites
  echo ^(often install App Installer / winget from Microsoft Store^) and re-run install.bat.
) else (
  echo Install finished successfully.
)
echo Opening the log in Notepad...
if exist "%LOGFILE%" start "" notepad "%LOGFILE%"
echo.
pause
