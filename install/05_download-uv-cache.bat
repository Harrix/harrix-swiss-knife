@echo off
REM Populate only install\dependencies\uv-cache\ using uv sync.
REM Useful when uv cache needs frequent refreshes.

cd /d "%~dp0"

set LOGFILE=%~dp0download-uv-cache.log
echo Writing log to "%LOGFILE%"
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$script = (Resolve-Path -LiteralPath (Join-Path (Get-Location) 'download-bundle.ps1')).Path; & $script -OnlyUvCache 2>&1 | Tee-Object -FilePath '%LOGFILE%' -Append | Out-Host; exit $LASTEXITCODE"

set EXITCODE=%ERRORLEVEL%
echo.
if %EXITCODE% neq 0 (
  echo download-uv-cache finished with error code %EXITCODE%.
  echo Log saved to "%LOGFILE%".
) else (
  echo download-uv-cache finished successfully.
  echo Log saved to "%LOGFILE%".
)

echo.
echo Press any key to close this window...
pause > nul
