"""pinterest_pins — 4-Language Global 20-pin batch generator (2026-05-06).

Adds 4 language x 5 pins = 20 standalone Pinterest pins (1000x1500) on top of
the existing queue. Uses Pollinations Flux + ffmpeg drawtext overlay (CJK fonts).

Categories:
  KO. Korean (5)        -> cheonmyeongdang.vercel.app/  (with anchors)
  EN. English (5)       -> cheonmyeongdang.vercel.app/en/{seo-page}.html
  JA. Japanese (5)      -> cheonmyeongdang.vercel.app/ja/{seo-page}.html
  ZH. Traditional Chinese (5) -> cheonmyeongdang.vercel.app/zh/{seo-page}.html

Output: queue/{slug}.png + queue.json (appended to existing made[]).
Pollinations Flux (free, no API key). UTM tagged URLs per language.

Constraints:
  - No specific company/celebrity/IP names. Generalize ("K-pop", "Korean drama").
  - Per-language fonts:
      ko -> Malgun Gothic Bold  (C:/Windows/Fonts/malgunbd.ttf)
      en -> Arial Bold          (C:/Windows/Fonts/arialbd.ttf)
      ja -> Yu Gothic Bold      (C:/Windows/Fonts/YuGothB.ttc)
      zh -> Microsoft YaHei Bold(C:/Windows/Fonts/msyhbd.ttc)
"""
import os, sys, json, urllib.request, urllib.parse, urllib.error, datetime, subprocess, time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
QUEUE_DIR = ROOT / "queue"
QUEUE_DIR.mkdir(exist_ok=True)
QUEUE_JSON = ROOT / "queue.json"
LOG = ROOT / "logs" / f"4lang20_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# Pre-resolved relative font paths for ffmpeg drawtext (Windows-style escape)
FONTS = {
    "ko": "C\\:/Windows/Fonts/malgunbd.ttf",
    "en": "C\\:/Windows/Fonts/arialbd.ttf",
    "ja": "C\\:/Windows/Fonts/YuGothB.ttc",
    "zh": "C\\:/Windows/Fonts/msyhbd.ttc",
}

BASE = "https://cheonmyeongdang.vercel.app"

