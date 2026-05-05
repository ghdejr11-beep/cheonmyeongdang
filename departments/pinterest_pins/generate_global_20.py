"""pinterest_pins — Global English 20-pin batch generator (2026-05-05).

Adds 20 standalone English Pinterest pins (1000x1500) on top of existing 5+1 queue.
Categories:
  A. Cheonmyeongdang EN (5)  -> cheonmyeongdang.vercel.app/en
  B. KORLENS (5)             -> korlens.app
  C. Mega Bundle (5)         -> ghdejr.gumroad.com/l/xuqbai
  D. Saju Diary qcjtu (3)    -> ghdejr.gumroad.com/l/qcjtu
  E. Tax-N-Benefit (2)       -> tax-n-benefit-api.vercel.app

Output: queue/{slug}.png + queue.json (appended to existing made[]).
Pollinations Flux (free, no API key). UTM tagged URLs.
Constraints: no specific company/celebrity/IP names. Generalize ("K-pop", "Korean drama").
"""
import os, sys, json, urllib.request, urllib.parse, datetime, subprocess, time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
QUEUE_DIR = ROOT / "queue"
QUEUE_DIR.mkdir(exist_ok=True)
QUEUE_JSON = ROOT / "queue.json"
LOG = ROOT / "logs" / f"global20_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


