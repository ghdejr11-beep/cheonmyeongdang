# PayPal Live Secret Rotate — 5분 원샷 가이드 (LOW priority)

**목적**: PayPal Live App secret 정기 rotation (분기 1회 권장 보안 baseline)
**현재 상태**: Live App 정상 작동 중. rotate는 옵션 보안 강화.

## 1클릭 직링크
- PayPal Developer Dashboard: https://developer.paypal.com/dashboard/applications/live
- 직접 본인 앱: https://developer.paypal.com/dashboard/applications/live → "Cheonmyeongdang" (또는 기존 앱명)

## 5단계 클릭 순서

### 1. Developer Dashboard 진입
- https://developer.paypal.com/dashboard/applications/live
- 본인 PayPal Business 계정 로그인 (ghdejr11@gmail.com 또는 사업자 계정)

### 2. Live App 선택
- "Apps & Credentials" → **Live** 탭 (Sandbox 아님 주의)
- 천명당/cheonmyeongdang 앱 클릭

### 3. 새 Secret 생성
- App Credentials 섹션 → **Client Secret** 우측 "Show / Hide" 옆 "Generate New Secret" 클릭
- **확인 모달** → "Generate New Secret" 재확인
- 새 secret 복사 (한 번만 표시됨!)

### 4. 새 Secret을 .secrets에 저장 (자동 PowerShell)
아래 1줄에서 `<NEW_SECRET>` 만 paste 후 실행:

```powershell
# 기존 secret 백업
Copy-Item "C:\Users\hdh02\.secrets\paypal.json" "C:\Users\hdh02\.secrets\paypal.backup.$(Get-Date -Format 'yyyyMMdd_HHmm').json" -ErrorAction SilentlyContinue

# 새 secret 적용
$paypal = Get-Content "C:\Users\hdh02\.secrets\paypal.json" | ConvertFrom-Json
$paypal.live_client_secret = "<NEW_SECRET>"
$paypal | ConvertTo-Json -Depth 5 | Set-Content "C:\Users\hdh02\.secrets\paypal.json" -Encoding utf8

# Vercel 환경변수 동기화 (vercel CLI 필요)
$env:PAYPAL_CLIENT_SECRET = "<NEW_SECRET>"
vercel env rm PAYPAL_CLIENT_SECRET production --yes
echo "<NEW_SECRET>" | vercel env add PAYPAL_CLIENT_SECRET production
vercel deploy --prod

Write-Host "PayPal secret rotated + Vercel synced"
```

### 5. 검증 (자동)
- https://cheonmyeongdang.vercel.app/api/confirm-payment 헬스체크
- PayPal Smart Buttons 라이브 결제 1건 테스트 ($0.01 microtransaction → 본인 환불)
- 24시간 후 기존 secret revoke 자동 (PayPal 정책)

## Rotate 주기 권장
- **분기 1회** (3개월) — Stripe/PCI baseline 동등
- 또는 **사고 발생 시 즉시** (e.g. .secrets 노출 의심)
- 다음 권장 rotate: **2026-08-07**

## 위험도 평가
- **LOW**: 현재 Live secret 노출 흔적 없음
- 24시간 grace period 이중 valid → downtime 0
- 실수 시 백업 파일에서 복구 가능

---
**예상 사용자 시간: 5분 (PayPal 로그인 60초 + Generate 30초 + paste & PowerShell 60초 + 검증 대기 90초)**