PINS = [
    # ========== KO. Korean (5) - main + anchors ==========
    {
        "lang": "ko",
        "slug": "ko-weekly-fortune-free-ai-saju",
        "headline": "이번 주 운세\n무료 AI 사주",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, traditional korean ink calligraphy on hanji paper, "
            "gold leaf accents, jade green and deep crimson palette, brass ink stone and brush, "
            "soft candle light, premium magazine editorial cover"
        ),
        "url_path": "/",
        "campaign": "ko_weekly_fortune",
        "description": (
            "이번 주 운세를 1분 만에 확인하세요. 천명당 AI 사주가 생년월일시만으로 "
            "올 한 주 재물운, 애정운, 건강운을 풀어드립니다. 1,000년 전통의 한국 사주 "
            "명리학을 AI가 현대 언어로 번역. 무료 운세 보기.\n\n"
            "#사주 #운세 #이번주운세 #한국전통 #천명당"
        ),
    },
    {
        "lang": "ko",
        "slug": "ko-husband-wife-saju-compatibility",
        "headline": "남편 아내\n사주 궁합",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, two stylized korean ink-brush dragons "
            "intertwined in romantic mandala on hanji paper, gold leaf and jade accents, "
            "dusty rose and cream palette, traditional minhwa folk art, editorial magazine layout"
        ),
        "url_path": "/#compatibility",
        "campaign": "ko_couple_compat",
        "description": (
            "남편과 아내의 사주 궁합, 진짜 잘 맞을까요? 천명당 AI가 두 사람의 천간지지 "
            "오행 균형을 분석해 결혼 궁합 점수를 0~100점으로 알려드립니다. 결혼 "
            "전후 모두 무료로 확인 가능.\n\n"
            "#사주궁합 #부부궁합 #결혼궁합 #사주 #천명당"
        ),
    },
    {
        "lang": "ko",
        "slug": "ko-dream-meaning-search",
        "headline": "꿈에서 본\n그것의 의미",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, ethereal misty korean traditional dream scene "
            "with floating moon, lotus flower and ink brush clouds on dark indigo silk, "
            "gold accents, mystical surreal painting, editorial magazine cover"
        ),
        "url_path": "/#dreams",
        "campaign": "ko_dream_search",
        "description": (
            "어젯밤 꾼 꿈, 무슨 의미일까요? 천명당 꿈해몽 데이터베이스에 350개 이상 "
            "키워드 등록. 이빨 빠지는 꿈, 시험 보는 꿈, 전남친 나오는 꿈까지 자연어로 "
            "검색해 길몽인지 흉몽인지 즉시 확인.\n\n"
            "#꿈해몽 #꿈풀이 #해몽 #한국전통 #천명당"
        ),
    },
    {
        "lang": "ko",
        "slug": "ko-2026-red-horse-year-fortune",
        "headline": "2026 빨간말의 해\n띠별 운세",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, stylized korean ink-brush red horse galloping "
            "across calendar 2026 on hanji parchment, gold and crimson palette, traditional "
            "minhwa folk painting, lunar new year theme, premium magazine editorial cover"
        ),
        "url_path": "/",
        "campaign": "ko_2026_redhorse",
        "description": (
            "2026 빨간 말띠의 해, 12간지별 한 해 운세. 쥐띠는 재물, 소띠는 건강, "
            "범띠는 직장, 토끼띠는 연애... 천명당 AI가 본인 사주와 결합해 띠별 "
            "월간 운세까지 무료 제공.\n\n"
            "#2026운세 #띠별운세 #말띠해 #신년운세 #천명당"
        ),
    },
    {
        "lang": "ko",
        "slug": "ko-kpop-idol-saju-style-analysis",
        "headline": "K-pop 스타\n사주 스타일",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, stylized vintage k-pop concert silhouette "
            "with stage lights, cherry blossom petals and saju chart overlay, neon pink "
            "and deep navy palette, premium editorial fanmag cover layout"
        ),
        "url_path": "/",
        "campaign": "ko_kpop_saju",
        "description": (
            "최애 아이돌의 사주는 어떤 모습? 한국 톱 K-pop 아티스트들의 생년월일을 "
            "사주 명식으로 풀어보면 무대 위 카리스마, 팀 케미, 솔로 운까지 다 보입니다. "
            "본인 사주와 궁합도 무료 비교.\n\n"
            "#K팝 #아이돌사주 #사주분석 #K팝팬 #천명당"
        ),
    },
    # ========== EN. English (5) ==========
    {
        "lang": "en",
        "slug": "en-saju-vs-western-astrology",
        "headline": "Korean Saju vs\nWestern Astrology",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, split composition korean saju ink chart "
            "with hanja calligraphy on left and western zodiac wheel on right on parchment, "
            "gold ink accents, deep navy and cream palette, editorial magazine cover"
        ),
        "url_path": "/en/saju-vs-western-astrology.html",
        "campaign": "en_saju_vs_western",
        "description": (
            "Korean Saju vs Western Astrology: what's the actual difference? Saju uses "
            "four pillars (year, month, day, hour) and a 60-year cycle of stems and "
            "branches. Western uses 12 sun signs in a 12-month cycle. Side-by-side guide "
            "with free birth chart calculator inside.\n\n"
            "#KoreanAstrology #Saju #Astrology #ZodiacSigns #BirthChart"
        ),
    },
    {
        "lang": "en",
        "slug": "en-four-pillars-of-destiny",
        "headline": "Four Pillars\nof Destiny",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, traditional korean saju chart with four "
            "vertical columns of hanja characters on aged hanji rice paper, ink brush "
            "calligraphy, deep red and gold accents, soft lantern lighting, editorial cover"
        ),
        "url_path": "/en/four-pillars-of-destiny.html",
        "campaign": "en_four_pillars",
        "description": (
            "Four Pillars of Destiny — the foundation of Korean Saju astrology. Your "
            "year, month, day and hour of birth each become a column of two hanja "
            "characters revealing one quarter of your life path. Total beginner walkthrough "
            "with free chart calculator.\n\n"
            "#FourPillars #Saju #KoreanAstrology #BaZi #BirthChart"
        ),
    },
    {
        "lang": "en",
        "slug": "en-2026-red-horse-zodiac",
        "headline": "2026: Year of\nthe Red Horse",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, stylized korean ink-brush red horse galloping "
            "across 2026 calendar on hanji parchment, gold and crimson palette, traditional "
            "minhwa folk painting style, lunar new year theme, magazine editorial cover"
        ),
        "url_path": "/en/korean-zodiac-2026-year-of-red-horse.html",
        "campaign": "en_2026_redhorse",
        "description": (
            "2026 is the Year of the Red Fire Horse in Korean zodiac — said to bring "
            "passion, bold change and big risks paying off. See how all 12 zodiac animals "
            "(rat, ox, tiger, rabbit, dragon, snake, horse, sheep, monkey, rooster, dog, "
            "pig) fare in 2026. Free monthly forecast.\n\n"
            "#KoreanZodiac #YearOfTheHorse #2026Horoscope #Saju #LunarNewYear"
        ),
    },
    {
        "lang": "en",
        "slug": "en-saju-compatibility-test-free",
        "headline": "Free Korean Saju\nCompatibility Test",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, two stylized korean ink-brush phoenixes "
            "intertwined over a saju chart on hanji paper, gold leaf and jade accents, "
            "dusty rose and cream palette, minhwa folk art, premium editorial cover"
        ),
        "url_path": "/en/saju-compatibility-test.html",
        "campaign": "en_saju_compat",
        "description": (
            "Free Korean Saju Compatibility Test. Enter two birthdates and find out if "
            "your stems-and-branches energy harmonizes or clashes. Used for 1,000 years "
            "to predict marriage, friendship and business partnerships in Korea. Takes "
            "60 seconds.\n\n"
            "#SajuCompatibility #KoreanAstrology #LoveCompatibility #Saju #Soulmate"
        ),
    },
    {
        "lang": "en",
        "slug": "en-ten-heavenly-stems-guide",
        "headline": "10 Heavenly Stems\nKorean Astrology",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, ten korean heavenly stem characters arranged "
            "in circular mandala on hanji paper, gold ink calligraphy, jade and crimson "
            "accents, soft candle light, editorial magazine layout"
        ),
        "url_path": "/en/ten-heavenly-stems.html",
        "campaign": "en_ten_stems",
        "description": (
            "10 Heavenly Stems (천간) — the core building blocks of Korean Saju. Each "
            "stem combines a yin/yang polarity with one of the five elements (Wood, Fire, "
            "Earth, Metal, Water) creating 10 unique energies. Beginner guide with chart.\n\n"
            "#HeavenlyStems #Saju #KoreanAstrology #FiveElements #FourPillars"
        ),
    },
    # ========== JA. Japanese (5) ==========
    {
        "lang": "ja",
        "slug": "ja-saju-vs-shichu-suimei",
        "headline": "韓国サジュ vs\n四柱推命",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, split composition korean saju chart left "
            "japanese shichu chart right on washi rice paper with cherry blossoms, soft "
            "pink and gold palette, sumi-e ink brush style, premium editorial cover"
        ),
        "url_path": "/ja/saju-vs-japanese-shichu-suimei.html",
        "campaign": "ja_saju_vs_shichu",
        "description": (
            "韓国サジュと日本の四柱推命、何が違う?どちらも年・月・日・時の四柱を使い、"
            "天干地支で運命を読む点では同じ祖先から派生した姉妹術ですが、解釈の流派と "
            "現代的な運用が異なります。並べて比較する完全ガイドと無料命式計算機。\n\n"
            "#四柱推命 #韓国占い #サジュ #命式 #占い"
        ),
    },
    {
        "lang": "ja",
        "slug": "ja-four-pillars-meishiki",
        "headline": "四柱八字\nあなたの命式",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, traditional korean saju chart with four "
            "vertical columns of kanji characters on washi rice paper with cherry blossom "
            "petals, sumi-e ink brush calligraphy, soft pink and gold palette, editorial cover"
        ),
        "url_path": "/ja/four-pillars-jukai.html",
        "campaign": "ja_four_pillars",
        "description": (
            "四柱八字(四柱推命の本場版)で読み解くあなたの命式。生まれた年月日時から "
            "8つの干支文字を並べ、五行のバランスで一生の運勢、性格、向いている職業まで "
            "一発で見えます。無料で命式を出してみる。\n\n"
            "#四柱八字 #命式 #四柱推命 #韓国占い #五行"
        ),
    },
    {
        "lang": "ja",
        "slug": "ja-2026-uma-year-zodiac",
        "headline": "2026 赤い馬の年\n干支運勢",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, stylized japanese-korean fusion red horse "
            "galloping across 2026 calendar on washi paper with cherry blossom petals, "
            "gold and crimson palette, sumi-e ink brush style, lunar new year, editorial cover"
        ),
        "url_path": "/ja/korean-zodiac-2026-uma.html",
        "campaign": "ja_2026_uma",
        "description": (
            "2026年は丙午(ひのえうま)、赤い火の馬の年。情熱と大胆な変化、リスクが "
            "報われる年と言われます。子・丑・寅・卯・辰・巳・午・未・申・酉・戌・亥 "
            "全12干支の月別運勢を無料公開。\n\n"
            "#2026運勢 #丙午 #干支 #韓国占い #新年"
        ),
    },
    {
        "lang": "ja",
        "slug": "ja-saju-aishou-test",
        "headline": "韓国式 相性占い\n無料",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, two stylized phoenixes intertwined over "
            "saju chart on washi paper with cherry blossom petals, gold leaf and jade "
            "accents, soft pink and cream palette, sumi-e ink brush, editorial cover"
        ),
        "url_path": "/ja/saju-aishou-test.html",
        "campaign": "ja_aishou_test",
        "description": (
            "韓国式相性占い、無料で60秒。二人の生年月日を入れるだけで天干地支の "
            "エネルギーが調和するか衝突するかを点数化。1,000年間、結婚・友情・"
            "仕事のパートナー選びに使われてきた本格派サジュ。\n\n"
            "#相性占い #韓国占い #サジュ #結婚相性 #恋愛"
        ),
    },
    {
        "lang": "ja",
        "slug": "ja-jukkan-junishi-basics",
        "headline": "十干十二支\n韓国占星術",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, ten heavenly stems and twelve earthly "
            "branches kanji arranged in circular mandala on washi paper with cherry "
            "blossoms, gold ink calligraphy, soft pink and crimson palette, editorial cover"
        ),
        "url_path": "/ja/jukkan-junishi.html",
        "campaign": "ja_jukkan_junishi",
        "description": (
            "十干十二支は韓国サジュ・四柱推命の基本。十干(甲乙丙丁戊己庚辛壬癸)は "
            "陰陽と五行を、十二支(子丑寅卯辰巳午未申酉戌亥)は12の動物と時間を "
            "表します。初心者向け完全ガイドと無料命式計算機。\n\n"
            "#十干十二支 #四柱推命 #サジュ #五行 #韓国占い"
        ),
    },
    # ========== ZH. Traditional Chinese (5) ==========
    {
        "lang": "zh",
        "slug": "zh-korean-bazi-vs-chinese-bazi",
        "headline": "韓國八字 vs\n中國八字",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, split composition korean bazi chart left "
            "chinese bazi chart right on red rice paper with gold lanterns, gold ink "
            "calligraphy, deep red and gold festive palette, premium editorial cover"
        ),
        "url_path": "/zh/korean-bazi-vs-chinese-bazi.html",
        "campaign": "zh_korean_vs_chinese_bazi",
        "description": (
            "韓國八字與中國八字,同源不同流。皆以年月日時四柱、天干地支推命,但韓國 "
            "薩柱(사주)在解讀流派、現代應用、十神六親的判讀上自成一格,並融入韓國 "
            "本土文化。並排對照完整指南附免費命盤計算機。\n\n"
            "#八字命理 #韓國八字 #薩柱 #命盤 #算命"
        ),
    },
    {
        "lang": "zh",
        "slug": "zh-four-pillars-mingli",
        "headline": "四柱命理\n你的命盤",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, traditional bazi chart with four vertical "
            "columns of chinese characters on red rice paper with gold lanterns, ink brush "
            "calligraphy, deep crimson and gold palette, festive premium editorial cover"
        ),
        "url_path": "/zh/four-pillars-mingli.html",
        "campaign": "zh_four_pillars",
        "description": (
            "四柱命理,從你出生的年月日時推出八個天干地支,組成命盤的四根支柱。 "
            "五行旺衰、十神格局、大運流年一目了然。完整新手指南+免費命盤排算工具, "
            "含實例解讀。\n\n"
            "#四柱命理 #命盤 #八字 #算命 #五行"
        ),
    },
    {
        "lang": "zh",
        "slug": "zh-2026-red-horse-zodiac",
        "headline": "2026 紅馬年\n生肖運勢",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, stylized chinese ink-brush red horse "
            "galloping across 2026 calendar on red rice paper with gold lanterns and "
            "plum blossoms, gold and crimson festive palette, lunar new year, editorial cover"
        ),
        "url_path": "/zh/zodiac-2026-red-horse.html",
        "campaign": "zh_2026_redhorse",
        "description": (
            "2026年丙午紅火馬年,熱情奔放、大膽變革、風險換報酬之年。鼠、牛、虎、"
            "兔、龍、蛇、馬、羊、猴、雞、狗、豬十二生肖2026流年運勢全公開,財運、 "
            "桃花、健康、事業逐月詳解,免費。\n\n"
            "#2026運勢 #紅馬年 #十二生肖 #流年運勢 #農曆新年"
        ),
    },
    {
        "lang": "zh",
        "slug": "zh-bazi-compatibility-test-free",
        "headline": "韓國八字合婚\n免費測試",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, two stylized phoenixes intertwined over "
            "bazi chart on red rice paper with gold lanterns, gold leaf and jade accents, "
            "deep red and gold palette, festive premium editorial cover"
        ),
        "url_path": "/zh/bazi-compatibility-test.html",
        "campaign": "zh_bazi_compat",
        "description": (
            "韓國八字合婚,免費60秒測試。輸入兩人生辰八字,系統自動判讀天干地支 "
            "能量是相生相合還是相沖相剋,給出婚姻、友情、事業合夥0~100分總評。 "
            "千年韓國薩柱合婚術,在線輕鬆使用。\n\n"
            "#八字合婚 #韓國八字 #婚姻配對 #算命 #姻緣"
        ),
    },
    {
        "lang": "zh",
        "slug": "zh-ten-stems-twelve-branches",
        "headline": "十天干 十二地支\n八字基礎",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, ten heavenly stems and twelve earthly "
            "branches chinese characters arranged in circular mandala on red rice paper "
            "with gold lanterns and plum blossoms, gold ink calligraphy, festive editorial cover"
        ),
        "url_path": "/zh/ten-stems-twelve-branches.html",
        "campaign": "zh_ten_stems_twelve_branches",
        "description": (
            "十天干(甲乙丙丁戊己庚辛壬癸)代表陰陽五行能量,十二地支(子丑寅卯辰巳 "
            "午未申酉戌亥)對應12生肖與時辰。八字命理的最基礎符號系統,新手必懂。 "
            "完整對照表+免費排盤工具。\n\n"
            "#天干地支 #八字基礎 #五行 #命理入門 #算命"
        ),
    },
]


