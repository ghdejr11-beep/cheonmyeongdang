"""pinterest_pins — 4-Language Global 12-pin batch (2026-05-07).

Adds 4 lang x 3 pins = 12 pins extending queue from 53 -> 65.

Topics (per lang):
  1) 2026 Horse Year personality (red horse / hinoeuma / 红马)
  2) 4 Pillars 직업운 / career / shokuun / 事業運
  3) 십신 (10 gods) overview
  4) 12운성 (12 life stages) overview
  -> we pick 3 of these 4 topics x 4 langs = 12 pins (drop "12 stages" to keep balance with sokwa/직업운/horse).

Per-language slugs / topics:
  ko: 2026말띠성격, 사주직업운, 십신소개
  en: 2026 horse personality, four-pillars career, ten gods overview
  ja: 2026丙午性格, 四柱職業運, 十神概要
  zh: 2026紅馬性格, 四柱事業運, 十神簡介

Output: queue/{slug}.png + queue.json appended.
"""
import os, sys, json, urllib.request, urllib.parse, urllib.error, datetime, subprocess, time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
QUEUE_DIR = ROOT / "queue"
QUEUE_DIR.mkdir(exist_ok=True)
QUEUE_JSON = ROOT / "queue.json"
LOG = ROOT / "logs" / f"4lang12_v2_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


FONTS = {
    "ko": "C\\:/Windows/Fonts/malgunbd.ttf",
    "en": "C\\:/Windows/Fonts/arialbd.ttf",
    "ja": "C\\:/Windows/Fonts/YuGothB.ttc",
    "zh": "C\\:/Windows/Fonts/msyhbd.ttc",
}

BASE = "https://cheonmyeongdang.vercel.app"

