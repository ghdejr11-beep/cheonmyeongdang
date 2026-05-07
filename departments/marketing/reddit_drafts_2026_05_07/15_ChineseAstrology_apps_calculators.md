# Reddit r/ChineseAstrology #15

**Subreddit:** r/ChineseAstrology
**Post type:** Tools / calculators discussion
**Send window:** 2026-05-08 ~ 2026-05-12

---

## Title

For people who use Bazi / Saju calculators — what's your shortlist for 2026? Sharing my testing notes on multilingual options

## Body (402 words)

Annual update on Bazi / Saju calculator quality. I've tested a bunch over the past 6 months because (1) I want to verify my own chart in multiple engines and (2) I have non-Chinese-reading family members who want to use the same tool.

Posting my shortlist criteria + observations in case it helps anyone else's tooling stack.

**My evaluation criteria**

1. **Math correctness** — does the engine produce the *deterministic* correct 8 characters and Daewoon table for known test cases?
2. **Daewoon direction** — correctly handles 陽男陰女 (forward) vs 陰男陽女 (backward) for the luck cycle, and starting age based on distance to next solar term
3. **Time-zone / longitude correction** — does it use **真太陽時 (true solar time)** or just standard time? Big accuracy difference if you were born in a non-Beijing-time location
4. **Multi-language output** — Chinese / Korean / Japanese / English, ideally all from the same engine so cross-checking is trivial
5. **Privacy** — does it store / sell birth data?

**Observations from my testing**

- Chinese-language calculators tend to be **best at the math** but often lack non-Chinese output and have iffy ad-tech / data-handling
- Korean Saju-style calculators tend to **explain the 神煞 better** because the Korean tradition kept those alive — but some are weaker on classical 用神 detection
- English-only calculators often **mishandle solar time and the 五虎遁 month-stem rule** — easy to spot when the test case shows wrong month pillar
- Multilingual calculators are still rare — there are maybe 3 or 4 that get all 4 (CN/KR/JP/EN) right, including the lunar/solar conversion edge cases

**A test case to validate any calculator**

Try birth: **1985-02-04 06:30 Seoul Korea**. The correct chart should be:
- Year pillar: 乙丑 (因為立春前)... [reader can verify]
- Month: depends on solar term boundary
- Day: 庚午
- Hour: 己卯

If a calculator gives you a different Year pillar for this date, it's mishandling the **立春 boundary** (Korean New Year date is BEFORE 立春), which is a common bug.

**My current 2026 shortlist** (deliberately not naming specific products to avoid the spam vibe — happy to share in comments if asked)

- Two engines pass all my correctness tests + offer 4-language output + don't appear to monetize stored data
- Both are free for the basic chart
- One has a deeper Daewoon analysis layer

What are people here using as their daily-driver calculator? Curious for recommendations.
