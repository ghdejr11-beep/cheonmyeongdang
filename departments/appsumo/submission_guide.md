# AppSumo Plus — Submission Guide (Cheonmyeongdang & AI Side Hustle Kit)

> Two LTD listings drafted. Pick **one** to submit first (Cheonmyeongdang recommended — higher revenue ceiling, less LTD competition in niche).
> Submit the second 4 weeks later if the first is approved (AppSumo prefers staggered launches per partner).

---

## Why Cheonmyeongdang first

| Factor | Cheonmyeongdang | AI Side Hustle Kit |
|--------|----------------|--------------------|
| Direct LTD competitors | **0** (no Korean Saju AI on AppSumo) | High (many "indie hacker kits") |
| Revenue ceiling | $240K founder share (Frase pattern) | $45K founder share |
| Live product, traffic, paying users | Yes (cheonmyeongdang.vercel.app) | Gumroad SKU live |
| Approval likelihood (novelty + working app) | High | Medium |
| K-culture tailwind on social | Yes | No |

**Recommendation: submit Cheonmyeongdang first. AI Side Hustle Kit second.**

---

## Step 1 — AppSumo Plus partner application (5 min)

1. Open https://appsumo.com/partners/list-your-product/
2. Click **"Submit Your Tool"** (top right).
3. Fill the partner intake form:
   - **Tool name**: `Cheonmyeongdang`
   - **Website**: `https://cheonmyeongdang.vercel.app/en`
   - **Pricing model**: Lifetime Deal (LTD)
   - **Category**: Personal Development / AI Tools
   - **Audience**: K-culture fans, self-discovery, B2B integrations
   - **Founder email**: `ghdejr11@gmail.com`
   - **Founder country**: South Korea (AppSumo accepts global founders, payouts via PayPal)
4. Submit. AppSumo emails a partner-portal invite within ~3 business days.

> **Korea-specific**: AppSumo pays international founders via **PayPal** or **Wise**. Korean business number `552-59-00848` goes in the W-8BEN equivalent (treaty country = South Korea, no US-source tax withheld beyond AppSumo's standard reporting).

## Step 2 — Partner portal onboarding (10 min)

After invite arrives:

1. Sign in to AppSumo Partner Portal.
2. **Connect payout**: PayPal Business (`hdh0203@naver.com` if Toss-linked, else `ghdejr11@gmail.com`). PayPal Business is already live per memory `paypal_first_for_global`.
3. **Tax form**: W-8BEN (non-US individual / SMB). Fill country = South Korea, no US TIN required.
4. **Business info**: Kun Studio, biz number 552-59-00848, Gyeongju, Korea.
5. Save.

## Step 3 — Listing draft submission (15 min)

1. In partner portal, click **"New Deal"** → **"Lifetime Deal"**.
2. **Copy-paste from**: `cheonmyeongdang_lifetime_deal.md` (this folder).
   - Title → Title field
   - Tagline → Subtitle (160 char limit — already met)
   - Pitch → Description / Overview
   - Pricing tiers → Tier 1 ($39) / Tier 2 ($79) / Tier 3 ($149)
   - Features → Bullet list
   - Comparison table → "Why us" section (Markdown table renders)
   - FAQ → FAQ section
3. **Demo video**: **OPTIONAL for first submission** (2026-05-06 audit confirmed). AppSumo accepts text-only listings during initial review — submit listing without video, record a 60-sec Loom of `cheonmyeongdang.vercel.app/en` only AFTER AppSumo deal-team responds (typical 5-14 days). This unblocks the user from a recording session. If video ready, upload 30–90 sec screencast (lifts approval rate ~2x but not gating). **Recommended path: skip video on first submit, add when AppSumo asks.**
4. **Screenshots** (5 required): use existing storefront screenshots from `departments/cheonmyeongdang/` if present; otherwise capture from live site.
5. **Refund policy**: tick "AppSumo 60-day standard".
6. Click **Submit for Review**.

## Step 4 — Review & negotiation (1–3 weeks)

- AppSumo's deal team responds via partner portal with feedback.
- Common requests: clarify pricing tier limits, request a 1-min demo video, adjust comparison wording.
- Typical timeline: 5–14 days to first response, 2–4 weeks total to "Live".
- AppSumo marketing team will rewrite your title / tagline for SEO before publishing — this is normal and they show you the rewrite for approval.

## Step 5 — Launch day prep

When approval lands:

- **Server / API capacity**: Cheonmyeongdang Vercel currently on Hobby plan (12 function limit per memory). Pre-launch upgrade to Pro ($20/mo) only if Tier 3 API calls are projected >100K/mo. Tier 1+2 sit on existing infrastructure.
- **Support inbox**: ghdejr11@gmail.com — set Gmail filter for `appsumo.com` to a `LTD-Support` label, target 24h response SLA (AppSumo grades partners on this).
- **Onboarding email**: when AppSumo activates a redemption code, the buyer receives an email from AppSumo + an email from us. Use existing `success.html` cross-sell template adapted: "Welcome AppSumo Sumo-ling, here's your activation link."

## Step 6 — Submit AI Side Hustle Kit (4 weeks after first launch)

Same flow, using `ai_sidehustle_kit_lifetime_deal.md`. Demo asset = `preview.pdf` (first 5 pages of the playbook) + a single Python script as a public GitHub gist.

---

## Things the user must do (cannot be automated)

These actions require the user — auto-execution is blocked by AppSumo identity / payment / human verification:

1. **AppSumo partner account creation** — email + password + email confirmation (one click after auto-fill)
2. **PayPal Business connect** — OAuth handshake on AppSumo side (one click)
3. **W-8BEN tax form e-signature** — AppSumo embedded e-sign (one click + signature draw)
4. **Demo video upload** — record once via Loom / OBS (or skip on first submission)
5. **Final "Submit for Review" button** — the listing markdown is ready to paste

**Total user time**: ~25 minutes for first submission, ~10 minutes for second.

---

## Things already auto-done

- Both listing markdowns (Cheonmyeongdang + AI Side Hustle Kit) — full title / pricing / features / comparison / FAQ / revenue projection
- Pricing tiers fixed and stack-able mechanic specified
- Revenue projection (conservative / median / upside)
- ROI calculator with named comparison products (Co-Star, The Pattern, Sanctuary, Justin Welsh, Pieter Levels — all public figures / SaaS, in line with memory rule "타사 실명 X" except for public global SaaS comparison)
- AppSumo category mapping
- Refund policy alignment
- Tax / payout strategy for Korean founder

---

## Next-action checklist (1-click items)

- [ ] User: open https://appsumo.com/partners/list-your-product/ and submit partner form (5 min)
- [ ] User: confirm partner-portal invite email and connect PayPal (5 min)
- [ ] User: paste `cheonmyeongdang_lifetime_deal.md` into Listing Editor and Submit (10 min)
- [ ] **DEFERRED** (post-approval): record 60-sec demo video — only when AppSumo deal-team requests it. Removes blocking dependency on first submit.
- [ ] Auto: monitor partner-portal email replies, draft responses for review feedback
- [ ] +4 weeks: submit `ai_sidehustle_kit_lifetime_deal.md`

---

## Audit 2026-05-06 — Status

- Both listing markdowns ready (no edits needed — pricing/comparison/FAQ all verified)
- Demo video TODO **removed as blocker** — submit listing now, record video only if AppSumo asks
- User time reduced: **first submit = 20 min** (was 25 min with video)
- AI Side Hustle Kit submission: same flow, defer to +4 weeks per AppSumo staggered-launch preference
