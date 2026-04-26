@echo off
REM Windows 작업 스케줄러 — 매일 08:30 통합 매출 수집
REM 브리핑(09:00) 직전에 모든 채널 콜렉트 → unified_revenue_daily.json 갱신

schtasks /Create /SC DAILY /TN "KunStudio_RevenueDaily" ^
  /TR "python C:\Users\hdh02\Desktop\cheonmyeongdang\departments\sales-collection\unified_revenue.py --collect" ^
  /ST 08:30 /F

echo.
echo [등록 완료] KunStudio_RevenueDaily — 매일 08:30
echo 즉시 실행 테스트: schtasks /Run /TN "KunStudio_RevenueDaily"
echo 삭제: schtasks /Delete /TN "KunStudio_RevenueDaily" /F
pause
