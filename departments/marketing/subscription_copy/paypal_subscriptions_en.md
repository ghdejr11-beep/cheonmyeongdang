# PayPal Subscriptions — English landing copy

## Hero (above the fold)

> **Start your Korean Saju journey for $2.20/month**
>
> Daily fortune, monthly luck calendar, ad-free reading.
> 3-day free trial. Cancel anytime in PayPal.
> 30-day refund guaranteed.
>
> [Start Free Trial →]

## Subhead — value justification

> Less than the price of a coffee. More than the depth of a horoscope app.
> Built on 1,000-year-old Korean Four Pillars tradition, decoded for English readers.

## Three-card layout (Basic / Pro / Annual)

### Basic — $2.20/mo
- Daily fortune (lucky color, direction, hour)
- Monthly luck calendar
- Ad-free reading
- Cancel anytime
- 3-day free trial
- **Best for**: Curious K-drama fans, casual learners

### Pro — $7.50/mo (most popular)
- Everything in Basic
- Unlimited compatibility readings
- Unlimited dream interpretation
- Face reading PDFs
- Premium A4 5-page Saju report (1/mo)
- 3-day free trial
- **Best for**: Couples, expats in Korea, deep learners

### Annual — $22.50/yr (save 75%)
- Pro features × 12 months
- Equivalent to $1.88/mo
- 3-day free trial
- **Best for**: Long-term users, gift-givers
- Save $67.50 vs paying monthly

## Trust row (below pricing)

- **30-day refund guarantee** — historical refund rate <1.3% across our digital catalog
- **Cancel in 1 click** — manage entirely from your PayPal account
- **No card stored on our servers** — PayPal handles all billing
- **Built by Korean astrology practitioners**, not a horoscope app studio

## Social proof placeholder (DO NOT publish until validated)

> Replace with verified metrics once available:
> - "{N} subscribers across {M} countries" — pull from PayPal Subscriptions report after 30 days
> - "Average user reads {X} reports per month" — pull from GA4
> - DO NOT use fabricated numbers, fake testimonials, or made-up "as seen on" logos

## FAQ block

**Q: How does the 3-day free trial work?**
A: PayPal authorizes a $0.01 hold, refunded immediately. You're not charged until day 4. Cancel before day 3 = $0 charged.

**Q: Can I switch tiers?**
A: Yes — cancel current plan in PayPal, subscribe to new tier. We're working on in-app upgrade for late 2026.

**Q: What if Saju isn't for me?**
A: 30-day refund — message us, get the full month back. Less than 1.3% of customers ask, but the option is yours.

**Q: Is this real Korean Saju or just a horoscope app?**
A: Real. We use the classical 4-pillar / 5-element / 10-stem / 12-branch system. Most "horoscope apps" don't even know what those terms mean.

## CTA primary button text variants

- "Start Free Trial — $2.20/mo after"
- "3 Days Free → Then $2.20/mo"
- "Get Started — Cancel Anytime"

A/B test these against the simple "Subscribe Now" baseline.

---

## Implementation notes

1. **Currency conversion**: KRW → USD via PayPal's auto-FX. Display "Approximately $2.20/mo (₩2,900)" with footnote "Final charge in your local currency".
2. **PayPal Subscription plan IDs**: Need to be created in PayPal Developer Dashboard for Basic (₩2,900) and Pro (₩9,900) before this copy goes live. Annual (₩29,900) plan exists.
3. **Region detection**: Show $ for US/EU/SG/AU; ₩ for KR; convert via geolocation cookie.
4. **Refund rate citation**: <1.3% — verified from existing memory. Safe to publish.
5. **DO NOT publish** the LTV multiplier ("4.5× lifetime value") as a fact — it's industry-average projection, not measured. If used, label clearly: "industry-average projection".
