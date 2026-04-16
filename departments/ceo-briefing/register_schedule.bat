@echo off
REM CEO 브리핑 자동 스케줄 등록
REM 9AM, 12PM, 3PM, 6PM, 9PM, 12AM 총 6회

set SCRIPT_PATH=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\ceo-briefing\briefing.py
set PYTHON_PATH=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe

echo 기존 스케줄 삭제 중...
schtasks /delete /tn "CEO_Briefing_09" /f 2>nul
schtasks /delete /tn "CEO_Briefing_12" /f 2>nul
schtasks /delete /tn "CEO_Briefing_15" /f 2>nul
schtasks /delete /tn "CEO_Briefing_18" /f 2>nul
schtasks /delete /tn "CEO_Briefing_21" /f 2>nul
schtasks /delete /tn "CEO_Briefing_00" /f 2>nul

echo 새 스케줄 등록 중...
schtasks /create /tn "CEO_Briefing_09" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 9" /sc daily /st 09:00 /f
schtasks /create /tn "CEO_Briefing_12" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 12" /sc daily /st 12:00 /f
schtasks /create /tn "CEO_Briefing_15" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 15" /sc daily /st 15:00 /f
schtasks /create /tn "CEO_Briefing_18" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 18" /sc daily /st 18:00 /f
schtasks /create /tn "CEO_Briefing_21" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 21" /sc daily /st 21:00 /f
schtasks /create /tn "CEO_Briefing_00" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 0" /sc daily /st 00:00 /f

echo.
echo ✅ 6개 스케줄 등록 완료!
echo 9시, 12시, 15시, 18시, 21시, 24시 자동 전송
pause
