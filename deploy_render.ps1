# Render 자동 배포 스크립트
# 실행: powershell -File deploy_render.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "=== Render 자동 배포 ===" -ForegroundColor Cyan
Write-Host ""

# .secrets 에서 Anthropic 키 읽기
$ak = ""
if (Test-Path .secrets) {
    $match = Get-Content .secrets | Select-String "ANTHROPIC_API_KEY="
    if ($match) { $ak = $match.ToString().Split("=",2)[1].Trim() }
}
if (-not $ak) {
    $ak = Read-Host "ANTHROPIC_API_KEY 입력"
}

# Render API 키 입력
$rk = Read-Host "Render API 키 붙여넣기"

Write-Host ""
Write-Host "서비스 생성 중..." -ForegroundColor Cyan

$body = @{
    type = "web_service"
    name = "saju-ai-saas"
    repo = "https://github.com/ghdejr11-beep/cheonmyeongdang"
    autoDeploy = "yes"
    branch = "claude/fix-powershell-rex-prefix-cXlUP"
    rootDir = "ebook_system/projects/saju_ai_saas"
    buildCommand = "pip install -r requirements.txt"
    startCommand = "uvicorn server:app --host 0.0.0.0 --port `$PORT"
    envVars = @(
        @{ key = "ANTHROPIC_API_KEY"; value = $ak }
        @{ key = "SESSION_SECRET"; value = "deokgune-saju-2026" }
        @{ key = "PYTHON_VERSION"; value = "3.11.0" }
    )
    plan = "free"
    runtime = "python"
    region = "oregon"
} | ConvertTo-Json -Depth 5

$headers = @{
    "Authorization" = "Bearer $rk"
    "Content-Type" = "application/json"
}

try {
    $r = Invoke-RestMethod -Uri "https://api.render.com/v1/services" -Method Post -Headers $headers -Body $body
    $sid = $r.service.id
    $url = $r.service.serviceDetails.url
    Write-Host ""
    Write-Host "==============================" -ForegroundColor Green
    Write-Host "  배포 성공!" -ForegroundColor Green
    Write-Host "==============================" -ForegroundColor Green
    Write-Host "  ID:  $sid"
    Write-Host "  URL: https://$url"
    Write-Host ""
    Write-Host "  빌드 2-3분 후 확인:" -ForegroundColor Yellow
    Write-Host "  https://$url/health"
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "실패: $($_.Exception.Message)" -ForegroundColor Red
    try {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        Write-Host $reader.ReadToEnd() -ForegroundColor Red
    } catch {}
}

Write-Host ""
Read-Host "엔터 누르면 종료"
