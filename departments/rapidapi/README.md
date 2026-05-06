# RapidAPI 부서 — Korean Saju (Bazi) API B2B 마켓플레이스

**상태**: 미발행 (사용자 1클릭 액션 대기)
**잠재 수익**: $749/mo (100 Pro subs × $9.99 × 75% 분배율, 60~120일 ETA)

## 현재 인프라 (구축 완료)

- ✅ `saju_openapi.yaml` — OpenAPI 3.0 스펙 (POST `/saju/reading` 1 endpoint)
- ✅ `rapidapi_listing.md` — 마켓플레이스 게시 양식 (제목/설명/4 가격 티어/cURL+Python+Node 샘플)
- ✅ Vercel 라이브 endpoint: `https://cheonmyeongdang.vercel.app/saju/reading`
  - vercel.json rewrite: `/api/saju-rapid` → `/api/compat?action=rapidapi-saju` (active)
  - 응답: 4 pillars + 5 elements 분포 + 일간성 분석 + Claude AI 영문 advice (3문장)

## B2B 가격 (RapidAPI 4 티어)

| 티어 | 월 | 쿼터 | 분배 후 (75%) |
|------|-----|------|----------------|
| Free | $0 | 100/일 | $0 |
| **Pro** | $9.99 | 10K/월 | **$7.49** ← 1차 목표 |
| Ultra | $49 | 100K/월 | $36.75 |
| Mega | $199 | 1M/월 | $149.25 |

**1차 매출 목표**: 100 Pro = $749/mo (월 ₩100만 수준)

## 사용자 1클릭 액션 (5분, 매출 unlock)

1. https://rapidapi.com/provider 가입 (PayPal payout · Stripe 불필요 — 한국 사업자 OK)
2. "Add new API" → 매뉴얼 입력 (yaml 파일 업로드 옵션은 베타)
3. `rapidapi_listing.md` 의 Title / Description / Categories / Tags 복붙
4. Endpoint 추가: `POST /saju/reading` + 샘플 request/response 붙여넣기
5. Pricing 4 티어 입력 (위 표)
6. Vercel 환경변수 추가: `RAPIDAPI_PROXY_SECRET=<dashboard에서 복사>` + `ANTHROPIC_API_KEY` (이미 설정)
7. Test → Publish (1~2 영업일 manual review)

## 후속 cross-sell (1차 listing 후 추가 가능)

| API | 가격 | 기존 엔진 재활용 |
|------|------|------------------|
| Korean Compatibility (Gunghap) | +$9.99/mo | `compat-engine` 재사용 |
| Korean Lucky Name Check | +$4.99/mo | name 五行 calc 재사용 |
| Korean Daily Fortune | +$2.99/mo | 60-Ganji rotation 재사용 |

## 모니터링 (라이브 후)

- RapidAPI 대시보드: 일간 호출량 / 신규 구독자 / Free→Pro 전환율
- Sales 통합: `departments/sales-collection/` 에 RapidAPI 매출 webhook 연결 후 매일 09시 텔레그램 보고서에 합산

## ⚠️ 주의사항

- 한국 사업자 552-59-00848 PayPal payout 가능 (memory: Stripe·Polar 한국 사용 불가)
- API key 노출 금지 (server proxy 경유, .gitignore 필수 — memory `feedback_api_key_security`)
- Rate limit 강제: Vercel function timeout 10초 + Anthropic API quota → Free 100/일 hard cap이 vercel side 보호막