PINS = [
    # ========== KO (3) ==========
    {
        "lang": "ko",
        "slug": "ko-2026-horse-year-personality-saju",
        "headline": "2026 말띠 성격\n사주로 풀다",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, stylized korean ink-brush red horse galloping "
            "across hanji parchment with soft cherry blossom petals, gold leaf accents, "
            "deep crimson and cream palette, traditional minhwa folk painting, premium "
            "magazine editorial cover layout"
        ),
        "url_path": "/",
        "campaign": "ko_2026_horse_personality",
        "description": (
            "2026 빨간 말띠의 해, 말띠로 태어난 사람의 진짜 성격은? 천간지지 사주로 "
            "풀어보면 자유로운 영혼·뜨거운 직진력·강한 독립심이 보입니다. 본인 "
            "사주와 결합한 무료 분석.\n\n"
            "#말띠성격 #2026말띠 #사주성격 #한국전통 #천명당"
        ),
    },
    {
        "lang": "ko",
        "slug": "ko-saju-career-fortune-job",
        "headline": "사주로 푸는\n직업운 가이드",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, traditional korean ink-brush calligraphy "
            "spelling four pillars on hanji paper next to compass and abacus, gold and "
            "jade green palette, soft candle light, premium magazine editorial cover"
        ),
        "url_path": "/",
        "campaign": "ko_saju_career",
        "description": (
            "사주로 보는 나의 직업운 — 사업 vs 직장, 창의직 vs 안정직, 솔로워크 "
            "vs 팀워크. 일간(日干) 오행과 십신 분포로 본인에게 맞는 진로를 "
            "AI가 무료 분석.\n\n"
            "#사주직업운 #직장운 #창업운 #진로 #천명당"
        ),
    },
    {
        "lang": "ko",
        "slug": "ko-ten-gods-sipsin-introduction",
        "headline": "십신(十神)\n사주의 핵심",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, ten korean ten-gods kanji characters arranged "
            "in circular mandala on hanji paper, gold ink calligraphy, jade and crimson accents, "
            "soft lantern lighting, editorial magazine cover layout"
        ),
        "url_path": "/",
        "campaign": "ko_sipsin_intro",
        "description": (
            "십신(十神)은 사주의 핵심 해석 도구. 비견·겁재·식신·상관·정재·편재·"
            "정관·편관·정인·편인 — 10가지 신(神)이 부모·재물·배우자·자녀·"
            "직업운까지 다 풀어줍니다. 초보자 가이드.\n\n"
            "#십신 #사주해석 #명리학 #사주공부 #천명당"
        ),
    },
    # ========== EN (3) ==========
    {
        "lang": "en",
        "slug": "en-2026-horse-year-personality",
        "headline": "2026 Horse Year\nPersonality",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, stylized korean ink-brush red horse galloping "
            "across hanji parchment with cherry blossom petals, gold leaf accents, deep "
            "crimson and cream palette, traditional minhwa folk painting, editorial cover"
        ),
        "url_path": "/en/korean-zodiac-2026-year-of-red-horse.html",
        "campaign": "en_2026_horse_personality",
        "description": (
            "Born in the Year of the Horse? 2026 is the Year of the Red Fire Horse — "
            "a once-in-60-years cycle. Your traits in Korean Saju: free spirit, fiery "
            "forward drive, strong independence. Free birth-chart breakdown inside.\n\n"
            "#KoreanZodiac #YearOfTheHorse #Saju #2026Horoscope #BirthChart"
        ),
    },
    {
        "lang": "en",
        "slug": "en-four-pillars-career-fortune",
        "headline": "4 Pillars Career\nFortune Guide",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, korean ink-brush four-pillar calligraphy "
            "on hanji paper next to compass and abacus, gold and jade green palette, "
            "soft candle light, premium magazine editorial cover layout"
        ),
        "url_path": "/en/four-pillars-of-destiny.html",
        "campaign": "en_career_fortune",
        "description": (
            "What does your Korean Saju say about your career? Day-stem element + ten "
            "gods reveal whether you thrive as entrepreneur, employee, creator or "
            "operator. Free AI-powered career-fit analysis based on your birth chart.\n\n"
            "#SajuCareer #KoreanAstrology #CareerFortune #FourPillars #BirthChart"
        ),
    },
    {
        "lang": "en",
        "slug": "en-ten-gods-overview-saju",
        "headline": "10 Gods (十神)\nSaju Decoder",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, ten chinese characters (ten-gods kanji) "
            "arranged in circular mandala on hanji paper, gold ink calligraphy, jade and "
            "crimson accents, soft lantern lighting, editorial magazine cover layout"
        ),
        "url_path": "/en/ten-heavenly-stems.html",
        "campaign": "en_ten_gods_overview",
        "description": (
            "The 10 Gods (十神) are Korean Saju's master decoder — Friend, Rival, Output, "
            "Creator, Direct Wealth, Indirect Wealth, Direct Officer, Indirect Officer, "
            "Direct Resource, Indirect Resource. Each governs family, money, partner, "
            "career and reputation. Beginner guide.\n\n"
            "#TenGods #Saju #KoreanAstrology #BaZi #FourPillars"
        ),
    },
    # ========== JA (3) ==========
    {
        "lang": "ja",
        "slug": "ja-2026-hinoeuma-personality",
        "headline": "2026 丙午生まれ\n性格分析",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, stylized japanese-korean fusion red horse "
            "galloping on washi paper with cherry blossom petals, gold and crimson palette, "
            "sumi-e ink brush style, lunar new year, premium editorial magazine cover"
        ),
        "url_path": "/ja/korean-zodiac-2026-uma.html",
        "campaign": "ja_hinoeuma_personality",
        "description": (
            "2026年は丙午(ひのえうま)、60年に1度の赤い火の馬の年。午年生まれの "
            "本当の性格は?四柱推命で読み解く自由奔放・情熱・独立心。本人の命式と "
            "組み合わせた無料診断付き。\n\n"
            "#丙午 #午年性格 #四柱推命 #2026運勢 #韓国占い"
        ),
    },
    {
        "lang": "ja",
        "slug": "ja-four-pillars-career-shokuun",
        "headline": "四柱八字で読む\n職業運ガイド",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, sumi-e ink brush four-pillar calligraphy "
            "on washi paper with compass and abacus, cherry blossom petals, gold and jade "
            "green palette, soft candle light, premium editorial cover layout"
        ),
        "url_path": "/ja/four-pillars-jukai.html",
        "campaign": "ja_career_shokuun",
        "description": (
            "あなたの職業運、四柱推命でわかる。日干の五行と十神の配置で、起業家タイプ・ "
            "サラリーマンタイプ・クリエイタータイプ・職人タイプを判定。本人の命式に "
            "基づくAI無料分析。\n\n"
            "#職業運 #四柱推命 #命式 #転職占い #韓国占い"
        ),
    },
    {
        "lang": "ja",
        "slug": "ja-ten-gods-jisshin-overview",
        "headline": "十神(十神)\n四柱の核心",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, ten kanji characters of ten-gods arranged "
            "in circular mandala on washi paper with cherry blossoms, gold ink calligraphy, "
            "jade and crimson accents, soft lantern lighting, editorial cover layout"
        ),
        "url_path": "/ja/jukkan-junishi.html",
        "campaign": "ja_jisshin_overview",
        "description": (
            "十神(じっしん)は四柱推命の最重要解読ツール。比肩・劫財・食神・傷官・"
            "正財・偏財・正官・偏官・印綬・偏印 — 10種の神が親・財運・配偶者・子供・"
            "仕事運を全部教えてくれる。初心者向け完全ガイド。\n\n"
            "#十神 #四柱推命 #命式読み方 #占い入門 #韓国占い"
        ),
    },
    # ========== ZH (3) ==========
    {
        "lang": "zh",
        "slug": "zh-2026-red-horse-personality",
        "headline": "2026 紅馬年生\n性格分析",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, stylized chinese ink-brush red horse "
            "galloping on red rice paper with gold lanterns and plum blossoms, gold and "
            "crimson festive palette, lunar new year, premium editorial magazine cover"
        ),
        "url_path": "/zh/zodiac-2026-red-horse.html",
        "campaign": "zh_red_horse_personality",
        "description": (
            "2026年丙午紅火馬年,60年一遇的紅馬年。午年生人的真實性格?八字命理 "
            "解讀:自由奔放、烈火直前、獨立性極強。配合本人命盤的免費深度分析。\n\n"
            "#紅馬年 #午年性格 #八字命理 #2026運勢 #韓國八字"
        ),
    },
    {
        "lang": "zh",
        "slug": "zh-four-pillars-career-fortune-shiyeyun",
        "headline": "四柱命理解\n你的事業運",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, chinese ink-brush four-pillar calligraphy "
            "on red rice paper next to compass and abacus, gold lanterns, gold and crimson "
            "festive palette, premium editorial magazine cover layout"
        ),
        "url_path": "/zh/four-pillars-mingli.html",
        "campaign": "zh_career_shiyeyun",
        "description": (
            "你的事業運,八字命理一覽無遺。日干五行+十神配置告訴你適合創業 vs 上班、 "
            "創意型 vs 穩定型、單打獨鬥 vs 團隊合作。基於命盤的AI免費深度解讀。\n\n"
            "#事業運 #八字命理 #職場運 #創業命盤 #韓國八字"
        ),
    },
    {
        "lang": "zh",
        "slug": "zh-ten-gods-shishen-introduction",
        "headline": "十神(十神)\n八字命理核心",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, ten chinese characters of ten-gods arranged "
            "in circular mandala on red rice paper with gold lanterns and plum blossoms, "
            "gold ink calligraphy, festive crimson palette, premium editorial cover layout"
        ),
        "url_path": "/zh/ten-stems-twelve-branches.html",
        "campaign": "zh_shishen_intro",
        "description": (
            "十神(十神)是八字命理最核心的解盤工具。比肩・劫財・食神・傷官・正財・"
            "偏財・正官・七殺・正印・偏印 — 10種神煞主管父母、財運、配偶、子女、 "
            "事業運。新手入門完整指南。\n\n"
            "#十神 #八字命理 #命盤解讀 #算命入門 #韓國八字"
        ),
    },
]


