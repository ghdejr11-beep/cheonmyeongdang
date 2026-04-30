# 천명당 안드로이드 인앱결제 SKU 가격 정책

**최종 확정일**: 2026-04-27
**통화**: KRW

## SKU 매핑 표

| SKU ID | 상품명 | 유형 | 갱신 주기 | 가격 (KRW) |
|---|---|---|---|---|
| `today_fortune` | 오늘 운세 | 무료 | - | 0 |
| `face_reading` | 관상 풀이 | 무료 | - | 0 |
| `palm_reading` | 손금 풀이 | 무료 | - | 0 |
| `dream_interpretation` | 꿈해몽 | 무료 | - | 0 |
| `saju_premium` | 사주 정밀 풀이 | 1회성 결제 | - | 9,900 |
| `gunghap` | 궁합 | 1회성 결제 | - | 9,900 |
| `comprehensive_reading` | 종합 풀이 | 1회성 결제 | - | **29,900** |
| `sinnyeon` | 신년운세 (연간) | 1회성 결제 | - | **15,000** |
| `monthly_premium` | 월회원권 (무제한) | **구독 (Subscription)** | **1개월 자동 갱신** | **29,900** |
| `no_ads` | 광고 없음 (영구) | 1회성 결제 | - | **9,900** |

### 월회원권 `monthly_premium` 상세

- **결제 타입**: 구독 (Subscription) — Play Console "정기결제 상품" 등록 필요
- **베이스 플랜 ID**: `monthly` (1개월 자동 갱신)
- **무료 체험**: 3일 (옵션, 신규 가입자 한정)
- **혜택**: 사주·궁합 무제한 + 매일 카톡 운세
  - 사주 정밀 풀이 (`saju_premium`) — 무제한
  - 궁합 (`gunghap`) — 무제한
  - 매일 아침 카톡 운세 발송 (전용 혜택)
  - ⚠️ **종합 풀이 (`comprehensive_reading`)는 월회원 포함 안 됨** — 별도 ₩15,000 결제 필요
- **가치 제안**:
  - 단건 사주(9,900원) 또는 단건 궁합(9,900원) **단일 구매 가격**으로 모든 풀이 무제한 + 매월 갱신
  - 월 1건 이상 결제 사용자는 **본전 이상**, 2건 이상은 **압도적 이득**
- **잠금 해제 OR 조건** (`js/cm-entitlement.js` 참고):
  - 사주 / 궁합: `hasMonthly || hasSaju` / `hasMonthly || hasGunghap`
  - 종합 풀이: `hasComprehensive` 만 (월회원도 별도 결제 필요)
- **참고**: Vercel/토스 결제 페이지(`api/payment-config.js`)에서는 동일 상품을 `subscribe_monthly_9900`로 운용. 향후 ID 통일 필요.

### 권한 매트릭스 (월회원 혜택 명확화 — 2026-04-27 확정)

| 콘텐츠                | 비결제자 | 월회원 ₩9,900/월 | 사주 단건 ₩9,900 | 궁합 단건 ₩9,900 | 종합풀이 ₩15,000 |
|----------------------|:-------:|:----------------:|:----------------:|:----------------:|:----------------:|
| 오늘 운세            | ✅       | ✅                | ✅                | ✅                | ✅                |
| 관상 / 손금 / 꿈해몽 | ✅       | ✅                | ✅                | ✅                | ✅                |
| 사주 정밀 풀이       | ❌       | **✅ 무료**       | ✅                | ❌                | ❌                |
| 궁합                 | ❌       | **✅ 무료**       | ❌                | ✅                | ❌                |
| **종합 풀이**         | ❌       | **❌ 별도결제**    | ❌                | ❌                | ✅                |
| 매일 카톡 운세       | ❌       | **✅ 전용**       | ❌                | ❌                | ❌                |

**잠금 해제 의사코드** (`js/cm-entitlement.js`):
```js
const hasMonthly        = userPurchases.includes('monthly_premium');
const hasSajuOneTime    = userPurchases.includes('saju_premium');
const hasGunghapOneTime = userPurchases.includes('gunghap');
const hasComprehensive  = userPurchases.includes('comprehensive_reading');

unlockSaju          = hasMonthly || hasSajuOneTime;     // 월회원 OR 단건
unlockGunghap       = hasMonthly || hasGunghapOneTime;  // 월회원 OR 단건
unlockComprehensive = hasComprehensive;                  // ⚠️ 단건만 — 월회원 무관
```

