@echo off
chcp 65001 >nul
REM 매주 월요일 08:00 실행
set PYEXE=python
set BASE=D:\cheonmyeongdang\departments\media\src
set PYTHONIOENCODING=utf-8
cd /d "%BASE%"
"%PYEXE%" refresh_meta_tokens.py
