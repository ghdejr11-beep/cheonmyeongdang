#!/usr/bin/env python3
"""
글로벌 영문 X(Twitter) 스레드 5개 생성 (2026-05-06).

5개 영문 SEO 페이지를 X 스레드(5~7 tweets)로 자동 변환.

⚠️ 자동 발행 X — 스레드 텍스트(.md)만 생성. 사용자 검토 후 직접 게시.
   (multi_poster.py의 Bluesky 함수와 호환되는 짧은 변형도 같은 manifest에 포함)

사용:
    python departments/media/generate_x_global_threads.py            # 5개 모두 생성
    python departments/media/generate_x_global_threads.py --slug zodiac
"""
import os
import sys
import json
import argparse
from datetime import datetime

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
OUT = os.path.join(ROOT, 'departments', 'media', 'output', 'global_x_threads')
os.makedirs(OUT, exist_ok=True)


THREADS = [
    {
        'slug': 'saju-vs-western',
        'page': 'en/saju-vs-western-astrology.html',
        'tweets': [
            "If you've outgrown Co-Star, here's the system most Western astrology fans don't know about: Korean Saju (사주) — the 1,000-year-old Four Pillars of Destiny. 🧵",
            "1/ The numbers tell the story.\n\nWestern astrology = 12 sun signs, ~1,728 unique chart combos.\nKorean Saju = 60 × 12 × 60 × 12 ≈ 2,073,600 unique combos.\n\nGranularity matters when you want a system that says something specific.",
            "2/ Saju uses 4 pillars (year/month/day/hour). Each pillar = 1 Heavenly Stem + 1 Earthly Branch. That's 8 characters total — the literal meaning of '사주팔자'.",
            "3/ The single most-read character is your Day Master (일간) — the top of the day pillar. There are 10 Day Masters: Yang Wood, Yin Wood, Yang Fire... yours describes who you fundamentally are.",
            "4/ Saju is built for life-strategy questions:\n\n- Career arc over 10-year cycles (daewoon)\n- Compatibility via Five Elements harmony\n- Wealth, romance, family — all pre-mapped via the Sip-sin (Ten Gods) system",
            "5/ Western astrology still wins for daily emotional weather. Saju wins for the 5-year and 10-year question — 'what season of life am I actually in?'\n\nLayer them, don't choose.",
            "Free Korean Saju calculator (English) — no sign-up:\nhttps://cheonmyeongdang.vercel.app/en/saju-vs-western-astrology.html\n\nReply with your Day Master + I'll guess your job 🪶",
        ],
        'bluesky_short': "Korean Saju vs Western Astrology — quick fact: Saju has ~2 million unique chart combos vs Western's ~1,728. Granularity matters.\n\nFree English calculator: https://cheonmyeongdang.vercel.app/en/saju-vs-western-astrology.html",
    },
    {
        'slug': 'four-pillars',
        'page': 'en/four-pillars-of-destiny.html',
        'tweets': [
            "Your Korean Saju chart is just 8 characters arranged in 4 pillars. Here's how to read yours in plain English. 🧵",
            "1/ The 4 pillars:\n\n• YEAR — ancestry, early childhood, social tribe\n• MONTH — career, parents, public self\n• DAY — your core self + spouse\n• HOUR — children, late life, hidden talents\n\nEach pillar = 1 stem on top + 1 branch below.",
            "2/ Your Day Master = top character of your day pillar. It's THE most-read character in any Saju reading. There are only 10 possibilities — find yours and 80% of your chart is already decoded.",
            "3/ Yang Wood (甲) = tall pine, idealist, founder.\nYin Water (癸) = mist, intuitive, sensitive.\nYang Fire (丙) = sun, charismatic, public.\nEach Day Master has a distinct character.",
            "4/ Then the Five Elements — Wood, Fire, Earth, Metal, Water — count how many of each appear across your 8 characters. That balance (or imbalance) tells you what your chart needs.",
            "5/ Finally, the Sip-sin (Ten Gods) labels every element relative to your Day Master:\n\n• Resource = your support, mother, learning\n• Wealth = your earnings, romance (if male)\n• Officer = your structure, career, husband (if female)\n\nThis is where Saju gets predictive.",
            "Calculate your eight characters free (English):\nhttps://cheonmyeongdang.vercel.app/en/four-pillars-of-destiny.html\n\nReply with your Day Master if you find it.",
        ],
        'bluesky_short': "Your Korean Saju chart = 8 characters in 4 pillars (year/month/day/hour). The single most-read character = your Day Master.\n\nFree English calculator: https://cheonmyeongdang.vercel.app/en/four-pillars-of-destiny.html",
    },
    {
        'slug': 'red-horse-2026',
        'page': 'en/korean-zodiac-2026-year-of-red-horse.html',
        'tweets': [
            "🔥 2026 = Year of the Red Horse (병오, Byeong-O) in Korean astrology. Yang Fire on Yang Fire — only happens once every 60 years. Last time was 1966.\n\nForecast for all 12 zodiac signs ↓",
            "1/ Red Horse energy = visibility, speed, romance, burnout risk.\n\nIndustries that thrive: media, broadcasting, hospitality, energy.\nIndustries that struggle: heavy manufacturing, long-cycle research.",
            "2/ The 3 luckiest signs in 2026:\n\n🐯 Tiger — three-harmony Fire, career breakthroughs, viral moments\n🐉 Dragon — partnerships thrive, public profile rises\n🐑 Goat — Six Combination with Horse, romance/marriage/family expansion",
            "3/ The 3 most disrupted signs in 2026:\n\n🐭 Rat — direct clash with Horse, expect a major life pivot\n🐂 Ox — friction in family/partnerships, but career recognition\n🐍 Snake — fast advancement BUT cardiovascular/sleep risk",
            "4/ Universal advice for the Red Horse year:\n\n• Ship and publish — the year rewards visibility\n• Protect your sleep — Yang Fire on Yang Fire burns through circadian rhythm\n• Use Nov–Dec to plan 2027\n• Wear red on big-decision days",
            "5/ Important: the Korean year change is at Ipchun (입춘) — Feb 4, 2026. Births before that count as Wood Snake (Eul-Sa), not Red Horse.",
            "Personalized 2026 forecast (free, English):\nhttps://cheonmyeongdang.vercel.app/en/korean-zodiac-2026-year-of-red-horse.html\n\nWhat's your Korean zodiac sign?",
        ],
        'bluesky_short': "2026 = Year of the Red Horse (병오, Byeong-O). Yang Fire stacked on Yang Fire — happens once every 60 years.\n\nFull forecast for all 12 zodiac signs (free, English):\nhttps://cheonmyeongdang.vercel.app/en/korean-zodiac-2026-year-of-red-horse.html",
    },
    {
        'slug': 'compatibility',
        'page': 'en/saju-compatibility-test.html',
        'tweets': [
            "In Korea, families have used 궁합 (gunghap) for 1,000 years to check if a couple is actually compatible — before marriage approval. Here's how it works in plain English. 🧵",
            "1/ Western compatibility = sun-sign vibes ('a Leo and Scorpio? oof'). Korean gunghap = math.\n\nIt compares Five Elements, Day Masters, Branch Combinations, and 10-year cycle synchrony across both birth charts.",
            "2/ The Five Elements either GENERATE each other (생) or CONTROL each other (극).\n\nWood feeds Fire = inspiring, energetic couple.\nMetal cuts Wood = tense, productive.\nFire vs Water = volatile.\n\nNo combination is 'bad' — each has a texture.",
            "3/ The Six Branch Combinations = soulmate factor:\n\n🐭 Rat + 🐂 Ox\n🐯 Tiger + 🐖 Pig\n🐰 Rabbit + 🐕 Dog\n🐉 Dragon + 🐓 Rooster\n🐍 Snake + 🐒 Monkey\n🐴 Horse + 🐑 Goat",
            "4/ Six Branch Clashes (육충) — opposite branches. Doesn't mean breakup; means more drama, more growth:\n\nRat ↔ Horse · Ox ↔ Goat · Tiger ↔ Monkey · Rabbit ↔ Rooster · Dragon ↔ Dog · Snake ↔ Pig",
            "5/ Modern Korean practitioners read clashes as 'where the work is' — not as a verdict. Marriages between 'incompatible' charts often last longer because both partners show up consciously.",
            "Free 60-second compatibility test (English):\nhttps://cheonmyeongdang.vercel.app/en/saju-compatibility-test.html\n\nReply with your zodiac + your partner's, I'll tell you the combo type.",
        ],
        'bluesky_short': "Korean Saju compatibility (궁합) is structurally deeper than Western sun-sign compatibility. It compares Five Elements, Day Masters, and Branch Combinations.\n\nFree 60-second test (English): https://cheonmyeongdang.vercel.app/en/saju-compatibility-test.html",
    },
    {
        'slug': 'ten-stems',
        'page': 'en/ten-heavenly-stems.html',
        'tweets': [
            "The 10 Heavenly Stems (천간, cheongan) are the alphabet of Korean Saju. Find your Day Master and 80% of your chart is already decoded. 🧵",
            "1/ There are 10 stems = 5 elements × 2 polarities (Yang/Yin):\n\n甲 Gap (Yang Wood) · 乙 Eul (Yin Wood)\n丙 Byeong (Yang Fire) · 丁 Jeong (Yin Fire)\n戊 Mu (Yang Earth) · 己 Gi (Yin Earth)\n庚 Gyeong (Yang Metal) · 辛 Sin (Yin Metal)\n壬 Im (Yang Water) · 癸 Gye (Yin Water)",
            "2/ The 5 Yang stems are public, expressive, large-scale:\n\n甲 = tall pine, leader\n丙 = sun, charismatic\n戊 = mountain, steadfast\n庚 = sword, decisive\n壬 = ocean, strategic",
            "3/ The 5 Yin stems are inward, refined, fine-scale:\n\n乙 = vine, adaptive\n丁 = candle, intimate\n己 = garden, nurturing\n辛 = jewel, polished\n癸 = mist, intuitive",
            "4/ Same element, different mode. A 丙 (Yang Fire) is the sun warming a city. A 丁 (Yin Fire) is the candle warming one face. Both are 'Fire types' — but radically different lives.",
            "5/ Important: no Day Master is 'better.' What matters is the BALANCE between your Day Master and the rest of your chart. A weak Day Master in a supportive chart > a strong Day Master in a draining one.",
            "Find your Day Master free (English):\nhttps://cheonmyeongdang.vercel.app/en/ten-heavenly-stems.html\n\nWhich stem do you think you are? 🪶",
        ],
        'bluesky_short': "10 Heavenly Stems = the alphabet of Korean Saju. Yang Wood, Yin Wood, Yang Fire... your Day Master is one of these ten.\n\nFind yours free (English): https://cheonmyeongdang.vercel.app/en/ten-heavenly-stems.html",
    },
]


