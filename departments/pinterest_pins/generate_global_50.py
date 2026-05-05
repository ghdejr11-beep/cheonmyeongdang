"""pinterest_pins — Global English 50-pin batch generator (2026-05-05).

Generates 50 K-aesthetic English Pinterest pins (1000x1500), 10 boards x 5 pins.
Targets: cheonmyeongdang.vercel.app/en, korlens.app, kunstudio.gumroad.com,
sebmuneunhyetaek (tax site), kunstudio.com.
Pollinations Flux (free). UTM tagged URLs. ~2 months daily-1-pin queue.

Output: queue/{slug}.png + queue.json (appended to existing made[]).
"""
import os, sys, json, urllib.request, urllib.parse, datetime, subprocess, time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
QUEUE_DIR = ROOT / "queue"
QUEUE_DIR.mkdir(exist_ok=True)
QUEUE_JSON = ROOT / "queue.json"
LOG = ROOT / "logs" / f"global50_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ============================================================
# 10 boards x 5 pins = 50 K-aesthetic Pinterest pins
# ============================================================
PINS = [
    # ==================== Board 1: Korean Saju & Astrology ====================
    {
        "board": 1, "slug": "korean-zodiac-2026-year-of-horse",
        "headline": "12 Korean Zodiac Animals: 2026 Year of the Horse",
        "image_prompt": "vertical pinterest pin 1000x1500, twelve korean zodiac animals circular mandala with majestic horse centered, gold leaf on indigo silk background, traditional minhwa folk painting style, soft watercolor textures, magazine cover layout",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "zodiac_2026_horse",
        "description": "12 Korean Zodiac Animals (2026 Year of the Horse). Discover what your birth year animal says about your love, career and luck in the new lunar year. Free Korean zodiac calculator inside.\n\n#KoreanZodiac #Saju #YearOfTheHorse #2026 #KoreanAstrology",
    },
    {
        "board": 1, "slug": "saju-four-pillars-explained",
        "headline": "Saju 4 Pillars: Year, Month, Day, Hour",
        "image_prompt": "vertical pinterest pin 1000x1500, four ornate stone pillars under starry night sky representing saju four pillars, deep navy and gold palette, ink brush hanja characters floating, ethereal mystical photography, magazine layout",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "saju_four_pillars",
        "description": "Saju 4 Pillars Explained: Year, Month, Day, Hour. The 1,000-year-old Korean astrology system decodes your destiny from these four time markers. Plain-English breakdown plus a free chart inside.\n\n#Saju #KoreanAstrology #FourPillars #Astrology #BirthChart",
    },
    {
        "board": 1, "slug": "korean-vs-chinese-astrology-5-differences",
        "headline": "Korean vs Chinese Astrology: 5 Differences",
        "image_prompt": "vertical pinterest pin 1000x1500, split vertical composition showing korean hanok temple on left and chinese pagoda on right, traditional ink wash painting style, dusty rose and jade green palette, elegant editorial layout",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "korean_vs_chinese_astrology",
        "description": "Korean vs Chinese Astrology: 5 Surprising Differences. Same 12 animals, very different systems. From the lunar calendar to elemental cycles, learn what makes Korean Saju unique. Free reading inside.\n\n#KoreanCulture #Astrology #Saju #ChineseZodiac #CulturalDifferences",
    },
    {
        "board": 1, "slug": "lucky-stones-by-korean-birth-year",
        "headline": "Lucky Stones by Korean Birth Year",
        "image_prompt": "vertical pinterest pin 1000x1500, twelve gemstones arranged in mandala on cream silk background, jade pearl amethyst topaz, soft window light, premium jewelry editorial flatlay, ivory and gold palette",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "lucky_stones_birth_year",
        "description": "Lucky Stones by Korean Birth Year. Each Korean zodiac animal has a power gemstone that boosts your saju energy. Find yours: jade for the rabbit, amethyst for the snake, and 10 more. Free guide inside.\n\n#KoreanZodiac #LuckyStones #Crystals #Saju #BirthstoneGuide",
    },
    {
        "board": 1, "slug": "korean-naming-tradition-birth-element",
        "headline": "Korean Naming Tradition by Birth Element",
        "image_prompt": "vertical pinterest pin 1000x1500, traditional korean hanja name characters carved on wooden plaque, ink brush calligraphy, soft golden lantern light, dried persimmon branch, deep brown and ivory palette, premium editorial flatlay",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "korean_naming_tradition",
        "description": "Korean Naming Tradition by Birth Element. Korean parents pick a baby's name from the missing element in the saju chart (wood, fire, earth, metal, water). Learn how it works plus free name suggestions.\n\n#KoreanNames #Saju #BabyNames #FiveElements #KoreanCulture",
    },

    # ==================== Board 2: K-pop Fan Culture ====================
    {
        "board": 2, "slug": "kpop-compatibility-korean-zodiac",
        "headline": "K-pop Compatibility by Korean Zodiac",
        "image_prompt": "vertical pinterest pin 1000x1500, dreamy pastel collage with twelve zodiac animals as anime mood characters, holographic glitter, soft pink lavender mint palette, kpop fan aesthetic mood board, magazine cover layout",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "kpop_compatibility_zodiac",
        "description": "K-pop Compatibility by Korean Zodiac. Find which Korean zodiac sign matches your bias type (no real names used). Free fan compatibility calculator with 12 animal personalities inside.\n\n#KpopFans #KoreanZodiac #Compatibility #Saju #KpopAesthetic",
    },
    {
        "board": 2, "slug": "kpop-aesthetic-mood-boards-2026",
        "headline": "K-pop Aesthetic Mood Boards 2026",
        "image_prompt": "vertical pinterest pin 1000x1500, dreamy pastel kpop aesthetic mood board collage with polaroids dried flowers ribbons holographic stickers, soft pink lavender cream palette, magazine cover layout, ultra aesthetic flatlay",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "kpop_mood_boards_2026",
        "description": "K-pop Aesthetic Mood Boards 2026. 30 dreamy mood board layouts for fan edits, story posts and journal pages. Pastel coquette, dark concept and dream pop palettes. Free template inside.\n\n#KpopAesthetic #MoodBoard #Aesthetic2026 #FanEdits #KoreanAesthetic",
    },
    {
        "board": 2, "slug": "kpop-fan-saju-reading-habit",
        "headline": "Build a K-pop Fan Saju Reading Habit",
        "image_prompt": "vertical pinterest pin 1000x1500, aesthetic open journal with korean zodiac stickers polaroids and pastel washi tape, soft window light, peach lavender cream palette, kpop fan journal flatlay, premium editorial photography",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "kpop_saju_habit",
        "description": "How to Build a K-pop Fan Saju Reading Habit. 5-minute daily Korean zodiac ritual for fans. Track moods, lucky days and bias compatibility. Free 30-day printable inside.\n\n#KpopFans #Saju #JournalAesthetic #DailyRoutine #KoreanZodiac",
    },
    {
        "board": 2, "slug": "korean-stage-names-meanings",
        "headline": "Korean Stage Names & Their Meanings",
        "image_prompt": "vertical pinterest pin 1000x1500, beautiful hangul calligraphy name characters glowing on dark velvet background with golden particles and stars, ethereal kpop aesthetic, deep purple and gold palette, magazine layout",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "korean_stage_names",
        "description": "Korean Stage Names & Their Meanings. Why do K-pop idols choose mononyms? A guide to common Korean naming patterns, hanja meaning and how Western fans can decode them. Free hangul cheat sheet.\n\n#KpopFans #Hangul #KoreanCulture #StageNames #LearnKorean",
    },
    {
        "board": 2, "slug": "kdrama-filming-locations-tier-list",
        "headline": "K-drama Filming Locations Tier List",
        "image_prompt": "vertical pinterest pin 1000x1500, cinematic korean filming location mosaic with bukchon hanok alley nami island han river bridge sunset, moody travel photography, warm golden palette, magazine collage layout",
        "url_base": "https://korlens.app",
        "campaign": "kdrama_locations_tier",
        "description": "K-drama Filming Locations Tier List 2026. 25 iconic spots ranked by accessibility and photo opp. Bukchon, Nami Island, Han River bridges and more. Map plus walking route inside.\n\n#KdramaLocations #KoreaTravel #Bukchon #NamiIsland #VisitKorea",
    },

    # ==================== Board 3: Korean Travel ====================
    {
        "board": 3, "slug": "seoul-vs-busan-where-to-go",
        "headline": "Seoul vs Busan: Where Should You Go?",
        "image_prompt": "vertical pinterest pin 1000x1500, split composition showing seoul skyline at top and busan beach gamcheon village at bottom, cinematic travel photography, golden hour lighting, magazine cover layout",
        "url_base": "https://korlens.app",
        "campaign": "seoul_vs_busan",
        "description": "Seoul vs Busan: Where Should You Go in 2026? A side-by-side comparison of food, vibes, cafes and hidden gems. Pick the right city for your travel style. Free 5-day itinerary inside.\n\n#SeoulTravel #BusanTravel #KoreaTravel #VisitKorea #TravelPlanning",
    },
    {
        "board": 3, "slug": "hidden-hanok-villages-guide",
        "headline": "Hidden Hanok Villages You Have Not Heard Of",
        "image_prompt": "vertical pinterest pin 1000x1500, secret hanok village courtyard at golden hour, traditional curved tile roofs, paper lanterns glowing, cherry blossom petals falling, warm peach and brown palette, cinematic travel photography",
        "url_base": "https://korlens.app",
        "campaign": "hidden_hanok_villages",
        "description": "Hidden Hanok Villages You Have Not Heard Of. Skip Bukchon. 7 traditional Korean villages with zero tourist crowds, golden roof aesthetics and incredible cafes. Map and locals' tips inside.\n\n#HanokVillage #KoreaTravel #HiddenGems #VisitKorea #TravelKorea",
    },
    {
        "board": 3, "slug": "korean-cafe-aesthetics-insta",
        "headline": "Korean Cafe Aesthetics: Your Next Insta Spot",
        "image_prompt": "vertical pinterest pin 1000x1500, dreamy korean cafe interior with floral latte art on marble table, dried roses, soft window light, ivory and dusty rose palette, premium editorial flatlay photography, ultra aesthetic",
        "url_base": "https://korlens.app",
        "campaign": "korean_cafe_aesthetics",
        "description": "Korean Cafe Aesthetics: Your Next Insta Spot. 20 dreamy cafes in Seoul, Busan and Jeju where every corner is a photo. Floral lattes, hanok interiors and rooftop sunsets. Map and instagram tips inside.\n\n#KoreanCafe #CafeAesthetic #SeoulCafe #Instagrammable #KoreaTravel",
    },
    {
        "board": 3, "slug": "jeju-3-day-itinerary",
        "headline": "Jeju Island 3-Day Travel Guide",
        "image_prompt": "vertical pinterest pin 1000x1500, jeju island volcanic coast with sunrise peak hallasan and tangerine groves, dreamy cinematic travel photography, teal and golden palette, magazine cover layout",
        "url_base": "https://korlens.app",
        "campaign": "jeju_3_day_itinerary",
        "description": "Jeju Island Travel Guide: 3-Day Itinerary. The ultimate weekend in Korea's volcanic paradise. Sunrise Peak, hidden beaches, oreum hikes and the best tangerine cafes. Map and checklist inside.\n\n#JejuIsland #KoreaTravel #Itinerary #VisitKorea #TravelGuide",
    },
    {
        "board": 3, "slug": "korean-convenience-store-tier-list",
        "headline": "Korean Convenience Store Tier List",
        "image_prompt": "vertical pinterest pin 1000x1500, korean convenience store snacks flatlay with banana milk triangle kimbap honey butter chips arranged on pastel grid, soft natural light, ivory and pastel palette, premium editorial photography",
        "url_base": "https://korlens.app",
        "campaign": "korean_cvs_tier_list",
        "description": "Korean Convenience Store Tier List. The ultimate guide to GS25 vs CU vs 7-Eleven snacks tourists love. Banana milk, triangle kimbap, honey butter chips and 30 more ranked. Free map inside.\n\n#KoreanFood #CVSSnacks #KoreaTravel #BananaMilk #VisitKorea",
    },

    # ==================== Board 4: Hangul & Calligraphy ====================
    {
        "board": 4, "slug": "beautiful-hangul-calligraphy-quotes",
        "headline": "Beautiful Hangul Calligraphy Quotes",
        "image_prompt": "vertical pinterest pin 1000x1500, elegant hangul calligraphy quote on cream rice paper with ink brush strokes, dried wildflower, soft window light, ivory and ink black palette, premium editorial flatlay",
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "hangul_calligraphy_quotes",
        "description": "Beautiful Hangul Calligraphy Quotes. 30 inspirational Korean quotes hand-rendered in traditional ink brush calligraphy. Free phone wallpaper pack and printable journal pages inside.\n\n#Hangul #KoreanCalligraphy #Quotes #KoreanAesthetic #PrintableArt",
    },
    {
        "board": 4, "slug": "10-korean-words-no-translation",
        "headline": "10 Korean Words That Do Not Translate",
        "image_prompt": "vertical pinterest pin 1000x1500, hangul characters floating over warm watercolor pastel background with dried botanicals, soft cream and peach palette, dreamy editorial layout, premium aesthetic photography",
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "untranslatable_korean_words",
        "description": "10 Korean Words That Do Not Translate to English. Han, jeong, nunchi and 7 more concepts unique to Korean culture. Plain English explanations plus free hangul flashcard pack inside.\n\n#LearnKorean #Hangul #KoreanCulture #LanguageLearning #KoreanWords",
    },
    {
        "board": 4, "slug": "hangul-tattoo-design-inspiration",
        "headline": "Hangul Tattoo Design Inspiration",
        "image_prompt": "vertical pinterest pin 1000x1500, minimalist hangul calligraphy tattoo on porcelain skin, fine line ink, soft natural light, ivory and ink black palette, dreamy editorial close-up photography",
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "hangul_tattoo_inspiration",
        "description": "Hangul Tattoo Design Inspiration. 25 minimalist Korean character tattoos with translations and meaning guides. Avoid common mistakes (do not use Google Translate). Free font pack inside.\n\n#HangulTattoo #KoreanTattoo #MinimalistTattoo #TattooInspo #KoreanCulture",
    },
    {
        "board": 4, "slug": "learn-hangul-30-minutes",
        "headline": "Learn Hangul in 30 Minutes",
        "image_prompt": "vertical pinterest pin 1000x1500, hangul alphabet chart on cream paper with ink brush, vintage open notebook, soft window light, ivory and brown palette, premium editorial flatlay photography",
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "learn_hangul_30min",
        "description": "Learn Hangul in 30 Minutes (Beginner Guide). The Korean alphabet has only 14 consonants and 10 vowels. With this proven memory trick, anyone can read hangul today. Free PDF flashcards inside.\n\n#LearnHangul #LearnKorean #LanguageLearning #StudyAesthetic #KoreanCulture",
    },
    {
        "board": 4, "slug": "korean-aesthetic-notion-templates",
        "headline": "Korean Aesthetic Notion Templates",
        "image_prompt": "vertical pinterest pin 1000x1500, dreamy notion template mockup on laptop with hangul headers and pastel widgets, ceramic mug dried flowers, soft window light, ivory and sage palette, ultra aesthetic flatlay",
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "korean_aesthetic_notion",
        "description": "Korean Aesthetic Notion Templates 2026. 25 minimalist Notion pages with hangul headers, pastel widgets, mood trackers and study planners. Free preview pack inside.\n\n#NotionTemplate #KoreanAesthetic #StudyPlanner #DigitalPlanner #Hangul",
    },

    # ==================== Board 5: Korean Food & Cafes ====================
    {
        "board": 5, "slug": "top-10-korean-street-foods",
        "headline": "Top 10 Korean Street Foods",
        "image_prompt": "vertical pinterest pin 1000x1500, vibrant korean street food market scene with tteokbokki hotteok mandu skewers in steaming pots, warm tungsten lantern light, deep red and amber palette, cinematic food photography",
        "url_base": "https://korlens.app",
        "campaign": "top_korean_street_foods",
        "description": "Top 10 Korean Street Foods You Must Try. From tteokbokki to hotteok, the ultimate Seoul foodie tier list with where to find them. Free Myeongdong food map inside.\n\n#KoreanStreetFood #SeoulFood #KoreaTravel #Tteokbokki #FoodieGuide",
    },
    {
        "board": 5, "slug": "hanok-cafe-vibes-photography",
        "headline": "Hanok Cafe Vibes Photography",
        "image_prompt": "vertical pinterest pin 1000x1500, traditional hanok cafe interior with paper sliding doors brass kettle ceramic teaware, soft window light streaming through wood lattice, warm beige and brown palette, premium editorial photography",
        "url_base": "https://korlens.app",
        "campaign": "hanok_cafe_photography",
        "description": "Hanok Cafe Vibes Photography Guide. 20 traditional Korean tea houses where every corner is photo gold. Camera settings, golden hour timing and best seats inside.\n\n#HanokCafe #KoreanCafe #PhotographyGuide #SeoulCafe #VisitKorea",
    },
    {
        "board": 5, "slug": "korean-tea-ceremony-aesthetic",
        "headline": "Korean Tea Ceremony Aesthetic",
        "image_prompt": "vertical pinterest pin 1000x1500, traditional korean tea ceremony flatlay with celadon teapot wooden tray dried flowers and incense smoke, soft window light, ivory and sage palette, premium editorial photography",
        "url_base": "https://korlens.app",
        "campaign": "korean_tea_ceremony",
        "description": "Korean Tea Ceremony Aesthetic. The 500-year-old darye ritual decoded plus 5 modern home setups. Tea types, tools and slow-living tips. Free starter checklist inside.\n\n#KoreanTea #TeaCeremony #SlowLiving #KoreanAesthetic #MindfulLiving",
    },
    {
        "board": 5, "slug": "kdrama-foods-to-try",
        "headline": "K-drama Foods to Try at Home",
        "image_prompt": "vertical pinterest pin 1000x1500, korean food spread with bibimbap ramyeon kimbap fried chicken on wooden table, soft window light, warm orange and brown palette, premium overhead food photography flatlay",
        "url_base": "https://korlens.app",
        "campaign": "kdrama_foods_to_try",
        "description": "K-drama Foods to Try at Home. The 15 dishes you keep seeing on screen, ranked by ease and addictiveness. Bibimbap, ramyeon, fried chicken and more. Free recipe card inside.\n\n#KdramaFood #KoreanFood #BibimBap #KoreanRecipes #FoodieGuide",
    },
    {
        "board": 5, "slug": "korean-cvs-snacks-ranked",
        "headline": "Korean Convenience Store Snacks Ranked",
        "image_prompt": "vertical pinterest pin 1000x1500, korean convenience store snack haul flatlay with banana milk shrimp crackers honey butter chips choco pies on pastel grid background, soft natural light, premium editorial flatlay",
        "url_base": "https://korlens.app",
        "campaign": "korean_cvs_snacks_ranked",
        "description": "Korean Convenience Store Snacks Ranked. The ultimate hit list of 30 must-try Korean snacks. Banana milk, shrimp crackers, choco pie and more. Free shopping checklist inside.\n\n#KoreanSnacks #CVS #KoreaTravel #FoodieGuide #BananaMilk",
    },

    # ==================== Board 6: Saju Diary & Journaling ====================
    {
        "board": 6, "slug": "saju-daily-reflection-journal-setup",
        "headline": "Saju Daily Reflection Journal Setup",
        "image_prompt": "vertical pinterest pin 1000x1500, open journal with saju daily prompts brass pen ceramic mug dried lavender on linen tablecloth, soft window light, ivory and sage palette, premium editorial flatlay photography",
        "url_base": "https://kunstudio.gumroad.com/l/qcjtu",
        "campaign": "saju_daily_journal_setup",
        "description": "Saju Daily Reflection Journal Setup. The 10-minute morning routine that turns Korean astrology into a self-discovery practice. 7 prompts plus a free printable starter pack inside.\n\n#SajuJournal #KoreanAstrology #JournalIdeas #DailyReflection #SelfDiscovery",
    },
    {
        "board": 6, "slug": "saju-12-month-diary-workbook-bilingual",
        "headline": "12-Month Saju Diary Workbook (Bilingual)",
        "image_prompt": "vertical pinterest pin 1000x1500, beautiful bilingual workbook open to monthly saju forecast pages with korean hangul and english text, dried botanicals brass pen, soft window light, ivory and golden palette, premium editorial flatlay",
        "url_base": "https://kunstudio.gumroad.com/l/qcjtu",
        "campaign": "saju_12month_bilingual",
        "description": "12-Month Saju Diary Workbook (Bilingual). A guided yearlong journal in Korean and English. 365 daily prompts, monthly forecasts and a birth chart worksheet. Free 30-page preview inside.\n\n#SajuDiary #BilingualJournal #KoreanAstrology #Workbook #YearlyPlanner",
    },
    {
        "board": 6, "slug": "korean-birth-element-affirmations",
        "headline": "Korean Birth Element Affirmations",
        "image_prompt": "vertical pinterest pin 1000x1500, five elements wood fire earth metal water symbols arranged in pentagon on cream paper with watercolor wash, soft window light, ivory and sage palette, premium editorial photography",
        "url_base": "https://kunstudio.gumroad.com/l/qcjtu",
        "campaign": "birth_element_affirmations",
        "description": "Korean Birth Element Affirmations. 50 daily affirmations matched to your saju element (wood, fire, earth, metal, water). Free phone wallpaper pack and printable cards inside.\n\n#Affirmations #KoreanAstrology #Saju #FiveElements #SelfCare",
    },
    {
        "board": 6, "slug": "saju-compatibility-tracker-pages",
        "headline": "Saju Compatibility Tracker Pages",
        "image_prompt": "vertical pinterest pin 1000x1500, aesthetic compatibility tracker journal pages with saju chart hearts and zodiac stickers, brass pen dried flowers, soft window light, dusty rose and ivory palette, premium editorial flatlay",
        "url_base": "https://kunstudio.gumroad.com/l/qcjtu",
        "campaign": "saju_compatibility_tracker",
        "description": "Saju Compatibility Tracker Pages. Track your relationships through the lens of Korean astrology. 12 zodiac match grids, monthly check-ins and red flag prompts. Free preview inside.\n\n#SajuCompatibility #JournalPages #RelationshipTracker #KoreanAstrology #LoveJournal",
    },
    {
        "board": 6, "slug": "year-of-snake-2026-reflection-prompts",
        "headline": "Year of the Snake 2026 Reflection Prompts",
        "image_prompt": "vertical pinterest pin 1000x1500, mystical snake illustration coiled around moon and stars on velvet sky, gold leaf accents and journal pages floating, deep navy and gold palette, ethereal editorial photography",
        "url_base": "https://kunstudio.gumroad.com/l/qcjtu",
        "campaign": "snake_2026_reflection_prompts",
        "description": "Year of the Snake 2026 Reflection Prompts. 31 deep journal questions inspired by the Korean lunar new year. Shed old skin, set intentions, decode your saju year. Free printable inside.\n\n#YearOfTheSnake #LunarNewYear #JournalPrompts #KoreanAstrology #2026",
    },

    # ==================== Board 7: Korean Founder Story ====================
    {
        "board": 7, "slug": "solo-founder-3-saas-30-days",
        "headline": "Solo Founder Builds 3 SaaS in 30 Days",
        "image_prompt": "vertical pinterest pin 1000x1500, minimalist desk flatlay with laptop notebook coffee and three product mockups, soft window light, beige and sage palette, premium editorial indie hacker aesthetic photography",
        "url_base": "https://kunstudio.com",
        "campaign": "solo_founder_3_saas",
        "description": "Solo Founder Builds 3 SaaS in 30 Days. A Korean indie hacker shipping fortune-telling, tax and travel apps with zero ad spend. Tech stack, daily routine and revenue numbers inside.\n\n#IndieHacker #SoloFounder #BuildInPublic #SaaS #Bootstrap",
    },
    {
        "board": 7, "slug": "korea-next-ai-frontier",
        "headline": "Why Korea is the Next AI Frontier",
        "image_prompt": "vertical pinterest pin 1000x1500, futuristic seoul skyline at twilight with neon signs and holographic data streams, cyberpunk meets traditional korean aesthetic, deep teal and magenta palette, cinematic editorial photography",
        "url_base": "https://kunstudio.com",
        "campaign": "korea_ai_frontier",
        "description": "Why Korea is the Next AI Frontier. 5 reasons Korea is becoming the unexpected AI superpower in 2026. Government policy, dev culture, and breakout startups. Free industry report inside.\n\n#KoreaTech #AIFrontier #StartupTrends #KoreanInnovation #IndieHacker",
    },
    {
        "board": 7, "slug": "indie-hacker-korean-edition",
        "headline": "Indie Hacker Korean Edition",
        "image_prompt": "vertical pinterest pin 1000x1500, indie hacker workspace flatlay with macbook hangul keyboard ceramic coffee mug and notebook on warm wooden desk, soft window light, beige and copper palette, premium editorial photography",
        "url_base": "https://kunstudio.com",
        "campaign": "indie_hacker_korean",
        "description": "Indie Hacker Korean Edition. How a Korean solo developer makes monthly recurring revenue with global products. Stack, channels, mistakes and what works. Free playbook inside.\n\n#IndieHacker #SoloFounder #Bootstrap #StartupStory #BuildInPublic",
    },
    {
        "board": 7, "slug": "zero-ad-spend-revenue-journey",
        "headline": "0 Ad Spend Revenue Journey",
        "image_prompt": "vertical pinterest pin 1000x1500, minimalist growth chart on whiteboard with sticky notes and laptop on desk, soft window light, ivory and forest green palette, premium editorial founder aesthetic photography",
        "url_base": "https://kunstudio.com",
        "campaign": "zero_ad_spend_journey",
        "description": "0 Ad Spend Revenue Journey. How a solo Korean founder grew 3 products with only Pinterest, TikTok and SEO. Channel breakdown, content cadence and lessons. Free template inside.\n\n#IndieHacker #ZeroBudget #Bootstrap #ContentMarketing #StartupGrowth",
    },
    {
        "board": 7, "slug": "korean-hustle-culture-reframed",
        "headline": "Korean Hustle Culture Reframed",
        "image_prompt": "vertical pinterest pin 1000x1500, peaceful seoul morning with steaming coffee on balcony overlooking hanok rooftops, soft sunrise light, warm peach and ivory palette, premium editorial slow living photography",
        "url_base": "https://kunstudio.com",
        "campaign": "korean_hustle_reframed",
        "description": "Korean Hustle Culture Reframed. From burnout to balance: a Korean founder's slow living manifesto. Why doing less can ship more. Free 5-step framework inside.\n\n#SlowLiving #FounderMindset #WorkLifeBalance #IndieHacker #KoreanCulture",
    },

    # ==================== Board 8: Korean Spirituality ====================
    {
        "board": 8, "slug": "korean-shaman-tradition-modern",
        "headline": "Korean Shaman Tradition Modern Take",
        "image_prompt": "vertical pinterest pin 1000x1500, mystical korean shaman ritual scene with hanbok robes drum candles and silk fans, ethereal mist soft golden light, deep red and gold palette, cinematic spiritual photography",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "korean_shaman_modern",
        "description": "Korean Shaman Tradition: Modern Interpretation. The 5,000-year-old mudang practice still alive in Seoul today. History, rituals and how it influences saju astrology. Free guide inside.\n\n#KoreanShaman #Mudang #KoreanSpirituality #Saju #KoreanCulture",
    },
    {
        "board": 8, "slug": "buddhist-temple-stay-aesthetics",
        "headline": "Buddhist Temple Stay Aesthetics",
        "image_prompt": "vertical pinterest pin 1000x1500, tranquil korean buddhist temple courtyard at dawn with stone pagoda lotus pond and pine trees in mist, soft golden light, deep green and ivory palette, cinematic spiritual photography",
        "url_base": "https://korlens.app",
        "campaign": "buddhist_temple_stay",
        "description": "Buddhist Temple Stay Aesthetics. 8 Korean temples that offer overnight stays. Wake up to dawn chants, vegetarian food and stunning mountain views. Free booking guide inside.\n\n#TempleStay #KoreanBuddhism #SlowTravel #KoreaTravel #SpiritualRetreat",
    },
    {
        "board": 8, "slug": "mountain-spirit-folklore",
        "headline": "Korean Mountain Spirit Folklore",
        "image_prompt": "vertical pinterest pin 1000x1500, ethereal korean mountain spirit sanshin painting with white tiger pine tree and ancient sage in mystical mist, traditional minhwa folk style, deep green and gold palette, magazine layout",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "mountain_spirit_folklore",
        "description": "Korean Mountain Spirit Folklore. The legend of sanshin and the white tiger spirit shaping Korean shamanism for 1,000 years. Stories, paintings and meaning. Free zine inside.\n\n#KoreanFolklore #Sanshin #KoreanCulture #Mythology #Spirituality",
    },
    {
        "board": 8, "slug": "korean-funeral-birth-rituals",
        "headline": "Korean Birth & Memorial Rituals",
        "image_prompt": "vertical pinterest pin 1000x1500, traditional korean ritual altar with celadon ceramics rice cake offerings and incense smoke, soft warm candlelight, deep red and ivory palette, cinematic editorial photography",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "korean_birth_memorial_rituals",
        "description": "Korean Birth and Memorial Rituals Explained. The 100-day baby celebration, first birthday doljanchi and memorial jesa. Cultural meaning and modern adaptations. Free guide inside.\n\n#KoreanCulture #Doljanchi #Jesa #KoreanRituals #FamilyTraditions",
    },
    {
        "board": 8, "slug": "eastern-vs-western-astrology",
        "headline": "Eastern vs Western Astrology",
        "image_prompt": "vertical pinterest pin 1000x1500, split composition with western zodiac wheel on left and korean saju chart on right, gold celestial accents on midnight blue background, ethereal editorial photography, magazine layout",
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "eastern_vs_western_astrology",
        "description": "Eastern vs Western Astrology: Side-by-Side. Sun sign, Moon sign, day pillar, hour pillar. How Korean Saju and Western astrology actually compare. Free dual reading inside.\n\n#Astrology #Saju #ZodiacSigns #EasternAstrology #BirthChart",
    },

    # ==================== Board 9: K-aesthetic Productivity ====================
    {
        "board": 9, "slug": "korean-aesthetic-notion-setup",
        "headline": "Korean Aesthetic Notion Setup",
        "image_prompt": "vertical pinterest pin 1000x1500, dreamy macbook flatlay with korean aesthetic notion dashboard hangul headers ceramic mug dried flowers, soft window light, ivory and sage palette, ultra aesthetic premium photography",
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "korean_notion_setup",
        "description": "Korean Aesthetic Notion Setup. The 5-page minimalist dashboard that 12,000 students use to plan their day. Hangul headers, pastel widgets, mood tracker. Free preview inside.\n\n#NotionAesthetic #KoreanAesthetic #StudyPlanner #DigitalPlanner #Hangul",
    },
    {
        "board": 9, "slug": "hanok-inspired-workspace-vibes",
        "headline": "Hanok-Inspired Workspace Vibes",
        "image_prompt": "vertical pinterest pin 1000x1500, modern minimalist workspace with korean hanok inspired wood paneling paper lantern ceramic mug and notebook, soft window light, warm beige and brown palette, premium editorial photography",
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "hanok_workspace_vibes",
        "description": "Hanok-Inspired Workspace Vibes. Bring the calm of a 500-year-old Korean home into your desk setup. 7 minimalist swaps and a mood board. Free Pinterest collection inside.\n\n#KoreanAesthetic #Workspace #DeskSetup #SlowLiving #HanokVibes",
    },
    {
        "board": 9, "slug": "korean-coffee-shop-productivity",
        "headline": "Korean Coffee Shop Productivity",
        "image_prompt": "vertical pinterest pin 1000x1500, dreamy korean cafe workspace with macbook latte art notebook on marble table, soft window light, ivory and dusty rose palette, premium editorial flatlay photography",
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "korean_cafe_productivity",
        "description": "Korean Coffee Shop Productivity. Why Seoul cafes are the world's best deep work spots. Aesthetic playlists, must-order menu and 5 etiquette rules. Free cafe map inside.\n\n#CafeWork #DeepWork #KoreanCafe #Productivity #StudyAesthetic",
    },
    {
        "board": 9, "slug": "handwritten-hangul-bullet-journal",
        "headline": "Handwritten Hangul Bullet Journal",
        "image_prompt": "vertical pinterest pin 1000x1500, beautiful open bullet journal with hand drawn hangul calligraphy headers brass pen washi tape and dried flowers, soft window light, ivory and sage palette, premium editorial flatlay",
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "hangul_bullet_journal",
        "description": "Handwritten Hangul Bullet Journal Setup. Combine Korean calligraphy with the bujo system for a stunning daily planner. Layouts, fonts and supplies. Free printable inside.\n\n#BulletJournal #Hangul #JournalAesthetic #KoreanAesthetic #BujoSetup",
    },
    {
        "board": 9, "slug": "slow-living-korean-way",
        "headline": "Slow Living the Korean Way",
        "image_prompt": "vertical pinterest pin 1000x1500, peaceful korean morning ritual with green tea pottery dried flowers and open journal on linen tablecloth, soft window light, ivory and sage palette, premium editorial slow living photography",
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "slow_living_korean",
        "description": "Slow Living the Korean Way. From temple stays to morning tea rituals, the 7 principles of Korean slow living. Daily practices anyone can try. Free starter guide inside.\n\n#SlowLiving #KoreanCulture #MindfulLiving #SelfCare #Aesthetic",
    },

    # ==================== Board 10: Korean AI / Tech ====================
    {
        "board": 10, "slug": "korean-tax-filing-30-minutes-ai",
        "headline": "Korean Tax Filing in 30 Minutes (AI)",
        "image_prompt": "vertical pinterest pin 1000x1500, modern minimalist macbook screen showing korean tax dashboard with charts and ai assistant, ceramic coffee notebook and pen on wood desk, soft window light, ivory and teal palette, premium editorial photography",
        "url_base": "https://xn--vk1bm74ahqd.com",
        "campaign": "korean_tax_30min_ai",
        "description": "Korean Tax Filing in 30 Minutes with AI. The simple step-by-step that helps small business owners submit hometax returns without hiring an accountant. Free walkthrough inside.\n\n#KoreanTax #SmallBusiness #AITools #TaxFiling #SoloFounder",
    },
    {
        "board": 10, "slug": "saju-api-for-developers",
        "headline": "Saju API for Developers",
        "image_prompt": "vertical pinterest pin 1000x1500, code editor with korean saju api endpoints on dark mode screen with neon blue and pink syntax highlighting, ceramic mug, premium editorial dev aesthetic photography, modern minimalist",
        "url_base": "https://kunstudio.com",
        "campaign": "saju_api_developers",
        "description": "Saju API for Developers. The first English-language Korean astrology API. Birth chart, compatibility, and daily horoscope endpoints. Free tier 1,000 requests per month. Docs inside.\n\n#API #DeveloperTools #IndieHacker #SajuAPI #KoreanAstrology",
    },
    {
        "board": 10, "slug": "korean-llm-use-cases",
        "headline": "Korean LLM Use Cases",
        "image_prompt": "vertical pinterest pin 1000x1500, futuristic data visualization with korean hangul characters flowing through neural network nodes, deep navy and electric blue palette, holographic glow, cinematic tech editorial photography",
        "url_base": "https://kunstudio.com",
        "campaign": "korean_llm_use_cases",
        "description": "Korean LLM Use Cases 2026. 10 ways Korean-language large language models outperform global ones for translation, sentiment and search. Industry case studies inside.\n\n#KoreanAI #LLM #AITrends #KoreaTech #MachineLearning",
    },
    {
        "board": 10, "slug": "k-tech-founder-story",
        "headline": "K-Tech Founder Story",
        "image_prompt": "vertical pinterest pin 1000x1500, korean indie hacker silhouette working at desk with city skyline view at sunset, warm tungsten light, ivory and copper palette, cinematic editorial founder portrait photography",
        "url_base": "https://kunstudio.com",
        "campaign": "k_tech_founder_story",
        "description": "K-Tech Founder Story. From zero to global product launch in 90 days. A Korean solo dev's stack, schedule, and the cultural lessons they learned. Free playbook inside.\n\n#FounderStory #KoreanFounder #IndieHacker #StartupJourney #BuildInPublic",
    },
    {
        "board": 10, "slug": "korean-indie-dev-tools-2026",
        "headline": "Korean Indie Dev Tools 2026",
        "image_prompt": "vertical pinterest pin 1000x1500, minimalist developer toolkit flatlay with macbook ceramic mug notebook and labeled app icons on wood desk, soft window light, ivory and sage palette, premium editorial dev aesthetic photography",
        "url_base": "https://kunstudio.com",
        "campaign": "korean_indie_dev_tools",
        "description": "Korean Indie Dev Tools 2026. The 15-tool stack a Korean solo founder uses to ship products under $50/month. From hosting to analytics to AI helpers. Free tool list inside.\n\n#DeveloperTools #IndieHacker #DevStack #SoloFounder #StartupTools",
    },
]


