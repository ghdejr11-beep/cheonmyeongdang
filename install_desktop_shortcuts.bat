@echo off
chcp 65001 >nul
title 바탕화면 바로가기 설치
cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_desktop_shortcuts.ps1"

echo.
pause
