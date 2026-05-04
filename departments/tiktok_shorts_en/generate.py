"""tiktok_shorts_en — 영문 K-culture 30초 TikTok 쇼츠 자동 생성 (광고비 0).

방식: 최근 SEO 블로그 1편 → 6 슬라이드 (Pollinations 이미지) + 핵심 텍스트 오버레이
+ 무료 BGM (Suno Sori Atlas) → ffmpeg 1080x1920 9:16 → mp4 출력.

시간: ~2분, 비용 ₩0 (Pollinations + ffmpeg + 기존 BGM 무료).
출력: D:/kunstudio-outputs/tiktok_en/{date}_{slug}.mp4
스케줄: 매일 10:00 schtask (KunStudio_TikTokEn_Daily).
업로드: Upload-Post API (이미 라이브) 또는 사용자 수동.
"""
import os
import sys
import json
import re
import urllib.request
import urllib.parse
import subprocess
import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON_ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
SEO_PUB = CHEON_ROOT / "departments" / "seo_blog_factory" / "published.json"
OUT_DIR = Path(r"D:\kunstudio-outputs\tiktok_en")
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG = ROOT / "logs" / f"shorts_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)
QUEUE = ROOT / "queue.json"

# 기본 BGM (Sori Atlas Suno 음원이 있으면 사용, 없으면 무음)
BGM_CANDIDATES = [
    Path(r"D:\kunstudio-outputs\audiobooks\korean_coffee_culture.mp3"),
    Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\tax\server\public\assets\cm_jingle_v1.mp3"),
]


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_secrets():
    env = {}
    p = CHEON_ROOT / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def load_queue():
    if QUEUE.exists():
        return json.loads(QUEUE.read_text(encoding="utf-8"))
    return {"made": []}


def claude_extract_hooks(api_key, title, kw):
    """Claude API: SEO 글의 hook 6줄 (slide당 1줄) 추출."""
    body = json.dumps({
        "model": "claude-sonnet-4-5",
        "max_tokens": 1500,
        "system": "Generate 6 punchy English text overlays for a TikTok video about Korean culture. Each line ~6-12 words, hook style, gen Z voice, NO hashtags, NO emojis, attention-grabbing.",
        "messages": [{"role": "user", "content":
            f"Topic: {title}\nSEO keyword: {kw}\n\nReturn strict JSON: {{\"hooks\": [\"line 1\", \"line 2\", ..., \"line 6\"]}}"
        }],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    text = data["content"][0]["text"]
    m = re.search(r"\{[\s\S]*\}", text)
    return json.loads(m.group(0))["hooks"]


def fetch_image(prompt, slug, idx):
    seed = (abs(hash(slug)) + idx * 1000) % 100000
    url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
        f"?width=720&height=1280&seed={seed}&nologo=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def overlay_text(img_path: Path, text: str, out_path: Path):
    """ffmpeg로 텍스트 오버레이 (Pollinations 이미지 위에)."""
    # font: Windows 기본 Arial Bold
    font = "C\\:/Windows/Fonts/arialbd.ttf"
    safe_text = text.replace(":", "\\:").replace("'", "\\'").replace('"', '')
    drawtext = (
        f"drawtext=fontfile='{font}':"
        f"text='{safe_text}':"
        f"fontcolor=white:fontsize=58:"
        f"box=1:boxcolor=black@0.65:boxborderw=18:"
        f"x=(w-text_w)/2:y=h*0.78"
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(img_path),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{drawtext}",
        "-frames:v", "1",
        str(out_path),
    ], check=True, capture_output=True)


def main():
    env = load_secrets()
    api_key = env.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("[ERR] ANTHROPIC_API_KEY missing")

    if not SEO_PUB.exists():
        sys.exit("[ERR] SEO blog factory not run yet")

    pub = json.loads(SEO_PUB.read_text(encoding="utf-8"))
    posts = pub.get("published", [])
    if not posts:
        sys.exit("[INFO] no SEO posts to base shorts on")

    q = load_queue()
    made_kws = {x["kw"] for x in q.get("made", [])}
    candidates = [p for p in posts if p["kw"] not in made_kws]
    if not candidates:
        log("All SEO posts already shortified")
        return

    post = candidates[0]
    slug = post["slug"]
    title = post["title"]
    kw = post["kw"]
    log(f"=== {kw} ({title}) ===")

    # 1) 6 hook
    hooks = claude_extract_hooks(api_key, title, kw)
    log(f"  hooks: {hooks}")

    # 2) 이미지 6장 + 텍스트 오버레이
    work = OUT_DIR / f"{datetime.date.today()}_{slug}_work"
    work.mkdir(parents=True, exist_ok=True)
    slides = []
    image_prompts = [
        f"vertical 9:16 photo, korean culture related to {kw}, scene {i+1}, premium photography, 1080x1920"
        for i in range(6)
    ]
    for i, (hook, prompt) in enumerate(zip(hooks, image_prompts)):
        raw = fetch_image(prompt, slug, i)
        raw_path = work / f"raw_{i}.jpg"
        raw_path.write_bytes(raw)
        slide_path = work / f"slide_{i}.jpg"
        try:
            overlay_text(raw_path, hook, slide_path)
        except subprocess.CalledProcessError:
            # 실패 시 텍스트 없이 raw 사용
            slide_path = raw_path
        slides.append(slide_path)
        log(f"  slide {i}: {slide_path.name}")

    # 3) ffconcat → 슬라이드쇼
    concat = work / "concat.txt"
    duration_per = 5.0
    lines = ["ffconcat version 1.0"]
    for s in slides:
        lines.append(f"file '{s.as_posix()}'")
        lines.append(f"duration {duration_per}")
    lines.append(f"file '{slides[-1].as_posix()}'")
    concat.write_text("\n".join(lines), encoding="utf-8")

    silent = work / "silent.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat),
        "-vf", "scale=1080:1920,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-r", "30",
        str(silent),
    ], check=True, capture_output=True)

    # 4) BGM 합성
    bgm = next((b for b in BGM_CANDIDATES if b.exists()), None)
    final = OUT_DIR / f"{datetime.date.today().isoformat()}_{slug}.mp4"
    if bgm:
        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(silent),
            "-i", str(bgm),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            str(final),
        ], check=True, capture_output=True)
    else:
        # 무음 그대로
        silent.replace(final)

    log(f"[OK] {final} ({final.stat().st_size//1024//1024}MB)")
    q["made"].append({
        "kw": kw, "slug": slug, "title": title,
        "made_at": datetime.datetime.now().isoformat(),
        "file": str(final.name),
    })
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
