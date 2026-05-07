@echo off
REM Convenience entrypoint for offline-first install.
REM Delegates to install\install-all-offline.bat (runs elevated and logs).

cd /d "%~dp0"
call ".\install\install-all-offline.bat"

