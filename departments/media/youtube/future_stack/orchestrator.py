#!/usr/bin/env python3
"""
Future Stack — AI/Claude 튜토리얼 롱폼 (5~10분) 자동 생성·업로드.

파이프라인:
  1. Claude → 5~10분 튜토 스크립트 (인트로·본론 3~5 단계·아웃트로)
  2. OpenAI TTS (nova, 여성 친근 톤)
  3. FAL Flux → 가로 이미지 8~12장 (1920x1080)
  4. ffmpeg → 가로 롱폼 (Ken Burns + BGM)
  5. YouTube 업로드

Task Scheduler: 주 2회 화·금 08:00
"""
import sys, os, json, datetime, random, subprocess, re, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DEPT = Path(__file__).parent
sys.path.insert(0, str(DEPT.parent / "shared"))

from claude_script import generate as claude_gen
from tts import synthesize
from youtube_upload import upload_video

STORAGE = Path(r"D:\cheonmyeongdang-outputs\youtube\future_stack")
STORAGE.mkdir(parents=True, exist_ok=True)
(STORAGE / "output").mkdir(exist_ok=True)
(STORAGE / "assets").mkdir(exist_ok=True)

SECRETS = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets")
FFMPEG = r"C:\Users\hdh02\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

TOPICS = [
    "Automate anything with Claude Agent SDK in 10 minutes",
    "Build a faceless YouTube pipeline with AI",
    "Claude vs ChatGPT vs Gemini — which wins in 2026?",
    "Use Claude API to replace 3 SaaS subscriptions",
    "AI-powered Gmail automation for solopreneurs",
    "Deploy your Claude bot to Railway in 5 minutes",
    "How to chain Claude + Zapier for unstoppable workflows",
    "Gumroad + Claude — build a $1k/week passive income app",
    "Turn your writing into an AI assistant — full tutorial",
    "Scrape any website with Claude's computer use",
]


def load_secrets():
    env = {}
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def fal_image(api_key, prompt, dest):
    req = urllib.request.Request(
        "https://fal.run/fal-ai/flux/schnell",
        data=json.dumps({
            "prompt": prompt, "image_size": "landscape_16_9",
            "num_inference_steps": 4,
        }).encode(),
        headers={"Authorization": f"Key {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        url = json.loads(r.read())["images"][0]["url"]
    with urllib.request.urlopen(url, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())


def render_longform(audio_path, images, out_path, bgm=None):
    """ffmpeg — 가로 16:9, Ken Burns 이미지 시퀀스 + 내레이션 + BGM."""
    # 오디오 총 길이 확인
    probe = subprocess.run(
        [FFMPEG.replace("ffmpeg.exe","ffprobe.exe"), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
        capture_output=True, text=True,
    )
    dur = float(probe.stdout.strip() or 300)
    per = max(15, int(dur / len(images)) + 2)

    list_txt = STORAGE / "output" / "_list.txt"
    with open(list_txt, "w", encoding="utf-8") as f:
        for img in images:
            clip = STORAGE / "output" / f"_c_{img.stem}.mp4"
            if not clip.exists():
                subprocess.run([
                    FFMPEG, "-y", "-loop", "1", "-i", str(img),
                    "-vf", f"scale=3840:2160,zoompan=z='min(zoom+0.001,1.3)':d={per*25}:s=1920x1080:fps=25",
                    "-t", str(per), "-c:v", "libx264", "-preset", "veryfast", "-crf", "25",
                    "-pix_fmt", "yuv420p", str(clip),
                ], check=True, capture_output=True)
            f.write(f"file '{clip.as_posix()}'\n")

    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_txt),
        "-i", str(audio_path),
    ]
    if bgm and bgm.exists():
        cmd += ["-stream_loop", "-1", "-i", str(bgm),
                "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.15[b];[v][b]amix=inputs=2:duration=shortest[a]",
                "-map", "0:v", "-map", "[a]"]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_path)]
    subprocess.run(cmd, check=True)
    return out_path


def main():
    env = load_secrets()
    fal_key = env.get("FAL_API_KEY") or env.get("FAL_KEY")
    if not fal_key:
        print("❌ FAL_API_KEY 없음")
        sys.exit(1)

    today = datetime.date.today()
    topic = TOPICS[today.toordinal() % len(TOPICS)]
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower())[:50]
    print(f"📝 토픽: {topic}")

    # 1. 스크립트 (5~10분 ≈ 700~1200 단어)
    prompt = f"""Write a YouTube tutorial script about: "{topic}"

Requirements:
- 6-8 minutes when spoken (≈ 900-1200 words)
- Strong hook in first 15 seconds
- 4-6 concrete actionable steps with examples
- Include at least 1 specific code snippet or tool name
- Mention exact pricing/links if known (verify before making up)
- Conversational American English
- No markdown, no stage directions, no emojis
- CTA at end: "Subscribe for more AI automation tutorials"
- Always disclose: this is educational, not financial advice, results may vary
Return only the spoken script."""
    script = claude_gen(prompt, max_tokens=3500).strip()
    print(f"📃 스크립트 {len(script)}자")

    # 2. TTS
    audio = STORAGE / "output" / f"{slug}.mp3"
    synthesize(script, audio, voice="en-US-JennyNeural")
    print(f"🔊 {audio.name}")

    # 3. 이미지 10장
    img_prompts = [
        "Futuristic AI laptop with glowing code, cinematic dark setup",
        "Developer workspace with multiple monitors showing AI tools",
        "Abstract neural network glowing blue, 3D render",
        "Claude AI interface screen mockup, clean modern UI",
        "Python code editor with syntax highlighting, cinematic",
        "Server rack room with glowing cables, cloud computing",
        "Hands on keyboard with floating holographic UI elements",
        "Money and data flowing into AI brain, conceptual",
        "Graph chart on monitor showing exponential growth",
        "Person silhouette with AI helper hologram, productivity",
    ]
    imgs = []
    for i, p in enumerate(img_prompts, 1):
        dest = STORAGE / "assets" / f"img_{slug}_{i}.png"
        if not dest.exists():
            try:
                fal_image(fal_key, p, dest)
            except Exception as e:
                print(f"  ⚠️ img {i}: {e}")
                continue
        imgs.append(dest)
    if len(imgs) < 5:
        print("❌ 이미지 5장 미만")
        sys.exit(1)

    # 4. 렌더
    out = STORAGE / "output" / f"{slug}.mp4"
    bgm = STORAGE / "assets" / "bgm.mp3"
    render_longform(audio, imgs, out, bgm=bgm if bgm.exists() else None)
    print(f"🎬 {out.name}")

    # 5. 업로드
    title = topic
    description = f"""{topic}

In this video you'll learn practical AI automation strategies using Claude, ChatGPT, and modern dev tools.

⏰ Timestamps:
00:00 Intro

🔗 Resources mentioned:
- Claude: https://anthropic.com
- FAL AI: https://fal.ai

#AI #ClaudeAI #Automation #Tutorial #Coding #Anthropic #Python

⚠️ Educational content only, not financial advice. Results vary.
"""
    try:
        vid = upload_video(
            video_path=out,
            channel="kunstudio",         # KunStudio
            title=title[:100], description=description,
            tags=["AI", "Claude", "Anthropic", "automation", "tutorial", "ChatGPT", "Python", "faceless"],
            privacy="private", category_id="27",  # Education
        )
        print(f"🎥 https://youtu.be/{vid}")
    except FileNotFoundError as e:
        print(f"❌ OAuth 미설정: {e}")


if __name__ == "__main__":
    main()
