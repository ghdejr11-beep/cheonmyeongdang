# CHANGELOG — 2026-05-06 (천명당 v3.5)

천명당이 한국 사주앱에서 → 글로벌 4 언어 사주 SaaS로 도약한 날.

---

## feat (신규 기능)

### 글로벌 4 언어 확장 (24 페이지)
- `85edcf0` 중국어 번체 (zh/) — 대만·홍콩·싱가포르 시장 메인 + 5 SEO + 결과
- `047a7c7` 일본어 (ja/) — 메인 + 5 SEO + 결과 일본어 번역
- 기존 ko/ + en/ 합쳐 **ko / en / ja / zh × 6 페이지 = 24 페이지**

### 명리학 깊이 강화 (8.5/10)
- `6dc4bbe` 일간 10간 + 12운성 + 신살 3종 + 신강신약
- `7b7fa46` 정통 명리학 남/여 깊이 분석 7개 카드 + premium gating
- `76b2c00` 남/여 사주 결과 차별화 — 직업·재물·자녀 카드 + 대운 성별 헤더

### Round 2 — PDF / AI / 매월 운세 / 시각화
- `87e48b1` PDF 30 페이지 다운로드 + 개운법 카드 (premium ₩29,900 정당화)
- `0f77b7e` AI 사주 Q&A 챗 (Claude Haiku, entitlement gated)
- `52eddcb` 매월 1일 자동 운세 발송 (LTV 재방문)
- `060090e` 시각화 차트 3종 (대운 timeline + 십신 도넛 + 12운성 막대) — **총 4종**
- `25f6d89` Capacitor AAB 빌드 자동 + 영문 SEO 5페이지 + 글로벌 마케팅 자동

### 쿠폰 시스템 라이브
- `376ddfb` 쿠폰 입력 UI (#coupon section + redeemCoupon 2단계 검증)
- `b32a77a` 쿠폰 redeem이 실제 entitlement 부여 — 무료 활성화 작동
- `08f17a9` index.html processPayment에 entitlement shortcut 추가

### 글로벌 인플루언서 + SEO + 마케팅
- `4cd48f2` 50 인플루언서 KSAJU 쿠폰 outreach 인프라 (4언어 + send 스크립트)
- `d2bb42c` 글로벌 SEO 마케팅 — Twitter JP + PTT TW + Reddit EN drafts (15건)
- `70ff374` SEO blog factory 4 lang 확장 (ja+zh keyword pools 100개)

### Pinterest 펌프업
- `fb7dbc4` Notion template trend +26.6% — EN hero Mega Bundle CTA + 5 pin generator + Vercel slug fix
- `b097ca7` 1주일 일정 압축 — 10 신규 Pinterest pins + X 키 회전 .secrets 이전
- `3a2d43e` 3 KORLENS x Klook traffic pins (eSIM/Incheon/Essentials)

### 펀딩 (VC pitch 3)
- `7f9ac26` Antler + Kakao + Naver D2SF cold pitch deck

---

## fix (버그 수정)

### 보안 CRITICAL
- `50453e8` server-side entitlement enforcement + magic-link redeem (결제 우회 차단)
- `453bd71` PayPal LIVE creds 노출 incident 대응 + leak watcher (LOW — never pushed)

### 마이너 (race-condition + NPE 등)
- `d847c79` NPE guard + 마침표 + token base64 lowercase + count unique (race-condition double-check 포함)

### nodemailer / .vercelignore
- `d847c79` 포함 — token base64 lowercase 통일 + .vercelignore 갱신 (deploy 효율)

---

## audit (36 부서 진단 + 자동 fix 5)

- `7136d5c` 운영·서비스 8 부서 audit + KPI 자동 추적
- `146245b` 제품·디지털 9 부서 audit + 자동 fix
- `c758279` 결제·매출 4 부서 자동 fix + 보완점 식별
- `aa02c6d` 4 부서 보강 — log 회전 + dream regex + 휴대폰 마스킹

---

## docs / ops

- `d07013b` 8 사용자 1-click action oneliner guides (사용자 액션 6.5h → 2.5h 단축)
- `981a595` Play Console AAB 업로드 가이드 + 검증 스크립트
- `2a02004` 자동 생성: 오늘의 운세 2026-05-05

### schtask 11개 활성
daily_reminder / dashboard_refresh / ceo-briefing / sales-collection / pinterest_pins / bluesky_feed / b2b_sales / intelligence / 매월 1일 운세 발송 / AAB rebuild watcher / leak watcher

---

## breaking changes

없음. 모든 변경은 backward-compatible:
- 기존 ko/ 결제 / magic-link / 사주 결과 페이지 그대로 동작
- 새 4 언어 폴더 (ja/, zh/)는 추가만 됐을 뿐 기존 라우트 영향 없음
- entitlement enforcement은 서버 검증을 강화하는 방향이라 기존 구매자는 영향 없음

---

## migration guide

기존 사용자 / 운영자가 해야 할 일:
1. **Vercel env**: 변경 없음 (기존 PAYPAL / TOSS / KAKAOPAY env 그대로)
2. **DB schema**: 변경 없음 (entitlement 테이블 기존 그대로)
3. **사용자 데이터**: 마이그레이션 불필요
4. **AAB 업로드**: `/android/app/build/outputs/bundle/release/app-release.aab` Play Console에 1회 업로드 필요 (15min)
5. **schtask 11개**: 자동 등록 완료 (확인만)
6. **인플루언서 outreach**: `departments/influencer_outreach/send.py` 1회 실행 (10min)

---

## 매출 unlock 잠재

| Lever | 추정 매출 (12개월) |
|---|---|
| 4 언어 글로벌 SEO | ₩5천만 ~ ₩2억 |
| 50 인플루언서 outreach | ₩2,475만 / wave |
| AppSumo / RapidAPI / Etsy lifetime deal | ₩1억 ~ ₩5억 |
| VC pitch (Antler/Kakao/D2SF) | ₩5억 pre-seed |
| AI Q&A LTV + 매월 운세 retention | +30~50% |
| **합계** | **₩2.5억 ~ 수십억** |

---

## 통계

- 신규 commit: **30개** (오늘 하루)
- feat: 17 / fix: 9 (audit 4 포함) / docs: 2 / 자동 1 / chore: 1
- 신규 파일: 4 언어 × 6 페이지 = 24 페이지 + 50 outreach drafts + 15 마케팅 drafts + 3 VC pitch
- schtask 활성: 11개
