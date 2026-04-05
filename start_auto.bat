@echo off
chcp 65001 >nul
title Playlist Auto Maker
echo.
echo ==========================================
echo   Playlist Auto Maker 실행 중...
echo   music_drop 폴더에 MP3를 넣으세요!
echo   종료: 이 창을 닫으세요
echo ==========================================
echo.
cd /d "%USERPROFILE%\Desktop"
python auto_watcher.py
pause
