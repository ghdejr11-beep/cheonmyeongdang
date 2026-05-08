@echo off
REM Inner Archetypes Shorts v2 — Windows Task Scheduler 등록.
REM 매일 6편 (오전 3편 + 오후 3편) 자동 발행.
REM 관리자 권한으로 실행하지 않아도 됨 (사용자 본인 계정).
REM
REM 등록 후 schtasks /Query /TN KunStudio_InnerArchetypes_Shorts_AM /V 로 확인.
REM 삭제: schtasks /Delete /TN KunStudio_InnerArchetypes_Shorts_AM /F

setlocal
set PY=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe
set SRC=D:\cheonmyeongdang\departments\media\src

echo === Inner Archetypes Shorts AM (매일 08:30, 3편) ===
schtasks /Create /TN "KunStudio_InnerArchetypes_Shorts_AM" /SC DAILY /ST 08:30 ^
  /TR "cmd /c cd /d %SRC% && %PY% inner_archetypes_shorts_v2.py --slot morning >> ..\logs\inner_archetypes_shorts.log 2>&1" ^
  /RL HIGHEST /F

echo === Inner Archetypes Shorts PM (매일 14:30, 3편) ===
schtasks /Create /TN "KunStudio_InnerArchetypes_Shorts_PM" /SC DAILY /ST 14:30 ^
  /TR "cmd /c cd /d %SRC% && %PY% inner_archetypes_shorts_v2.py --slot evening >> ..\logs\inner_archetypes_shorts.log 2>&1" ^
  /RL HIGHEST /F

echo.
echo === 확인:
schtasks /Query /TN "KunStudio_InnerArchetypes_Shorts_AM" | findstr /C:"AM"
schtasks /Query /TN "KunStudio_InnerArchetypes_Shorts_PM" | findstr /C:"PM"

endlocal
echo.
echo [Done] 매일 08:30 + 14:30 에 자동 실행됩니다.
echo logs: %SRC%\..\logs\inner_archetypes_shorts.log