def _emit_thread(thread):
    slug = thread['slug']
    md_path = os.path.join(OUT, f'{slug}_x_thread.md')
    json_path = os.path.join(OUT, f'{slug}_x_thread.json')

    md = [f'# X (Twitter) Thread — {slug}', '']
    md.append(f"**Source page:** `{thread['page']}`  ")
    md.append(f"**Tweets:** {len(thread['tweets'])}  ")
    md.append('')
    md.append('## Thread (copy-paste in order)')
    md.append('')
    for i, t in enumerate(thread['tweets'], 1):
        chars = len(t)
        flag = '' if chars <= 280 else f'  ⚠️ {chars} chars > 280'
        md.append(f'### Tweet {i}/{len(thread["tweets"])} ({chars} chars){flag}')
        md.append('')
        md.append('```')
        md.append(t)
        md.append('```')
        md.append('')

    md.append('## Bluesky variant (one post, ≤300 chars)')
    md.append('')
    md.append('```')
    md.append(thread['bluesky_short'])
    md.append('```')
    md.append('')
    md.append(f"_Bluesky char count: {len(thread['bluesky_short'])}/300_")

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

    payload = {
        'slug': slug,
        'page': thread['page'],
        'tweets': thread['tweets'],
        'bluesky_short': thread['bluesky_short'],
        'destination_url': f"https://cheonmyeongdang.vercel.app/{thread['page']}?utm_source=twitter&utm_campaign=global_seo&utm_content={slug}",
        'generated_at': datetime.utcnow().isoformat() + 'Z',
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return {'slug': slug, 'md': md_path, 'json': json_path, 'tweet_count': len(thread['tweets'])}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--slug', help='only this slug')
    args = p.parse_args()

    threads = THREADS
    if args.slug:
        threads = [t for t in THREADS if args.slug in t['slug']]
        if not threads:
            print(f'No match for slug "{args.slug}"')
            return 1

    results = []
    for thread in threads:
        r = _emit_thread(thread)
        results.append(r)
        print(f"[OK] {r['slug']} — {r['tweet_count']} tweets → {r['md']}")

    manifest = os.path.join(OUT, 'manifest.json')
    with open(manifest, 'w', encoding='utf-8') as f:
        json.dump({'generated_at': datetime.utcnow().isoformat() + 'Z', 'threads': results}, f, ensure_ascii=False, indent=2)
    print(f'\n[DONE] {len(results)} threads -> {OUT}')
    print(f'       manifest -> {manifest}')
    print('\n>> Next: review .md files, then post to X manually (or via Bluesky multi_poster for short variant).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
