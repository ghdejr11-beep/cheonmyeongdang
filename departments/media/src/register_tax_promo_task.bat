@echo off
REM 세금N혜택 5월 마케팅 자동 발행 — Windows Task Scheduler 등록.
REM 매일 18:00 실행, 5월 1일 시작 ~ 5월 31일까지.
REM 관리자 권한 필요.
REM
REM 등록 후 schtasks /Query /TN KunStudio_TaxPromoDaily /V 로 확인.
REM 삭제: schtasks /Delete /TN KunStudio_TaxPromoDaily /F

setlocal
set PY=python
set SRC=D:\cheonmyeongdang\departments\media\src

echo === KunStudio_TaxPromoDaily (매일 18:00, 5월 1일 시작) ===
schtasks /Create /TN "KunStudio_TaxPromoDaily" /SC DAILY /ST 18:00 /SD 2026/05/01 /ED 2026/05/31 ^
  /TR "cmd /c cd /d %SRC% && %PY% tax_promo_pipeline.py post-today >> ..\logs\tax_promo_task.log 2>&1" ^
  /RL HIGHEST /F

echo.
echo === Done. 확인:
schtasks /Query /TN KunStudio_TaxPromoDaily | findstr /C:"KunStudio_TaxPromoDaily"

endlocal