def fetch_image(prompt, slug, max_retries=6):
    seed = abs(hash(slug)) % 100000
    url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
        f"?width=1000&height=1500&seed={seed}&nologo=true&model=flux"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    backoff = 15
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries:
                log(f"  429 rate-limited, sleeping {backoff}s (attempt {attempt}/{max_retries})")
                time.sleep(backoff)
                backoff = min(backoff * 2, 120)
                continue
            raise
        except Exception as e:
            if attempt < max_retries:
                log(f"  fetch error {type(e).__name__}, sleeping {backoff}s (attempt {attempt}/{max_retries})")
                time.sleep(backoff)
                backoff = min(backoff * 2, 120)
                continue
            raise


def overlay_text(in_path, headline, lang, out_path):
    """ffmpeg drawtext - language-specific font, bold white headline on dark box."""
    font = FONTS.get(lang, FONTS["en"])
    # Two lines: split on newline. ffmpeg drawtext supports literal \n via PCRE? No --
    # we use two drawtext layers stacked.
    lines = headline.split("\n")
    if len(lines) == 1:
        lines.append("")

    def esc(s):
        return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace('"', "")[:60]

    line1 = esc(lines[0])
    line2 = esc(lines[1])

    # CJK characters render larger; reduce font size for Chinese/Japanese/Korean
    fsize = 78 if lang == "en" else 90

    # First line at y=120, second line at y=120+fsize+20
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

    for pin in PINS:
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
        full_desc = pin["description"] + f"\n\n👉 {full_url}"

        q["made"].append({
            "slug": slug,
            "kw": f"{lang}_{pin['campaign']}",
            "title": pin["headline"].replace("\n", " "),
            "made_at": datetime.datetime.now().isoformat(),
            "image_path": str(png_path),
            "description": full_desc,
            "destination_url": full_url,
            "lang": lang,
            "source": "4lang_20_2026_05_06",
            "status": "queued",
        })
        added += 1
        by_lang[lang] += 1
        # save incrementally so partial runs don't lose progress
        QUEUE_JSON.write_text(
            json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        time.sleep(8)  # spread requests to avoid Pollinations 429

    log(f"DONE: added {added} pins (ko={by_lang['ko']} en={by_lang['en']} ja={by_lang['ja']} zh={by_lang['zh']})")
    log(f"      failed {len(failed)}, queue total = {len(q['made'])}")
    if failed:
        log(f"FAILED slugs: {failed}")
    return added


if __name__ == "__main__":
    main()
