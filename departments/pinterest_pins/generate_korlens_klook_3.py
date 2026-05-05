"""pinterest_pins — KORLENS x Klook 3-pin batch (2026-05-06).

Generates 3 standalone English Pinterest pins (1000x1500) targeting global
foreign-traveler search traffic. Each pin links to a brand-new KORLENS blog
post with embedded Klook AID 120494 (eSIM 20% / hotels 6.5% commission).

Output: queue/{slug}.png + queue.json append.
Requires: ffmpeg on PATH, internet (Pollinations Flux, free, no API key).
"""
import os, sys, json, urllib.request, urllib.parse, datetime, subprocess, time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
QUEUE_DIR = ROOT / "queue"
QUEUE_DIR.mkdir(exist_ok=True)
QUEUE_JSON = ROOT / "queue.json"
LOG = ROOT / "logs" / f"korlens_klook_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


PINS = [
    {
        "slug": "korea-esim-2026-first-timer-guide",
        "title": "Korea eSIM 2026\\nFirst-Timer's Guide",
        "headline": "Korea eSIM 2026: First-Timer's Guide",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, smartphone showing korea map signal "
            "bars and esim setup screen on cafe table with iced americano, soft "
            "morning sunlight, seoul skyline soft bokeh background, magazine cover "
            "layout, premium travel editorial photography, warm peach palette"
        ),
        "url_base": "https://korlens.app/blog/korea-esim-guide",
        "campaign": "korea_esim_pinterest",
        "description": (
            "Korea eSIM 2026: First-Timer's Guide. Skip the airport SIM counter. "
            "Everything you need about Korean mobile data: which plan size for "
            "your trip, eSIM vs physical SIM, hotspot rules, Naver Map setup, "
            "and the cheapest no-counter option that works the moment you land.\n\n"
            "#KoreaTravel #VisitKorea #TravelTips #Connectivity #FirstTrip "
            "#TravelHacks"
        ),
    },
    {
        "slug": "incheon-airport-to-seoul-arex-vs-bus",
        "title": "Incheon to Seoul\\nAREX, Bus, or Taxi?",
        "headline": "Incheon Airport to Seoul: Honest Comparison",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, AREX express train arriving at "
            "incheon airport platform, traveler with luggage, soft window light, "
            "modern airport architecture, navy and ivory palette, cinematic "
            "travel magazine cover layout, premium editorial photography"
        ),
        "url_base": "https://korlens.app/blog/incheon-airport-to-seoul",
        "campaign": "incheon_to_seoul_pinterest",
        "description": (
            "Incheon Airport to Seoul: AREX, Bus, or Taxi? Five real ways to get "
            "from ICN into central Seoul ranked by speed, cost and luggage-"
            "friendliness. Written by Seoul locals. Updated for 2026.\n\n"
            "#KoreaTravel #SeoulTravel #IncheonAirport #TravelTips #VisitKorea "
            "#FirstTrip"
        ),
    },
    {
        "slug": "korea-travel-essentials-checklist-2026",
        "title": "Korea Travel\\n2026 Essentials",
        "headline": "Korea Travel 2026 Essentials Checklist",
        "image_prompt": (
            "vertical pinterest pin 1000x1500, flat lay of korea travel essentials "
            "passport hanbok keychain map naver map screen tteok-bokki postcard "
            "korean won bills, beige linen tablecloth top down, soft morning "
            "light, magazine cover layout, premium aesthetic flatlay"
        ),
        "url_base": "https://korlens.app/blog",
        "campaign": "korea_essentials_pinterest",
        "description": (
            "Korea Travel 2026 Essentials Checklist. Everything we wish we knew "
            "before our first trip: eSIM setup, AREX vs limousine bus, Naver Map "
            "vs Google, KakaoTaxi, hidden Seoul restaurants, Jeju 3-day plan, "
            "Korean BBQ etiquette and Korea vs Japan honest comparison.\n\n"
            "#KoreaTravel #SeoulItinerary #VisitKorea #TravelChecklist #Hangul"
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
            "source": "korlens_klook_3_2026_05_06",
            "status": "queued",
        })
        added += 1
        time.sleep(2)

    QUEUE_JSON.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"DONE: added {added} pins, queue total = {len(q['made'])}")
    return added


if __name__ == "__main__":
    main()
