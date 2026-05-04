@echo off
REM Convenience entrypoint for Windows users.
REM Delegates to scripts\install.bat (which runs the PowerShell deploy elevated).

cd /d "%~dp0"
call ".\scripts\install.bat"
