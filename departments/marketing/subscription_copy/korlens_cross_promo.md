# KORLENS → Cheonmyeongdang Cross-promo

## Current state (verified)
KORLENS layout footer already cross-links to Cheonmyeongdang at:
- `app/layout.tsx` lines 208-234 — 4 blog post links (wedding etiquette, business etiquette, soju culture, Korean tax)
- `app/layout.tsx` line 253 — Saju Diary EN ($7.99)
- `app/layout.tsx` line 257 — Saju Intro Guide
- `app/layout.tsx` line 314 — Free Korean Saju EN
- `app/layout.tsx` line 323 — `/tiers` (subscription tiers page on cheonmyeongdang)

## Proposed addition — KORLENS results page CTA

**Location**: `app/places/[contentId]/page.tsx` (or wherever a foreign visitor sees their "result" — restaurant, festival, hidden-pick result page)

**Component to add** (snippet, drop into the bottom of the result page below the main content):

```tsx
{/* Cross-promo: foreign traveler → Saju curiosity */}
<aside className="mt-8 p-4 rounded-xl border border-amber-300/40 bg-gradient-to-br from-amber-50/50 to-rose-50/30 dark:from-amber-950/20 dark:to-rose-950/15">
  <div className="text-xs font-semibold text-amber-700 dark:text-amber-400 tracking-wider mb-1">CURIOUS ABOUT KOREA?</div>
  <h3 className="font-bold text-zinc-900 dark:text-zinc-100 mb-1">Curious about Korean astrology? Get your Saju.</h3>
  <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-3">
    Korea's 1,000-year-old fortune system reads your birth date+hour into 4 pillars and 5 elements. Free reading takes 60 seconds — no signup.
  </p>
  <a
    href="https://cheonmyeongdang.vercel.app/en/?utm_source=korlens&utm_campaign=results_page_cta&utm_content=traveler_saju"
    target="_blank"
    rel="noopener noreferrer"
    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-sm font-semibold transition-colors"
  >
    🔮 Get My Free Saju →
  </a>
</aside>
```

## Implementation note
- This is a **draft proposal** for the KORLENS repo, not committed here.
- Owner of korlens repo decides whether to add it.
- If added, the UTM tagging (`utm_campaign=results_page_cta`) will let GA4 attribute Saju conversions back to KORLENS traffic.
- Expected lift: ~2-5% click-through on result pages (industry benchmark for contextual cross-product CTAs), but actually measure don't claim.

## Why it works
- KORLENS audience = foreign travelers / expats curious about Korean culture
- Saju is the deepest Korean cultural artifact most foreigners haven't met
- Free preview reduces friction to zero
- "60 seconds, no signup" lowers commitment threshold
