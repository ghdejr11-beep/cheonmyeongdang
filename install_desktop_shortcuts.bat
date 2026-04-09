@echo off
chcp 65001 >nul
title 바탕화면 바로가기 설치
cd /d "%~dp0"

echo ============================================================
echo  자동 업로더 바탕화면 바로가기 생성
echo ============================================================
echo.
echo  바탕화면에 아래 2개 아이콘이 만들어집니다:
echo    1. 12시간 믹스 자동 업로드.lnk
echo    2. 가사 노래 자동 업로드.lnk
echo.

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $link1 = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\12시간 믹스 자동 업로드.lnk'); ^
   $link1.TargetPath = '%~dp0auto_watcher.bat'; ^
   $link1.WorkingDirectory = '%~dp0'; ^
   $link1.IconLocation = 'shell32.dll,137'; ^
   $link1.Description = '12시간 루프 BGM YouTube 자동 업로드'; ^
   $link1.Save(); ^
   $link2 = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\가사 노래 자동 업로드.lnk'); ^
   $link2.TargetPath = '%~dp0lyrics_watcher.bat'; ^
   $link2.WorkingDirectory = '%~dp0'; ^
   $link2.IconLocation = 'shell32.dll,130'; ^
   $link2.Description = '가사 있는 짧은 노래 YouTube 자동 업로드'; ^
   $link2.Save(); ^
   Write-Host '✓ 바탕화면에 바로가기 2개 생성 완료' -ForegroundColor Green"

echo.
echo 완료. 아무 키나 누르면 창 닫힘.
pause >nul
