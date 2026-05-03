@echo off
REM Seasonal SNS poster - register 3 daily tasks
REM 1) 09:05 jongsose (May 1 - May 31)
REM 2) 18:05 eobonal  (May 1 - May 8, auto-inactive after)
REM 3) 21:05 kdp_family (May 1 - May 31)

setlocal
set PY=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe
set SRC=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\src
set LOG=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\logs\seasonal_task.log

echo === Cleanup existing tasks ===
schtasks /Delete /TN "KunStudio_Seasonal_Jongsose" /F 1>nul 2>nul
schtasks /Delete /TN "KunStudio_Seasonal_Eobonal"  /F 1>nul 2>nul
schtasks /Delete /TN "KunStudio_Seasonal_KDP"      /F 1>nul 2>nul

echo.
echo === 1) Jongsose 09:05 daily ===
schtasks /Create /TN "KunStudio_Seasonal_Jongsose" /SC DAILY /ST 09:05 /SD 2026/05/02 /ED 2026/05/31 /TR "%SRC%\run_seasonal_jongsose.bat" /F

echo.
echo === 2) Eobonal 18:05 daily (auto-inactive after 5/8) ===
schtasks /Create /TN "KunStudio_Seasonal_Eobonal" /SC DAILY /ST 18:05 /SD 2026/05/02 /ED 2026/05/31 /TR "%SRC%\run_seasonal_eobonal.bat" /F

echo.
echo === 3) KDP family 21:05 daily ===
schtasks /Create /TN "KunStudio_Seasonal_KDP" /SC DAILY /ST 21:05 /SD 2026/05/02 /ED 2026/05/31 /TR "%SRC%\run_seasonal_kdp.bat" /F

echo.
echo === Done. Verify: ===
schtasks /Query /TN "KunStudio_Seasonal_Jongsose" 2>nul
schtasks /Query /TN "KunStudio_Seasonal_Eobonal"  2>nul
schtasks /Query /TN "KunStudio_Seasonal_KDP"      2>nul

endlocal
