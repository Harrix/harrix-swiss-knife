@echo off
REM Run download-bundle.ps1 elevated with -Force.

cd /d "%~dp0"
echo Starting elevated bundle download (UAC prompt may appear)...

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$script = (Resolve-Path -LiteralPath (Join-Path (Get-Location) 'download-bundle.ps1')).Path; if (-not (Test-Path -LiteralPath $script)) { Write-Error ('Not found: ' + $script); exit 1 }; $deps = (Join-Path (Get-Location) 'dependencies'); if (-not (Test-Path -LiteralPath $deps)) { New-Item -ItemType Directory -Path $deps -Force | Out-Null }; $log = (Join-Path (Resolve-Path -LiteralPath $deps).Path 'download-bundle.log'); $cmd = ('& ' + [char]34 + $script + [char]34 + ' -Force *>> ' + [char]34 + $log + [char]34); $p = Start-Process -FilePath powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-Command',$cmd; exit $(if ($null -ne $p.ExitCode) { $p.ExitCode } else { 1 })"

set EXITCODE=%ERRORLEVEL%
echo.
if %EXITCODE% neq 0 (
  echo Bundle download finished with error code %EXITCODE%.
)
pause
