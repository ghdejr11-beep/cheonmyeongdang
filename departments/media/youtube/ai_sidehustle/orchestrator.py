#!/usr/bin/env python3
"""
AI Side Hustle 쇼츠 (60초) 자동 생성·업로드.

파이프라인:
  1. Claude → 60초 스크립트 (훅·팁·CTA)
  2. OpenAI TTS (onyx, 남성 저음 = Motivation 톤)
  3. FAL Flux → 세로 이미지 5장 (9:16)
  4. ffmpeg → 세로 60초 영상 (이미지 슬라이드 + BGM + 자막)
  5. YouTube Shorts 업로드

Task Scheduler: 매일 아침 06:00
"""
import sys, os, json, datetime, random, subprocess, re, urllib.request, urllib.parse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DEPT = Path(__file__).parent
sys.path.insert(0, str(DEPT.parent / "shared"))

from claude_script import generate as claude_gen
from tts import synthesize
from youtube_upload import upload_video

STORAGE = Path(r"D:\cheonmyeongdang-outputs\youtube\ai_sidehustle")
STORAGE.mkdir(parents=True, exist_ok=True)
(STORAGE / "output").mkdir(exist_ok=True)
(STORAGE / "assets").mkdir(exist_ok=True)

SECRETS = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets")
FFMPEG = r"C:\Users\hdh02\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

# 동적 토픽 (topic_refresh.py가 매주 갱신). 파일 없으면 내장 기본값.
TOPICS_FILE = Path(__file__).parent / "topics.json"
HISTORY_FILE = Path(__file__).parent / "run_history.jsonl"

DEFAULT_TOPICS = [
    "3 AI tools that make $100 a day while you sleep",
    "Why every freelancer should use Claude API in 2026",
    "How I built a faceless YouTube channel in 30 days",
    "One Gumroad product that prints money monthly",
    "The fastest way to monetize ChatGPT skills",
    "5 AI side hustles that actually work",
    "Make money selling AI prompts — beginner guide",
    "How to automate Amazon KDP with AI",
    "Turn ChatGPT into a $2000/month writer",
    "The AI skill landlords wish they had",
]


def load_topics():
    if TOPICS_FILE.exists():
        try:
            data = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
            topics = data.get("topics", [])
            if len(topics) >= 5:
                return topics
        except Exception as e:
            print(f"⚠️ topics.json 파싱 실패: {e}")
    return DEFAULT_TOPICS


def load_secrets():
    env = {}
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def pollinations_image(prompt, dest, seed=None):
    # Free Flux via Pollinations (no API key required)
    q = urllib.parse.quote(prompt)
    seed_q = f"&seed={seed}" if seed is not None else ""
    url = f"https://image.pollinations.ai/prompt/{q}?width=1080&height=1920&nologo=true&model=flux{seed_q}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        f.write(r.read())


