#!/usr/bin/env python3
"""
AI Side Hustle 장편(8~10분) 영상 자동 생성 파이프라인.
쇼츠와 동일 토픽에서 깊이 있는 버전 제작.

전략 근거 (Agent 리서치 2026-04):
- 장편 RPM $1~30 vs 쇼츠 $0.03~0.06 → 10~50배 수익
- 파이낸스/B2B 니치 RPM $0.15~0.45 진입 가능
- 주 2회 장편 + 매일 쇼츠 퍼널

파이프라인:
1. Claude → 8~10분 스크립트 (1,500~2,000 단어)
2. Edge TTS (또는 ElevenLabs if key) → 긴 MP3
3. Pollinations Flux × 20~30장 (16:9 가로)
4. ffmpeg → 가로 1920x1080 MP4 + BGM + 챕터
5. YouTube 장편 업로드 (wealth 채널)

Task Scheduler: 매주 월·목 07:00
"""
import sys, os, json, datetime, random, subprocess, re, urllib.request, urllib.parse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DEPT = Path(__file__).parent
sys.path.insert(0, str(DEPT.parent / "shared"))

from claude_script import generate as claude_gen
from tts import synthesize
from youtube_upload import upload_video

STORAGE = Path(r"D:\cheonmyeongdang-outputs\youtube\ai_sidehustle_longform")
STORAGE.mkdir(parents=True, exist_ok=True)
(STORAGE / "output").mkdir(exist_ok=True)
(STORAGE / "assets").mkdir(exist_ok=True)

FFMPEG = r"C:\Users\hdh02\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

LONG_TOPICS = [
    "How I would make $10,000 a month with AI in 2026 (step by step)",
    "The complete AI side hustle blueprint — 5 businesses you can start this week",
    "I tested 10 AI tools for making money online — here's what actually works",
    "Why 99% of AI side hustles fail and how to be in the 1%",
    "Building a $5k/month Claude Agent business with zero coding",
    "The faceless YouTube automation empire — full breakdown",
    "From 0 to $3,000/month selling AI prompts on Gumroad",
    "Amazon KDP in 2026 — the truth nobody tells you",
    "Claude vs ChatGPT for real-world money-making tasks",
    "The AI skill gap in 2026 — why some freelancers make 10x more",
]


def pollinations_image(prompt, dest, seed=None):
    q = urllib.parse.quote(prompt)
    seed_q = f"&seed={seed}" if seed is not None else ""
    url = f"https://image.pollinations.ai/prompt/{q}?width=1920&height=1080&nologo=true&model=flux{seed_q}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        f.write(r.read())


def render_long_form(audio_path, images, out_path, per_image_sec=18):
    """가로 16:9 슬라이드쇼 + BGM 오버레이."""
    list_txt = STORAGE / "output" / "_longlist.txt"
    with open(list_txt, "w", encoding="utf-8") as f:
        for img in images:
            clip = STORAGE / "output" / f"_l_{img.stem}.mp4"
            if not clip.exists():
                subprocess.run([
                    FFMPEG, "-y", "-loop", "1", "-i", str(img),
                    "-vf", f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.0004,1.12)':d={per_image_sec*30}:s=1920x1080:fps=30",
                    "-t", str(per_image_sec), "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-pix_fmt", "yuv420p", str(clip),
                ], check=True, capture_output=True)
            f.write(f"file '{clip.as_posix()}'\n")

    subprocess.run([
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_txt),
        "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
        "-shortest", str(out_path),
    ], check=True)
    return out_path


