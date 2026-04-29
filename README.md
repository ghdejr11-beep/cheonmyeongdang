# 천명당 (Cheonmyeongdang)

An ancient Eastern wisdom, reimagined for today. Experience a personalized destiny reading crafted from the moment you were born.

## AdSense 광고 단위 설정

무료 콘텐츠 영역(사주/궁합/타로/별자리/꿈해몽/오늘의 운세 결과)에 6개의 AdSense 슬롯이 배치되어 있습니다. 유료 페이지(`pay.html`, `success.html`, 월회원 영역)에는 광고가 노출되지 않습니다.

### 1. AdSense 신청
1. https://adsense.google.com 접속 → "시작하기"
2. 사이트 URL: `https://cheonmyeongdang.vercel.app`
3. 결제 정보(쿤스튜디오 사업자) 입력 → 1~14일 내 승인 메일 도착
4. 승인 후 발급되는 Publisher ID: `ca-pub-XXXXXXXXXXXXXXXX` 메모

### 2. 광고 단위 6개 생성 (AdSense 콘솔 → 광고 → 광고 단위별)
| 위치 | 추천 형식 | data-ad-slot 입력 위치 |
|---|---|---|
| 사주 결과 하단 | 디스플레이 (반응형) | `index.html` line ~1914 |
| 궁합 결과 하단 | 디스플레이 (반응형) | `index.html` line ~2019 |
| 타로 결과 하단 | 디스플레이 (반응형) | `index.html` line ~2231 |
| 별자리 운세 하단 | 디스플레이 (반응형) | `index.html` line ~2347 |
| 꿈해몽 채팅 하단 | In-feed (fluid) | `index.html` line ~2393 |
| 오늘의 운세 하단 | 디스플레이 (반응형) | `index.html` line ~2273 |

### 3. 코드 교체
`index.html` 전역 검색·치환 (`PLACEHOLDER` → 실제값):
- `ca-pub-PLACEHOLDER` → `ca-pub-XXXXXXXXXXXXXXXX` (Publisher ID, 7곳: head 1 + ins 6)
- `data-ad-slot="0000000001"` → 사주 슬롯 ID
- `data-ad-slot="0000000002"` → 궁합 슬롯 ID
- `data-ad-slot="0000000003"` → 타로 슬롯 ID
- `data-ad-slot="0000000004"` → 별자리 슬롯 ID
- `data-ad-slot="0000000005"` → 꿈해몽 슬롯 ID
- `data-ad-slot="0000000006"` → 오늘의 운세 슬롯 ID

### 4. ads.txt (선택, 권장)
승인 후 AdSense 콘솔 → 사이트 → ads.txt 다운로드 → `public/ads.txt` 또는 루트에 배치 → Vercel 재배포

### 정책 준수
- 유료 SKU/월회원 페이지에는 광고 X (정책 준수)
- 자동 클릭 유도/무한 스크롤 광고 X
- 본인 클릭 금지 (계정 정지 사유)

## 가격표 (KRW)

| 상품 | SKU (앱) | 결제 타입 | 가격 |
|---|---|---|---|
| 사주 정밀 풀이 | `saju_premium` | 1회성 | ₩9,900 |
| 궁합 | `gunghap` | 1회성 | ₩9,900 |
| 종합 풀이 (사주+궁합 묶음, 24% OFF) | `comprehensive_reading` | 1회성 | ₩15,000 |
| **월회원권 (사주·궁합 무제한)** | **`monthly_premium`** | **구독 (1개월 자동 갱신)** | **₩9,900 / 월** |

> 월회원권 — 사주 정밀 / 궁합 무제한 + 매일 카톡 운세 (※ **종합 풀이는 단건 결제만** ₩15,000)
> 단건 1번 가격(9,900원)으로 한 달 무제한 — 2건 이상 결제 사용자에게 압도적 이득.
> 자세한 정책은 [`departments/cheonmyeongdang/sku_pricing.md`](departments/cheonmyeongdang/sku_pricing.md) 참고.

## 결제 시스템

### 웹 (Vercel + 토스페이먼츠)
- `pay.html` — 토스 v2 위젯 결제 페이지 (1회성 결제)
- `success.html` — 결제 완료 + 영수증 + 월회원권일 경우 30일 entitlement 저장
- `fail.html` — 결제 실패 안내
- `api/payment-config.js` — 클라이언트 키 + SKU 카탈로그 노출
- `api/confirm-payment.js` — 토스 시크릿키 결제 확정 (서버사이드)

### 앱 (Google Play 인앱결제)
- `@capgo/native-purchases` 사용
- `index.html` 의 `window.CMD_IAP_SKU_MAP` 매핑 + `runNativeIAP()`
- 구독 SKU는 베이스 플랜 ID `monthly` (1개월 자동 갱신)

## 월회원 일일 운세 자동 발송

월회원(`subscribe_monthly_9900`)은 매일 **오전 8시**에 본인 사주 기반
"오늘의 운세"를 카카오톡(알림톡) 또는 텔레그램으로 자동 수령한다.

### 흐름
1. **결제 시 정보 수집** — `pay.html` 월회원 카드에서 생년월일/생시/음양력/성별/텔레그램 chat_id 입력
2. **결제 승인 후 등록** — `success.html` → `/api/confirm-payment` → `/api/subscribe-fortune`
   - Vercel은 영구 디스크 없음 → 신규 가입자 정보를 관리자 텔레그램으로 푸시,
     로컬 PC의 `subscribers.json` 에 수동/스크립트 동기화
   - `paid_until = 결제일 + 30일`, 만료 시 자동 비활성화
