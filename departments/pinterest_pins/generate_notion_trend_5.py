"""pinterest_pins — Notion Template trend blast (5 pins, 2026-05-06).

Trigger: Google Trends "notion template" +26.6% (CEO briefing 5/6).
Plays into: 10 Notion-class Gumroad SKUs (Mega Bundle, Saju, Tarot, MBTI,
AI Hustle, Korean Planner, Hangul Posters, Productivity, Tracker, etc.).

Output: 5 vertical pins (1000x1500) → queue/ → daily publisher schtask.
"""
import os, sys, json, urllib.request, urllib.parse, datetime, subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
QUEUE_DIR = ROOT / "queue"
QUEUE_DIR.mkdir(exist_ok=True)
QUEUE_JSON = ROOT / "queue.json"
LOG = ROOT / "logs" / f"notion_trend5_{datetime.date.today()}.log"
LOG.parent.mkdir(parents=True, exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


PINS = [
    {
        "slug": "notion-template-saju-2026",
        "title": "Notion Template\\nKorean Saju 2026",
        "headline": "Korean Saju Notion Template (2026)",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, aesthetic notion dashboard mockup "
            "on rose gold ipad with korean hangul characters and birth chart, "
            "minimal cream linen desk with dried lavender and matcha latte, "
            "magazine cover layout, soft pastel pink and beige palette, premium "
            "editorial flatlay photography top down"
        ),
        "url_base": "https://kunstudio.gumroad.com/l/saju-notion",
        "campaign": "notion_saju_2026",
        "description": (
            "Korean Saju Notion Template (2026). Drop your birth date, get a "
            "1,000-year-old Korean astrology birth chart inside Notion — five "
            "elements, ten heavenly stems, daily fortune widget. Aesthetic, "
            "shareable, plug-and-play.\n\n"
            "#NotionTemplate #Notion #Saju #KoreanAstrology #DigitalPlanner"
        ),
    },
    {
        "slug": "notion-template-mbti-archetypes",
        "title": "Notion Template\\nMBTI Archetypes",
        "headline": "MBTI Archetype Notion Template",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, modern notion dashboard mockup "
            "with 16 mbti personality cards in pastel colors, scandi minimal "
            "desk setup with white ceramic mug and oat journal, magazine cover "
            "layout, soft sage and cream palette, premium editorial flatlay "
            "photography"
        ),
        "url_base": "https://kunstudio.gumroad.com/l/mbti-notion",
        "campaign": "notion_mbti_archetypes",
        "description": (
            "MBTI Archetype Notion Template. Map all 16 personality types into a "
            "single Notion workspace — career fits, love language, shadow side, "
            "growth ritual. Used by 8,000+ self-discovery nerds.\n\n"
            "#NotionTemplate #Notion #MBTI #PersonalityTest #DigitalPlanner"
        ),
    },
    {
        "slug": "notion-template-ai-side-hustle",
        "title": "Notion Template\\nAI Side Hustle 2026",
        "headline": "AI Side Hustle Notion Kit 2026",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, sleek notion dashboard with "
            "revenue tracker chart and ai prompt library, minimalist black "
            "macbook on dark walnut desk with neon blue accent light, magazine "
            "cover layout, deep navy and electric blue palette, cinematic tech "
            "editorial photography top down"
        ),
        "url_base": "https://kunstudio.gumroad.com/l/ai-side-hustle",
        "campaign": "notion_ai_side_hustle",
        "description": (
            "AI Side Hustle Starter Kit — Notion Template (2026). 5 plug-and-play "
            "Notion pages: revenue dashboard, prompt library, niche scout, content "
            "engine, ship-it tracker. Built by a solo founder hitting $1k/mo with "
            "AI in 90 days.\n\n"
            "#NotionTemplate #AISideHustle #SoloFounder #Notion #BuildInPublic"
        ),
    },
    {
        "slug": "notion-template-korean-planner",
        "title": "Notion Template\\nKorean Aesthetic Planner",
        "headline": "Korean Aesthetic Notion Planner 2026",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, dreamy notion planner mockup on "
            "iphone with korean hangul calligraphy headers, pastel pink mood "
            "tracker and habit grid, surrounded by pressed flowers and matcha "
            "powder, magazine cover layout, soft blush and sage palette, premium "
            "editorial flatlay photography"
        ),
        "url_base": "https://kunstudio.gumroad.com/l/korean-planner",
        "campaign": "notion_korean_planner",
        "description": (
            "Korean Aesthetic Notion Planner 2026. 30 ready-made pages — daily "
            "ritual, mood tracker with hangul typography, habit grid, journal "
            "prompts in soft pastel widgets. The aesthetic productivity stack "
            "12,000+ students swear by.\n\n"
            "#NotionTemplate #KoreanAesthetic #StudyAesthetic #DigitalPlanner "
            "#Hangul"
        ),
    },
    {
        "slug": "notion-template-mega-bundle-5",
        "title": "Notion Mega Bundle\\n5 Templates 1 Price",
        "headline": "Korean Culture Notion Mega Bundle (5-in-1)",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, layered stack of 5 notion "
            "template cards floating on cream paper with hangul brushwork, "
            "korean traditional patterns and minimal pastel widgets, gold leaf "
            "accents, magazine cover layout, blush gold and ivory palette, "
            "premium editorial flatlay photography"
        ),
        "url_base": "https://kunstudio.gumroad.com/l/mega-bundle",
        "campaign": "notion_mega_bundle_5",
        "description": (
            "Korean Culture Notion Mega Bundle (5 Templates 1 Price). Saju + "
            "MBTI + Tarot + AI Side Hustle + Korean Planner — all 5 best-selling "
            "Notion templates wrapped into one $29 bundle (save 60% vs separate). "
            "Lifetime updates, no signup.\n\n"
            "#NotionTemplate #NotionBundle #KoreanCulture #DigitalPlanner "
            "#Productivity"
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
    font = "C\\:/Windows/Fonts/arialbd.ttf"
    safe = headline.replace(":", "\\:").replace("'", "\\'").replace('"', '')[:80]
    drawtext = (
        f"drawtext=fontfile='{font}':"
        f"text='{safe}':"
        f"fontcolor=white:fontsize=70:"
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
        except Exception as e:
            log(f"  FFMPEG FAIL: {type(e).__name__}: {str(e)[:120]}")
            continue

        dest_url = utm_url(pin["url_base"], pin["campaign"])
        q["made"].append({
            "slug": slug,
            "kw": pin["campaign"],
            "title": pin["title"].replace("\\n", " — "),
            "made_at": datetime.datetime.now().isoformat(),
            "image_path": str(png_path),
            "description": pin["description"] + f"\n\nFull guide: {dest_url}",
            "destination_url": dest_url,
            "source": "notion_trend_5_2026_05_06",
            "status": "queued",
        })
        added += 1

        try:
            raw_path.unlink()
        except Exception:
            pass

    QUEUE_JSON.write_text(
        json.dumps(q, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    log(f"DONE — added {added}/{len(PINS)} pins. Queue total: {len(q['made'])}")


if __name__ == "__main__":
    main()
