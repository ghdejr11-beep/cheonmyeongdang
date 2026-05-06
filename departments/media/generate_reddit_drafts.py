#!/usr/bin/env python3
"""
Reddit 드래프트 5건 생성 — 글로벌 영문 SEO 페이지 기반 (2026-05-06).

타겟 서브레딧:
  - r/AskAstrologers (~115K)
  - r/asianastrology (~3K, niche)
  - r/Korea (~1.4M)
  - r/kpop (~500K)
  - r/Astrology (~700K)

⚠️ 자동 발행 X — 이전 reddit_drafts_2026_05.md 패턴 따라 사용자 직접 발송.
   각 draft는 (1) 80% 가치 / 20% 링크 (2) 신규 계정 자기링크 차단 정책 회피 위해
   첫 댓글에 링크 (parent post는 self-link 없음).

사용:
    python departments/media/generate_reddit_drafts.py
"""
import os
import sys
import json
import argparse
from datetime import datetime

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
OUT = os.path.join(ROOT, 'departments', 'media', 'output', 'global_reddit_drafts')
os.makedirs(OUT, exist_ok=True)


DRAFTS = [
    {
        'slug': 'askastrologers-saju-vs-western',
        'subreddit': 'r/AskAstrologers',
        'flair_suggestion': 'Discussion',
        'title': "For those who've explored both: how does Korean Saju (4 pillars) actually compare to Western chart reading in your experience?",
        'body': """I'm a working astrologer-curious person who's been digging into Korean Saju (사주팔자, four pillars of destiny) for the past year and the granularity has me re-thinking my Western chart approach.

A few things I've noticed but want to sanity-check with this community:

1. **Combination count.** Western natal chart with sun/moon/rising = ~1,728 distinct combinations. Korean Saju with year/month/day/hour stem+branch combos = ~2 million. Is the Western system getting the same depth from aspects/houses that I'm just under-using?

2. **Day Master vs Sun sign.** Saju's Day Master (one of 10 Heavenly Stems) functions roughly like a "core self" indicator but is much more specific than a 30-day sun sign. Does anyone here use a similar single-anchor approach in Western practice?

3. **Time horizon.** Saju has built-in 10-year cycles (daewoon) — your reading literally tells you what season of life you're in for the next decade. The closest Western equivalent I see is progressed Sun/Moon, but it doesn't seem as central. Curious what others use.

4. **Compatibility math.** Saju gunghap uses Five Elements harmony (Wood feeds Fire, Metal cuts Wood, etc.). Western synastry uses aspects and house overlays. Anyone find one more practically actionable than the other?

Not trying to claim one is "better" — both are pattern languages, both are valuable. Just curious how practitioners here relate to the comparison.

(Happy to share the calculator I've been using if anyone wants to compare a chart side-by-side. It's a free Korean Saju tool with English translations.)""",
        'first_comment_link': 'The free calculator I mentioned (no sign-up): https://cheonmyeongdang.vercel.app/en/saju-vs-western-astrology.html',
        'best_post_time_utc': 'Tue/Wed 14:00 UTC',
    },
    {
        'slug': 'asianastrology-four-pillars',
        'subreddit': 'r/asianastrology',
        'flair_suggestion': 'BaZi/Saju',
        'title': "Plain-English breakdown of the Four Pillars of Destiny — would love feedback from this community",
        'body': """I've been writing English-language explainers of Korean Saju (Four Pillars / 사주팔자) for an audience that's familiar with Western astrology but new to BaZi/Saju, and I'd love a sanity check from people who actually study this seriously.

My four-pillar shorthand:

- **YEAR pillar** = ancestry, generational karma, social tribe (also gives the popular "Korean zodiac animal")
- **MONTH pillar** = career, parents, public-facing self (and the foundation for Day Master strength calculations)
- **DAY pillar** = your core self (top stem = Day Master) + spouse (bottom branch)
- **HOUR pillar** = children, late-life wisdom, hidden talents

Then for each Day Master I've written a one-paragraph plain-English profile (Yang Wood = "tall pine, leader, idealist", Yin Water = "mist, intuitive, sensitive", etc.).

Two things I'd love feedback on:

1. **Korean vs Chinese emphasis.** I've been leaning into the Sip-sin (Ten Gods) framework because that's how Korean readers approach charts day-to-day. Is that the right emphasis for an English audience, or should I introduce Lu/Yi (LingQi) etc. earlier?

2. **The "early jashi" convention.** I'm using the modern Korean default (early jashi = next day's pillar). I know Chinese BaZi readers often differ. How do you handle this when explaining to beginners?

For anyone curious, here's where I've collected the explainer so far. Open to corrections — this is a community-improving project, not a marketing post:
https://cheonmyeongdang.vercel.app/en/four-pillars-of-destiny.html""",
        'first_comment_link': '(no separate first-comment needed — link is in body for niche/expert sub)',
        'best_post_time_utc': 'Mon/Thu 12:00 UTC',
    },
    {
        'slug': 'korea-saju-english-tool',
        'subreddit': 'r/Korea',
        'flair_suggestion': 'Culture',
        'title': "Made a free Korean Saju (사주) site for non-Korean speakers — would love an accuracy check from anyone who grew up with 명리",
        'body': """Hi r/Korea — I'm a 1985-born Korean who built a free Saju site primarily for international visitors and overseas Koreans who can't easily read Korean-language Saju content.

Features:
- Free Four Pillars calculation with English explanations
- Compatibility (gunghap / 궁합) test
- 2026 forecast (Year of the Red Horse, 병오)
- Day Master + Five Elements summary

I'd really value an accuracy check from people who grew up around Saju culture. Specifically:

- Does the early-jashi handling match what your family practiced?
- Does the gunghap explanation capture the nuance, or is it too "Westernized"?
- Are there cultural concepts I'm flattening unnecessarily for English readers?

Also genuinely curious how often r/Korea readers actually use Saju in 2026 — is it still common to check 궁합 before introducing partners to family, or has that mostly faded?

Site (no login, no email gate): https://cheonmyeongdang.vercel.app/en/

감사합니다 — appreciate any honest feedback (positive or sharp)!""",
        'first_comment_link': '(no separate first-comment needed — site link is part of the genuine ask)',
        'best_post_time_utc': 'Wed/Sat 02:00 UTC (10:00 KST)',
    },
    {
        'slug': 'kpop-zodiac-2026',
        'subreddit': 'r/kpop',
        'flair_suggestion': 'Discussion',
        'title': "2026 is the Year of the Red Horse (병오) in Korean astrology — and it's a big deal for K-pop. Here's why.",
        'body': """If you've been hearing your Korean friends mention 병오년 (Byeong-O year) and weren't sure what the fuss is about: 2026 is the Year of the Red Horse in Korean Saju, which only comes around once every 60 years (last one was 1966).

Why does this matter for K-pop and Korean culture watchers?

**The energy of 병오 = Yang Fire stacked on Yang Fire.** That translates to:

- **Visibility / fast career arcs.** Industries that depend on attention (media, broadcasting, entertainment) historically peak. 1966 saw the Beatles' global peak and a wave of new media; 2026 is being widely talked about in Korea as a year for breakout artists.
- **Burnout risk.** Yang Fire on Yang Fire is intense. Don't be surprised if hiatus / health-break announcements cluster this year.
- **Romance announcements / public relationships.** The Horse pillar amplifies public-facing emotion. Privacy walls tend to crack.

**Which Korean zodiac signs ride the wave best?**

- 🐯 Tiger (1986, 1998, 2010 idols) — three-harmony Fire combination, breakout year
- 🐉 Dragon (1988, 2000, 2012 idols) — partnership year, brand/label deals
- 🐑 Goat (1991, 2003 idols) — Six Combination with Horse, romance/family-related news

**Most disrupted:** 🐭 Rat-year idols (1996, 2008) — direct branch clash, expect job/contract pivots.

This is just the surface. Full forecast for all 12 signs (free, English): https://cheonmyeongdang.vercel.app/en/korean-zodiac-2026-year-of-red-horse.html

Curious — what year were your bias born? 👀""",
        'first_comment_link': '(link already in body — pop-culture audience tolerates it)',
        'best_post_time_utc': 'Fri/Sat 16:00 UTC',
    },
    {
        'slug': 'astrology-day-master',
        'subreddit': 'r/Astrology',
        'flair_suggestion': 'Educational',
        'title': "If your sun sign feels too vague, try this: the 10 Heavenly Stems from Korean Saju act like 10 'core self' archetypes",
        'body': """A lot of beginners say "I'm a Sagittarius" but it doesn't quite click. Korean Saju has a single-anchor character called the **Day Master (일간)** that's narrower than a sun sign — and many people find it lands harder.

There are exactly 10 possible Day Masters, organized as 5 elements × 2 polarities:

- 甲 (Gap) — Yang Wood. Tall pine. Leader, idealist, builder.
- 乙 (Eul) — Yin Wood. Vine. Adaptive, persistent, collaborative.
- 丙 (Byeong) — Yang Fire. Sun. Charismatic, public, generous.
- 丁 (Jeong) — Yin Fire. Candle. Focused, intimate, mentoring.
- 戊 (Mu) — Yang Earth. Mountain. Steadfast, dignified, slow-moving.
- 己 (Gi) — Yin Earth. Garden. Nurturing, detail-oriented, anxious-giver.
- 庚 (Gyeong) — Yang Metal. Sword. Direct, justice-driven, principled.
- 辛 (Sin) — Yin Metal. Jewel. Polished, articulate, image-conscious.
- 壬 (Im) — Yang Water. Ocean. Strategic, systems-thinker, uncontainable.
- 癸 (Gye) — Yin Water. Mist. Intuitive, perceptive, soft-power.

The fun thing is that "same element, different polarity" produces wildly different lives. A Yang Fire (Byeong) is the sun warming a city. A Yin Fire (Jeong) is a candle warming one face. Both are "Fire types" — but their actual existence is barely related.

You find your Day Master from your full birth date and hour (it's the top character of your day pillar in the Four Pillars chart).

For Western astrology folks: think of it as a more granular sun-sign substitute that's hyper-specific because it's tied to your literal birth day, not your 30-day birth window.

Free calculator that does this in English: https://cheonmyeongdang.vercel.app/en/ten-heavenly-stems.html

Reply with which stem you think you are based on the descriptions — curious if r/Astrology folks land closer to their Day Master or their Sun sign in self-image.""",
        'first_comment_link': '(link in body)',
        'best_post_time_utc': 'Sun/Mon 14:00 UTC',
    },
]