> ⚠️ Play Console 구독 상품 등록 시 "구독자 무료 콘텐츠"에 **종합 풀이를 포함시키지 말 것** (월회원도 별도 결제). 사주/궁합만 포함.

## 마케팅 카피 (번들 할인율 재계산)

- 사주 정밀 풀이 + 궁합 개별 합계: 9,900 + 9,900 = **19,800원**
- 종합 풀이 단일가: **15,000원**
- 절약 금액: 19,800 - 15,000 = **4,800원**
- **할인율: 약 24%** (4,800 / 19,800 ≒ 24.24%)

### 카피 후보
- "사주+궁합 따로 사면 19,800원, 종합 풀이로 한 번에 15,000원 (24% 할인)"
- "두 개 묶어 4,800원 더 저렴하게"
- "프리미엄 두 가지를 종합 풀이 하나로 — 24% OFF"

### 월회원권 카피 후보 (재계산 — 종합풀이 제외)
- "사주 9,900 + 궁합 9,900 = 19,800원 가치 + 매일 카톡 운세 → 월 9,900원"
- "월 1번이라도 사주 또는 궁합 풀이하면 본전, 2번이면 압도적 이득"
- "단건 사주 1번 가격으로 한 달 동안 사주·궁합 무제한 + 매일 카톡 운세"
- "9,900원 / 월 — 사주·궁합 무한반복 + 매일 아침 8시 카톡 운세 발송"
- ⚠️ "종합 풀이는 별도 ₩15,000 — 1회성 깊은 풀이를 원하실 때"

## 변경 이력

- **2026-04-30 (오후): 웹 기준으로 가격 통일** (CEO 재지시 — 매출 인상 우선)
  - 종합풀이 **₩29,900** (웹 기준 채택, 앱 Play Console 인상 필요)
  - 월회원권 **₩29,900/월** (웹 기준 채택, 앱 Play Console 인상 필요)
  - 신년운세 **₩15,000** (웹 ₩15,000 / 앱 `sinnyeon_20000`→`sinnyeon_15000` 수정)
  - 광고없음 **₩9,900** (웹/앱 동일)
  - 사주 정밀 **₩9,900** + 궁합 **₩9,900** (웹/앱 동일)
- 2026-04-27 (저녁): **`monthly_premium` 월회원권 추가** (구독, 9,900원/월). 모든 유료 SKU 잠금 해제 OR 조건. 부록 B/D 체크리스트 갱신.
- 2026-04-27 (오전): `comprehensive_reading` 가격 29,000 → **15,000** 정정 (CEO 지시)
- 2026-04-27: 보조 Agent — 기존 코드 매핑 분석 및 Play Console 등록 가이드 추가

---

## 부록 A. 기존 코드의 SKU 매핑 (index.html line 4664~4680 기준)

`@capgo/native-purchases ^8.0.0` 사용. 현재 `index.html` 4664행 `window.CMD_IAP_SKU_MAP`:

| 현재 등록 SKU | 표시 이름 (코드 키) | 가격 (코드) | 정책 부합 여부 |
|---|---|---|---|
| `subscribe_monthly_9900` | 무제한 사주 구독권 (3일 무료체험) | 월 9,900 | ❌ 본 정책 외 → 비활성화 권장 |
| `consult_premium_19900` | 프리미엄 30분 1:1 심층 상담권 | 19,900 | ❌ 본 정책 외 → 비활성화 권장 |
| `gpt_chat_2900` | AI 명리학자 1:1 실시간 상담 | 2,900 | ❌ 본 정책 외 → 비활성화 권장 |
| `saju_detail_29900` | 사주 상세 풀이 | **29,900** | ⚠️ **₩9,900으로 인하 필요** → `saju_premium` SKU로 대체 |
| `compat_detail_9900` | 궁합 상세 분석 | 9,900 | ✅ 일치 → `gunghap`으로 ID 통일 권장 |
| `sinnyeon_20000` (prefix) | 신년운세 YYYY | 20,000 | ❌ 본 정책 외 → 비활성화 권장 |

