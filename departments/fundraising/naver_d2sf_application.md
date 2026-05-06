# 네이버 D2SF (Naver D2 Startup Factory) — Cold Contact Form

**Apply URL:** https://d2startup.com/contact (D2SF 공식 컨택)
**대안 URL:** https://d2startup.com/ (메인) → "Contact / Pitch" 폼
**참고:** D2SF는 cold form 제출 → 심사역 검토 → 1차 미팅 → IC → 텀시트 단계
**작성일:** 2026-05-06

---

## 폼 항목별 답변 (한국어 — 폼에 그대로 복붙)

---

### 1. 회사명 (Company)

```
쿤스튜디오 (KunStudio)
```

---

### 2. 사업자등록번호 (Business Registration Number)

```
552-59-00848 (간이과세, 정보통신업)
```

---

### 3. 대표자 (Founder)

```
홍덕훈 (Deokhoon Hong) — 1985년생, 1인 운영, AI 엔지니어 6년+
```

---

### 4. 본사 소재지 (HQ Address)

```
경상북도 경주시 외동읍 (비수도권)
```

---

### 5. 설립일 (Founded)

```
2026-04-01 (지원 시점 Day 36)
```

---

### 6. 사업 분야 (Business Domain)

```
AI SaaS — 한국 정통 명리학(사주) 글로벌 4언어 서비스 (B2C 구독 + B2B API)
```

---

### 7. 한 줄 소개 (One-liner, 200자 이내)

```
글로벌 점성술 시장 $12.8B 중 비어 있던 'Asian Saju AI' 카테고리를 한·영·일·중 4개 언어로 채우는 SaaS. Co-Star가 서양 점성술이라면, 천명당은 정통 한국 명리학 + Claude AI Q&A를 글로벌에 처음 공급한다.
```

---

### 8. 핵심 기술 / 제품 (Core Tech / Product)

```
[제품] 천명당 (Cheonmyeongdang) — https://cheonmyeongdang.vercel.app

[Day 36 라이브 기능]
1. 4개 언어 (한·영·일·중) — 단일 사주 사이트 중 최초 4언어 라이브
2. 정통 명리학 깊이 8.5/10 — 60갑자, 십신 10개, 12운성, 합·충·형·해·파, 대운·세운·월운
3. AI Q&A — Claude Haiku 통합. 사용자가 자연어로 "이 직장 그만둘까?" 질문 → 사주 기반 답변. 한계비용 ~₩30/쿼리
4. 자체 Saju Engine — 350+ 해석 룰 (확장 가능)
5. 매직링크 OTP — 비밀번호 없이 30초 가입
6. 시각화 4기둥 차트 + 십신 휠 (자체 SVG 렌더러)
7. PDF 리포트 + 모바일 AAB (Google Play 내부 테스트)
8. PayPal Smart Buttons 라이브 (200+ 국가 결제)
9. Gumroad 18 SKU + Etsy 40 listings + RapidAPI submitted (다채널 분산)

[Tech Stack]
- Frontend: Vanilla JS + Vercel Edge
- Backend: Vercel Serverless Functions (Node.js)
- AI: Claude Haiku (Anthropic) + 자체 Saju 엔진
- DB: Supabase (PostgreSQL)
- 결제: PayPal Smart Buttons + Gumroad + Etsy
- i18n: 자체 다국어 라우팅 (/ko, /en, /ja, /zh)
```

---

### 9. 시장 (Market)

```
[TAM] 글로벌 점성술 시장 $12.8B (2026, Allied Market Research)
[SAM] 한국+일본+중화권+동아시아 디아스포라 $5B (KOFICE 2024 + 동아시아 무역)
[SOM] 영어권 K-wave 인접 (3년 capture 4%) $200M

[Comparable companies]
- 포스텔러 (Posteller): 시리즈 B ₩85억 valuation, B2B 운세 API (한국 only)
- 점신 (Jeomsin): 한국 1위 운세 앱 (한국 only, 사람 상담)
- Co-Star Astrology (US): $25M+ raised, $400K MRR (서양 점성술 only)
- The Pattern (US): $50M+ raised (서양 점성술 only)

[공백] 정통 한국 명리학 깊이 + AI Q&A + 4개 언어 + 글로벌 결제 → 천명당이 처음.
```

---

### 10. 차별성 / 경쟁우위 (Differentiation)

