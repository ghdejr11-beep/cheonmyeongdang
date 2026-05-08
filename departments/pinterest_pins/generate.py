"""pinterest_pins — SEO 블로그별 Pinterest 핀 5장 자동 생성 (1000x1500 세로 + 텍스트 오버레이).

각 SEO 블로그 1편당 5 variation 핀 생성 → output/{slug}/pin_{i}.jpg + description.txt
→ 사용자가 Pinterest 웹 일괄 업로드 (drag-drop) → 핀당 1,000~5,000 노출 가능.

자동: 매일 12:30 schtask. 새 SEO 블로그 → 5 핀 자동 생성.
Pinterest API approval 후엔 publish.py로 자동 게시 (TODO).
"""
import os, sys, json, urllib.request, urllib.parse, datetime, subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON_ROOT = Path(r"D:\cheonmyeongdang")
SEO_PUB = CHEON_ROOT / "departments" / "seo_blog_factory" / "published.json"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
QUEUE = ROOT / "queue.json"
LOG = ROOT / "logs" / f"pins_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_queue():
    if QUEUE.exists():
        return json.loads(QUEUE.read_text(encoding="utf-8"))
    return {"made": []}


# Pinterest 핀 5 variation prompts
PIN_STYLES = [
    "vertical pinterest pin design 1000x1500, scenic photo of {topic}, soft pastel colors, premium magazine layout",
    "vertical pinterest pin 1000x1500, korean culture {topic}, infographic style, light beige background, elegant",
    "vertical pinterest pin 1000x1500, {topic} aesthetic photo, golden hour lighting, journal magazine cover",
    "vertical pinterest pin 1000x1500, korean lifestyle {topic}, top down flat lay photography, neutral palette",
    "vertical pinterest pin 1000x1500, {topic} with korean flag colors red blue subtle, modern minimal layout",
]


def fetch_image(prompt, slug, idx):
    seed = (abs(hash(slug)) + idx * 1000) % 100000
    url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
        f"?width=1000&height=1500&seed={seed}&nologo=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def overlay_text(in_path, title, out_path):
    """ffmpeg drawtext — Pinterest 핀 상단에 굵은 제목 오버레이."""
    font = "C\\:/Windows/Fonts/arialbd.ttf"
    safe = title.replace(":", "\\:").replace("'", "\\'").replace('"', '')[:60]
    drawtext = (
        f"drawtext=fontfile='{font}':"
        f"text='{safe}':"
        f"fontcolor=white:fontsize=68:"
        f"box=1:boxcolor=black@0.72:boxborderw=22:"
        f"x=(w-text_w)/2:y=80:"
        f"line_spacing=10"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", str(in_path),
        "-vf", f"scale=1000:1500,{drawtext}",
        "-frames:v", "1", str(out_path),
    ], check=True, capture_output=True)


def description(post):
    """Pinterest 핀 description (2~5문장 + 키워드 + URL)."""
    title = post["title"]
    kw = post["kw"]
    url = f"https://cheonmyeongdang.vercel.app/blog/en/{post['slug']}.html"
    return f"""{title}

Discover the complete guide on {kw} — written by Korean culture insiders for global readers.

✓ Curated tips and insider details
✓ Easy to follow for first-timers
✓ Korean cultural context included

Full article: {url}

#KoreanCulture #{kw.replace(' ','').title()} #VisitKorea #KoreanLifestyle #KoreanInsights
"""


def main():
    if not SEO_PUB.exists():
        sys.exit("[ERR] SEO published.json missing")

    pub = json.loads(SEO_PUB.read_text(encoding="utf-8"))
    posts = pub.get("published", [])
    q = load_queue()
    made = {x["kw"] for x in q.get("made", [])}
    candidates = [p for p in posts if p["kw"] not in made]
    if not candidates:
        log("All blogs have pins")
        return

    post = candidates[0]
    slug = post["slug"]
    topic = post["kw"]
    title = post["title"]
    log(f"=== {slug} ===")

    pin_dir = OUT / slug
    pin_dir.mkdir(exist_ok=True)

    for i, style_tpl in enumerate(PIN_STYLES):
        prompt = style_tpl.format(topic=topic)
        try:
            raw = fetch_image(prompt, slug, i)
            raw_path = pin_dir / f"raw_{i}.jpg"
            raw_path.write_bytes(raw)
            pin_path = pin_dir / f"pin_{i}.jpg"
            try:
                overlay_text(raw_path, title, pin_path)
            except subprocess.CalledProcessError:
                pin_path = raw_path
            log(f"  pin {i}: {pin_path.name} ({pin_path.stat().st_size//1024}KB)")
        except Exception as e:
            log(f"  pin {i} FAIL: {type(e).__name__}: {str(e)[:80]}")

    desc_path = pin_dir / "description.txt"
    desc_path.write_text(description(post), encoding="utf-8")
    log(f"  desc → {desc_path.name}")

    q["made"].append({
        "kw": topic, "slug": slug, "title": title,
        "made_at": datetime.datetime.now().isoformat(),
        "pin_dir": str(pin_dir.relative_to(ROOT)),
    })
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n>>> Pinterest 일괄 업로드:")
    print(f"   1) https://www.pinterest.com/pin-builder 접속")
    print(f"   2) {pin_dir}/pin_*.jpg 5장 drag-drop")
    print(f"   3) {desc_path} 내용 description에 복붙")
    print(f"   4) 5번 publish — 1분 소요\n")


if __name__ == "__main__":
    main()
