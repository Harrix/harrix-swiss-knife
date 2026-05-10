@echo off
REM Run download-bundle.ps1 elevated with -Force (installers only: Git, Python, Node.js, uv, VS Code).

cd /d "%~dp0"

set "LOGFILE=%~dp0dependencies\download-bundle-installers.log"

echo Starting elevated bundle download (installers only) (UAC prompt may appear)...
echo Writing log to "%LOGFILE%"
echo If GitHub returns HTTP 403 (rate limit), set user env var GITHUB_TOKEN and retry.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$script = (Resolve-Path -LiteralPath (Join-Path (Get-Location) 'download-bundle.ps1')).Path; if (-not (Test-Path -LiteralPath $script)) { Write-Error ('Not found: ' + $script); exit 1 }; $deps = (Join-Path (Get-Location) 'dependencies'); if (-not (Test-Path -LiteralPath $deps)) { New-Item -ItemType Directory -Path $deps -Force | Out-Null }; $log = (Join-Path (Resolve-Path -LiteralPath $deps).Path 'download-bundle-installers.log'); $cmd = ('& { & ' + [char]34 + $script + [char]34 + ' -Force -SkipBinaries *>&1 ' + [char]124 + ' Tee-Object -FilePath ' + [char]34 + $log + [char]34 + ' }'); $p = Start-Process -FilePath powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-Command',$cmd; exit $(if ($null -ne $p.ExitCode) { $p.ExitCode } else { 1 })"

set EXITCODE=%ERRORLEVEL%
echo.
echo Elevated process exit code: %EXITCODE%
echo Full log: "%LOGFILE%"
if exist "%LOGFILE%" (
  if %EXITCODE% neq 0 (
    echo.
    echo Last lines from log:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-Content -LiteralPath '%LOGFILE%' -Tail 40 | ForEach-Object { Write-Host $_ }"
  )
) else (
  echo WARNING: Log file was not created - check UAC prompt was accepted.
)

echo.
if %EXITCODE% neq 0 (
  echo Bundle download (installers only) finished with error code %EXITCODE%.
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