def fetch_image(prompt, slug, max_retries=4):
    seed = abs(hash(slug)) % 100000
    url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
        f"?width=1000&height=1500&seed={seed}&nologo=true&model=flux"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    backoff = 10
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries:
                log(f"  429 rate-limited, sleeping {backoff}s ({attempt}/{max_retries})")
                time.sleep(backoff)
                backoff = min(backoff * 2, 90)
                continue
            raise
        except Exception as e:
            if attempt < max_retries:
                log(f"  fetch error {type(e).__name__}, sleeping {backoff}s ({attempt}/{max_retries})")
                time.sleep(backoff)
                backoff = min(backoff * 2, 90)
                continue
            raise


def overlay_text(in_path, headline, lang, out_path):
    font = FONTS.get(lang, FONTS["en"])
    lines = headline.split("\n")
    if len(lines) == 1:
        lines.append("")

    def esc(s):
        return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace('"', "")[:60]

    line1 = esc(lines[0])
    line2 = esc(lines[1])

    fsize = 78 if lang == "en" else 90
    y2 = 120 + fsize + 30

    drawtext1 = (
        f"drawtext=fontfile='{font}':"
        f"text='{line1}':"
        f"fontcolor=white:fontsize={fsize}:"
        f"box=1:boxcolor=black@0.78:boxborderw=22:"
        f"x=(w-text_w)/2:y=120"
    )
    drawtext2 = ""
    if line2:
        drawtext2 = (
            f",drawtext=fontfile='{font}':"
            f"text='{line2}':"
            f"fontcolor=white:fontsize={fsize}:"
            f"box=1:boxcolor=black@0.78:boxborderw=22:"
            f"x=(w-text_w)/2:y={y2}"
        )

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(in_path),
            "-vf", f"scale=1000:1500,{drawtext1}{drawtext2}",
            "-frames:v", "1", str(out_path),
        ],
        check=True, capture_output=True,
    )


