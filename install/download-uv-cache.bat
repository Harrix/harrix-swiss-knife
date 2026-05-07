@echo off
REM Populate only install\dependencies\uv-cache\ using uv sync.
REM Useful when uv cache needs frequent refreshes.

cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$script = (Resolve-Path -LiteralPath (Join-Path (Get-Location) 'download-bundle.ps1')).Path; & $script -OnlyUvCache; exit $LASTEXITCODE"

set EXITCODE=%ERRORLEVEL%
echo.
if %EXITCODE% neq 0 (
  echo download-uv-cache finished with error code %EXITCODE%.
  pause
)
