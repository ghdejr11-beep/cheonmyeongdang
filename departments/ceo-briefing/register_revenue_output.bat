@echo off
REM 수익 집계 일일 실행 (ceo-briefing 스케줄과 별도 돌리고 싶을 때)
REM Windows Task Scheduler 등록:
REM   schtasks /create /tn "Revenue_Output" /tr "C:\Users\hdh02\Desktop\cheonmyeongdang\departments\ceo-briefing\register_revenue_output.bat" /sc daily /st 08:30 /f

set PY=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe
set SCRIPT=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\ceo-briefing\revenue_output.py
"%PY%" "%SCRIPT%"
