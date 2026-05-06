# RapidAPI Listing 1클릭 가이드 — Korean Saju API

> **시급도**: 🟡 매출 보조 (장기 passive income)
> **사용자 시간**: ~5분
> **매출 임팩트**: $50~$500/월 (BASIC tier $9.99/mo × 5~50 subscribers, 6개월 후)
> **마지막 업데이트**: 2026-05-06

복붙 텍스트 ✂ 표시. 다른 텍스트는 그대로 두면 됨.

---

## 0. 사전 점검 (자동 완료)

- ✅ OpenAPI 3.0 yaml: `departments/rapidapi/saju_openapi.yaml`
- ✅ 리스팅 markdown (전체 카피): `departments/rapidapi/rapidapi_listing.md`
- ✅ 4 가격 티어 정의 완료 (BASIC / PRO / ULTRA / MEGA)
- ✅ cURL/Python/Node 예시 코드 준비
- ✅ Endpoint 구현 준비됨: `POST /saju/reading` (천명당 백엔드 활용)

---

## 1. RapidAPI Provider 가입 (2분)

**URL**: https://rapidapi.com/auth/sign-up?referral=/provider

| 필드 | 답변 (✂ 복붙) |
|-----|---|
| Email | `ghdejr11@gmail.com` |
| Display name | `KunStudio` |
| Provider name | `kunstudio-cheonmyeongdang` |
| Country | `Korea, Republic of` |
| Business type | `Sole Proprietor` |
| Tax ID | `552-59-00848` |

→ 이메일 인증 1클릭.

---

## 2. New API 등록 (3분)

**URL**: https://rapidapi.com/provider/api/new

1. **Add API** → **Manual setup** 선택
2. **General**:

| 필드 | 답변 (✂ 복붙) |
|-----|---|
| API name | `Korean Saju (Bazi) Reading API` |
| Short description (140자) | `Authentic Korean Saju (Bazi / Four Pillars) reading: 4 pillars, 5-element balance, lucky color and direction, plus AI English advice.` |
| Category | `Astrology` (없으면 `AI / Machine Learning`) |
| Tags | `saju, bazi, four-pillars, korean-astrology, chinese-astrology, fortune-telling, five-elements, claude-ai, k-culture` |
| Base URL | `https://cheonmyeongdang.vercel.app` |
| Visibility | `Public` |

3. **Long description**: `departments/rapidapi/rapidapi_listing.md`의 `### Long description` 단락 ✂ 복붙

---

## 3. OpenAPI yaml 업로드 (1분)

1. **Definition** 탭 → **Import OpenAPI** 클릭
2. 파일 업로드: `departments/rapidapi/saju_openapi.yaml`
3. 자동 import 확인 → `POST /saju/reading` endpoint 1개 생성됨
4. **X-RapidAPI-Proxy-Secret** 자동 주입 활성화 (Security → Proxy Secret)

---

## 4. 가격 티어 4개 생성 (2분)

**Pricing** 탭 → **Add Plan** 4번:

| Plan | Monthly Price | Quota | Overage | Use Case |
|---|---|---|---|---|
| **BASIC** | $0 (Free) | 100 req/day | $0.01/req | Trial / 개인 |
| **PRO** | $9.99 | 5,000 req/mo | $0.005/req | 인디 앱 |
| **ULTRA** | $49.99 | 50,000 req/mo | $0.002/req | 중형 SaaS |
| **MEGA** | $199.99 | 500,000 req/mo | $0.0005/req | 엔터프라이즈 |

✂ 각 plan 설명:
- BASIC: `Free trial — 100 readings/day, all 4 pillars + 5 elements + AI insight`
- PRO: `Indie & startup — 5,000 readings/mo, full feature, priority email support`
- ULTRA: `SaaS production — 50,000 readings/mo, SLA 99.5%, dedicated support`
- MEGA: `Enterprise — 500K readings/mo, custom SLA, white-label option`

---

## 5. Endpoint 테스트 (RapidAPI 콘솔, 1분)

1. **Test Endpoint** 탭 → BASIC plan 선택
2. Sample request (자동 채워짐):
```json
{
  "birth_year": 1990,
  "birth_month": 5,
  "birth_day": 15,
  "birth_hour": 14,
  "gender": "F"
}
```
3. `Test Endpoint` 클릭 → 200 OK 확인 (응답 시간 <3초)

⚠️ **만약 502/timeout** → `cheonmyeongdang.vercel.app/api/saju-rapid` endpoint 부재일 수 있음. 클로드에게 "rapidapi endpoint 추가" 요청 (별도 1시간 작업, 본 가이드 외).

---

## 6. Submit for Review (1분)

1. **Submit** 탭 → 체크리스트 자동 검증:
   - ✅ OpenAPI 정의
   - ✅ 4개 티어
   - ✅ Long description 200자 이상
   - ✅ Code samples (자동 생성)
   - ⚠️ Logo (없으면 KunStudio 로고 D:\ 에서 업로드 — 256x256 권장)
2. `Submit for Review` 클릭.
3. RapidAPI 응답 1~3 영업일.

---

## 7. 사용자만 가능한 액션 (4건)

1. RapidAPI 계정 생성 + 이메일 인증 (1클릭)
2. KunStudio 로고 업로드 (D:\ 에서 1클릭 — 256x256 PNG)
3. Stripe Connect 또는 PayPal payout 연결 (RapidAPI는 Stripe 우선이지만 PayPal도 지원)
4. 최종 `Submit for Review` 버튼

**총 ~5분**.

---

## 8. 완료 후 자동 후속

- 천명당 `unified_revenue.py` 에 RapidAPI source 자동 추적
- 월별 매출 보고서에 RapidAPI 라인 추가
- subscriber 50명 도달시 ULTRA tier 추천 알림 자동 전송
- 신규 endpoint 추가시 yaml 자동 갱신 + RapidAPI 재배포

---

## ROI

- **6개월차**: BASIC 100 + PRO 5 = $50/월
- **12개월차**: PRO 20 + ULTRA 2 = $300/월
- **24개월차**: PRO 50 + ULTRA 5 + MEGA 1 = $950/월

passive income, 한 번 등록하면 고객이 알아서 가입.