> 정책표의 SKU ID(`today_fortune`, `saju_premium`, `gunghap`, `comprehensive_reading`)와 현재 코드 ID(`saju_detail_29900` 등)가 다르므로, 코드와 Play Console에서 ID를 통일해야 함. 무료 4종(오늘운세/관상/손금/꿈해몽)은 코드에 SKU 매핑 없이 잠금 없이 노출 중 — **추가 코드 수정 불필요**.

---

## 부록 B. Play Console 등록 가이드 (사용자 직접 작업)

### B-1. 기존 SKU 비활성화
Play Console > 수익화 > 인앱 상품에서 다음 4종을 **비활성** 상태로 전환:
- `subscribe_monthly_9900`
- `consult_premium_19900`
- `gpt_chat_2900`
- `sinnyeon_20000`

> 결제 이력이 있는 사용자 보호를 위해 **삭제하지 말고 비활성**.

### B-2. 신규 SKU 등록 (4개)

#### 일반 인앱 상품 (1회성, 3개)

| Product ID | 이름 | 설명 | 가격 (KRW) |
|---|---|---|---|
| `saju_premium` | 사주 정밀 풀이 | 사주팔자 기반 정밀 풀이 1회 (직업·재물·건강·인연 포함) | 9,900 |
| `gunghap` | 궁합 | 두 사람 사주 비교 분석 1회 | 9,900 |
| `comprehensive_reading` | 종합 풀이 | 사주 정밀 + 궁합 묶음 패키지 (24% 할인) | 15,000 |

#### 정기결제 (구독) 상품 (1개) — Play Console > 수익화 > **구독** 메뉴

| Product ID | 이름 | 설명 | 베이스 플랜 ID | 가격 (KRW) |
|---|---|---|---|---|
| `monthly_premium` | 월회원권 | 모든 유료 풀이 무제한 액세스 (사주·궁합·종합) | `monthly` (1개월 자동 갱신) | 9,900 |

- **베이스 플랜**: 1개월 자동 갱신, ID = `monthly` (앱 코드의 `planIdentifier: 'monthly'`와 일치 필수)
- **무료 체험 오퍼**: 3일 (선택) — 신규 가입자 한정으로 등록 권장
- **결제 주기**: 매월 동일 일자 자동 갱신
- **취소 정책**: Play Store > 구독 메뉴에서 사용자가 직접 해지 가능

> 기존 `compat_detail_9900` 가 활성 상태라면 그대로 두고 `gunghap`을 신규 등록할지, ID를 통일할지 선택. ID 통일 권장.

### B-3. 가격 동기화 검증
- 한국(KRW) 가격 9,900 / 9,900 / 15,000 정확히 입력
- 세금 자동 적용 (간이과세자)

---

## 부록 C. 빌드 영향 (versionCode)

- 현재: `android/app/build.gradle` versionCode **8** / versionName **1.3.1**
- SKU 매핑 변경 시 신규 빌드 필요: versionCode **9** / versionName **1.4.0** 권장
- 빌드: `npx cap sync` → `gradlew.bat bundleRelease` → AAB 사용자 업로드

---

## 부록 D. 사용자 직접 액션 요약 (체크리스트)

- [ ] Play Console에서 `saju_premium` 신규 등록 (₩9,900, 인앱)
- [ ] Play Console에서 `gunghap` 신규 등록 (₩9,900, 인앱) — 또는 기존 `compat_detail_9900` 활용
- [ ] Play Console에서 `comprehensive_reading` 신규 등록 (₩15,000, 인앱)
- [ ] **Play Console > 수익화 > 구독에서 `monthly_premium` 정기결제 상품 등록 (₩9,900/월, 베이스 플랜 ID `monthly`, 3일 무료체험)** ⭐ 신규
- [ ] 기존 4종 SKU 비활성화 (`subscribe_monthly_9900`, `consult_premium_19900`, `gpt_chat_2900`, `sinnyeon_20000`)
  - ※ `subscribe_monthly_9900` 비활성화 후 `monthly_premium`로 마이그레이션 — 결제 이력 사용자는 만료 시까지 유효
- [ ] (코드 동기화 후) versionCode 9 / versionName 1.4.0 빌드 업로드
- [ ] **토스 콘솔에서 정기결제(빌링키) 라이브 신청** (웹 결제 자동갱신용 — 별도 심사 1~3영업일)

---

문서 작성: 2026-04-27 (보조 Agent — 기존 다른 Agent 작성분 보강)

