@echo off
chcp 65001 >nul
title [Auto Watcher] 8시간 루프 자동 업로드
cd /d "%~dp0"

echo ============================================================
echo  8시간 루프 믹스 자동 업로드
echo  [12시간은 YouTube 삭제 위험이라 8시간으로 낮춤]
echo ============================================================
echo.
echo  감시 폴더: %USERPROFILE%\Desktop\music_drop
echo  로그 파일: %USERPROFILE%\Desktop\playlist_output\auto_log.txt
echo.
echo  종료: Ctrl+C 또는 창 닫기
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 이 설치되지 않았거나 PATH 에 없습니다.
    echo         https://www.python.org/downloads/ 에서 설치 후 재시도
    pause
    exit /b 1
)

python auto_watcher.py

echo.
echo ============================================================
echo  프로그램 종료됨 (에러로 멈췄을 수 있음)
echo ============================================================
pause