def utm_url(url_path, lang, campaign):
    full = BASE + url_path
    sep = "&" if "?" in full else "?"
    return (
        f"{full}{sep}utm_source=pinterest"
        f"&utm_medium=social&utm_campaign={lang}_{campaign}"
    )


def main():
    if QUEUE_JSON.exists():
        q = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
    else:
        q = {"made": []}
    if "made" not in q:
        q["made"] = []

    existing_slugs = {x.get("slug") for x in q["made"]}
    added = 0
    failed = []
    by_lang = {"ko": 0, "en": 0, "ja": 0, "zh": 0}

    # 5-min budget guard: leave early if we exceed ~280s wall time
    start = time.time()
    BUDGET_SEC = 280

    for pin in PINS:
        if time.time() - start > BUDGET_SEC:
            log(f"BUDGET HIT after {int(time.time()-start)}s, deferring remaining {len(PINS)-PINS.index(pin)} pins")
            break
        slug = pin["slug"]
        lang = pin["lang"]
        if slug in existing_slugs:
            log(f"SKIP {slug} (already in queue)")
            continue
        log(f"=== [{lang}] {slug} ===")

        png_path = QUEUE_DIR / f"{slug}.png"
        raw_path = QUEUE_DIR / f"{slug}_raw.jpg"

        try:
            log(f"  fetching pollinations...")
            raw = fetch_image(pin["image_prompt"], slug)
            raw_path.write_bytes(raw)
            log(f"  raw -> {raw_path.name} ({len(raw)//1024}KB)")
        except Exception as e:
            log(f"  POLLINATIONS FAIL: {type(e).__name__}: {str(e)[:120]}")
            failed.append(slug)
            continue

        try:
            overlay_text(raw_path, pin["headline"], lang, png_path)
            log(f"  overlay -> {png_path.name} ({png_path.stat().st_size//1024}KB)")
        except subprocess.CalledProcessError as e:
            log(f"  ffmpeg FAIL, using raw: {(e.stderr or b'')[:140]!r}")
            png_path = raw_path

        full_url = utm_url(pin["url_path"], lang, pin["campaign"])
        full_desc = pin["description"] + f"\n\n{chr(128073)} {full_url}"

        q["made"].append({
            "slug": slug,
            "kw": f"{lang}_{pin['campaign']}",
            "title": pin["headline"].replace("\n", " "),
            "made_at": datetime.datetime.now().isoformat(),
            "image_path": str(png_path),
            "description": full_desc,
            "destination_url": full_url,
            "lang": lang,
            "source": "4lang_12_v2_2026_05_07",
            "status": "queued",
        })
        added += 1
        by_lang[lang] += 1
        QUEUE_JSON.write_text(
            json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        time.sleep(4)

    elapsed = int(time.time() - start)
    log(f"DONE in {elapsed}s: added {added} pins (ko={by_lang['ko']} en={by_lang['en']} ja={by_lang['ja']} zh={by_lang['zh']})")
    log(f"      failed {len(failed)}, queue total = {len(q['made'])}")
    if failed:
        log(f"FAILED slugs: {failed}")
    return added


if __name__ == "__main__":
    main()
