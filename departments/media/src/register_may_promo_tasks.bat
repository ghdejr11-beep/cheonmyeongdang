@echo off
REM ============================================================
REM KunStudio 5월 마케팅 자동 발송 — Windows Task Scheduler 등록
REM 매일 09:00 (slot 0) + 19:00 (slot 1) 발송, 5/1 시작 ~ 5/31 종료
REM 사이트 회전: 천명당 / 세금N혜택 / KORLENS (라운드로빈)
REM 7채널: Bluesky/Discord/Mastodon/X/Threads/Instagram/Telegram
REM
REM 관리자 권한으로 실행 권장 (/RL HIGHEST 사용).
REM 등록 후 확인:  schtasks /Query /TN KunStudio_MayPromo_AM
REM 삭제:         schtasks /Delete /TN KunStudio_MayPromo_AM /F
REM ============================================================

setlocal
set PY=python
set SRC=D:\cheonmyeongdang\departments\media\src
set LOG=D:\cheonmyeongdang\departments\media\logs\may_promo_task.log

echo ===== 기존 태스크 정리 (있으면 삭제) =====
schtasks /Delete /TN "KunStudio_MayPromo_AM" /F 1>nul 2>nul
schtasks /Delete /TN "KunStudio_MayPromo_PM" /F 1>nul 2>nul
schtasks /Delete /TN "KunStudio_TaxPromoDaily" /F 1>nul 2>nul

echo.
echo ===== 1) 매일 09:00 (slot 0) 등록 =====
schtasks /Create /TN "KunStudio_MayPromo_AM" /SC DAILY /ST 09:00 /SD 2026/05/01 /ED 2026/05/31 ^
  /TR "cmd /c cd /d %SRC% && %PY% may_promo_runner.py --slot 0 >> \"%LOG%\" 2>&1" ^
  /RL HIGHEST /F

echo.
echo ===== 2) 매일 19:00 (slot 1) 등록 =====
schtasks /Create /TN "KunStudio_MayPromo_PM" /SC DAILY /ST 19:00 /SD 2026/05/01 /ED 2026/05/31 ^
  /TR "cmd /c cd /d %SRC% && %PY% may_promo_runner.py --slot 1 >> \"%LOG%\" 2>&1" ^
  /RL HIGHEST /F

echo.
echo ===== 3) 세금N혜택 18:00 콘텐츠 발행 (기존 유지) =====
schtasks /Create /TN "KunStudio_TaxPromoDaily" /SC DAILY /ST 18:00 /SD 2026/05/01 /ED 2026/05/31 ^
  /TR "cmd /c cd /d %SRC% && %PY% tax_promo_pipeline.py post-today >> ..\logs\tax_promo_task.log 2>&1" ^
  /RL HIGHEST /F

echo.
echo ===== 등록 완료. 확인: =====
schtasks /Query /TN "KunStudio_MayPromo_AM"   2>nul
schtasks /Query /TN "KunStudio_MayPromo_PM"   2>nul
schtasks /Query /TN "KunStudio_TaxPromoDaily" 2>nul

endlocal