def fetch_image(prompt, slug):
    seed = abs(hash(slug)) % 100000
    url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
        f"?width=1000&height=1500&seed={seed}&nologo=true&model=flux"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=240) as r:
        return r.read()


def overlay_text(in_path, headline, out_path):
    """ffmpeg drawtext - bold white headline on dark box, top of pin."""
    font = "C\\:/Windows/Fonts/arialbd.ttf"
    safe = headline.replace(":", "\\:").replace("'", "\\'").replace('"', '')[:80]
    drawtext = (
        f"drawtext=fontfile='{font}':"
        f"text='{safe}':"
        f"fontcolor=white:fontsize=64:"
        f"box=1:boxcolor=black@0.78:boxborderw=24:"
        f"x=(w-text_w)/2:y=110:"
        f"line_spacing=14"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(in_path),
            "-vf", f"scale=1000:1500,{drawtext}",
            "-frames:v", "1", str(out_path),
        ],
        check=True, capture_output=True,
    )


def utm_url(base, campaign, board):
    sep = "&" if "?" in base else "?"
    return (
        f"{base}{sep}utm_source=pinterest&utm_medium=affiliate"
        f"&utm_campaign={campaign}&utm_content=board_{board}"
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

    for i, pin in enumerate(PINS, 1):
        slug = pin["slug"]
        if slug in existing_slugs:
            log(f"[{i}/50] SKIP {slug} (already in queue)")
            continue
        log(f"[{i}/50] === board {pin['board']} :: {slug} ===")

        png_path = QUEUE_DIR / f"{slug}.png"
        raw_path = QUEUE_DIR / f"{slug}_raw.jpg"

        # retry pollinations up to 3x
        raw = None
        for attempt in range(3):
            try:
                log(f"  fetching pollinations (attempt {attempt+1})...")
                raw = fetch_image(pin["image_prompt"], slug)
                raw_path.write_bytes(raw)
                log(f"  raw -> {raw_path.name} ({len(raw)//1024}KB)")
                break
            except Exception as e:
                log(f"  POLLINATIONS FAIL #{attempt+1}: {type(e).__name__}: {str(e)[:120]}")
                time.sleep(5)

        if raw is None:
            failed.append(slug)
            continue

        try:
            overlay_text(raw_path, pin["headline"], png_path)
            log(f"  overlay -> {png_path.name} ({png_path.stat().st_size//1024}KB)")
        except subprocess.CalledProcessError as e:
            log(f"  ffmpeg FAIL, using raw: {e.stderr[:100] if e.stderr else ''}")
            png_path = raw_path

        full_url = utm_url(pin["url_base"], pin["campaign"], pin["board"])
        full_desc = pin["description"] + f"\n\nFull guide: {full_url}"

        q["made"].append({
            "slug": slug,
            "kw": pin["campaign"],
            "title": pin["headline"],
            "board": pin["board"],
            "made_at": datetime.datetime.now().isoformat(),
            "image_path": str(png_path),
            "description": full_desc,
            "destination_url": full_url,
            "source": "global_50_2026_05_05",
            "status": "queued",
        })
        added += 1

        # save after every pin to checkpoint
        QUEUE_JSON.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(2)

    log(f"DONE: added {added}/50 pins, queue total = {len(q['made'])}")
    if failed:
        log(f"FAILED: {failed}")
    return added


if __name__ == "__main__":
    main()
