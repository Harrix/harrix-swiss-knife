@echo off
REM Run install zip pipeline steps 01 through 05 in order.
REM Optional log cleanup: 06_clean-logs.bat (not included here).
REM Steps 01-02 elevate via UAC; 03-05 run in this window.

cd /d "%~dp0"

set EXITCODE=0

echo === Step 1/5: binaries ===
call "%~dp001_download-bundle-force-binaries.bat"
if errorlevel 1 (
  set EXITCODE=%ERRORLEVEL%
  goto :done
)

echo === Step 2/5: installers ===
call "%~dp002_download-bundle-force-installers.bat"
if errorlevel 1 (
  set EXITCODE=%ERRORLEVEL%
  goto :done
)

echo === Step 3/5: repo snapshots ===
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download-repos.ps1"
if errorlevel 1 (
  set EXITCODE=%ERRORLEVEL%
  goto :done
)

echo === Step 4/5: uv cache ===
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download-uv-cache.ps1"
if errorlevel 1 (
  set EXITCODE=%ERRORLEVEL%
  goto :done
)

echo === Step 5/5: build zips ===
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build-install-zips.ps1"
if errorlevel 1 set EXITCODE=%ERRORLEVEL%

:done
echo.
if %EXITCODE% neq 0 (
  echo build-all stopped with error code %EXITCODE%.
) else (
  echo build-all finished successfully. Zips are in this folder.
  echo Optional: 06_clean-logs.bat
)

echo.
echo Press any key to close this window...
pause > nul

exit /b %EXITCODE%