```
1. 4개 언어 글로벌 라이브 — 한국 사주 사이트 중 글로벌 다국어 라이브 회사 0
   K-pop/K-drama로 늘어난 영어권/일본/중화권 디아스포라 수요를 첫 번째로 흡수.

2. AI Q&A 한계비용 ≈ ₩0 (Claude Haiku, 쿼리당 ~₩30)
   유저가 질문할수록 unit economics 개선 — 'engagement = profit' 구조.

3. 정통 명리학 깊이 8.5/10 (자체 평가)
   60갑자 + 십신 10개 + 12운성 전 영역 커버. 대부분 글로벌 점성술/타로 앱은 깊이 4~5/10.

4. 1인 운영 = burn rate ₩28만/월
   Claude Code + 90+ Python 자동화로 10인 팀 경제성 달성.
   동일 자본으로 5~10배 활주 가능.

5. 네이버 생태계 시너지
   - 네이버 운세 / 네이버 지식인 검색 트래픽 → 천명당 SEO 진입로
   - 네이버 클로바 X / 하이퍼클로바 X 한국어 모델과의 미래 통합 가능성
   - 네이버 페이 / 네이버 멤버십 결제 채널 추가 잠재력 (현재 PayPal only)
```

---

### 11. 비즈니스 모델 (Business Model)

```
3-stack 수익구조 (현재 라이브):

(1) B2C 구독 — ₩9,900 / ₩19,900 / ₩29,900 monthly (마진 88%)
(2) B2C lifetime + AppSumo LTD — $4.99~$29.99 (Gumroad 18 SKU, 마진 95%)
(3) B2B API — RapidAPI $49/$249/$749 monthly (제출 완료, 마진 92%)

[Unit Economics 목표]
- CAC ≈ ₩0 (Pinterest organic + K-wave SEO + 어필리에이트 30%)
- LTV (구독 12개월 blended): ~₩160,000
- Payback: 1개월 미만 (CAC > 0일 경우에도)
```

---

### 12. Traction (Day 36, 솔직 표기)

```
[실 매출] ₩0 — 1개월차, organic acquisition 단계, 광고비 미집행

[Day 36 라이브 인프라]
- 4개 언어 MVP 라이브 (한·영·일·중)
- PayPal Smart Buttons 라이브 (5/3, 200+ 국가)
- Gumroad 18 SKU 준비
- Etsy 40 listings 준비
- RapidAPI submitted
- Pinterest 4언어 20핀 자동 생성 큐
- 인플루언서 50명 outreach DM 준비
- 모바일 AAB Google Play 내부 테스트

[정부 검증]
- 모두의 창업 4/19 Tech Track 신청
- K-Startup AI리그 5/5 제출 (project ID 20452291)

[Speed proof]
1인이 36일 만에 4언어 SaaS + 다채널 결제 라이브.
Burn rate ₩28만/월. 동일 시점 일반 스타트업 burn ₩2,000만+/월 대비 70배 효율.
```

---

### 13. 팀 (Team)

```
홍덕훈 (Deokhoon Hong) — 솔로 파운더, 1985년생 (만 41세)
- AI/SaaS 엔지니어 6년+
- 풀스택 (Vercel + Claude API + PostgreSQL + i18n)
- 솔로 라이브 제품 5개 운영:
  1. 천명당 (이 신청)
  2. KORLENS — 방한 외국인 4언어 AI 가이드 (30M 관광객 TAM)
  3. 세금N혜택 — 한국 세금·정부지원 AI
  4. HexDrop — 모바일 퍼즐 게임 (Play 내부 테스트)
  5. K-Wisdom — 글로벌 한국 문화 유튜브 채널
- AI 코파일럿: Claude Sonnet 4.6 + Claude Code + 90+ Python 자동화

[고용 계획 — 시드 후]
- 월 12: 명리학 전문 자문 1 retainer (콘텐츠 깊이) + 그로스/마케팅 1 풀타임
- 월 18: AI 엔지니어 1 풀타임 (B2B API + 모바일 네이티브)
```

---

### 14. 투자 요청 (Funding Ask)

