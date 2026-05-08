@echo off
set PY=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe
set SRC=D:\cheonmyeongdang\departments\media\src
set LOG=D:\cheonmyeongdang\departments\media\logs\seasonal_task.log
cd /d "%SRC%"
"%PY%" -X utf8 seasonal_poster.py jongsose >> "%LOG%" 2>&1
