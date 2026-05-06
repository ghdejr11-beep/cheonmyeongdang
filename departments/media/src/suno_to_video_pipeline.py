"""Suno MP3 → fal.ai Kling 5s clips × 8 → ffmpeg combine + audio overlay → final MP4.

비용: 8 clips × $0.27 = $2.16 (~₩3,000)
모델: fal-ai/kling-video/v2.1/standard/text-to-video (or v1.6 fallback)
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
OUT_DIR = Path(r"D:\kunstudio-outputs\suno_video_2026-05-04")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────── Suno 입력 ───────────────
SUNO_MP3 = ROOT / "departments" / "tax" / "server" / "public" / "assets" / "cm_jingle_v1.mp3"

# ─────────────── 8 장면 프롬프트 (38초 곡 = 5초×8) ───────────────
PROMPTS = [
    "Korean woman in business attire smiling, modern office background, soft warm lighting, cinematic",
    "Korean money won bills floating in air with golden particles, elegant minimalist design",
    "Smartphone screen showing calculator app with refund amount in Korean won, hands typing",
    "Korean tax document with magnifying glass revealing hidden refund amounts, professional desk setup",
    "Happy Korean family receiving good news on smartphone, kitchen interior, golden hour light",
    "Bank account balance increasing on screen with Korean won numbers, smooth animation",
    "Korean office worker checking phone in cafe, surprised happy expression, warm tones",
    "Korean text logo '세금N혜택' glowing on dark background with golden particles, premium feel",
]


def load_secrets():
    env = {}
    p = ROOT / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v
    return env


def fal_request(model: str, payload: dict, api_key: str):
    """fal.run 동기 호출. 큐 처리는 fal 내부."""
    url = f"https://queue.fal.run/{model}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.loads(r.read())
    request_id = body.get("request_id")
    status_url = body.get("status_url") or f"https://queue.fal.run/{model}/requests/{request_id}/status"
    response_url = body.get("response_url") or f"https://queue.fal.run/{model}/requests/{request_id}"
    return request_id, status_url, response_url


def fal_wait(status_url: str, response_url: str, api_key: str, max_seconds: int = 600):
    """폴링하여 완료 대기 후 결과 반환."""
    start = time.time()
    while time.time() - start < max_seconds:
        req = urllib.request.Request(status_url, headers={"Authorization": f"Key {api_key}"})
        with urllib.request.urlopen(req, timeout=20) as r:
            s = json.loads(r.read())
        st = s.get("status")
        elapsed = int(time.time() - start)
        print(f"  [{elapsed:3d}s] status={st}")
        if st == "COMPLETED":
            req2 = urllib.request.Request(response_url, headers={"Authorization": f"Key {api_key}"})
            with urllib.request.urlopen(req2, timeout=20) as r2:
                return json.loads(r2.read())
        if st in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"fal job {st}: {s}")
        time.sleep(8)
    raise TimeoutError(f"fal job timed out after {max_seconds}s")


def download(url: str, dst: Path, retries: int = 5):
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=180) as r:
                dst.write_bytes(r.read())
            print(f"  saved {dst.name} ({dst.stat().st_size//1024}KB)")
            return
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:100]}"
            print(f"  download attempt {attempt+1}/{retries} failed: {last_err}")
            time.sleep(8 * (attempt + 1))
    raise RuntimeError(f"download failed after {retries} retries: {last_err}")


def gen_clip(idx: int, prompt: str, api_key: str) -> Path:
    out = OUT_DIR / f"clip_{idx:02d}.mp4"
    if out.exists() and out.stat().st_size > 100_000:
        print(f"[clip {idx}] cached → skip")
        return out
    print(f"[clip {idx}] {prompt[:70]}")
    model = "fal-ai/kling-video/v1.6/standard/text-to-video"
    payload = {
        "prompt": prompt,
        "duration": "5",
        "aspect_ratio": "16:9",
        "negative_prompt": "blurry, low quality, distorted, text, watermark",
    }
    rid, status_url, response_url = fal_request(model, payload, api_key)
    print(f"  request_id={rid}")
    result = fal_wait(status_url, response_url, api_key)
    video_url = (result.get("video") or {}).get("url")
    if not video_url:
        raise RuntimeError(f"no video url in: {result}")
    download(video_url, out)
    return out


def combine(clips: list, audio_mp3: Path, out_path: Path):
    """ffmpeg concat clips + overlay audio."""
    list_file = OUT_DIR / "concat.txt"
    list_file.write_text("\n".join(f"file '{c.as_posix()}'" for c in clips), encoding="utf-8")

    silent_video = OUT_DIR / "silent_combined.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(silent_video),
    ], check=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(silent_video),
        "-i", str(audio_mp3),
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        str(out_path),
    ], check=True)
    print(f"\n[OK] final → {out_path}  ({out_path.stat().st_size//1024//1024} MB)")


def main():
    env = load_secrets()
    api_key = env.get("FAL_API_KEY") or env.get("FAL_KEY")
    if not api_key:
        sys.exit("[ERR] FAL_API_KEY missing in .secrets")

    if not SUNO_MP3.exists():
        sys.exit(f"[ERR] suno mp3 not found: {SUNO_MP3}")

    print(f"=== Suno → Video Pipeline ===")
    print(f"  audio: {SUNO_MP3.name}")
    print(f"  clips: {len(PROMPTS)} × 5s = ~{len(PROMPTS)*5}s")
    print(f"  cost:  ~${len(PROMPTS)*0.27:.2f}\n")

    clips = []
    for i, p in enumerate(PROMPTS):
        clips.append(gen_clip(i, p, api_key))

    final = OUT_DIR / "final_38s.mp4"
    combine(clips, SUNO_MP3, final)
    print(f"\nUPLOAD: python whisper_atlas_yt_api_uploader.py --video {final} --title '...'")


if __name__ == "__main__":
    main()