3. **운세 생성** — `daily_fortune_generator.py` → Claude API (생년월일·시·성별·오늘 일진)
4. **발송 우선순위** (`daily_fortune_send.py`):
   1. 카카오 알림톡 (Solapi, 템플릿 승인 후) — 정보성, 차단 불가
   2. 카카오 친구톡 (Solapi, 채널 친구 한정) — 광고 가능
   3. 텔레그램 (1:1, 폴백)

### 파일 구조
- `departments/cheonmyeongdang/data/subscribers.json` — 회원 명단 (스키마 포함)
- `departments/cheonmyeongdang/daily_fortune_generator.py` — Claude 운세 생성
- `departments/cheonmyeongdang/daily_fortune_send.py` — 발송 (Solapi/Telegram)
- `departments/cheonmyeongdang/daily_fortune_run.py` — schtasks 진입점
- `departments/cheonmyeongdang/register_daily_fortune.bat` — 매일 08:00 등록 스크립트
- `departments/cheonmyeongdang/logs/daily_fortune_YYYY-MM-DD.json` — 발송 로그
- `api/subscribe-fortune.js` — Vercel 가입자 등록 API

### 환경 변수 (.secrets)
- `ANTHROPIC_API_KEY` — Claude API
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — 폴백 발송 + 관리자 알림
- `SOLAPI_API_KEY`, `SOLAPI_API_SECRET` — 카카오 알림톡/친구톡 (사용자 가입 후)
- `KAKAO_PF_ID` — 천명당 카카오 채널 ID (월렛: 908652)
- `KAKAO_TEMPLATE_DAILY_FORTUNE` — 알림톡 템플릿 ID (승인 후)
- `SOLAPI_SENDER_PHONE` — SMS 폴백용 발신번호 (카카오 알림톡 거부 시)

### 설치 (1회)
```bat
cd C:\Users\hdh02\Desktop\cheonmyeongdang\departments\cheonmyeongdang
register_daily_fortune.bat
```

### 카카오 알림톡 정식 가입 (사용자 액션, 1~2주)
1. **카카오 비즈니스 채널** — 이미 완료 (@cheonmyeongdang, 월렛 908652)
2. **Solapi 가입** → API key/secret 발급 → `.secrets` 에 저장
   - 또는 NHN Bizmessage / 알리고(Aligo) 사용 가능 (Solapi 권장: 가성비)
3. **알림톡 발신 프로필 등록** (Solapi 콘솔에서 카카오 채널 연동, 검토 1~2일)
4. **알림톡 템플릿 신청** — "{name}님 오늘의 운세" 변수 3개 (`#{name}`, `#{fortune}`, `#{score}`) 승인 1~5일
5. 템플릿 승인 후 `KAKAO_TEMPLATE_DAILY_FORTUNE` 에 templateId 등록 → 자동 알림톡 발송 시작
6. 미가입 단계에서는 **텔레그램으로 즉시 발송**됨 (가입자에게 텔레그램 봇 등록 안내)

### 테스트
```bat
python departments\cheonmyeongdang\daily_fortune_generator.py
python departments\cheonmyeongdang\daily_fortune_send.py --dry-run
python departments\cheonmyeongdang\daily_fortune_run.py
```

### 잠금 해제 로직 (`js/cm-entitlement.js`)
```js
// 사주/궁합: 월회원권 OR 단건 결제 (OR 조건)
window.CmEntitlement.canUnlock('saju')          // 월회원 OR saju_premium
window.CmEntitlement.canUnlock('gunghap')       // 월회원 OR gunghap
// 종합 풀이는 단건 결제(₩15,000)만 — 월회원에 포함되지 않음
window.CmEntitlement.canUnlock('comprehensive') // comprehensive_reading 결제만
```

## 토스 정기결제 (자동 갱신) — 별도 신청 필요

웹 측 월회원권은 현재 **1회성 결제로 처리** (1개월 무제한 후 만료).
실제 자동 갱신을 구현하려면:

1. **토스 콘솔 → 정기결제(빌링) 신청** (1~3영업일 심사)
2. 라이브 빌링키(BillingAuth) 클라이언트 키/시크릿 키 발급
3. `pay.html` → `requestBillingAuth()` 호출로 카드 등록 + 빌링키 발급
4. `api/confirm-payment.js` → 빌링키 기반 `payments/billing/{billingKey}` 호출
5. Vercel Cron 또는 외부 스케줄러로 매월 자동 청구
6. 갱신 실패 시 `cm_subscription.active = false` 처리

> 참고: <https://docs.tosspayments.com/guides/v2/billing/integration>

## 개발

```bash
# Vercel 로컬 개발
vercel dev

# 안드로이드 빌드 (Capacitor)
npx cap sync
cd android && ./gradlew bundleRelease
```

## 환경변수 (Vercel)

| 변수 | 용도 |
|---|---|
| `TOSS_CLIENT_KEY` | 토스 클라이언트 키 (frontend 노출 OK) |
| `TOSS_SECRET_KEY` | 토스 시크릿 키 (서버 전용, 절대 노출 금지) |
| `TOSS_BILLING_CLIENT_KEY` | (예정) 토스 빌링 클라이언트 키 |
| `TOSS_BILLING_SECRET_KEY` | (예정) 토스 빌링 시크릿 키 |

## 문의
- 사업자: 쿤스튜디오 · 대표 홍덕훈
- 사업자등록번호: 552-59-00848
- 이메일: ghdejr11@gmail.com
