@echo off
REM Run install zip pipeline steps 01 through 05 in order.
REM Optional log cleanup: 06_clean-logs.bat (not included here).
REM Calls the underlying scripts (no per-step "close this window" pause).
REM Steps 1-2 show a UAC prompt; 3-5 run in this window.

setlocal EnableExtensions
cd /d "%~dp0"

set "EXITCODE=0"

echo.
echo === Step 1/5: media binaries (UAC) ===
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download-bundle-runas.ps1" -Kind Binaries
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
  echo Step 1 failed with exit code %EXITCODE%.
  goto :done
)

echo.
echo === Step 2/5: installers Git / uv / VS Code (UAC) ===
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download-bundle-runas.ps1" -Kind Installers
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
  echo Step 2 failed with exit code %EXITCODE%.
  goto :done
)

echo.
echo === Step 3/5: repo snapshots ===
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download-repos.ps1"
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
  echo Step 3 failed with exit code %EXITCODE%.
  goto :done
)

echo.
echo === Step 4/5: uv cache ===
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download-uv-cache.ps1"
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
  echo Step 4 failed with exit code %EXITCODE%.
  goto :done
)

echo.
echo === Step 5/5: build zip archives ===
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build-install-zips.ps1"
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
  echo Step 5 failed with exit code %EXITCODE%.
  goto :done
)

:done
echo.
if not "%EXITCODE%"=="0" (
  echo build-all stopped with error code %EXITCODE%.
) else (
  echo build-all finished successfully. Zips are in this folder.
  echo Optional: 06_clean-logs.bat
)

echo.
echo Press any key to close this window...
pause > nul

endlocal & exit /b %EXITCODE%