def emit(d):
    slug = d['slug']
    md_path = os.path.join(OUT, f'{slug}.md')
    body_chars = len(d['body'])
    md = [
        f'# Reddit Draft — {slug}',
        '',
        f'**Subreddit:** {d["subreddit"]}  ',
        f'**Suggested flair:** {d["flair_suggestion"]}  ',
        f'**Best post window (UTC):** {d["best_post_time_utc"]}  ',
        f'**Body length:** {body_chars} chars  ',
        '',
        '## Title',
        '',
        '```',
        d['title'],
        '```',
        '',
        '## Body (paste into Reddit text box)',
        '',
        d['body'],
        '',
        '## First-comment link strategy',
        '',
        d['first_comment_link'],
        '',
        '## Reminders',
        '- Self-promo ratio: 80% value / 20% link.',
        "- New account karma < 50? Skip the body link, post the comment-link only after 1 community-positive reply.",
        '- Subreddit rules vary — check sticky/wiki before posting (especially r/Korea, r/Astrology have evolving self-link rules).',
        '- After posting, monitor 30 min for mod-removal; if removed, message mods politely.',
    ]
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    return {'slug': slug, 'md': md_path, 'subreddit': d['subreddit'], 'body_chars': body_chars}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--slug', help='only this slug')
    args = p.parse_args()

    drafts = DRAFTS
    if args.slug:
        drafts = [d for d in DRAFTS if args.slug in d['slug']]
        if not drafts:
            print(f'No match for slug "{args.slug}"')
            return 1

    results = []
    for d in drafts:
        r = emit(d)
        results.append(r)
        print(f"[OK] {r['subreddit']} — {r['slug']} → {r['md']}")

    manifest = os.path.join(OUT, 'manifest.json')
    with open(manifest, 'w', encoding='utf-8') as f:
        json.dump({'generated_at': datetime.utcnow().isoformat() + 'Z', 'drafts': results}, f, ensure_ascii=False, indent=2)
    print(f'\n[DONE] {len(results)} Reddit drafts -> {OUT}')
    print(f'       manifest -> {manifest}')
    print('\n>> Next: review .md files, then submit to Reddit manually (one per day max, different subs).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
