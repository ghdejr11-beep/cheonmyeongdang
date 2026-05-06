"""pinterest_pins — 5 more pins v2 (heavy hit Korea travel + Saju keywords).

Generates 5 standalone English Pinterest pins (1000x1500). Different focus
from previous batches: Korean food / hidden gems / saju love / hanbok / temple stay.

Output: queue/{slug}.png + queue.json append.
"""
import os, sys, json, urllib.request, urllib.parse, datetime, subprocess, time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
QUEUE_DIR = ROOT / "queue"
QUEUE_DIR.mkdir(exist_ok=True)
QUEUE_JSON = ROOT / "queue.json"
LOG = ROOT / "logs" / f"more5v2_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


PINS = [
    {
        "slug": "olive-young-shopping-guide-pin",
        "title": "Olive Young\\nWhat to Actually Buy",
        "headline": "Olive Young: What to Actually Buy in 2026",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, neat flatlay of korean skincare bottles "
            "anua beauty of joseon skin1004 numbuzin on cream linen background, soft "
            "morning window light, magazine cover layout, beige pink palette, premium "
            "editorial photography top down"
        ),
        "url_base": "https://korlens.app/blog/olive-young-shopping-guide",
        "campaign": "olive_young_pin",
        "description": (
            "Olive Young in Seoul: A First-Timer's Shopping Strategy 2026. What to "
            "buy at Olive Young vs duty-free vs pharmacies — written by Seoulites who "
            "shop there every month. The genuinely cheaper-here list inside.\n\n"
            "#KBeauty #OliveYoung #KoreanSkincare #SeoulShopping #KoreanCulture"
        ),
    },
    {
        "slug": "korean-temple-stay-experience",
        "title": "Korean Temple Stay\\n3-Day Reset",
        "headline": "Korean Temple Stay 3-Day Reset",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, traditional korean buddhist temple "
            "haedong yonggungsa ocean cliff, monks in grey robes meditating, soft "
            "golden hour lighting cherry blossom petals, magazine cover layout, "
            "deep navy and amber palette, cinematic travel editorial photography"
        ),
        "url_base": "https://korlens.app/blog",
        "campaign": "temple_stay_pin",
        "description": (
            "Korean Temple Stay 3-Day Reset (Templestay). What it actually feels "
            "like to spend 3 days at a Korean buddhist temple — meditation, monk "
            "meals, 4am bell ceremonies. A Seoul mind-detox antidote.\n\n"
            "#KoreaTravel #Templestay #VisitKorea #BuddhistMeditation #KoreanCulture"
        ),
    },
    {
        "slug": "hanbok-rental-bukchon-photo",
        "title": "Hanbok Rental\\nBukchon Photo Spots",
        "headline": "Hanbok Rental + Bukchon Photo Spots",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, woman in pastel pink hanbok walking "
            "down bukchon hanok village stone path with traditional roofs and red "
            "lantern, soft afternoon golden light, cherry blossom petals, magazine "
            "cover layout, premium editorial travel photography"
        ),
        "url_base": "https://korlens.app/blog",
        "campaign": "hanbok_bukchon_pin",
        "description": (
            "Hanbok Rental + Bukchon Photo Spots Map. Where to rent (₩15,000-30,000), "
            "the 9 historic stone-path photo angles, why hanbok gets you free palace "
            "entry, and the rule about modern accessories.\n\n"
            "#KoreaTravel #Hanbok #SeoulItinerary #VisitKorea #BukchonHanok"
        ),
    },
    {
        "slug": "saju-compatibility-couples-2026",
        "title": "Saju Compatibility\\nFor Couples 2026",
        "headline": "Saju Compatibility for Couples 2026",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, two intertwined korean saju charts "
            "with hanja calligraphy on parchment, gold leaf accents, soft candlelight, "
            "rose petals, mystical romantic atmosphere, magazine cover layout, "
            "deep crimson and gold palette, cinematic editorial photography"
        ),
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "saju_couples_pin",
        "description": (
            "Saju Compatibility for Couples 2026 — the 1,000-year-old Korean "
            "astrology system that maps your birth chart against your partner's "
            "across 5 elements. Free reading inside, no signup.\n\n"
            "#KoreanAstrology #SajuCompatibility #SoulmateTest #BirthChart "
            "#KoreanCulture"
        ),
    },
    {
        "slug": "korean-bbq-etiquette-foreigners",
        "title": "Korean BBQ\\nThe 7 Rules",
        "headline": "Korean BBQ: The 7 Rules Foreigners Miss",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, sizzling korean bbq grill at table "
            "samgyeopsal pork belly with banchan side dishes, soft warm cinematic "
            "restaurant lighting, korean restaurant interior background bokeh, "
            "magazine cover layout, deep amber and emerald palette, cinematic "
            "editorial food photography"
        ),
        "url_base": "https://korlens.app/blog/korean-bbq-etiquette",
        "campaign": "korean_bbq_pin",
        "description": (
            "Korean BBQ: The 7 Rules Foreigners Miss. What to never do at a Korean "
            "BBQ table (pour your own drink first), how to use the lettuce wrap "
            "correctly, what banchan refills are free, and the soju etiquette "
            "K-drama actually got right.\n\n"
            "#KoreaTravel #KoreanBBQ #SeoulFood #VisitKorea #KoreanCulture"
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
            "source": "more_5_v2_2026_05_06",
            "status": "queued",
        })
        added += 1
        time.sleep(2)

    QUEUE_JSON.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"DONE: added {added} pins, queue total = {len(q['made'])}")
    return added


if __name__ == "__main__":
    main()
