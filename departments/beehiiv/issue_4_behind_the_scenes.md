---
title: "AI + 5,000-Year Tradition: How We Built Cheonmyeongdang"
slug: behind-the-scenes
seo_title: "Korean Saju Weekly #4: Behind the Scenes of Cheonmyeongdang's AI Saju Engine"
seo_description: "How a solo Korean indie team paired ancient Saju logic with modern AI to make Korean astrology accessible worldwide. Engineering and design notes."
publish_day: "Tuesday"
publish_date: "2026-06-10"
issue_number: 4
word_count_target: 1150
utm_campaign: "behind-the-scenes"
referral_code: "sumo-ling"
---

# AI + 5,000-Year Tradition

> *"The hardest engineering problem wasn't the AI. It was making 5,000-year-old logic legible without flattening it."*

Welcome to **Korean Saju Weekly Issue #4**. Today's issue is different.

A lot of you have asked: *"How is this actually built? Is it AI making things up? Or is there real Saju logic in there?"*

Fair questions. Astrology + AI is exactly the kind of pairing that earns skepticism — and should. So today I'm going to walk you through **how Cheonmyeongdang actually works**, what's deterministic, what's AI, and where each handoff happens.

You'll come out of this issue with a clearer mental model of what the tool is and isn't. That clarity is what Saju has always been about: showing you the structure, then letting you choose.

---

## The Two-Layer Architecture

Cheonmyeongdang is built as **two layers**:

1. **The Saju Engine** — deterministic, rule-based. Calculates your 8 characters from birth data and runs traditional Korean Saju logic on them. Zero AI in this layer.
2. **The Translation Layer** — AI-powered. Takes the engine's output and renders it into clean, readable English (or Japanese, or Chinese), respecting cultural framing.

This separation matters. The engine produces the same chart for the same birth data, every time, with the same logic Korean Saju masters have used for centuries. The AI doesn't decide what's in your chart. It only decides how to *explain* it.

---

## Layer 1: The Engine (Deterministic)

The engine does what a traditional Korean Saju master does mentally — but reproducibly.

### Step 1: Calendar Conversion

Your Gregorian birth date gets converted to the Korean **lunisolar calendar**, accounting for solar terms (절기). The day-pillar calculation uses the **60-day stem-branch cycle** running continuously since astronomical reckoning began.

### Step 2: 8-Character Generation

From the converted date and time, the engine generates your **four pillars × two characters = 8 characters**:

- Year Pillar (Stem + Branch)
- Month Pillar (Stem + Branch)
- Day Pillar (Stem + Branch — **your Day Master is the stem here**)
- Hour Pillar (Stem + Branch)

This is pure arithmetic against historical tables. No interpretation yet.

### Step 3: Ten Gods Analysis (십신)

The engine compares each of your 8 characters to your Day Master and assigns its **Ten Gods role**: peer, output, wealth, authority, knowledge — split by polarity. This produces your relationship-and-resource map.

### Step 4: Twelve Life-Stages (십이운성)

Each character is assigned one of 12 life-stages relative to your Day Master, telling you the strength-state of each part of your chart.

### Step 5: Spirit Killers (신살)

The engine checks your 8 characters against the **22 named Sinsal patterns** (Peach Blossom, Travel Horse, Heavenly Noble, etc.) and flags which ones are active.

### Step 6: 10-Year Luck Cycles (대운)

Calculates your Daewoon sequence — your 10-year luck windows from birth onward, projected through age 100.

All of this is **pure logic**. No AI, no randomness, no "vibes." If you ran the same birth data through three traditional Korean Saju masters, you'd get the same engine output.

---

## Layer 2: The AI Translation

This is where AI enters — and where the careful work happens.

The engine output is technically dense: 8 characters in Hanja, ten gods labeled in classical Korean, life-stages with 1,000-year-old terminology. A traditional Saju reading by a Korean master takes 30+ minutes of verbal explanation.

The AI's job is to render this dense output into **clear, accurate, culturally-respectful English**.

### What the AI Does

- Translates Hanja terms into intelligible English (e.g., 정관 → "Direct Officer / legitimate authority")
- Sequences the explanation in a reader-friendly order
- Adjusts metaphors to be culturally accessible without flattening
- Generates the prose around the deterministic facts

### What the AI Does NOT Do

- It does not invent characters that aren't in your chart
- It does not generate Daewoon cycles
- It does not pick your Sinsal patterns
- It does not predict outcomes the engine didn't surface

This is the rule we held: **the AI never modifies the chart, only explains it.**

---

## Why This Matters

A lot of "AI astrology" tools generate readings end-to-end with a language model. They sound plausible, but the underlying analysis is whatever the model fabricated. Two runs can give different "charts."

That breaks the entire premise of Saju, which is that **your chart is your chart** — fixed at birth, read consistently across centuries.

By separating the deterministic engine from the AI translation, we get the best of both:

- **Consistency**: same chart, same engine output, every time
- **Accessibility**: clean English explanations that respect the source material
- **Integrity**: a Korean Saju master could verify the engine output line by line

This is how we got Korean traditional Saju practitioners to vouch for the tool. The engine is the same logic they use. The AI just makes it readable to someone who didn't grow up with the vocabulary.

---

## What's Next (And What We Won't Build)

A lot of tools in this space chase engagement metrics — daily push notifications, gamified streaks, personalized horoscopes that change every hour. We're explicitly not doing that.

Saju is a **structural reading tool**. Your chart doesn't change daily. The macro tide does, slowly. So the right product cadence is monthly, not daily.

What we're building next:

- **Compatibility readings** in English (Day Master to Day Master, Ten Gods overlap)
- **Career fit module** that maps your chart to industry archetypes
- **Annual forecast PDFs** for Premium subscribers
- **Multi-language expansion** (already in Japanese and Chinese — adding Spanish next)

What we're explicitly not building:

- Daily push notifications
- "Lucky number of the day"
- AI chatbots that pretend to be a Saju master
- Anything that obscures the engine vs translation distinction

If we keep that line clear, this stays useful instead of becoming another vibes app.

---

## Try the Engine Yourself

The free version of Cheonmyeongdang shows you the engine output (translated) for free, no signup, in 60 seconds.

**[Get My Free Saju Reading →](https://cheonmyeongdang.com/saju?utm_source=beehiiv&utm_medium=newsletter&utm_campaign=behind-the-scenes)**

If you want the full Premium reading — with all 22 Sinsal patterns, 30-year Daewoon map, and quarterly forecast PDFs — refer a friend with code **`sumo-ling`** and you both unlock a free month.

**[Get your referral link →](https://cheonmyeongdang.com/refer?code=sumo-ling)**

---

## Coming in Issue #5 (June 24)

I'll do one of the most-requested topics: a public-figure chart read. Specifically, I'll walk through what Korean Saju says about **BTS RM's birth chart** — using only publicly known birth data, framed as cultural commentary rather than personal claim. It'll be a fun way to see the engine and translation work end to end on someone you already have intuition about.

Until then,
The Korean Saju Weekly Team

*Forwarded? [Subscribe here](https://cheonmyeongdang.beehiiv.com/subscribe).*
