@echo off
setlocal enabledelayedexpansion
set PY=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe

REM Use Python script wrapper - but schtasks /TR requires full path with single quoting
REM Test: schtasks /Change with single line backslash escaping

schtasks /Change /TN "KunStudio_Sales" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\intelligence\sales_collector.py\"" > %TEMP%\fix_sales.log 2>&1
type %TEMP%\fix_sales.log

echo ---After change---
schtasks /Query /TN "KunStudio_Sales" /XML > %TEMP%\sales_xml.log
findstr /C:"<Command>" /C:"<Arguments>" %TEMP%\sales_xml.log
