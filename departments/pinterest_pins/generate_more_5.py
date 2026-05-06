"""pinterest_pins — 5 more pins (mix: cheonmyeongdang Saju + KORLENS Klook).

Generates 5 standalone English Pinterest pins (1000x1500). Targets long-tail
keywords for 천명당 Saju (US-east global) and KORLENS Korea travel niche.

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
LOG = ROOT / "logs" / f"more5_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


PINS = [
    {
        "slug": "saju-vs-western-astrology-difference",
        "title": "Korean Saju vs\\nWestern Astrology",
        "headline": "Korean Saju vs Western Astrology",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, split screen: left half traditional "
            "korean saju chart with hanja characters parchment lantern light, right "
            "half western zodiac wheel constellations indigo night sky with stars, "
            "split editorial magazine cover layout, deep navy and amber palette"
        ),
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "saju_vs_western",
        "description": (
            "Korean Saju vs Western Astrology — what the 1,000-year-old Korean "
            "system reveals that birth-month signs miss. Saju maps your birth "
            "year, month, day AND hour into 8 characters across 5 elements. "
            "Free reading inside.\n\n"
            "#KoreanAstrology #Saju #Astrology #BirthChart #FourPillars"
        ),
    },
    {
        "slug": "naver-map-vs-google-maps-korea",
        "title": "Why Google Maps\\nFails in Korea",
        "headline": "Why Google Maps Fails in Korea",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, smartphone showing korean naver map "
            "navigation screen seoul subway routing, side by side with crossed out "
            "google maps, soft cafe morning light flat lay top down, magazine cover "
            "layout, premium travel editorial photography, beige and amber palette"
        ),
        "url_base": "https://korlens.app/blog",
        "campaign": "naver_vs_google",
        "description": (
            "Why Google Maps fails in Korea (and what to use instead). Korean "
            "government does not allow Google to host detailed map data overseas — "
            "walking and transit routing is degraded inside Korea. Install Naver "
            "Map and Kakao Map before you fly.\n\n"
            "#KoreaTravel #SeoulTravel #TravelTips #VisitKorea #FirstTrip"
        ),
    },
    {
        "slug": "kakaotaxi-foreigner-guide-korea",
        "title": "KakaoTaxi for\\nForeigners in Korea",
        "headline": "KakaoTaxi for Foreigners in Korea",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, korean taxi at seoul gangnam street "
            "night with neon signs reflection, smartphone showing kakaotaxi app in "
            "english, soft bokeh city lights, cinematic travel magazine cover layout, "
            "deep navy and warm amber palette, premium editorial photography"
        ),
        "url_base": "https://korlens.app/blog",
        "campaign": "kakaotaxi_foreigner",
        "description": (
            "KakaoTaxi for foreigners in Korea — yes you can book in English, no "
            "you do not need a Korean phone number. Same metered rate as a regular "
            "taxi, no language friction, works at every airport and city. Setup in "
            "5 minutes once you have a Korean eSIM.\n\n"
            "#KoreaTravel #KakaoTaxi #SeoulTravel #TravelHacks #VisitKorea"
        ),
    },
    {
        "slug": "korea-travel-budget-7days-2026",
        "title": "Korea 7-Day\\nBudget Breakdown 2026",
        "headline": "Korea 7-Day Budget Breakdown 2026",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, korean won bills 50000 ten thousand "
            "fanned out next to seoul subway card and small notebook with itinerary "
            "on linen tablecloth, soft morning window light flat lay top down, "
            "magazine cover layout, beige and emerald palette, premium aesthetic"
        ),
        "url_base": "https://korlens.app/blog",
        "campaign": "korea_budget_7days",
        "description": (
            "Korea 7-day budget breakdown 2026 — exactly what we spent on a "
            "Seoul plus Jeju trip. Hotels, food, transport, eSIM, attractions — "
            "honest line-by-line numbers in USD and KRW. No upsells.\n\n"
            "#KoreaTravel #SeoulTravel #JejuIsland #TravelBudget #VisitKorea"
        ),
    },
    {
        "slug": "what-is-saju-1000-year-korean-astrology",
        "title": "What is Saju?\\n1,000 Years of Korea",
        "headline": "What is Saju? 1,000 Years of Korean Astrology",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, ancient korean joseon dynasty hanja "
            "manuscript with glowing brush ink calligraphy, candle and incense smoke, "
            "wooden temple pillar background, mystical golden hour lighting, "
            "magazine cover layout, deep crimson and gold palette, cinematic"
        ),
        "url_base": "https://cheonmyeongdang.vercel.app/en",
        "campaign": "what_is_saju_pinterest",
        "description": (
            "What is Saju? The 1,000-year-old Korean astrology system that reads "
            "your destiny from your birth year, month, day and hour. Eight "
            "characters across four pillars. The framework K-pop fans and "
            "Korean dramas keep referencing.\n\n"
            "#Saju #KoreanAstrology #Astrology #KoreanCulture #BirthChart"
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
            "source": "more_5_2026_05_06",
            "status": "queued",
        })
        added += 1
        time.sleep(2)

    QUEUE_JSON.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"DONE: added {added} pins, queue total = {len(q['made'])}")
    return added


if __name__ == "__main__":
    main()