```
[금액] $300,000 (약 ₩4억)
[형태] 시드 (CB / SAFE 모두 협의 가능)
[기간] 12~18개월 runway

[활용 계획]
1. 한국 1위 진입 (점신·포스텔러 다음 #3): $120K (40%)
   - 네이버 검색광고 + 인플루언서 어필리에이트 풀 확장
2. 글로벌 4언어 SEO + 인플루언서: $90K (30%)
   - Pinterest/Instagram/TikTok 4언어 콘텐츠 파이프라인
3. 명리학 지식 그래프 350 → 2,000 룰: $60K (20%)
   - 명리학 전문가 자문 retainer + 데이터 큐레이션 외주
4. B2B API GTM: $30K (10%)
   - AppSumo LTD 캠페인 + RapidAPI 마케팅
```

---

### 15. 12개월 후 목표 (12-Month Goal)

```
- 한국 사주 앱 점유율 #3 진입 (점신·포스텔러 다음)
- 영어/일본/중화권 사주 AI #1 (현재 경쟁자 0)
- ARR ₩4~8억
- 유료 구독자 5,000~10,000명
- B2B API 5~10개 페잉 클라이언트 (K-pop 팬 플랫폼 + 동아시아 데이팅 앱)
- 시리즈 A ready ($1M~$3M, 글로벌 컨슈머 AI VC)
```

---

### 16. 왜 네이버 D2SF인가 (Why Naver D2SF)

```
1. 컨슈머 AI 포트폴리오 적합성
   D2SF는 컨슈머·AI·콘텐츠 영역에서 한국 → 글로벌 엣지를 가진 회사를 선호.
   천명당은 한국 IP(명리학) × 글로벌 LLM(Claude)의 정확한 교집합.

2. 네이버 생태계 시너지
   - 네이버 검색 운세 트래픽 → 천명당 인입 채널
   - 네이버 클로바 X / 하이퍼클로바 X 한국어 모델 통합 잠재력
   - 네이버 페이 결제 채널 추가
   - 라인(LINE) 일본 진출 시 LINE 친구 추가형 사주 챗봇 기회

3. D2SF 네트워크 = 한국 컨슈머 AI 1티어
   포트폴리오사들과의 cross-promo, B2B API 초기 고객 확보 가능.

4. 현금 효율 검증된 1인 솔로 파운더
   Burn rate ₩28만/월. D2SF 시드 $300K = 18개월+ runway 확보 가능.
   동일 자금으로 일반 팀 대비 5~10배 길게 활주.
```

---

### 17. 데모 / 첨부 자료 (Demo / Attachments)

```
[라이브 URL]
- 천명당 메인: https://cheonmyeongdang.vercel.app
- KORLENS: https://korlens.app
- 세금N혜택: https://sehyetaek.vercel.app
- K-Wisdom YouTube: @kunstudiokr / @kwisdom_kr

[첨부 자료]
- KunStudio_AILeague_EN.pptx (영문 IR 덱)
- KORLENS_Product_EN.pptx (4언어 관광 AI)
- 30일 traction proof: PayPal 콘솔 + Gumroad 18 SKU + Vercel Analytics
- 사업자등록증 (요청 시 제공)
```

---

### 18. 연락처 (Contact)

```
대표: 홍덕훈 (Deokhoon Hong)
이메일: ghdejr11@gmail.com
회사: 쿤스튜디오 (KunStudio)
주소: 경상북도 경주시 외동읍
※ 휴대폰은 미팅 셋업 후 직접 공유 (cold form 본문 마스킹)
```

---

## 폼 제출 전 체크리스트

- [ ] 휴대폰 번호는 폼 본문에 **마스킹** 또는 미입력 (070-****-****, 010-****-****)
- [ ] 첨부: KunStudio_AILeague_EN.pptx + KORLENS_Product_EN.pptx (이미 round2_2026_05 폴더에 보유)
- [ ] 라이브 URL 3개 모두 동작 재확인 (제출 직전)
- [ ] 매출 ₩0 정직 표기 — D2SF는 reference check 강함, 부풀린 traction은 즉시 reject
- [ ] 비수도권(경주) 가점이 있는지 폼에서 체크 옵션 확인 (있으면 체크)

## 후속 액션

- D2SF 응답 SLA: 보통 2~4주
- 1차 미팅 (30분, 줌) → 2차 심층 (90분, 오프라인 분당 본사) → IC → 텀시트
- 미팅 시 라이브 데모 + Vercel Analytics + PayPal 콘솔 화면공유 준비
