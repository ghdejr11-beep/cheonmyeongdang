@echo off
chcp 65001 >nul
title [Lyrics Watcher] 가사 있는 짧은 노래 자동 업로드
cd /d "%~dp0"

echo ============================================================
echo  가사 있는 짧은 노래 자동 업로드
echo ============================================================
echo.
echo  감시 폴더: %USERPROFILE%\Desktop\lyrics_drop
echo  로그 파일: %USERPROFILE%\Desktop\playlist_output\lyrics_log.txt
echo.
echo  사용법:
echo   1. 가사 있는 MP3 를 lyrics_drop 폴더에 드롭
echo   2. (선택) 가사 .lrc 파일을 MP3 와 같은 이름으로 같이 넣기
echo   3. (선택) 배경 이미지 bg.png 또는 bg.jpg 를 폴더에 넣기
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

python lyrics_watcher.py

echo.
echo ============================================================
echo  프로그램 종료됨 (에러로 멈췄을 수 있음)
echo ============================================================
pause
