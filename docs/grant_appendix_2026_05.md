# 사업계획서 보강 부록 (2026-05-07)

본 부록은 2026년 5월 라운드 정부지원 사업 신청서(K-Startup AI 리그 / 관광 AI / K-Global / 모두의창업 / 백업·재도전) 5종 docx에 첨부 가능한 추가 자료입니다. 검증 결과 docx 5종 모두에서 누락 또는 약하게 다뤄진 3개 영역(정통 명리학 깊이 / AI Q&A·매직링크 인프라 / VC·투자 트랙) 및 매출 잠재 시나리오를 보강합니다.

---

## 0. 신청 기업 기본 정보 (재확인용)

| 항목 | 값 |
|---|---|
| 기업명 | 쿤스튜디오 (KunStudio) |
| 대표자 | 홍덕훈 (Hong Dukhun, 1985년생) |
| 사업자번호 | 552-59-00848 |
| 개업일 | 2026-04-01 |
| 업종 | SW개발업 (간이과세) |
| 소재지 | 경상북도 경주시 (비수도권) |
| 주력 서비스 | 천명당 (cheonmyeongdang.com) — AI 사주 SaaS |
| 매출 (2026-05-07 기준) | ₩0 (라이브 D+34일, 검증 단계) |

---

## 1. 매출 잠재 unlock 시나리오 (₩0 → ₩2.5억)

현재 매출 ₩0은 정직하게 인정합니다. 대신 자동화 인프라가 11종 schtask + 4 언어 글로벌 진출로 이미 구축되어 있어, 채널별 unlock 단계마다 매출이 단계적으로 발생하는 시나리오입니다.

| 단계 | 시점 | 발생 채널 | 보수 추정 | 도달 요건 |
|---|---|---|---|---|
| Stage 0 | 5월~6월 | PayPal Smart Buttons + Ko-fi Tips | 월 ₩50만 | SEO blog factory 9건 indexed |
| Stage 1 | 7월~8월 | RapidAPI (B2B API) + Etsy 디지털 다운로드 | 월 ₩300만 | RapidAPI listing 승인 + Etsy Vela 5SKU |
| Stage 2 | 9월~10월 | AppSumo Lifetime Deal | 일시 ₩3,000만 + 월 ₩500만 recurring | AppSumo 심사 통과 (D-30 작업 중) |
| Stage 3 | 11월~12월 | Pinterest 53핀 → 천명당 ko/en/ja/zh 유입 폭증 | 월 ₩2,000만 | Pinterest 누적 100K impressions |
| Stage 4 | 2027 Q1 | VC Seed (Antler / Kakao Ventures / D2SF) | ₩2.5억 ~ ₩수십억 | MAU 5,000 + revenue traction |

**누적 unlock 잠재(보수)**: 12개월 ₩2.5억 SaaS revenue + Seed 투자 ₩2.5억 = **약 ₩5억 이상**

---

## 2. 정통 명리학 깊이 (점신 / 포스텔러 대비 차별점)

천명당의 핵심 차별점은 **AI 위에 진짜 명리학이 얹혀 있다**는 점입니다. 경쟁 서비스가 평균 3~4 항목 (사주팔자 / 일주 / 운세) 만 다루는 반면, 천명당은 **8.5/10 점수의 정통 명리학 8 영역**을 모두 커버합니다.

| 영역 | 천명당 | 점신 | 포스텔러 |
|---|---|---|---|
| 음양(陰陽) | O | O | O |
| 오행(五行) 상생상극 | O 풀 차트 | 일부 | 일부 |
| 십신(十神) | O | X | X |
| 12운성(運星) | O | X | X |
| 신살(神煞) | O | X | X |
| 대운(大運) 10년 분석 | O 차트 시각화 | 텍스트만 | 텍스트만 |
| 합충(合冲) 분석 | O | X | X |
| AI 자연어 Q&A | O 매월 무제한 | X | X |

**근거 자료**: `departments/tax/applications/round2_2026_05/INELIGIBILITY_LABELS.md` 및 `db/saju_traditional_v3_5.json` (8 영역 × 4 언어 = 32 데이터셋).

---

## 3. AI Q&A 챗 + 매직링크 인프라

### 3.1 AI Q&A 챗

