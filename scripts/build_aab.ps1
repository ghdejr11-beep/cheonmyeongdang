# ====================================================================
# Cheonmyeongdang Capacitor AAB Build (PowerShell)
# Result: android\app\build\outputs\bundle\release\app-release.aab
# User action: Upload to Play Console (https://play.google.com/console)
# ====================================================================
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "[1/4] Capacitor sync..." -ForegroundColor Cyan
Push-Location $Root
try {
    & npx cap sync android
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "cap sync failed - continuing with existing www"
    }
} catch {
    Write-Warning "cap sync exception: $_"
}
Pop-Location

Write-Host "[2/4] Gradle bundleRelease..." -ForegroundColor Cyan
Push-Location (Join-Path $Root 'android')
try {
    & .\gradlew.bat bundleRelease --no-daemon
    if ($LASTEXITCODE -ne 0) { throw "gradle bundleRelease failed (exit $LASTEXITCODE)" }
} finally {
    Pop-Location
}

Write-Host "[3/4] Verify AAB..." -ForegroundColor Cyan
$Aab = Join-Path $Root 'android\app\build\outputs\bundle\release\app-release.aab'
if (-not (Test-Path $Aab)) {
    Write-Error "AAB not produced at $Aab"
    exit 1
}
$Size = (Get-Item $Aab).Length
$SizeMb = [math]::Round($Size / 1MB, 2)
Write-Host "[OK] AAB built: $Aab" -ForegroundColor Green
Write-Host "[OK] Size: $Size bytes ($SizeMb MB)" -ForegroundColor Green

Write-Host "`n[4/4] Next steps:" -ForegroundColor Yellow
Write-Host "    1. Open https://play.google.com/console"
Write-Host "    2. Cheonmyeongdang app -> Production -> Create new release"
Write-Host "    3. Upload: $Aab"
Write-Host "    4. Release notes: v1.3.1 - Saju + Compatibility 강화"
