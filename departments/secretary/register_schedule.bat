@echo off
REM 비서부 자동 스케줄 등록
REM 9AM, 12PM, 3PM, 6PM, 9PM, 12AM — CEO 브리핑과 동일 시간대 총 6회

set SCRIPT_PATH=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\secretary\secretary.py
set EDITOR_PATH=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\secretary\editor.py
set PYTHON_PATH=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe

echo 기존 비서부 스케줄 삭제 중...
schtasks /delete /tn "Secretary_09" /f 2>nul
schtasks /delete /tn "Secretary_12" /f 2>nul
schtasks /delete /tn "Secretary_15" /f 2>nul
schtasks /delete /tn "Secretary_18" /f 2>nul
schtasks /delete /tn "Secretary_21" /f 2>nul
schtasks /delete /tn "Secretary_00" /f 2>nul
schtasks /delete /tn "Editor_Daily" /f 2>nul

echo.
echo 새 스케줄 등록 중...

REM 비서부 - 6회 (3시간마다)
schtasks /create /tn "Secretary_09" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 3" /sc daily /st 09:00 /f
schtasks /create /tn "Secretary_12" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 3" /sc daily /st 12:00 /f
schtasks /create /tn "Secretary_15" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 3" /sc daily /st 15:00 /f
schtasks /create /tn "Secretary_18" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 3" /sc daily /st 18:00 /f
schtasks /create /tn "Secretary_21" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 3" /sc daily /st 21:00 /f
schtasks /create /tn "Secretary_00" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" 3" /sc daily /st 00:00 /f

REM 편집부 - 하루 1회 (오전 9시 직후, KDP 거절 일괄 분석)
schtasks /create /tn "Editor_Daily" /tr "\"%PYTHON_PATH%\" \"%EDITOR_PATH%\"" /sc daily /st 09:05 /f

echo.
echo ===========================================
echo [OK] 비서부 자동 스케줄 등록 완료!
echo ===========================================
echo.
echo [일정]
echo  - 비서부: 매일 9, 12, 15, 18, 21, 24시 (6회)
echo  - 편집부: 매일 9시 5분 (KDP 거절 처리)
echo.
echo 확인: schtasks /query /tn "Secretary_*" /fo LIST
echo.
pause