def fal_image(api_key, prompt, dest):
    # Kept as fallback if FAL credits restored; not used by default
    req = urllib.request.Request(
        "https://fal.run/fal-ai/flux/schnell",
        data=json.dumps({
            "prompt": prompt, "image_size": "portrait_16_9",
            "num_inference_steps": 4,
        }).encode(),
        headers={"Authorization": f"Key {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        url = json.loads(r.read())["images"][0]["url"]
    with urllib.request.urlopen(url, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())


def render_short(script_text, audio_path, images, out_path):
    """ffmpeg — 세로 9:16, 자막 overlay, 이미지 슬라이드."""
    # 각 이미지 12초 slide
    per = 12
    list_txt = STORAGE / "output" / "_shortlist.txt"
    with open(list_txt, "w", encoding="utf-8") as f:
        for img in images:
            clip = STORAGE / "output" / f"_s_{img.stem}.mp4"
            if not clip.exists():
                subprocess.run([
                    FFMPEG, "-y", "-loop", "1", "-i", str(img),
                    "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0008,1.15)':d={per*30}:s=1080x1920:fps=30",
                    "-t", str(per), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
                    "-pix_fmt", "yuv420p", str(clip),
                ], check=True, capture_output=True)
            f.write(f"file '{clip.as_posix()}'\n")
    # 오디오 길이에 맞춰 자르기
    subprocess.run([
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_txt),
        "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(out_path),
    ], check=True)
    return out_path


def main():
    env = load_secrets()
    today = datetime.date.today()
    topics = load_topics()
    topic = topics[today.toordinal() % len(topics)]
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower())[:50]

    print(f"📝 토픽: {topic}")

    # 1. Claude 스크립트
    prompt = f"""Write a YouTube Shorts script for this topic: "{topic}"

Requirements:
- 55-60 seconds when spoken (≈ 140-160 words)
- Strong hook in first 3 seconds
- 3 specific actionable points
- CTA at the end: "Follow for more AI money tips"
- Plain text only, no markdown, no stage directions
- Natural conversational American English
- Educational framing, NEVER promise guaranteed income
Return only the spoken script."""
    script = claude_gen(prompt, max_tokens=600).strip()
    print(f"📃 스크립트 {len(script)}자")
    # 품질검증에 쓰도록 스크립트 캐시
    (STORAGE / "output" / f"{slug}.txt").write_text(script, encoding="utf-8")

    # 2. TTS
    audio = STORAGE / "output" / f"{slug}.mp3"
    synthesize(script, audio, voice="en-US-GuyNeural")
    print(f"🔊 {audio.name}")

    # 3. 이미지 5장
    img_prompts = [
        f"Cinematic faceless motivation: laptop with glowing AI interface, dark studio, money icons, 9:16",
        f"Modern desk with ChatGPT screen glowing, coffee cup, entrepreneur vibe, 9:16",
        f"Stack of dollars and AI chip, sci-fi background, 9:16",
        f"Hand typing on keyboard at night, multiple monitors showing code, 9:16",
        f"Rising graph chart hologram over city skyline, financial success, 9:16",
    ]
    imgs = []
    base_seed = today.toordinal()
    # quality_check로 개별 이미지 검증 + 최대 2회 재시도
    from quality_check import check_image
    for i, p in enumerate(img_prompts, 1):
        dest = STORAGE / "assets" / f"img_{slug}_{i}.png"
        attempts = 0
        while attempts < 3:
            if not dest.exists():
                try:
                    pollinations_image(p, dest, seed=base_seed + i + attempts * 100)
                except Exception as e:
                    print(f"  ⚠️ img {i} try{attempts+1}: {e}")
                    attempts += 1
                    continue
            ok, msg = check_image(dest)
            if ok:
                print(f"  ✅ img {i}: {msg}")
                imgs.append(dest)
                break
            else:
                print(f"  🔁 img {i} try{attempts+1}: {msg} — 재생성")
                try: dest.unlink()
                except Exception: pass
                attempts += 1
        else:
            print(f"  ❌ img {i}: 3회 실패, 스킵")
    if len(imgs) < 3:
        print("❌ 이미지 3장 미만")
        sys.exit(1)

    # 4. 렌더
    out = STORAGE / "output" / f"{slug}.mp4"
    render_short(script, audio, imgs, out)
    print(f"🎬 {out.name} ({out.stat().st_size/1024/1024:.1f} MB)")

    # 4.5. 전체 품질 검증
    from quality_check import check_all
    report = check_all(slug, script, audio, imgs, out)
    if not report["passed"]:
        print(f"🚨 품질 검증 실패: {json.dumps(report['checks'], ensure_ascii=False)}")
        # 치명적이지 않으면 업로드 계속. 결과는 history에 기록.
    else:
        print(f"✅ 품질 검증 통과")

    # 4.6. Submagic 후처리 (API 키 있으면 자막+B-roll+BGM 자동 추가)
    try:
        from submagic import post_process_shorts
        enhanced = post_process_shorts(out, title=topic[:80], language="en")
        if enhanced:
            out = enhanced  # 업로드 대상 교체
    except Exception as e:
        print(f"  ⚠️ Submagic 단계 스킵: {e}")

    # 5. 업로드
    title = f"{topic} #Shorts"
    description = f"""{topic}

#Shorts #AI #SideHustle #MakeMoneyOnline #ChatGPT #ClaudeAI

⚠️ This is for educational purposes only, not financial advice. Your results will vary."""

    # Append canonical AI-themed affiliate block (matches D:\scripts\ai_sidehustle_update_descriptions.py
    # so newly uploaded AI Side Hustle videos already ship with the rich 5-link block — KunStudio
    # Mega Bundle / AI Saju Prompt Pack / Saju Workbook / Gumroad / Toss).
    try:
        sys.path.insert(0, r"D:\scripts")
        from yt_affiliate_lib import append_affiliate_block as _append_affiliate_block
        from pathlib import Path as _Path
        _aff_json = _Path(r"D:\scripts\ai_sidehustle_affiliates.json")
        if _aff_json.exists():
            description = _append_affiliate_block(
                description, title,
                ["AI", "side hustle", "make money", "ChatGPT", "Claude", "faceless", "shorts", "passive income"],
                _aff_json,
            )
    except Exception as _e:
        print(f"  ⚠️ AI affiliate block append skipped: {_e}")
    vid = None
    try:
        vid = upload_video(
            video_path=out,
            channel="wealth",
            title=title[:100], description=description,
            tags=["AI", "side hustle", "make money", "ChatGPT", "Claude", "faceless", "shorts", "passive income"],
            privacy="private", category_id="22",
        )
        print(f"🎥 https://youtu.be/{vid}")
    except FileNotFoundError as e:
        print(f"❌ OAuth 미설정: {e}")

    # 6. run_history 기록 (feedback_loop.py에서 사용)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "date": datetime.date.today().isoformat(),
            "topic": topic,
            "slug": slug,
            "video_id": vid,
            "video_size_mb": round(out.stat().st_size / 1024 / 1024, 2),
            "quality_passed": report["passed"],
            "quality_checks": report["checks"],
        }, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
