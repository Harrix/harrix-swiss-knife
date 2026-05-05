@echo off
REM Convenience entrypoint for Windows users.
REM Delegates to install\install.bat (which runs the PowerShell deploy elevated).

cd /d "%~dp0"
call ".\install\install.bat"
