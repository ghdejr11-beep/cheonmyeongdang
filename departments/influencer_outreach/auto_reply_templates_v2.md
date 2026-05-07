# Influencer Auto-Reply Templates v2 (English)

**Version:** 2.0  
**Created:** 2026-05-07  
**Purpose:** Pattern-classified auto-reply drafts for KunStudio / cheonmyeongdang influencer outreach replies. Triggered by `monitor_influencer_replies.py` keyword classification.

Patterns covered:

1. **interested** — Open to collaboration, asks for next steps
2. **declined** — Politely declines or not a fit
3. **partnership_ask** — Counter-proposes a paid/long-term arrangement
4. **question** — Has clarifying questions before deciding

---

## 1. Pattern: `interested`

**Trigger keywords (case-insensitive):**
`interested`, `i'd love to`, `let's do it`, `sounds great`, `count me in`, `happy to collaborate`, `let's chat`, `dm me`, `send me details`, `excited`, `looks fun`, `i'm in`

**Reply template:**

```
Subject: Re: {original_subject} — Quick next steps

Hi {first_name},

Amazing — really happy you're up for this! Here's the simplest path forward so we don't burn time:

1. Free reading link (your unique reader code, no signup, ~3 min):
   https://cheonmyeongdang.vercel.app/?ref={code}

2. If it resonates, here's a 15-second hook + 1 swipeable carousel template you can repurpose:
   https://cheonmyeongdang.vercel.app/creator-kit

3. Affiliate share — 30% recurring on every paid plan from your link, $0.50 per free reading.
   Stripe payout monthly, $20 min. Sign up here (60 sec):
   https://cheonmyeongdang.vercel.app/affiliate?ref={code}

No usage rights claim — your post stays yours forever.
No exclusivity. No content approval needed.

If you'd rather just get a flat fee instead of revenue share, reply with your usual rate for one feed post + one story and I'll send a quick PO.

Looking forward to it,
Deokhoon (KunStudio founder)
hdh@kunstudio.kr · @kunstudio
```

---

## 2. Pattern: `declined`

**Trigger keywords:**
`not a fit`, `not the right fit`, `pass`, `decline`, `not interested`, `not at this time`, `unfortunately`, `currently full`, `booked`, `appreciate but`, `not for me`, `unsubscribe`, `please remove`

**Reply template (graceful, no pushback, leave door open):**

```
Subject: Re: {original_subject}

Hi {first_name},

Totally understand — thank you for taking the time to reply, that alone puts you above 95% of the inbox.

I'll take you off the active outreach list. If anything changes, or if you ever want a free reading just for personal curiosity (no obligation, no follow-up), this link is always open:
https://cheonmyeongdang.vercel.app/?ref=friend

Wishing your channel a great quarter.

— Deokhoon
KunStudio · cheonmyeongdang.vercel.app
```

**Auto-action:** Add sender to `do_not_contact.json` so future outreach scripts skip them.

---

## 3. Pattern: `partnership_ask`

**Trigger keywords:**
`rate card`, `media kit`, `rates`, `pricing`, `budget`, `paid partnership`, `flat fee`, `usage rights`, `whitelisting`, `exclusive`, `monthly retainer`, `long-term`, `negotiate`, `agency`, `manager`, `representation`

**Reply template (open the door, anchor with affiliate, ask for kit):**

```
Subject: Re: {original_subject} — Happy to work out paid terms

Hi {first_name},

Thanks for being upfront about rates — saves us both a week of dancing around it.

Here's how I usually structure these so it's fair both ways:

**Option A — Performance hybrid (my preference)**
- $150 flat for 1 feed post + 1 story (covers production)
- + 30% recurring affiliate on every paid plan from your link (lifetime per customer)
  Most partners with 50k+ engaged followers clear $400-$1,200/mo on the affiliate side alone after 60 days.

**Option B — Flat only**
- I'm comfortable up to $500 for 1 post + 1 story + 14-day usage rights for paid social.
- Whitelisting +$200 (30 days). Exclusivity +50%.
- Larger packages (3-month retainer, multi-platform): happy to scope if you send your media kit.

Could you send over:
1. Your one-sheet / rate card (or just a link)
2. Engaged-follower count + average reach last 30 days
3. Audience country split (we monetize best in US/JP/TW/SG)

I'll come back within 24 hours with a concrete number, contract template, and Stripe invoice.

— Deokhoon
KunStudio · hdh@kunstudio.kr
```

**Auto-action:** Flag thread for human review before final commit (>$100 spend).

---

## 4. Pattern: `question`

**Trigger keywords:**
`question`, `clarify`, `more info`, `tell me more`, `how does it work`, `what is`, `explain`, `details`, `who are you`, `what's the catch`, `is this real`, `legit`, `?`

**Reply template (answer the obvious 5 questions upfront so they don't have to ask):**

```
Subject: Re: {original_subject} — All your questions, answered

Hi {first_name},

Great questions — here's the full picture so you can decide in 60 seconds:

**1. What is it?**
Cheonmyeongdang ("Hall of Heavenly Mandate") is a Korean Saju (사주, traditional birth-chart astrology) reading tool. Free 3-min reading, paid plans for monthly fortune + AI Q&A chat. Live in 4 languages (KO/EN/JA/ZH). Built solo by me — no VC, no scammy upsell.

**2. Who's behind it?**
KunStudio, sole proprietorship registered in Korea (사업자등록번호 552-59-00848). Founder: Hong Deokhoon, building since April 2026. Real name, real address, real bank account on the receipts.

**3. Is the content authentic or just AI slop?**
Saju engine is a real ephemeris-based 사주 calculator (천간/지지/오행/십성), not LLM hallucination. The interpretation copy was reviewed by a Korean 명리학자 (named credit removed at her request). AI is only used for personalized chat layer on top.

**4. What do you actually want from me?**
One honest review/post — hate it, love it, or meh, all fine. No script, no required hashtags, no approval rights. If you do post, you get a 30% lifetime affiliate cut on any reader who pays through your link. That's it.

**5. What's the catch?**
None on your side. On mine: I'm betting that authentic creators talking about Korean culture will outperform paid ads in JP/TW/EN markets. So far the data agrees.

Try the free reading here, it'll explain itself faster than I can:
https://cheonmyeongdang.vercel.app/?ref={code}

Anything else, just hit reply — I read every email myself.

— Deokhoon
KunStudio
```

---

## Classifier rules (order of precedence)

When multiple patterns match, apply in this order:

1. `declined` — if any decline keyword present, never mark as `interested`
2. `partnership_ask` — paid/rate keywords beat generic "interested"
3. `question` — only if no commitment keywords AND has `?` or info-seeking phrase
4. `interested` — fallback positive
5. `unknown` — none of the above → flag for human review, no auto-reply

## Send rules

- **Never auto-send.** Templates are saved as draft in Gmail with label `auto_reply_draft_v2`.
- Human reviews + clicks Send (~10 sec per draft).
- After send, monitor records `replied_at` in `outreach_log.json` so we don't double-reply.
- For `partnership_ask` over $100 implied spend, draft is created but flagged in Telegram for explicit owner approval.

## Variables to substitute

- `{first_name}` — extracted from From header (heuristic: first word, capitalized)
- `{original_subject}` — original Subject without "Re:" prefix (de-duplicated)
- `{code}` — partner code generated from sender domain (8-char hash)

## Versioning

- v1 (2026-04): Single generic reply for any inbound. ~12% reply→action rate.
- v2 (2026-05-07): 4-pattern classifier + drafts. Target: 30%+ reply→action rate, zero "wrong tone" misfires.
