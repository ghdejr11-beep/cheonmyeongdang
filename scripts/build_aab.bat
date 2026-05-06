@echo off
REM ====================================================================
REM 천명당 Capacitor AAB 빌드 자동
REM 결과: android\app\build\outputs\bundle\release\app-release.aab
REM 사용자 액션: Play Console 업로드 1클릭 (https://play.google.com/console)
REM ====================================================================
setlocal
set ROOT=%~dp0..
echo [1/4] Capacitor sync...
pushd "%ROOT%"
call npx cap sync android
if errorlevel 1 (
  echo [WARN] cap sync failed - continuing with existing www
)

echo [2/4] Gradle bundleRelease...
pushd "%ROOT%\android"
call gradlew.bat bundleRelease --no-daemon
set BUILD_RC=%ERRORLEVEL%
popd
popd

if not "%BUILD_RC%"=="0" (
  echo [ERROR] gradle bundleRelease exit %BUILD_RC%
  exit /b %BUILD_RC%
)

echo [3/4] Verify AAB...
set AAB=%ROOT%\android\app\build\outputs\bundle\release\app-release.aab
if not exist "%AAB%" (
  echo [ERROR] AAB not produced at %AAB%
  exit /b 1
)

for %%I in ("%AAB%") do set AAB_SIZE=%%~zI
echo [OK] AAB built: %AAB%
echo [OK] Size: %AAB_SIZE% bytes

echo [4/4] Next steps:
echo     1. Open https://play.google.com/console
echo     2. Cheonmyeongdang app → Production → Create new release
echo     3. Upload: %AAB%
echo     4. Release notes: v1.3.1 — Saju + Compatibility 강화

endlocal
exit /b 0
