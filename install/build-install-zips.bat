@echo off
REM Build two distributable zip archives:
REM   1) install-harrix-swiss-knife.zip (online install kit)
REM      - includes dependencies (excluding repos, uv-cache, *.log)
REM      - includes: harrix-swiss-knife.ps1, install.bat, install-with-log.ps1
REM   2) install-offline-harrix-swiss-knife.zip (offline install kit)
REM      - includes dependencies (including uv-cache and repos, excluding *.log)
REM      - includes: harrix-swiss-knife.ps1, install-all-offline.bat, install-all-offline-with-log.ps1
REM
REM Output zip files are created next to this script (install\).

cd /d "%~dp0"

set OUT_ONLINE=%~dp0install-harrix-swiss-knife.zip
set OUT_OFFLINE=%~dp0install-offline-harrix-swiss-knife.zip

echo Building:
echo   "%OUT_ONLINE%"
echo   "%OUT_OFFLINE%"
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop'; " ^
  "$root = (Resolve-Path -LiteralPath (Get-Location)).Path; " ^
  "$deps = Join-Path $root 'dependencies'; " ^
  "$outOnline = '%OUT_ONLINE%'; $outOffline = '%OUT_OFFLINE%'; " ^
  "function New-CleanDir([string]$p){ if(Test-Path -LiteralPath $p){ Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue }; New-Item -ItemType Directory -Path $p -Force | Out-Null } " ^
  "function Copy-IfExists([string]$src,[string]$dstDir){ if(Test-Path -LiteralPath $src){ Copy-Item -LiteralPath $src -Destination (Join-Path $dstDir (Split-Path -Leaf $src)) -Force } else { throw ('Not found: ' + $src) } } " ^
  "function Copy-Deps([string]$srcDeps,[string]$dstDeps,[string[]]$excludeDirs){ if(-not (Test-Path -LiteralPath $srcDeps)){ throw ('Not found: ' + $srcDeps) }; New-Item -ItemType Directory -Path $dstDeps -Force | Out-Null; Get-ChildItem -LiteralPath $srcDeps -Force | ForEach-Object { if($_.PSIsContainer){ if($excludeDirs -contains $_.Name){ return }; Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dstDeps $_.Name) -Recurse -Force } else { if($_.Name -like '*.log'){ return }; Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dstDeps $_.Name) -Force } } } " ^
  "function Zip-Dir([string]$dir,[string]$zip){ if(Test-Path -LiteralPath $zip){ Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue }; Compress-Archive -LiteralPath (Join-Path $dir '*') -DestinationPath $zip -Force } " ^
  "$stageBase = Join-Path $env:TEMP ('hsk-install-zip-' + [guid]::NewGuid().ToString('N')); " ^
  "$stageOnline = Join-Path $stageBase 'online'; $stageOffline = Join-Path $stageBase 'offline'; " ^
  "try { " ^
  "  New-CleanDir $stageOnline; New-CleanDir $stageOffline; " ^
  "  Copy-IfExists (Join-Path $root 'harrix-swiss-knife.ps1') $stageOnline; " ^
  "  Copy-IfExists (Join-Path $root 'install.bat') $stageOnline; " ^
  "  Copy-IfExists (Join-Path $root 'install-with-log.ps1') $stageOnline; " ^
  "  Copy-Deps $deps (Join-Path $stageOnline 'dependencies') @('repos','uv-cache'); " ^
  "  Zip-Dir $stageOnline $outOnline; " ^
  "  Copy-IfExists (Join-Path $root 'harrix-swiss-knife.ps1') $stageOffline; " ^
  "  Copy-IfExists (Join-Path $root 'install-all-offline.bat') $stageOffline; " ^
  "  Copy-IfExists (Join-Path $root 'install-all-offline-with-log.ps1') $stageOffline; " ^
  "  Copy-Deps $deps (Join-Path $stageOffline 'dependencies') @(); " ^
  "  Zip-Dir $stageOffline $outOffline; " ^
  "  Write-Host 'OK' -ForegroundColor Green; " ^
  "} finally { Remove-Item -LiteralPath $stageBase -Recurse -Force -ErrorAction SilentlyContinue }"

set EXITCODE=%ERRORLEVEL%
echo.
if %EXITCODE% neq 0 (
  echo Build failed with error code %EXITCODE%.
) else (
  echo Build finished successfully.
)
echo.
pause