def main():
    today = datetime.date.today()
    # 주 2회 (월/목) 실행 가정. 토픽은 날짜 기반 순환.
    topic = LONG_TOPICS[today.toordinal() % len(LONG_TOPICS)]
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower())[:60]
    print(f"📝 장편 토픽: {topic}")

    # 1) 8~10분 스크립트 (대략 1,500~2,000 단어)
    prompt = f"""Write a YouTube long-form video script (8~10 minutes spoken, 1500~2000 words) for this topic: "{topic}"

Requirements:
- Strong hook in first 15 seconds: a claim or story
- 5 chapters clearly separated with [CHAPTER X: Title] markers
- Each chapter 250~400 words
- Specific tactics with numbers (revenue, time saved, click-through rates)
- Natural conversational American English
- 1 rhetorical question per chapter to keep engagement
- CTA at the end: "Subscribe for weekly deep-dives" + rich comment prompt
- NEVER promise guaranteed income. Use "potential / ranges"
- Plain text, no markdown, no stage directions
Return only the spoken script."""
    script = claude_gen(prompt, max_tokens=3500).strip()
    print(f"📃 {len(script)}자")
    (STORAGE / "output" / f"{slug}.txt").write_text(script, encoding="utf-8")

    # 2) TTS
    audio = STORAGE / "output" / f"{slug}.mp3"
    if not audio.exists():
        synthesize(script, audio, voice="en-US-GuyNeural")
    print(f"🔊 {audio.name}")

    # 3) 이미지 20장 (챕터별 4장 × 5챕터)
    base_seed = today.toordinal() * 10
    img_prompts = [
        f"Cinematic entrepreneur desk with AI workflow glowing, laptop + code + money, 16:9, dark studio, moody lighting",
        f"Dollar bills flying around an AI chip, futuristic glow, 16:9 wide cinematic",
        f"Abstract data visualization flowing over city skyline dusk, 16:9",
        f"Person typing on modern keyboard multiple monitors showing analytics, 16:9",
        f"Graphs rising in hologram, success metaphor, 16:9",
        f"Home office minimal setup with ring light and camera, content creator vibe, 16:9",
        f"Stacks of coins transforming into digital currency, abstract 16:9",
        f"AI assistant hologram floating near worker, productive scene, 16:9",
        f"Rocket launching from laptop screen, startup growth metaphor, 16:9",
        f"Modern coffee shop digital nomad working on AI, 16:9",
        f"Wall of product mockups showcasing digital goods, marketing 16:9",
        f"Luxurious mountain view with laptop, lifestyle freedom 16:9",
        f"Robot assistant organizing virtual files, automation 16:9",
        f"Timeline with milestones and growth arrows, 16:9 infographic",
        f"Team collaboration but faceless silhouettes, 1-person scaled operation, 16:9",
        f"Chart showing compound growth, success pattern, 16:9",
        f"Sunrise over ocean with motivational vibe, 16:9 cinematic",
        f"Person reading book with glowing ideas icons, 16:9",
        f"Modern futuristic workspace neon details, 16:9",
        f"Celebration of achievement subtle confetti, 16:9",
    ]
    imgs = []
    for i, p in enumerate(img_prompts, 1):
        dest = STORAGE / "assets" / f"img_{slug}_{i:02d}.png"
        if not dest.exists():
            try:
                pollinations_image(p, dest, seed=base_seed + i)
                print(f"  ✅ img {i}/20: {dest.stat().st_size/1024:.0f} KB")
            except Exception as e:
                print(f"  ⚠️ img {i}: {e}")
                continue
        imgs.append(dest)
    if len(imgs) < 10:
        print("❌ 이미지 10장 미만")
        sys.exit(1)

    # 4) 렌더 (per_image 18초 × 20장 = 360초 = 6분, 오디오 길이에 맞춰 shortest로 cut)
    out = STORAGE / "output" / f"{slug}.mp4"
    render_long_form(audio, imgs, out, per_image_sec=30)  # 20장 × 30초 = 10분
    print(f"🎬 {out.name} ({out.stat().st_size/1024/1024:.1f} MB)")

    # 5) 업로드 (privacy=private 테스트)
    title = f"{topic} | Long-form deep dive"
    description = f"""{topic}

This long-form video explores the topic in depth — practical tactics, numbers, and frameworks.

🎯 Chapter list in video.
🔔 Subscribe for weekly deep-dives.

⚠️ Educational content only, not financial advice. Your results will vary.

#AI #SideHustle #MakeMoneyOnline #ClaudeAI #ChatGPT #PassiveIncome #Entrepreneurship
"""
    try:
        vid = upload_video(
            video_path=out,
            channel="wealth",
            title=title[:100], description=description,
            tags=["AI", "long form", "side hustle", "make money", "Claude", "ChatGPT", "entrepreneurship", "deep dive"],
            privacy="private", category_id="22",
        )
        print(f"🎥 https://youtu.be/{vid}")
    except FileNotFoundError as e:
        print(f"❌ OAuth 미설정: {e}")


if __name__ == "__main__":
    main()
