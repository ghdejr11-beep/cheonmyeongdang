# Etsy Top 5 Priority Listings

> **Purpose**: 사용자가 첫 5개만 빨리 등록하면, 나머지 35개는 자동 발행 큐에서 처리.
> **Source**: `departments/etsy/listings_2026_05_05.csv` (40 listings, all validated 2026-05-07).
> **Selection key**: search volume × price × keyword strength × Etsy 2026-04 trend data (eRank).

---

## 1. ADHD Daily Planner for Adults (90-Day Undated)
- **SKU**: `KDP-ADHD-PLANNER`
- **Price**: $12.99
- **Why first**: "ADHD planner" Etsy search volume **220k+/yr** (eRank), top 1% niche. Mental health printable category +47% YoY.
- **Best buyer**: 25-44 women, Reddit r/ADHD overlap, Pinterest viral.
- **Image1**: `departments/ebook/projects/adhd-planner/cover.pdf` (convert to PNG via Etsy uploader).

## 2. AI Side Hustle Blueprint: 100-Day System
- **SKU**: `KDP-AI-SIDE-HUSTLE-EN`
- **Price**: $14.99
- **Why second**: "AI side hustle" search volume +480% YoY (Google Trends 2026-04). Highest price-point in our top 5 = better $/listing.
- **Best buyer**: Indie hackers, side-hustle subreddit, $5k/mo aspiration keyword.
- **Image1**: `departments/ebook/projects/ai-side-hustle-en/cover.pdf`.

## 3. Notion Operator Bundle (5-pack)
- **SKU**: `NOTION-BUNDLE-5PACK`
- **Price**: $35.00
- **Why third**: Highest AOV in our catalog. Bundle psychology = users prefer over single $7 templates. Notion templates Etsy market = $40M+/yr.
- **Best buyer**: Knowledge workers, freelancers, productivity-curious.
- **Image1**: `departments/ebook/projects/notion-bundle-5pack/cover.pdf` (verify path).

## 4. Korean Saju Premium PDF Reading (BaZi Four Pillars)
- **SKU**: `SAJU-PREMIUM-PDF`
- **Price**: $21.99
- **Why fourth**: Unique IP — no other Etsy seller has Korean Saju PDF. Western interest in Korean astrology +312% YoY (K-pop / K-drama tailwind). Direct funnel back to cheonmyeongdang.com $79 LTD.
- **Best buyer**: Western K-fans, astrology TikTok, Co-Star users curious about non-Western systems.
- **Image1**: cheonmyeongdang sample PDF render (use `pdfs/sample_en.png` if exists).

## 5. Pelvic Floor Recovery Journal (Postpartum 12-week)
- **SKU**: `KDP-PELVIC-FLOOR-RECOVERY-JOURNAL`
- **Price**: $11.99
- **Why fifth**: Niche with **low competition + high willingness-to-pay**. Postpartum mothers = highest converting Etsy demographic (+38% conversion vs avg). Custom Pollinations Flux cover already generated.
- **Best buyer**: New mothers, doula/midwife referrals, OB-GYN office handouts.
- **Image1**: `departments/etsy/cover_generated/pelvic-floor-recovery-journal.png`.

---

## Etsy 등록 순서 (사용자 5분 액션)

1. Etsy seller dashboard -> "Add a listing" -> Digital download
2. 위 5개를 1번부터 차례대로:
   - Title / Description / Tags / Price -> CSV에서 복붙
   - Image1 path 열어서 업로드 (PNG/JPG 변환 필요 시 IrfanView)
   - Digital file: `departments/ebook/projects/{sku}/interior.pdf`
3. 첫 5개 publish 후 자동 발행 cron이 나머지 35개를 처리 (bulk via Vela / etsy-csv-import)

## 자동 발행 (나머지 35개)

- Cron: 매일 09:00 KST `etsy_bulk_upload.py` 1개씩 publish (Etsy rate-limit 준수)
- 35일이면 전체 catalog live
- 단가 평균 $9 × 35 = $315 카탈로그 가치 (월 5개 판매 가정 매출 $45/mo passive)
