@echo off
REM 3개 신규 YouTube 채널 자동 발행 — Windows Task Scheduler 등록.
REM 관리자 권한 필요 (우클릭 → "관리자 권한으로 실행").
REM
REM 등록 후 schtasks /Query /TN KunStudio_WhisperAtlas /V 로 확인.
REM 삭제: schtasks /Delete /TN KunStudio_WhisperAtlas /F

setlocal
set PY=python
set SRC=C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\src

echo === Whisper Atlas (매일 02:00) ===
schtasks /Create /TN "KunStudio_WhisperAtlas" /SC DAILY /ST 02:00 ^
  /TR "cmd /c cd /d %SRC% && %PY% whisper_atlas_pipeline.py >> ..\logs\whisper_atlas.log 2>&1" ^
  /RL HIGHEST /F

echo === Wealth Blueprint (매일 04:00) ===
schtasks /Create /TN "KunStudio_WealthBlueprint" /SC DAILY /ST 04:00 ^
  /TR "cmd /c cd /d %SRC% && %PY% wealth_blueprint_pipeline.py >> ..\logs\wealth_blueprint.log 2>&1" ^
  /RL HIGHEST /F

echo === Inner Archetypes (화/금 06:00) ===
schtasks /Create /TN "KunStudio_InnerArchetypes" /SC WEEKLY /D TUE,FRI /ST 06:00 ^
  /TR "cmd /c cd /d %SRC% && %PY% inner_archetypes_pipeline.py >> ..\logs\inner_archetypes.log 2>&1" ^
  /RL HIGHEST /F

echo.
echo === Done. 확인:
schtasks /Query /TN KunStudio_WhisperAtlas | findstr /C:"KunStudio_WhisperAtlas"
schtasks /Query /TN KunStudio_WealthBlueprint | findstr /C:"KunStudio_WealthBlueprint"
schtasks /Query /TN KunStudio_InnerArchetypes | findstr /C:"KunStudio_InnerArchetypes"

endlocal
pause
