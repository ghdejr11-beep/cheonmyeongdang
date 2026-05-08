# Etsy Top 5 — One-Shot Sheet (5분 실행)

> **목적**: 한 페이지에서 Etsy 가입 → Vela 연결 → Top 5 listing publish 까지 모든 페이스트 가능 텍스트를 모아둠.
> **사용자 시간**: ~20분 (이전 25분 대비 5분 단축)
> **보조 문서**: `docs/etsy_vela_oneliners.md` (전체 40 listing CSV bulk), `docs/etsy_top5_priority.md` (선정 근거)
> **마지막 업데이트**: 2026-05-07

---

## 0. 진행 흐름 (총 ~20분)

| Step | 시간 | URL |
|------|------|-----|
| 1. Etsy 셀러 가입 | 8분 | https://www.etsy.com/sell |
| 2. Payoneer 연결 (Etsy 한국 미지원) | 5분 | https://www.payoneer.com |
| 3. Vela 가입 + Etsy OAuth | 2분 | https://www.getvela.com/signup |
| 4. CSV bulk 업로드 (40 listings 전체) | 3분 | Vela `Listings → Import CSV` |
| 5. Top 5만 먼저 Publish (남은 35는 큐) | 2분 | Vela `Drafts` 탭 |

---

## 1. Etsy 가입 폼 답변 (✂ 복붙)

**URL 직링크**: https://www.etsy.com/sell

| 필드 | 답변 |
|-----|------|
| Email | `ghdejr11@gmail.com` |
| Shop name (1순위) | `KunstudioStudio` |
| Shop name (중복시 2순위) | `CheonmyeongdangShop` |
| Shop name (3순위) | `DeokguStudio` |
| Currency | `USD` |
| Shop language | `English` |
| Country | `South Korea` |
| Sales tax | `Skip` (Etsy 자동 VAT 처리) |
| Stock photo / 첫 listing walkthrough | `Skip` (Vela 사용 예정) |

⚠️ Etsy Payments 한국 미지원 → Payoneer 연결 단계로 자동 이동.

---

## 2. Payoneer 연결 (사업자번호 552-59-00848)