- 매월 1일 자동 갱신되는 사주 풀이 + 사용자가 자연어로 질문 가능 ("올해 이직 운은?", "결혼 시기는?")
- Anthropic Claude Sonnet API 기반 + 정통 명리학 RAG (8 영역 데이터셋 임베드)
- 4 언어 동시 지원 (ko / en / ja / zh)
- 월 ₩2,900 구독자에게 무제한 제공, 무료 사용자에게 일 3회

### 3.2 매직링크 (Magic Link) 결제

- 회원가입 없이 이메일 1줄로 결제 → 매직링크로 즉시 PDF 30p + AI 챗 액세스
- PayPal Smart Buttons (글로벌) + 한국 PG 보조 (Toss 라이브키 진행 중)
- D+3 / D+7 / D+14 winback 메일 자동 시퀀스 (cron 등록 완료)

### 3.3 자동화 11 schtask 인프라

| 작업 | 주기 | 목적 |
|---|---|---|
| KunStudio_Daily_Briefing | 매일 09:00 | 매출/CS/SEO 요약 |
| KunStudio_KWisdom_Daily | 매일 07:00 | 글로벌 K-콘텐츠 채널 운영 |
| KunStudio_SEO_Blog_Factory | 매주 월/목 | 4 언어 SEO 블로그 자동 발행 |
| KunStudio_Pinterest_Pin | 매일 13:00 | 53핀 카테고리 자동 핀 |
| KunStudio_Winback_D3_D7_D14 | 매일 11:00 | 환불/winback 메일 |
| KunStudio_PG_Mail_Monitor | 매일 10:00 | 토스/갤럭시아 회신 모니터 |
| KunStudio_Grant_Result_Monitor | 매일 11:00 | 정부지원 결과 발표 모니터 (신규) |
| KunStudio_Cheonmyeongdang_OG | 매주 일요일 | 4 언어 24 페이지 OG 갱신 |
| KunStudio_AppSumo_Etsy_Sync | 매일 14:00 | 외부 마켓플레이스 동기화 |
| KunStudio_Affiliate_Track | 매일 15:00 | 어필리에이트 (30%) 정산 추적 |
| KunStudio_Dashboard_Refresh | 매일 18:00 | 종합 대시보드 갱신 |

---

## 4. VC / 투자 트랙 (Antler / Kakao Ventures / D2SF)

| VC | 단계 | 진행 상태 | 다음 액션 |
|---|---|---|---|
| Antler Korea | Pre-seed | Pitch deck v1 작성 (KunStudio_AILeague_EN.pptx 기반) | 6월 cohort 신청 |
| Kakao Ventures | Seed | 워밍업 (Kakao 결제 라이브 기반 association) | MAU 1,000 도달 시 콜드 |
| D2SF (네이버) | Seed | KORLENS 관광 AI 트랙으로 접근 | 관광 AI 정부지원 통과 후 |

피치덱 자료: `departments/tax/applications/round2_2026_05/KunStudio_AILeague_EN.pptx`, `KORLENS_Product_EN.pptx` (영문 + 한글 버전 모두 보유)

---

## 5. 마일스톤 (5/20 → 6 → 9 → 12)

| 시점 | 마일스톤 | KPI |
|---|---|---|
| 5/20 | K-Startup AI 리그 / 관광 AI 신청서 마감 제출 | docx 5종 + 부록 1종 첨부 완료 |
| 6월 말 | K-Startup 결과 발표 + KoDATA 회신 처리 | 통과 시 6/30 협약 / 부적격 시 KoDATA 사후 등록 |
| 9월 말 | AppSumo Lifetime Deal 런칭 + Pinterest 100K imp | MAU 1,000 / MRR ₩300만 |
| 12월 말 | 4 언어 글로벌 SaaS 안정 + VC Seed 라운드 오픈 | MAU 5,000 / MRR ₩1,000만 / Seed term sheet 1+ |

---

## 6. 첨부 가능 형태

본 부록은 다음 정부지원 PMS / 제출 시스템에 PDF 변환 후 첨부 가능합니다:

- K-Startup PMS (`사업계획서_AI리그_2026.docx`의 별첨)
- 한국관광공사 관광 AI 제출 시스템 (`사업계획서_관광AI_2026.docx`의 별첨)
- 모두의창업 (`사업계획서_모두의창업_2026.docx`의 별첨)
- KoDATA 사전등록 (5/12 회신 후 동봉)

PDF 변환: `pandoc grant_appendix_2026_05.md -o grant_appendix_2026_05.pdf` (자동 변환 가능)
