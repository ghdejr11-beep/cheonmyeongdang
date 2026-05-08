@echo off
REM KunStudio Grant Result Monitor - daily 11:00
cd /d "D:\cheonmyeongdang\departments\tax"
python grant_result_monitor.py >> logs\grant_monitor_stdout.log 2>&1
