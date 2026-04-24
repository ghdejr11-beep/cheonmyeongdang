@echo off
REM Weekly refresh: topic refresh + YouTube analytics feedback
REM Task Scheduler: Sunday 23:00

cd /d "%~dp0"
python topic_refresh.py >> logs_weekly.log 2>&1
echo. >> logs_weekly.log
python feedback_loop.py >> logs_weekly.log 2>&1
