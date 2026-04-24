@echo off
REM Sleep Gyeongju 주 2회 자동 생성·업로드
REM Task Scheduler:
REM   schtasks /create /tn "YT_SleepGyeongju" /tr "C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\youtube\sleep_gyeongju\run_weekly.bat" /sc weekly /d MON,THU /st 03:00 /f

set PY=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe
set SCRIPT=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\youtube\sleep_gyeongju\orchestrator.py
"%PY%" "%SCRIPT%" >> "D:\cheonmyeongdang-outputs\youtube\sleep_gyeongju\output\run.log" 2>&1
