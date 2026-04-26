@echo off
REM tax 부서 - 지원사업 공고 모니터링 일일 실행
REM Windows Task Scheduler 등록:
REM   schtasks /create /tn "Tax_LeadWatcher" /tr "C:\Users\hdh02\Desktop\cheonmyeongdang\departments\tax\run_daily.bat" /sc daily /st 09:00 /f

set PY=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe
set SCRIPT=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\tax\lead_watcher.py
"%PY%" "%SCRIPT%"
