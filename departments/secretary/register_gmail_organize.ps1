# 비서부 Gmail 자동 정리 스케줄 등록 (관리자 권한 X)
# 작업명: KunStudio_GmailOrganize
# 매일 09:30 실행 -> python gmail_organizer.py --all

$TaskName  = "KunStudio_GmailOrganize"
$ScriptDir = "D:\cheonmyeongdang\departments\secretary"
$Python    = "C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe"
$LogFile   = Join-Path $ScriptDir "logs\gmail_organize.log"

# logs 폴더 보장
if (-not (Test-Path (Join-Path $ScriptDir "logs"))) {
    New-Item -ItemType Directory -Path (Join-Path $ScriptDir "logs") | Out-Null
}

# 기존 작업 있으면 제거 (재등록)
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "[INFO] 기존 작업 제거: $TaskName"
}

# Action: cmd.exe 로 wrap 해서 stdout/stderr 로그 파일 추가
$cmdLine = "/c `"`"$Python`" `"$ScriptDir\gmail_organizer.py`" --all >> `"$LogFile`" 2>&1`""
$Action  = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $cmdLine -WorkingDirectory $ScriptDir

# Trigger: 매일 09:30
$Trigger = New-ScheduledTaskTrigger -Daily -At "09:30"

# Principal: 현재 사용자, 최고 권한 X (사용자 권한)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# Settings: 누락된 시간 기동 + 배터리 무관
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask -TaskName $TaskName `
    -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings `
    -Description "비서부 Gmail 자동 정리 (분류 + 30일+광고 archive + 텔레그램 보고)"

Write-Host "[OK] 등록 완료: $TaskName (매일 09:30)"
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, NextRunTime
