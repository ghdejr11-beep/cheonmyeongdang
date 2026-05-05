# B2B Lead Sourcing Guide — Saju Engine API

**Goal:** Fill `cold_emails_2026_05_05.json` placeholders (`{COMPANY_NAME}`, `{RECIPIENT_NAME}`, `{RECIPIENT_EMAIL}`) with real leads in under 60 minutes.

**Tools:**
- Apollo.io (free tier: 50 credits / month — enough for 50 verified emails)
- LinkedIn Sales Navigator (1-month free trial if you do not have one)
- Hunter.io (backup email verifier — free 25 / month)

---

## Sector A — Korean OTA / Travel (10 leads)

**Apollo / LinkedIn search filters:**
- Industry: `Travel & Leisure`, `Online Marketplace`
- Location: `South Korea`
- Company headcount: `50–1000`
- Keywords: `OTA`, `travel platform`, `tour`, `experience marketplace`
- Titles: `Head of Product`, `CTO`, `VP Engineering`, `Growth Lead`, `Partnerships`

**Sample target companies (publicly known Korean OTA / travel tech):**
1. MyRealTrip (마이리얼트립) — experience-based travel marketplace
2. Triple (트리플) — AI travel companion app
3. Yanolja (야놀자) — accommodation + leisure super-app
4. Interpark Tour (인터파크투어) — package travel
5. Modetour (모두투어) — travel agency with digital arm

**LinkedIn search URL pattern:**
```
linkedin.com/search/results/people/?keywords=Head%20of%20Product&geoUrn=%5B%22105149562%22%5D&industryUrn=%5B%2271%22%5D&company=<COMPANY>
```

---

## Sector B — Korean Game / Entertainment (10 leads)

**Apollo / LinkedIn search filters:**
- Industry: `Computer Games`, `Entertainment`
- Location: `South Korea`
- Headcount: `100+`
- Keywords: `mobile game`, `gacha`, `K-pop`, `entertainment`, `fan platform`
- Titles: `Product Manager`, `Game Designer`, `Live Ops Lead`, `Director of Content`

**Sample categories (search by category, not by named brand to keep emails clean):**
1. Mid-tier Korean mobile game studios (mid-core RPG, idle, life-sim)
2. K-pop fan platform startups
3. Webtoon publishers expanding to interactive content
4. Korean indie game collectives
5. Entertainment-tech holding companies (search "엔터테크" / "fan platform")

**Pitch angle:** Daily fortune mission, character compatibility match, lucky-color skin / cosmetic recommendation.

---

## Sector C — Matching / Dating Apps (10 leads, global)

**Apollo / LinkedIn search filters:**
- Industry: `Internet`, `Dating`
- Location: `United States`, `United Kingdom`, `Singapore`, `Indonesia`, `Vietnam`, `Japan`
- Headcount: `20–500`
- Keywords: `dating app`, `matchmaking`, `compatibility`, `K-pop fan`, `niche dating`
- Titles: `CEO`, `Founder`, `Head of Product`, `Growth`

**Sample sub-niches to target (avoid named brands in pitch — describe category):**
1. K-pop / K-drama fandom dating apps (English-speaking audience)
2. Astrology-first dating apps (already have zodiac — bolt-on Saju)
3. Asian-diaspora dating apps in US / UK / SEA
4. Compatibility-quiz lead-gen marketing apps
5. Niche community dating (Asian culture, language exchange)

**Search query example (Apollo):**
```
title contains "founder" OR "CEO" AND industry = "dating" AND keyword = "compatibility"
```

---

## Sector D — Global Astrology / Wellness Apps (10 leads)

**Apollo / LinkedIn search filters:**
- Industry: `Wellness`, `Consumer Software`, `Mobile App`
- Location: `United States`, `United Kingdom`, `Australia`, `Canada`
- Headcount: `10–500`
- Keywords: `astrology`, `horoscope`, `tarot`, `spiritual`, `mindfulness`
- Titles: `Founder`, `CEO`, `Head of Content`, `Product Lead`

**Sample reference apps (publicly listed in App Store top charts — known Astrology category):**
1. Co-Star (NYC) — birth-chart astrology
2. The Pattern (LA) — personality + astrology
3. Sanctuary (NYC) — live astrologer chat
4. Nebula — horoscope + tarot
5. Chani — astrology subscription app

**Pitch angle:** Korean Saju add-on white-label license — first mover for Korean module in Western astrology stack.

---

## Sector E — Department Store / Retail (10 leads)

**Apollo / LinkedIn search filters:**
- Industry: `Retail`, `Consumer Goods`, `Department Stores`
- Location: `South Korea`, `Japan`, `Singapore`, `Hong Kong`
- Headcount: `1000+`
- Keywords: `loyalty`, `marketing tech`, `personalization`, `seasonal campaign`
- Titles: `CMO`, `Head of Digital Marketing`, `Loyalty Lead`, `CRM Manager`

**Sample categories (use category descriptors in email, not brand names):**
1. Korean major department store groups (loyalty + push notification budgets)
2. Korean / Japanese duty-free chains (Chinese tourist segment)
3. K-beauty omnichannel retailers
4. Asian fashion mall operators
5. Cosmetic brand DTC apps with daily content sections

**Pitch angle:** "Lucky shopping day" daily push, sales-day Saju compatibility coupons, lucky-color outfit picks. Posteller already validated retail tie-ins as a viable category.

---

## Workflow

1. Open Apollo.io → log in (sign up free if needed)
2. For each sector, run filter combinations above → filter to verified emails only
3. Export 10 leads per sector to CSV (50 total)
4. Open `cold_emails_2026_05_05.json` in VS Code or Notion
5. Map sector tags → replace `{COMPANY_NAME}`, `{RECIPIENT_NAME}`, `{RECIPIENT_EMAIL}` per row
6. Save → review priority-high rows first
7. Run `python send_b2b_emails.py --confirm` after explicit user approval

**Time estimate:** 45–60 minutes for full 50-lead fill.

**Spam-safety note:** Apollo verified emails have <3 percent bounce rate. Send 10 per day across 5 days (already wired into `send_b2b_emails.py`) — Gmail caps unverified domain sends, so this stays under the radar.
