#!/usr/bin/env python3
"""
Sleep Gyeongju — FAL Flux로 경주 사찰 이미지 생성 → Ken Burns 효과 → 8시간 영상.

파이프라인:
1. FAL Flux API로 경주 사찰·폭포·산·연못 이미지 20~30장 자동 생성
2. ffmpeg Ken Burns (zoompan) 각 이미지 30초 슬로우 줌
3. 크로스페이드 루프 + 사용자 준비 음악(assets/music.mp3)
4. (별도) upload.py 로 유튜브 업로드

의존:
    .secrets: FAL_API_KEY (이미 있음)
    assets/music.mp3 (사용자가 CC0 트랙 배치)
"""
import os, sys, json, subprocess, urllib.request, hashlib
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DEPT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\youtube\sleep_gyeongju")
# 대용량 산출물은 D: 로 (C: 공간 부족)
STORAGE = Path(r"D:\cheonmyeongdang-outputs\youtube\sleep_gyeongju")
ASSETS = STORAGE / "assets"
IMAGES = ASSETS / "images"
OUTPUT = STORAGE / "output"
IMAGES.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

SECRETS = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets")
FFMPEG = r"C:\Users\hdh02\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

PROMPTS = [
    "Ancient Korean buddhist temple at dawn, misty mountains, cinematic, 16:9, ultra detailed, warm soft light",
    "Bulguksa temple courtyard with stone pagoda, autumn leaves, golden hour, cinematic",
    "Korean mountain waterfall, lush moss, peaceful stream, soft morning fog",
    "Seokguram grotto interior style, warm candlelight, serene buddhist atmosphere",
    "Zen garden with raked sand and stones, Japanese influence, minimal, overcast",
    "Korean hanok village at twilight, glowing paper lanterns, traditional roofs",
    "Bamboo forest pathway, sunlight filtering through, cinematic depth",
    "Ancient pine tree in Korean mountain, ethereal mist, soft blue hour",
    "Temple bell pavilion on mountainside, autumn sunrise, cinematic wide",
    "Lotus pond in Korean temple, summer afternoon, tranquil reflection",
    "Stone buddha statue covered in moss, ancient forest, dappled sunlight",
    "Korean mountain monastery, deep winter snow, silent meditation scene",
    "Temple stairs covered in red maple leaves, autumn, soft rain",
    "Traditional Korean gate Iljumun at dawn, mystical fog, cinematic",
    "Incense smoke rising in temple hall, warm low light, spiritual",
    "Korean rice paddies before temple, dawn mist, cinematic ultrawide",
    "Mountain cloudscape above Korean temple roof, dramatic, golden hour",
    "Wooden temple hall interior with paper screens, meditation cushion, soft light",
    "Korean celadon ceramic on temple altar, candlelight, peaceful",
    "Stone stairs up to mountain temple, autumn, cinematic perspective",
]


def load_secrets():
    env = {}
    if SECRETS.exists():
        for line in SECRETS.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def fal_generate(api_key, prompt, seed=None):
    """FAL Flux Schnell — 빠르고 저렴 (약 $0.003/장)."""
    url = "https://fal.run/fal-ai/flux/schnell"
    body = {"prompt": prompt, "image_size": "landscape_16_9", "num_inference_steps": 4}
    if seed:
        body["seed"] = seed
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return data["images"][0]["url"]


def download(url, dest):
    if dest.exists() and dest.stat().st_size > 1000:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "SleepGyeongju/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())


def generate_images(api_key, prompts):
    paths = []
    for i, p in enumerate(prompts, 1):
        pid = hashlib.md5(p.encode()).hexdigest()[:10]
        dest = IMAGES / f"img_{i:02d}_{pid}.png"
        if dest.exists() and dest.stat().st_size > 10000:
            print(f"  [skip {i:02d}] {dest.name}")
            paths.append(dest)
            continue
        try:
            print(f"  🎨 [{i:02d}/{len(prompts)}] {p[:50]}...")
            url = fal_generate(api_key, p)
            download(url, dest)
            paths.append(dest)
        except Exception as e:
            print(f"     ⚠️ 실패: {e}")
    return paths


def render(images, music, target_hours=8, per_image_sec=30):
    """ffmpeg zoompan Ken Burns + 크로스페이드."""
    if not images:
        print("❌ 이미지 없음")
        return None
    if not music or not music.exists():
        print("❌ music.mp3 없음 — assets/music.mp3 준비 후 재실행")
        print(f"   추천 CC0 음악: https://pixabay.com/music/search/meditation%20ambient/")
        return None

    # 임시 클립 생성: 각 이미지 → zoompan 슬로우 줌 mp4
    per_frames = per_image_sec * 25  # 25fps
    clip_list = OUTPUT / "clips.txt"
    with open(clip_list, "w", encoding="utf-8") as f:
        for i, img in enumerate(images):
            clip = OUTPUT / f"_clip_{i:02d}.mp4"
            if not clip.exists():
                zoom_cmd = [
                    FFMPEG, "-y", "-loop", "1", "-i", str(img),
                    "-vf",
                    f"scale=3840:2160,zoompan=z='min(zoom+0.0015,1.5)':d={per_frames}:s=1920x1080:fps=25",
                    "-t", str(per_image_sec),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
                    "-pix_fmt", "yuv420p",
                    str(clip),
                ]
                print(f"  🎞️ 클립 {i+1}/{len(images)} 렌더...")
                subprocess.run(zoom_cmd, check=True, capture_output=True)
            # 전체 목표 시간 채울 때까지 반복 참조
            needed_loops = max(1, (target_hours * 3600) // (len(images) * per_image_sec) + 1)
        # 루프 목록 작성
        loops = max(1, (target_hours * 3600) // (len(images) * per_image_sec) + 1)
        for _ in range(loops):
            for i in range(len(images)):
                f.write(f"file '{(OUTPUT / f'_clip_{i:02d}.mp4').as_posix()}'\n")

    # 최종 concat + 음악
    out = OUTPUT / f"sleep_gyeongju_{target_hours}h.mp4"
    print(f"\n🎬 최종 렌더링 ({target_hours}시간)...")
    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", str(clip_list),
        "-stream_loop", "-1", "-i", str(music),
        "-t", str(target_hours * 3600),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ {out} ({out.stat().st_size/1024/1024:.1f} MB)")
    return out


def main():
    env = load_secrets()
    key = env.get("FAL_API_KEY") or env.get("FAL_KEY")
    if not key:
        print("❌ .secrets 에 FAL_API_KEY 없음")
        sys.exit(1)

    print(f"🎨 FAL Flux Schnell 으로 {len(PROMPTS)}장 이미지 생성 (≈ ${len(PROMPTS)*0.003:.2f})")
    imgs = generate_images(key, PROMPTS)
    print(f"  완료: {len(imgs)}장")

    music = ASSETS / "music.mp3"
    render(imgs, music, target_hours=8, per_image_sec=30)


if __name__ == "__main__":
    main()
