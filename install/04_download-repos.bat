@echo off
REM Snapshot working trees of sibling repos (no .git, gitignored excluded).
REM Useful when repo snapshots need frequent refreshes for offline distribution.

cd /d "%~dp0"

set LOGFILE=%~dp0download-repos.log
echo Writing log to "%LOGFILE%"
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$script = (Resolve-Path -LiteralPath (Join-Path (Get-Location) 'download-bundle.ps1')).Path; & $script -OnlyRepos 2>&1 | Tee-Object -FilePath '%LOGFILE%' -Append | Out-Host; exit $LASTEXITCODE"

set EXITCODE=%ERRORLEVEL%
echo.
if %EXITCODE% neq 0 (
  echo download-repos finished with error code %EXITCODE%.
  echo Log saved to "%LOGFILE%".
) else (
  echo download-repos finished successfully.
  echo Log saved to "%LOGFILE%".
)

echo.
echo Press any key to close this window...
pause > nul