PINS = [
    # ========== A. Cheonmyeongdang EN (5) ==========
    {
        "slug": "saju-compatibility-soulmate-birth-year",
        "headline": "Korean Saju Compatibility: Find Your Soulmate",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, two stylized korean ink-brush dragons "
            "intertwined in romantic mandala, gold leaf accents on dusty rose paper, "
            "traditional minhwa folk art, soft watercolor, premium magazine cover, editorial"
        ),
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "saju_compat_soulmate",
        "description": (
            "Korean Saju Compatibility: Find Your Soulmate by Birth Year. The 1,000-year-old "
            "Korean astrology system reveals which birth-year pairings spark love and which "
            "fizzle. Free compatibility calculator inside.\n\n"
            "#KoreanAstrology #Saju #Compatibility #Soulmate #KoreanZodiac"
        ),
    },
    {
        "slug": "saju-vs-western-astrology-differences",
        "headline": "Saju vs Western Astrology: 5 Differences",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, split composition korean saju ink chart "
            "left and western zodiac wheel right on parchment, gold ink, deep navy and "
            "cream palette, premium editorial layout, soft candlelight"
        ),
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "saju_vs_western",
        "description": (
            "Saju vs Western Astrology: 5 Surprising Differences. Both decode personality "
            "from birth, but Korean Saju uses 4 pillars and 60-year cycles while Western "
            "uses 12 sun signs. See which fits you best. Free side-by-side test inside.\n\n"
            "#KoreanAstrology #Saju #Astrology #ZodiacSigns #Compatibility"
        ),
    },
    {
        "slug": "korean-zodiac-animal-career-path",
        "headline": "Your Korean Zodiac Animal & Career",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, twelve korean zodiac animals arranged "
            "around a vintage compass, gold and emerald palette, traditional minhwa "
            "folk painting style, parchment texture, magazine editorial cover layout"
        ),
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "zodiac_career",
        "description": (
            "Your Korean Zodiac Animal Says THIS About Your Career. Tigers lead, rabbits "
            "diplomat, dragons innovate. Discover the career path your birth year was "
            "built for. Free 1-minute reading inside.\n\n"
            "#KoreanZodiac #CareerAdvice #Saju #KoreanAstrology #BirthYear"
        ),
    },
    {
        "slug": "saju-four-pillars-beginner-guide-2026",
        "headline": "How to Read Saju 4 Pillars (Beginner)",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, traditional korean saju chart with four "
            "vertical columns of hanja characters, ink brush calligraphy on rice paper, "
            "deep red and gold accents, soft lantern lighting, editorial magazine cover"
        ),
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "saju_four_pillars_2026",
        "description": (
            "How to Read Saju 4 Pillars: Beginner Guide 2026. Year, Month, Day, Hour. "
            "Each pillar reveals one quarter of your destiny in Korean astrology. Step-by-"
            "step for total beginners with free chart calculator.\n\n"
            "#Saju #KoreanAstrology #FourPillars #BaZi #Astrology2026"
        ),
    },
    {
        "slug": "lucky-color-direction-korean-element",
        "headline": "Lucky Color & Direction by Birth Element",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, five korean elemental color swatches "
            "wood green fire red earth yellow metal white water blue arranged in "
            "circular bagua, gold leaf, parchment background, premium editorial design"
        ),
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "lucky_color_direction",
        "description": (
            "Lucky Color & Direction by Korean Birth Element. Wood-Fire-Earth-Metal-Water "
            "each pair with a color and compass direction that boost your fortune. Find "
            "yours from your birth year. Free element calculator inside.\n\n"
            "#FengShui #KoreanAstrology #LuckyColor #Saju #FiveElements"
        ),
    },
    # ========== B. KORLENS (5) ==========
    {
        "slug": "seoul-hidden-cafes-locals-secret",
        "headline": "10 Hidden Cafes in Seoul Locals Love",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, cozy hidden seoul hanok cafe interior with "
            "warm pendant lights, latte art on wooden table, dried flowers in vase, "
            "moody warm cinematic photography, peach and amber palette, magazine layout"
        ),
        "url_base": "https://korlens.app",
        "campaign": "seoul_hidden_cafes",
        "description": (
            "10 Hidden Cafes in Seoul Locals Won't Tell You. Skip the tourist chains. A "
            "Seoul native shares 10 secret hanok cafes, rooftop espresso bars and book "
            "cafes the guidebooks miss. Map and route inside.\n\n"
            "#SeoulCafe #SeoulTravel #KoreaTravel #HiddenGems #VisitKorea"
        ),
    },
    {
        "slug": "busan-vs-jeju-korean-beach-guide",
        "headline": "Busan vs Jeju: Which Beach Is Right",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, split composition busan haeundae beach "
            "left jeju black-sand coast right, golden hour, cinematic travel photography, "
            "azure and turquoise palette, premium magazine editorial cover layout"
        ),
        "url_base": "https://korlens.app",
        "campaign": "busan_vs_jeju",
        "description": (
            "Busan vs Jeju: Which Korean Beach Is Right for You? Busan = city-energy and "
            "skyline sunsets. Jeju = volcanic black sand and waterfall hikes. Side-by-side "
            "guide with free 3-day itinerary inside.\n\n"
            "#BusanTravel #JejuIsland #KoreaTravel #BeachVacation #VisitKorea"
        ),
    },
    {
        "slug": "korea-7-day-itinerary-1000-budget",
        "headline": "Korea 7-Day Itinerary ($1,000 Budget)",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, open travel journal with korea map, train "
            "ticket, polaroid of palace, brass pen and dried cherry blossom, soft window "
            "light, neutral cream and sage palette, premium editorial flatlay"
        ),
        "url_base": "https://korlens.app",
        "campaign": "korea_7day_itinerary",
        "description": (
            "Korea Travel Itinerary 7 Days: $1,000 Total Budget. Seoul to Busan to Jeju "
            "with day-by-day costs, hostel picks and KTX hacks. Free downloadable PDF "
            "with map and packing list inside.\n\n"
            "#KoreaTravel #SeoulTravel #BudgetTravel #TravelItinerary #VisitKorea"
        ),
    },
    {
        "slug": "kdrama-filming-locations-visit-korea",
        "headline": "Best K-Drama Locations You Can Visit",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, scenic korean drama-style location with "
            "stone steps, autumn maple leaves, traditional hanok rooftop, golden hour "
            "cinematic light, warm sienna and amber palette, premium editorial cover"
        ),
        "url_base": "https://korlens.app",
        "campaign": "kdrama_locations",
        "description": (
            "Best K-Drama Filming Locations You Can Visit. From Bukchon hanok stairs to "
            "Namsan tower benches, walk through 10 iconic Korean drama scenes in one trip. "
            "Free walking-route map inside.\n\n"
            "#KDrama #KoreaTravel #SeoulTravel #KDramaLocations #VisitKorea"
        ),
    },
    {
        "slug": "korean-convenience-store-tier-list",
        "headline": "Korean Convenience Store Tier List",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, neat flatlay top down korean convenience "
            "store snacks ramen kimbap banana milk arranged in tier list grid on cream "
            "background, vibrant pop colors, magazine editorial flatlay, premium quality"
        ),
        "url_base": "https://korlens.app",
        "campaign": "convenience_store_tier",
        "description": (
            "Korean Convenience Store Tier List (Foodie Edition). 30 must-try snacks "
            "from Seoul convenience stores ranked S to F by a Korean foodie. Ramen, "
            "kimbap, banana milk, ice cream. Free shopping list inside.\n\n"
            "#KoreanFood #SeoulTravel #KoreaTravel #Foodie #ConvenienceStore"
        ),
    },
    # ========== C. Mega Bundle (5) ==========
    {
        "slug": "k-culture-mega-bundle-5-pdfs",
        "headline": "K-Culture Mega Bundle: 5 PDFs, 60 Pages",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, neat flatlay 5 korean cultural ebooks "
            "stacked with hanji paper, ink brush, dried flowers, brass pen, soft window "
            "light, warm cream and sage palette, premium editorial product mockup"
        ),
        "url_base": "https://ghdejr.gumroad.com/l/xuqbai",
        "campaign": "kculture_mega_bundle",
        "description": (
            "K-Culture Mega Bundle: 5 Premium PDFs in 60 Pages. Saju basics, Hangul "
            "calligraphy, Korean tea ceremony, K-aesthetic Notion templates, travel "
            "picks. $29.99 (vs $75 separate). Free 8-page sample inside.\n\n"
            "#KoreanCulture #DigitalDownload #Hangul #Saju #PrintablePlanner"
        ),
    },
    {
        "slug": "korean-tea-ceremony-chatgpt-prompts",
        "headline": "Korean Tea Ceremony ChatGPT Prompts",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, traditional korean tea ceremony flatlay "
            "with celadon teapot, green tea leaves, hanji paper, brass tray, soft window "
            "light, sage and cream palette, premium editorial product photography"
        ),
        "url_base": "https://ghdejr.gumroad.com/l/xuqbai",
        "campaign": "tea_ceremony_prompts",
        "description": (
            "Korean Tea Ceremony Prompts for ChatGPT (50 Prompts). Plan a darye, write "
            "tea ceremony invitations, learn the 5 senses ritual. 50 ready-to-paste "
            "prompts in the K-Culture Mega Bundle. $29.99.\n\n"
            "#ChatGPTPrompts #KoreanCulture #TeaCeremony #AIPrompts #Mindfulness"
        ),
    },
    {
        "slug": "kpop-fan-compatibility-chart-zodiac",
        "headline": "K-pop Fan Compatibility Chart",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, vibrant k-pop fan compatibility chart "
            "grid with 12 korean zodiac animals in cute kawaii illustration, pastel "
            "pink and lavender palette, magazine cover layout, premium editorial design"
        ),
        "url_base": "https://ghdejr.gumroad.com/l/xuqbai",
        "campaign": "kpop_compatibility_chart",
        "description": (
            "K-pop Fan Compatibility Chart by Korean Zodiac. Match your birth-year "
            "animal with your bias's. Tiger fans go ride-or-die, Rabbit fans go "
            "soft-stan. Free chart inside the K-Culture Mega Bundle.\n\n"
            "#Kpop #KpopFan #KoreanZodiac #Compatibility #FanLife"
        ),
    },
    {
        "slug": "hangul-aesthetic-notion-templates-10",
        "headline": "Hangul Aesthetic Notion Templates",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, aesthetic notion template laptop mockup "
            "with korean hangul calligraphy headers, dried flowers, ink brush, cream "
            "linen background, soft beige and sage palette, premium aesthetic flat lay"
        ),
        "url_base": "https://ghdejr.gumroad.com/l/xuqbai",
        "campaign": "hangul_notion_10",
        "description": (
            "Hangul Aesthetic Notion Templates: 10 Designs. Daily planner, study tracker, "
            "habit grid, mood journal — all with Korean hangul calligraphy headers and "
            "soft pastel widgets. Inside K-Culture Mega Bundle. $29.99.\n\n"
            "#NotionTemplate #Hangul #KoreanAesthetic #StudyAesthetic #DigitalPlanner"
        ),
    },
    {
        "slug": "travel-korea-like-local-top-50",
        "headline": "Travel Korea Like a Local: Top 50",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, open travel journal with korea map "
            "polaroid photos of palace street food and hanok, brass pen, dried "
            "flowers, soft window light, warm cream and amber palette, editorial flatlay"
        ),
        "url_base": "https://ghdejr.gumroad.com/l/xuqbai",
        "campaign": "korea_top_50_picks",
        "description": (
            "Travel Korea Like a Local: Top 50 Picks (Free Sample). Cafes, hanbok "
            "rentals, palaces, hidden bars, night markets. Curated by a Korean for "
            "first-timers. 8-page sample free inside the K-Culture Mega Bundle.\n\n"
            "#KoreaTravel #SeoulTravel #VisitKorea #TravelGuide #HiddenGems"
        ),
    },
    # ========== D. Saju Diary qcjtu (3) ==========
    {
        "slug": "saju-diary-12-month-self-discovery",
        "headline": "12-Month Saju Diary: Self-Discovery",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, open journal workbook with korean saju "
            "monthly forecast pages, brass pen, dried lavender, soft window light, "
            "linen tablecloth, neutral cream and sage palette, premium editorial flatlay"
        ),
        "url_base": "https://ghdejr.gumroad.com/l/qcjtu",
        "campaign": "saju_diary_self_discovery",
        "description": (
            "12-Month Saju Diary: Korean Astrology Self-Discovery. A guided yearlong "
            "journal with 365 daily prompts, 12 monthly saju forecasts and a birth "
            "chart worksheet. Free 30-page preview inside.\n\n"
            "#Saju #KoreanAstrology #Journal #SelfDiscovery #DigitalPlanner"
        ),
    },
    {
        "slug": "daily-saju-reflection-bilingual-workbook",
        "headline": "Daily Saju Reflection Workbook (EN/KR)",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, open bilingual saju workbook on linen "
            "tablecloth with brass pen, hanji bookmark, dried wildflowers, soft window "
            "light, cream and sage palette, premium editorial flatlay magazine layout"
        ),
        "url_base": "https://ghdejr.gumroad.com/l/qcjtu",
        "campaign": "saju_bilingual_workbook",
        "description": (
            "Daily Saju Reflection Workbook (Bilingual EN/KR). 365 daily prompts side "
            "by side in English and Hangul. Learn Korean while exploring saju astrology. "
            "Free 30-page preview before buying.\n\n"
            "#Saju #LearnKorean #Hangul #Journal #Bilingual"
        ),
    },
    {
        "slug": "year-of-snake-2026-saju-diary-preview",
        "headline": "Year of the Snake 2026: Saju Preview",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, stylized korean ink-brush snake coiled "
            "around saju calendar 2026 on parchment, gold and emerald palette, "
            "traditional minhwa folk painting style, premium magazine editorial cover"
        ),
        "url_base": "https://ghdejr.gumroad.com/l/qcjtu",
        "campaign": "snake_2026_preview",
        "description": (
            "Year of the Snake 2026: Saju Diary Sneak Peek. The wood-snake year favors "
            "patience and quiet wins. See your monthly forecast in the free 30-page "
            "Saju Diary preview before the new year hits.\n\n"
            "#YearOfTheSnake #Saju2026 #KoreanAstrology #LunarNewYear #Saju"
        ),
    },
    # ========== E. Tax-N-Benefit (2) ==========
    {
        "slug": "korean-tax-refund-2026-may-31-deadline",
        "headline": "Korean Tax Refund 2026: May 31 Deadline",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, organized tax filing flatlay with "
            "calculator, korean won banknotes, calendar marked may 31, brass pen, "
            "soft natural light, navy and gold palette, premium editorial magazine cover"
        ),
        "url_base": "https://tax-n-benefit-api.vercel.app",
        "campaign": "tax_refund_may31",
        "description": (
            "Korean Tax Refund Hack: 2026 Income Tax Filing (May 31 Deadline). Freelancers, "
            "side-hustlers and small biz owners — file in 5 minutes online and reclaim "
            "missed deductions. 9.9% fee, no consultant call needed.\n\n"
            "#KoreaTax #IncomeTax #TaxRefund #Freelancer #SideHustle"
        ),
    },
    {
        "slug": "korea-9pct-tax-filing-vs-30pct-fee",
        "headline": "9.9% Korean Tax Filing vs 30% Fees",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, side-by-side comparison chart 9.9 percent "
            "vs 30 percent tax filing fee on clean modern desk with calculator and "
            "laptop, navy and gold palette, premium editorial magazine cover layout"
        ),
        "url_base": "https://tax-n-benefit-api.vercel.app",
        "campaign": "tax_99_vs_30",
        "description": (
            "9.9% Fee Korean Tax Filing — vs 30% Competitors. Most Korean tax filing "
            "services charge up to 30% of your refund. Ours is flat 9.9%, fully online, "
            "5-minute filing. Free refund estimator inside.\n\n"
            "#KoreaTax #TaxFiling #IncomeTax #Freelancer #SmallBusiness"
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


def utm_url(base, campaign):
    sep = "&" if "?" in base else "?"
    return (
        f"{base}{sep}utm_source=pinterest"
        f"&utm_medium=affiliate&utm_campaign={campaign}"
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

    for pin in PINS:
        slug = pin["slug"]
        if slug in existing_slugs:
            log(f"SKIP {slug} (already in queue)")
            continue
        log(f"=== {slug} ===")

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
            overlay_text(raw_path, pin["headline"], png_path)
            log(f"  overlay -> {png_path.name} ({png_path.stat().st_size//1024}KB)")
        except subprocess.CalledProcessError as e:
            log(f"  ffmpeg FAIL, using raw: {(e.stderr or b'')[:100]!r}")
            png_path = raw_path

        full_url = utm_url(pin["url_base"], pin["campaign"])
        full_desc = pin["description"] + f"\n\nFull guide: {full_url}"

        q["made"].append({
            "slug": slug,
            "kw": pin["campaign"],
            "title": pin["headline"],
            "made_at": datetime.datetime.now().isoformat(),
            "image_path": str(png_path),
            "description": full_desc,
            "destination_url": full_url,
            "source": "global_20_2026_05_05",
            "status": "queued",
        })
        added += 1
        # save incrementally so partial runs don't lose progress
        QUEUE_JSON.write_text(
            json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        time.sleep(8)  # spread requests to avoid Pollinations 429

    log(f"DONE: added {added} pins, failed {len(failed)}, queue total = {len(q['made'])}")
    if failed:
        log(f"FAILED slugs: {failed}")
    return added


if __name__ == "__main__":
    main()
