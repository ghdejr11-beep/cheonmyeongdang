@echo off
chcp 65001 >nul
REM KunStudio 일일 자동 홍보
REM Usage:
REM   daily_promo.bat service  -> 요일별 서비스 홍보 (auto_promo.daily_promo)
REM   daily_promo.bat kdp      -> KDP 책 3권 순환 홍보

set PYEXE=python
set BASE=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\src
set PYTHONIOENCODING=utf-8

cd /d "%BASE%"

IF "%1"=="service" (
    "%PYEXE%" -c "from auto_promo import daily_promo; daily_promo()"
    exit /b
)

IF "%1"=="kdp" (
    "%PYEXE%" kdp_boost.py --limit 3
    exit /b
)

echo Usage: %0 [service^|kdp]
