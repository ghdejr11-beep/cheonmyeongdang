@echo off
chcp 65001 >nul
title [Telegram Commander] AI 팀 원격 명령
cd /d "%~dp0"

echo ============================================================
echo  AI 팀 텔레그램 원격 명령 봇
echo  [외출 중에도 텔레그램으로 AI 에게 명령 가능]
echo ============================================================
echo.
echo  텔레그램에서 사용할 수 있는 명령:
echo   /도움말  - 명령어 목록
echo   /노래 [주제]  - 가사 5곡 생성
echo   /리포트  - 분석부 즉시 실행
echo   /상태  - 시스템 상태 확인
echo   /사주 [생년월일]  - AI 사주 풀기
echo   (일반 메시지 = Claude 와 자유 대화)
echo.
echo  종료: Ctrl+C 또는 창 닫기
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 미설치
    pause
    exit /b 1
)

python telegram_commander.py

echo.
echo  프로그램 종료됨
pause
