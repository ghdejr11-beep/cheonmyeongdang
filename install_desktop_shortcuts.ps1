# 바탕화면 바로가기 생성 스크립트
# install_desktop_shortcuts.bat 가 호출함.
# 별도 .ps1 로 분리한 이유: cmd.exe 에서 powershell -Command 로 한국어
# 인라인 인자를 넘기면 인코딩이 깨져서 조용히 실패하는 경우가 있다.
# .ps1 파일을 직접 -File 로 실행하면 PowerShell 이 BOM/UTF-8 을
# 정확히 읽어서 한국어가 안 깨진다.

$ErrorActionPreference = "Stop"

$repo = $PSScriptRoot
if (-not $repo) {
    $repo = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$desktop = [Environment]::GetFolderPath("Desktop")

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " 바탕화면 바로가기 생성"                                       -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " 저장소: $repo"
Write-Host " 바탕화면: $desktop"
Write-Host ""

$ws = New-Object -ComObject WScript.Shell

function New-Shortcut {
    param(
        [string]$LinkName,
        [string]$TargetBat,
        [string]$IconRef,
        [string]$Description
    )
    $linkPath = Join-Path $desktop "$LinkName.lnk"
    $targetPath = Join-Path $repo $TargetBat

    if (-not (Test-Path $targetPath)) {
        Write-Host "  [SKIP] $TargetBat 파일이 없음 → 바로가기 생성 안 함" -ForegroundColor Yellow
        return
    }

    $sc = $ws.CreateShortcut($linkPath)
    $sc.TargetPath = $targetPath
    $sc.WorkingDirectory = $repo
    $sc.IconLocation = $IconRef
    $sc.Description = $Description
    $sc.Save()
    Write-Host "  [OK] $LinkName.lnk" -ForegroundColor Green
}

New-Shortcut -LinkName "12시간 믹스 자동 업로드" `
             -TargetBat "auto_watcher.bat" `
             -IconRef "shell32.dll,137" `
             -Description "12시간 루프 BGM YouTube 자동 업로드"

New-Shortcut -LinkName "가사 노래 자동 업로드" `
             -TargetBat "lyrics_watcher.bat" `
             -IconRef "shell32.dll,130" `
             -Description "가사 있는 짧은 노래 YouTube 자동 업로드"

Write-Host ""
Write-Host "생성된 바로가기:" -ForegroundColor Cyan
Get-ChildItem $desktop -Filter "*업로드*.lnk" | Select-Object Name | Format-Table -AutoSize

Write-Host ""
Write-Host "완료. 바탕화면을 확인하세요." -ForegroundColor Green
