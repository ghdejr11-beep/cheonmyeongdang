# RapidAPI Provider Listing — 5분 → 2분 원샷 가이드

**OpenAPI 검증**: `departments/rapidapi/saju_openapi.yaml` 검증 OK
**리스팅 본문**: `departments/rapidapi/listing_text_4lang.md` (4 lang 사전 작성)

## 1클릭 직링크
- 프로바이더 가입: https://rapidapi.com/auth/sign-up?referral=/provider
- 새 API 추가: https://rapidapi.com/provider/new
- 프로바이더 대시보드: https://rapidapi.com/provider

## 회원가입 form 답변 (paste용)

| 항목 | 값 |
|------|---|
| Email | ghdejr11@gmail.com |
| Username | kunstudio |
| Display name | KunStudio |
| Country | South Korea |
| Company / Brand | KunStudio (쿤스튜디오) |
| Website | https://cheonmyeongdang.vercel.app |
| Industry | Astrology / AI / Lifestyle |

## 7단계 등록 클릭 순서

1. **Add New API** → "Add API" 버튼
   - API Name: `Korean Saju (Bazi) — 4 Pillars, Compatibility, AI Q&A`
   - Category: **Astrology** (primary), **AI/ML**, **Lifestyle**
   - Tagline: `Authentic Korean Saju / Bazi reading API. 4 pillars, 5-element balance, two-person compatibility, monthly fortune, free-form AI Q&A.`

2. **OpenAPI 업로드**: "Import from OpenAPI" 클릭 →
   파일: `C:\Users\hdh02\Desktop\cheonmyeongdang\departments\rapidapi\saju_openapi.yaml`
   드래그앤드롭

3. **Base URL 확인**: `https://cheonmyeongdang.vercel.app`

4. **Long Description**: `departments/rapidapi/listing_text_4lang.md` 의 EN 섹션 long description 전체 paste

5. **Pricing 설정** (4 tier):

   | Plan | Monthly | Quota | Rate Limit | Overage |
   |------|---------|-------|------------|---------|
   | **BASIC (Free)** | $0 | 100/월 | 10/min | 차단 |
   | **PRO** | $9.99 | 5,000/월 | 60/min | $0.005/req |
   | **ULTRA** | $49.99 | 50,000/월 | 300/min | $0.002/req |
   | **MEGA** | $199.99 | 500,000/월 | 1,000/min | $0.001/req |

6. **Tags** (paste): `saju, bazi, four-pillars, korean-astrology, chinese-astrology, fortune-telling, five-elements, wuxing, hangul, korean, claude-ai, personality, daily-fortune, gunghap, k-culture, monthly-fortune, compatibility`

7. **Submit for Review** 클릭 → 검토 ETA 1~3일

## Locale 추가 (선택, +5분)
RapidAPI는 영어 기본만 자동 노출. 한국어/일본어/중문 hub 노출하려면:
- Hub Locale 추가 메뉴 → KO/JA/ZH 각각 Title + Description paste
- 본문은 `listing_text_4lang.md` 동일 파일에서 복사

## 수익 추정 (보수적)
- 첫 달: 가입 50, Free 30, PRO 8 = $80
- 3개월: PRO 30 + ULTRA 5 = $550/월
- 6개월: PRO 80 + ULTRA 15 + MEGA 1 = $1,750/월

---
**예상 사용자 시간: 2분 (가입 form 30초 + OpenAPI drag 15초 + Pricing 4tier 입력 60초 + Submit 15초)**
