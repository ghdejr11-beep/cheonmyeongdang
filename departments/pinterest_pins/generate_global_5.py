"""pinterest_pins — Global English 5-pin batch generator (2026-05-05).

Generates 5 standalone English Pinterest pins (1000x1500) targeting global free traffic.
Targets: cheonmyeongdang.vercel.app/en, korlens.app, Gumroad.

Output: queue/{slug}.png + queue/queue.json (appended to existing made[]).
Pollinations Flux (free, no API key). UTM tagged URLs.
"""
import os, sys, json, urllib.request, urllib.parse, datetime, subprocess, time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
QUEUE_DIR = ROOT / "queue"
QUEUE_DIR.mkdir(exist_ok=True)
QUEUE_JSON = ROOT / "queue.json"
LOG = ROOT / "logs" / f"global5_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# 5 global English pins targeting Pinterest SEO + revenue funnels
PINS = [
    {
        "slug": "korean-saju-beginners-guide",
        "title": "How to Read Korean Saju\\nA Beginner's Guide",
        "headline": "How to Read Korean Saju: A Beginner's Guide",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, mystical korean astrology saju chart "
            "with traditional ink brush hanja characters on parchment, soft golden "
            "lantern lighting, deep navy and red palette, elegant magazine cover "
            "layout, premium editorial photography"
        ),
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "saju_beginners_guide",
        "description": (
            "How to Read Korean Saju (사주): A Beginner's Guide. Discover the 1,000-year-old "
            "Korean astrology system that decodes your destiny from your birth year, month, "
            "day and hour. Learn the four pillars, ten heavenly stems and twelve earthly "
            "branches in plain English. Free reading inside.\n\n"
            "#KoreanCulture #Saju #Astrology #KoreanAstrology #Hangul"
        ),
    },
    {
        "slug": "seoul-hidden-gems-locals-pick",
        "title": "Top 7 Hidden Gems\\nin Seoul",
        "headline": "Top 7 Hidden Gems in Seoul (Local's Pick)",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, hidden alley in seoul ikseondong "
            "hanok village at golden hour, soft lantern glow, cherry blossom petals, "
            "moody cinematic travel photography, warm peach palette, magazine cover layout"
        ),
        "url_base": "https://korlens.app",
        "campaign": "seoul_hidden_gems",
        "description": (
            "Top 7 Hidden Gems in Seoul (Local's Pick). Skip the tourist traps. A Seoul "
            "native shares 7 secret cafes, hanok alleys and rooftop sunsets the guidebooks "
            "miss. Saved by 12,000+ travelers. Map and walking route inside.\n\n"
            "#SeoulTravel #KoreaTravel #HiddenGems #VisitKorea #KoreanCulture"
        ),
    },
    {
        "slug": "korean-zodiac-compatibility-soulmate",
        "title": "Korean Zodiac Compatibility\\nFind Your Soulmate",
        "headline": "Korean Zodiac Compatibility: Your Soulmate by Birth Year",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, twelve korean zodiac animals arranged "
            "in circular mandala, gold leaf on dusty rose background, traditional "
            "minhwa folk painting style, soft watercolor textures, romantic pastel palette"
        ),
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "zodiac_compatibility",
        "description": (
            "Korean Zodiac Compatibility: Your Soulmate by Birth Year. The 12 Korean zodiac "
            "animals (rat, ox, tiger, rabbit, dragon, snake, horse, sheep, monkey, rooster, "
            "dog, pig) reveal who you should and should not date. Free compatibility "
            "calculator inside.\n\n"
            "#KoreanZodiac #Saju #Compatibility #KoreanAstrology #SoulmateTest"
        ),
    },
    {
        "slug": "hangul-calligraphy-notion-template",
        "title": "Hangul Calligraphy\\nNotion Template",
        "headline": "Hangul Calligraphy Notion Template (Aesthetic 2026)",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, aesthetic notion template mockup with "
            "korean hangul calligraphy on cream paper, ink brush strokes, dried flowers, "
            "minimalist desk flat lay top down, soft beige and sage palette, premium aesthetic"
        ),
        "url_base": "https://kunstudio.gumroad.com",
        "campaign": "hangul_notion_template",
        "description": (
            "Hangul Calligraphy Notion Template (Aesthetic 2026). 30 ready-to-use Notion "
            "pages with Korean hangul calligraphy headers, soft pastel widgets, mood "
            "trackers and journal prompts. The aesthetic productivity stack 12,000+ "
            "students swear by.\n\n"
            "#NotionTemplate #Hangul #KoreanAesthetic #StudyAesthetic #DigitalPlanner"
        ),
    },
    {
        "slug": "saju-diary-12-month-workbook",
        "title": "Saju Diary\\n12-Month Workbook",
        "headline": "Saju Diary 12-Month Workbook (Free Preview)",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, open journal workbook with korean saju "
            "monthly horoscope pages, brass pen, dried lavender, soft window light, "
            "linen tablecloth, neutral cream and sage palette, premium editorial flatlay"
        ),
        "url_base": "https://kunstudio.gumroad.com/l/qcjtu",
        "campaign": "saju_diary_workbook",
        "description": (
            "Saju Diary 12-Month Workbook (Free Preview). A guided yearlong journal "
            "rooted in 1,000-year-old Korean astrology. 365 daily prompts, 12 monthly "
            "saju forecasts and a birth chart worksheet. Download the free 30-page "
            "preview before buying.\n\n"
            "#Saju #KoreanAstrology #Journal #Workbook #SelfDiscovery"
        ),
    },
]


def fetch_image(prompt, slug):
    seed = abs(hash(slug)) % 100000
    url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
        f"?width=1000&height=1500&seed={seed}&nologo=true&model=flux"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def overlay_text(in_path, headline, out_path):
    """ffmpeg drawtext - bold white headline on dark box, top of pin."""
    font = "C\\:/Windows/Fonts/arialbd.ttf"
    safe = headline.replace(":", "\\:").replace("'", "\\'").replace('"', '')[:80]
    drawtext = (
        f"drawtext=fontfile='{font}':"
        f"text='{safe}':"
        f"fontcolor=white:fontsize=72:"
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
    return f"{base}{sep}utm_source=pinterest&utm_medium=social&utm_campaign={campaign}"


def main():
    if QUEUE_JSON.exists():
        q = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
    else:
        q = {"made": []}
    if "made" not in q:
        q["made"] = []

    existing_slugs = {x.get("slug") for x in q["made"]}
    added = 0

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
            continue

        try:
            overlay_text(raw_path, pin["headline"], png_path)
            log(f"  overlay -> {png_path.name} ({png_path.stat().st_size//1024}KB)")
        except subprocess.CalledProcessError as e:
            log(f"  ffmpeg FAIL, using raw: {e.stderr[:100] if e.stderr else ''}")
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
            "source": "global_5_2026_05_05",
            "status": "queued",
        })
        added += 1
        time.sleep(2)

    QUEUE_JSON.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"DONE: added {added} pins, queue total = {len(q['made'])}")
    return added


if __name__ == "__main__":
    main()
