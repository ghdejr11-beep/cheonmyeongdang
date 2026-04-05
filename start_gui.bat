@echo off
chcp 65001 >nul
title Playlist Maker GUI
echo.
echo ==========================================
echo   Playlist Maker GUI 실행 중...
echo   브라우저가 자동으로 열립니다.
echo   종료: 이 창을 닫으세요
echo ==========================================
echo.
cd /d "%USERPROFILE%\Desktop"
python playlist_maker.py
pause
