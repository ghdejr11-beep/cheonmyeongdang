# Etsy Vela 40 Listings 1클릭 가이드

> **시급도**: 🟡 매출 보조 (글로벌 디지털 다운로드 채널)
> **사용자 시간**: ~25분 (Etsy 가입 15 + Vela 업로드 10)
> **매출 임팩트**: 30일 $150~$450 (10~30 sales × $9~$15) / 90일 $500~$2K
> **마지막 업데이트**: 2026-05-06

복붙 텍스트 ✂ 표시.

---

## 0. 사전 점검 (자동 완료)

- ✅ CSV 40 listings: `departments/etsy/listings_2026_05_05.csv` (UTF-8 BOM, 1511 lines, 41행 = 헤더+40)
- ✅ 이미지 manifest: `departments/etsy/images_manifest.csv`
- ✅ Pollinations 자동 생성 표지 5개: `departments/etsy/cover_generated/`
- ✅ KDP 33 + Notion 6 + Saju Premium PDF 1 = 40 listings
- ✅ 가격대: $4.99 ~ $35 (스위트스팟 $9.99)
- ✅ SKU prefix 매핑: `KDP-*` / `NOTION-*` / `SAJU-PREMIUM-PDF`

---

## 1. Etsy 셀러 가입 (15분)

**URL**: https://www.etsy.com/sell

| 필드 | 답변 (✂ 복붙) |
|-----|---|
| Email | `ghdejr11@gmail.com` |
| Shop name | `KunstudioStudio` (1순위) / `DeokguStudio` (2순위, 중복시) |
| Currency | `USD` (글로벌) |
| Shop language | `English` |
| Country | `South Korea` |
| Sales tax | `Skip` (디지털 다운로드 — Etsy 자동 VAT 처리) |

⚠️ **Etsy Payments 한국 미지원** → **Payoneer** 연결:
1. https://www.payoneer.com 사업자 계정 가입 (사업자번호 `552-59-00848`)
2. Payoneer USD 수령계좌 발급 → Etsy onboarding `Connect Payoneer` 선택
3. 본인 인증: 여권 스캔 + 사업자등록증 (PDF 저장 위치: `D:\사업자등록증\`)
4. Stock photo / 첫 listing walkthrough → `Skip` (Vela 사용)

---

## 2. Vela 가입 + 연결 (3분)

**URL**: https://www.getvela.com/signup

| 필드 | 답변 (✂ 복붙) |
|-----|---|
| Email | `ghdejr11@gmail.com` |
| Plan | `Free` (CSV import 무료) |

가입 후 → `Settings` → `Connect Etsy Shop` → OAuth 1클릭.

---

## 3. CSV 일괄 업로드 (5분)

**Vela**:

1. `Listings` → `Import CSV` 클릭
2. 파일 선택: `departments/etsy/listings_2026_05_05.csv`
3. **Column mapping** (자동 인식 — 헤더가 Vela 표준과 일치):
   - Title → Title
   - Description → Description
   - Price → Price
   - Tags → Tags
   - Image1 → Primary Image
   - Digital File → Digital File
   - SKU → SKU
4. `Validate` 버튼 → 40개 행 모두 OK 확인
5. `Push to Etsy` 클릭 → 모든 listing이 **Draft 상태**로 생성됨

---

## 4. 이미지 일괄 첨부 (3분)

Vela 이미지 picker 열기:
1. `Listings` → `Bulk Edit` → `Image Manager`
2. **Drag & Drop**:
   - `departments/etsy/cover_generated/` 폴더 통째로 → 5 Pollinations 표지 자동 매칭 (SKU 기반)
   - `cheonmyeongdang/departments/ebook/projects/<id>/cover.pdf` → 33 KDP 표지 (PDF rasterize 필요시 Vela 자동 처리)
3. SKU 매칭 자동 검증.

---

## 5. Draft 검토 + Publish (10분)

⚠️ **첫 등록은 Etsy 검토 통과해야 함** (1~3 영업일):

1. Vela → `Listings` → `Drafts` 탭 → 40개 모두 선택
2. 첫 5개를 먼저 `Publish` (Etsy 신규 셀러 limit 5 listings/day 가능)
3. Etsy 검토 통과 확인 후 나머지 35개 publish
4. **Listing fees**: 40 × $0.20 = **$8.00** (Vela가 자동 charge)

---

## 6. 카테고리 + 태그 사전 매핑 (자동 완료)

CSV 안에 모두 포함되어 있음:

| SKU prefix | Category | Top tags |
|---|---|---|
| KDP-* (33개) | `Books, Movies & Music > Books > Digital Books` | `printable, digital download, planner, ebook, ADHD, productivity` |
| NOTION-* (6개) | `Paper & Party Supplies > Paper > Stationery > Notebooks & Journals` | `notion template, productivity, digital planner` |
| SAJU-PREMIUM-PDF (1개) | `Spirituality & Religion > Astrology Readings` | `korean saju, bazi, four pillars, astrology, fortune` |

---

## 7. 사용자만 가능한 액션 (5건)

1. Etsy 셀러 가입 (이메일 인증 + 본인인증)
2. Payoneer 사업자 계정 연결 (OAuth)
3. Vela 가입 + Etsy OAuth
4. CSV 업로드 + Push (1클릭 후 자동)
5. Draft 5개 → Publish (1클릭)

**총 ~25분**.

---

## 8. 완료 후 자동 후속 (클로드 처리)

- Pinterest 핀 자동 생성 (Etsy listing URL → 매일 3 핀)
- 천명당 + KORLENS landing에 Etsy 링크 cross-link
- 매주 매출 보고서에 Etsy 라인 추가
- 30일 후 미판매 listing → 키워드 재분석 + 태그 갱신

---

## ROI

| 시점 | 매출 | 누적 |
|---|---|---|
| 7일 | 첫 sale ($9.99 - 6.5% Etsy fee) | $9.20 |
| 30일 | 10~30 sales × $9~$15 | $150~$450 |
| 90일 | 50~150 sales | $500~$2,000 |
| 180일 | 200+ sales (검색 안정화) | $2K~$5K |

**Etsy SEO + Pinterest 트래픽 노출 → 6개월 후 passive sale 안정화.**
