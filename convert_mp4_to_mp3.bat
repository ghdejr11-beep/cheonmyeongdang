@echo off
chcp 65001 > nul
echo ================================
echo   MP4 → MP3 일괄 변환 시작
echo ================================
echo.

set INPUT_DIR=C:\Users\hdh02\Desktop\playlist_auto\input_music

if not exist "%INPUT_DIR%" (
    echo [오류] 폴더를 찾을 수 없습니다: %INPUT_DIR%
    pause
    exit /b 1
)

cd /d "%INPUT_DIR%"

set COUNT=0
for %%f in (*.mp4) do set /a COUNT+=1

if %COUNT%==0 (
    echo MP4 파일이 없습니다.
    pause
    exit /b 0
)

echo 총 %COUNT%개의 MP4 파일을 변환합니다.
echo.

set SUCCESS=0
set FAILED=0

for %%f in (*.mp4) do (
    echo 변환 중: %%f
    ffmpeg -i "%%f" -vn -acodec libmp3lame -q:a 2 "%%~nf.mp3" -y 2>nul
    if errorlevel 1 (
        echo   [실패] %%f
        set /a FAILED+=1
    ) else (
        echo   [완료] %%~nf.mp3
        set /a SUCCESS+=1
    )
)

echo.
echo ================================
echo  완료: 성공 %SUCCESS%개 / 실패 %FAILED%개
echo ================================
pause
