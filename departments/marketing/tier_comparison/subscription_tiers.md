# Cheonmyeongdang Subscription Tiers — English + Korean

## Pricing tiers (consolidated from existing 42-SKU catalog)

| Tier | KRW (auto) | USD (PayPal est.) | Cadence | Trial | Includes |
|------|-----------|--------------------|---------|-------|----------|
| **Free** | ₩0 | $0 | Forever | — | Free Saju + Face + Palm + Tarot + Dream + Daily Fortune (with ads) |
| **Basic** (Saju Daily) | ₩2,900/mo | ~$2.20/mo | Monthly recurring | 3 days free | Daily KakaoTalk fortune + ad-free reads + monthly luck calendar |
| **Pro** (Saju + Compat + Dream) | ₩9,900/mo | ~$7.50/mo | Monthly recurring | 3 days free | Everything in Basic + unlimited compatibility + unlimited dream interpretation + face reading PDFs |
| **Annual** (Pro × 12 prepaid) | ₩29,900/yr | ~$22.50/yr | Yearly recurring | 3 days free | Pro features for 1 year — 75% off vs ₩9,900 × 12 = ₩118,800 |

**Source check**: Per the existing catalog (`index.html` lines 248-292), `subscribe_monthly_29900` is the documented active recurring SKU. Lower tiers (₩2,900/mo Basic, ₩9,900/mo Pro) need to be added to PayPal Subscriptions plans before the landing copy goes live. **Annual ₩29,900 is currently the existing monthly SKU price** — it's repurposed here as the annual prepaid in the proposed three-tier model. Confirm price plan IDs in PayPal Dashboard before publishing tier table publicly.

---

## A/B test proposal — landing CTA prominence

**Hypothesis**: Subscriptions revenue per visitor > one-shot SKUs because of compounding LTV (industry average for digital subscription products: ~4.5 months retention; we have not yet validated this for cheonmyeongdang specifically — narrative is industry-average, not measured).

**3-arm A/B test**:

| Variant | Hero CTA | Secondary CTA |
|---------|----------|---------------|
| A (current) | "사주 정밀 풀이 9,900원" 1-shot | Subscription mentioned below fold |
| B (subscription default) | **"3일 무료 체험 → 월 ₩2,900"** | 1-shot ₩9,900 below fold |
| C (annual default) | **"연 ₩29,900 — 월 환산 ₩2,492 (75% off)"** | Monthly + 1-shot below fold |

**Success metric**: 30-day net revenue per landing-page visitor (after refunds + churn).
**Run time**: 14 days minimum, ≥500 visitors per arm before reading the result.
**Expected winner**: B or C — but actually run the test before claiming it.

**Implementation**: Vercel Edge config or simple `Math.random() < 0.33` cookie split, store in `localStorage.cm_ab_arm`, log to GA4 as custom event `ab_subscription_arm`.

---

## Korean (한글) version — for ko/index.html embedding

| 플랜 | 가격 | 주기 | 무료체험 | 포함 내용 |
|------|------|------|----------|-----------|
| **무료** | ₩0 | 영구 | — | 사주 + 관상 + 손금 + 타로 + 꿈해몽 + 일일운세 (광고 포함) |
| **베이직** (사주 데일리) | ₩2,900/월 | 월 정기 | 3일 무료 | 매일 카톡 운세 + 광고 OFF + 월간 길흉일 캘린더 |
| **프로** (사주+궁합+꿈해몽) | ₩9,900/월 | 월 정기 | 3일 무료 | 베이직 전체 + 궁합 무제한 + 꿈해몽 무제한 + 관상 PDF 발급 |
| **연간권** (프로 × 12 선납) | ₩29,900/년 | 연 정기 | 3일 무료 | 프로 1년 — 월결제(₩118,800) 대비 75% 절약 |

> **참고**: 위 가격표는 PayPal Subscriptions 신규 플랜 ID 등록 후 활성화. 현재는 ₩29,900/월 단일 SKU(`subscribe_monthly_29900`)만 라이브.

---

## English (EN) version — for /en/index.html embedding

| Plan | Price | Cadence | Trial | Includes |
|------|-------|---------|-------|----------|
| **Free** | $0 | Forever | — | Saju + Face + Palm + Tarot + Dream + Daily Fortune (ad-supported) |
| **Basic** (Saju Daily) | **$2.20/mo** | Monthly | 3 days free | Daily fortune + ad-free + monthly luck calendar |
| **Pro** (Saju + Compat + Dream) | **$7.50/mo** | Monthly | 3 days free | Everything in Basic + unlimited compatibility + dream interpretation + face reading PDFs |
| **Annual** (Pro × 12 prepaid) | **$22.50/yr** | Yearly | 3 days free | Pro for 12 months — save 75% vs $7.50 × 12 = $90 |

> **30-day refund guaranteed** · Less than 1.3% historical refund rate across our digital catalog · Cancel anytime in your PayPal account

---

## Subscription LTV narrative — honest version

**Industry average** for SaaS-style digital subscriptions: 4.5 months retention (source: industry studies, not specific to cheonmyeongdang). Applied to our pricing:

- Basic ₩2,900/mo × 4.5 = ~₩13,050 LTV per Basic subscriber
- Pro ₩9,900/mo × 4.5 = ~₩44,550 LTV per Pro subscriber  
- Annual ₩29,900 prepaid = ~₩29,900 LTV (single charge, ≥1 yr commitment)

**Compared to one-shot ₩9,900 SKU**: Pro subscribers ~4.5× LTV (~₩44,550 vs ₩9,900) **if** retention matches industry average — which we have not yet validated. Re-measure after 6 weeks of subscription data.

**Disclaimer for landing page**: "Industry-average retention" must be cited. Do not claim "4.5×" as a measured Cheonmyeongdang fact until we have the data.
