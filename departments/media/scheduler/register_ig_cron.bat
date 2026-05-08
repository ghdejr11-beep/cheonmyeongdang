@echo off
chcp 65001 >nul
REM Instagram due-post checker: runs every hour
REM Registers a Windows Task Scheduler entry

set TASKNAME=MetaIGBulkScheduler
set SCRIPT=D:\cheonmyeongdang\departments\media\scheduler\meta_bulk_scheduler.py
set PYEXE=python

schtasks /Create /TN "%TASKNAME%" /TR "\"%PYEXE%\" \"%SCRIPT%\" --ig-run-due" /SC HOURLY /MO 1 /F

echo.
echo Registered Windows Task: %TASKNAME%
echo Runs every 1 hour, publishes IG posts whose scheduled_ts <= now.
echo.
echo Check: schtasks /Query /TN "%TASKNAME%"
echo Remove: schtasks /Delete /TN "%TASKNAME%" /F
pause
