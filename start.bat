@echo off
cd /d "%~dp0"
title SceneTalk - Starting...

powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"

echo.
echo Script finished. You can close this window now.
echo.
pause
