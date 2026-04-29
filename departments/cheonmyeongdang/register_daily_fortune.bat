@echo off
REM ==========================================================================
REM 천명당 월회원 일일 운세 자동 발송 — Windows Task Scheduler 등록
REM 매일 08:00 → daily_fortune_run.py 실행
REM ==========================================================================
setlocal

set TASKNAME=CheonmyeongdangDailyFortune
set PY=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe
set SCRIPT=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\cheonmyeongdang\daily_fortune_run.py
set RUNNER=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\cheonmyeongdang\run_daily_fortune.bat

REM 1) 실행 래퍼 bat 생성 (schtasks 인수 이스케이프 회피)
> "%RUNNER%" echo @echo off
>> "%RUNNER%" echo cd /d C:\Users\hdh02\Desktop\cheonmyeongdang\departments\cheonmyeongdang
>> "%RUNNER%" echo "%PY%" "%SCRIPT%" 1^>^> logs\daily_fortune_runner.log 2^>^&1

echo.
echo [1/2] 래퍼 bat 생성: %RUNNER%

REM 2) 기존 작업 제거 후 새로 등록 (매일 08:00)
schtasks /delete /tn "%TASKNAME%" /f >nul 2>&1
schtasks /create /tn "%TASKNAME%" /tr "\"%RUNNER%\"" /sc daily /st 08:00 /rl HIGHEST /f

if %ERRORLEVEL% EQU 0 (
    echo [2/2] schtasks 등록 완료: %TASKNAME% (매일 08:00)
    echo.
    echo 확인:    schtasks /query /tn "%TASKNAME%"
    echo 즉시실행: schtasks /run /tn "%TASKNAME%"
    echo 제거:    schtasks /delete /tn "%TASKNAME%" /f
) else (
    echo [ERR] schtasks 등록 실패. 관리자 권한으로 실행 필요할 수 있음.
)

endlocal