1. https://www.payoneer.com → `Sign Up` → `Business`
2. 사업자번호 `552-59-00848`, 상호 `쿤스튜디오`
3. 본인 인증: 여권 스캔 (또는 운전면허) + 사업자등록증 PDF (`D:\사업자등록증\`)
4. USD 수령계좌 발급 → Etsy onboarding `Connect Payoneer` 1클릭

---

## 3. Vela 가입 (✂ 복붙)

**URL**: https://www.getvela.com/signup

| 필드 | 답변 |
|-----|------|
| Email | `ghdejr11@gmail.com` |
| Plan | `Free` (CSV import 무료) |
| Etsy Shop | OAuth 1클릭 |

---

## 4. CSV bulk upload (40 listings)

1. Vela 로그인 → `Listings` → `Import CSV`
2. 파일: `D:\cheonmyeongdang\departments\etsy\listings_2026_05_05.csv`
3. `Validate` → 40 행 모두 OK 확인
4. `Push to Etsy` → 40개 모두 Draft 상태로 생성

---

## 5. Top 5 Publish (먼저, 신규 셀러 일일 limit 5개)

Vela `Drafts` 탭에서 아래 5개 SKU만 체크박스 → `Publish` 일괄.

### #1 ADHD Daily Planner (KDP-ADHD-PLANNER)
- **Price**: $12.99
- **Title**: `ADHD Daily Planner for Adults: 90-Day Undated Organizer with Brain Dump Pages, Dopamine Menu & Weekly Reviews`
- **Image1**: `D:\cheonmyeongdang\departments\ebook\projects\adhd-planner\cover.pdf`
- **Digital File**: `C:\...\adhd-planner\adhd_planner.pdf`
- **Why first**: "ADHD planner" Etsy search 220k+/yr, mental health printable +47% YoY
- **Tags (already in CSV)**: adhd daily planner, adult adhd journal, adhd planner women, printable, digital download...

### #2 AI Side Hustle Blueprint (KDP-AI-SIDE-HUSTLE-EN)
- **Price**: $14.99
- **Title**: `AI Side Hustle Blueprint: The 100-Day System to Build $5,000/Month Digital Products with Claude & ChatGPT`
- **Image1**: `C:\...\ai-side-hustle-en\cover.pdf`
- **Digital File**: `C:\...\ai-side-hustle-en\ai_side_hustle_en.pdf`
- **Why second**: "AI side hustle" +480% YoY. Highest price-point in top 5.

### #3 Notion Operator Bundle 5-pack (NOTION-BUNDLE-5PACK)
- **Price**: $35.00
- **Title**: `Notion Operator Bundle (5-pack)`
- **Image1**: `D:\notion_templates_2026_05_global_v2\_covers\BUNDLE_global.jpg`
- **Digital File**: `D:\notion_templates_2026_05_global_v2\_zips\KUNSTUDIO_GLOBAL_BUNDLE_5pack.zip`
- **Why third**: Highest AOV. Notion templates Etsy market = $40M+/yr.

### #4 Saju Premium PDF (SAJU-PREMIUM-PDF)
- **Price**: $21.99
- **Title**: `Saju Premium PDF Reading — Korean Four Pillars Astrology (BaZi)`
- **Image1**: `D:\saju_premium_pdf\_cover\saju_premium_cover.jpg`
- **Image2 (sample)**: `D:\saju_premium_pdf\output\saju_SAMPLE.pdf`
- **Digital File**: `D:\saju_premium_pdf\saju_premium_listing_pack.zip`
- **Why fourth**: Unique IP. Korean astrology Western interest +312% YoY. Direct funnel → cheonmyeongdang.com $79 LTD.

### #5 Pelvic Floor Recovery Journal (KDP-PELVIC-FLOOR-RECOVERY-JOURNAL)
- **Price**: $11.99
- **Title**: `Pelvic Floor Recovery Journal — Postpartum 12-Week Healing Tracker`
- **Image1**: `D:\cheonmyeongdang\departments\etsy\cover_generated\pelvic-floor-recovery-journal.png`
- **Digital File**: `C:\...\pelvic-floor-recovery-journal\pelvic_floor_recovery_journal.pdf`
- **Why fifth**: Postpartum = highest Etsy converting demographic (+38% vs avg).

---

## 6. Listing Fees

- **Top 5만 publish**: 5 × $0.20 = **$1.00** (Vela 자동 charge)
- **나머지 35 publish (D+1~D+8)**: 35 × $0.20 = **$7.00**
- **Total catalog**: $8.00 (~₩11,000)

---

## 7. 사용자만 가능한 액션 (5건)

1. ✋ Etsy 셀러 가입 (이메일 인증 + 본인인증)
2. ✋ Payoneer 사업자 연결 (여권/사업자등록증 OAuth)
3. ✋ Vela 가입 + Etsy OAuth
4. ✋ Vela CSV upload + `Push to Etsy` 1클릭
5. ✋ Top 5 Drafts → `Publish` 1클릭

**총 ~20분**.

---

## 8. 완료 후 자동 후속 (클로드 처리)

- D+1~D+8 자동 cron으로 매일 5개씩 publish (Etsy rate-limit 준수)
- Pinterest 핀 자동 생성: 매일 3 핀 (Etsy listing URL → Pinterest cross-post)
- 천명당 + KORLENS landing → Etsy 링크 cross-link
- 매주 매출 보고서에 Etsy 라인 추가
- 30일 후 미판매 listing → 키워드 재분석 + 태그 갱신

---

## 9. ROI 추정

| 시점 | 매출 | 누적 |
|---|---|---|
| 7일 | 첫 sale ($9.99 - 6.5% Etsy fee) | $9.20 |
| 30일 | 10~30 sales × $9~$15 | $150~$450 |
| 90일 | 50~150 sales | $500~$2,000 |
| 180일 | 200+ sales (검색 안정화) | $2K~$5K |

**Etsy SEO + Pinterest 트래픽 노출 → 6개월 후 passive sale 안정화.**
