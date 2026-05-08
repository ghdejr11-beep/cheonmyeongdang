"""Suno MP3 + Pollinations Flux 정적 이미지 8장 → ffmpeg crossfade → 38초 비디오 (무료)."""
import sys
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"D:\cheonmyeongdang")
OUT_DIR = Path(r"D:\kunstudio-outputs\suno_static_video_2026-05-04")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SUNO_MP3 = ROOT / "departments" / "tax" / "server" / "public" / "assets" / "cm_jingle_v1.mp3"

PROMPTS = [
    "Korean woman in elegant business attire smiling at camera, modern Korean office background, soft warm cinematic lighting, professional photography, 16:9",
    "Korean money 50000 won bills floating in air with golden particles, elegant minimalist composition, soft bokeh background",
    "Smartphone screen showing tax refund calculator app in Korean, hands typing on keyboard, golden hour lighting",
    "Korean tax document with magnifying glass revealing hidden won amounts, professional desk with laptop and coffee",
    "Happy Korean family of three receiving great news on smartphone, modern kitchen interior, warm golden lighting",
    "Bank account balance increasing on phone screen with Korean won numbers rising, dynamic composition",
    "Korean man in cafe checking phone surprised happy expression, urban Seoul cafe interior, warm tones",
    "Korean text logo TAX-N-BENEFIT 세금N혜택 glowing on dark gradient background with golden particles, premium luxury feel, 16:9 aspect",
]


def download_image(idx: int, prompt: str) -> Path:
    out = OUT_DIR / f"img_{idx:02d}.jpg"
    if out.exists() and out.stat().st_size > 10_000:
        print(f"[img {idx}] cached")
        return out
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1280&height=720&seed={idx*1000+777}&nologo=true"
    print(f"[img {idx}] {prompt[:60]}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        out.write_bytes(r.read())
    print(f"  saved {out.stat().st_size//1024}KB")
    return out


def make_video(images: list, audio: Path, out: Path):
    """각 이미지를 5초씩 표시 + crossfade transition."""
    duration_per = 5.0
    list_file = OUT_DIR / "ffmpeg_inputs.txt"

    # ffconcat with duration
    lines = ["ffconcat version 1.0"]
    for img in images:
        lines.append(f"file '{img.as_posix()}'")
        lines.append(f"duration {duration_per}")
    # 마지막 이미지 한 번 더 (concat demuxer 요구)
    lines.append(f"file '{images[-1].as_posix()}'")
    list_file.write_text("\n".join(lines), encoding="utf-8")

    # 1) 슬라이드쇼 무성 비디오
    silent = OUT_DIR / "silent.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-vf", "scale=1280:720,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-r", "30",
        str(silent),
    ], check=True)

    # 2) 음원 합치기
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(silent),
        "-i", str(audio),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0",
        "-shortest",
        str(out),
    ], check=True)
    print(f"\n[OK] {out} ({out.stat().st_size//1024//1024}MB)")


def main():
    if not SUNO_MP3.exists():
        sys.exit(f"[ERR] {SUNO_MP3} not found")
    print(f"=== Suno + Static Images Video (FREE) ===")
    print(f"  audio: {SUNO_MP3.name}")
    print(f"  imgs:  {len(PROMPTS)} × 5s = ~{len(PROMPTS)*5}s\n")

    images = [download_image(i, p) for i, p in enumerate(PROMPTS)]
    final = OUT_DIR / "final.mp4"
    make_video(images, SUNO_MP3, final)
    print(f"\n>>> 시청: {final}")


if __name__ == "__main__":
    main()
