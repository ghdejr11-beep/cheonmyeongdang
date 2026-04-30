#!/usr/bin/env python3
"""
yt_channel_common.py — 3개 신규 YouTube 채널 (Whisper Atlas / Wealth Blueprint /
Inner Archetypes) 공용 유틸.

기능:
- .secrets 로딩
- ffmpeg / 출력 폴더 / 로그 경로 표준화
- Pollinations Flux 무료 이미지 생성 (Free, 키 불필요)
- pinkblue noise / 화이트노이즈 자체 생성 (저작권 0%)
- 5분 → N시간 ffmpeg stream_loop 헬퍼
- upload_post_client.post_to_channel() 래퍼

채널 키 (Upload-Post.com 프로필):
    whisper_atlas, wealth_blueprint, inner_archetypes

원칙 (메모리):
- 모든 산출물은 D:\\kunstudio-outputs\\yt\\<channel>\\... 에 저장
- 콘텐츠에 본인·고객 개인정보 절대 X
- 음원은 CC0/자체 생성만, 저작권 음원 금지
- Wealth Blueprint 에서 투자 권유성 멘트 금지 (보험·금융 자문 회피)
"""
from __future__ import annotations
import os
import sys
import json
import time
import urllib.request
import urllib.parse
import subprocess
import datetime
import logging
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ───────── 표준 경로 ─────────
PROJECT_ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
SECRETS_PATH = PROJECT_ROOT / ".secrets"
SRC_DIR = PROJECT_ROOT / "departments" / "media" / "src"
LOG_DIR = PROJECT_ROOT / "departments" / "media" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 산출물은 D:\ (메모리 규칙: 신규 파일은 D:\)
STORAGE_ROOT = Path(r"D:\kunstudio-outputs\yt")
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

FFMPEG = r"C:\Users\hdh02\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

# Upload-Post 프로필 키 (upload_post_client.py 와 일치)
CHANNEL_KEYS = {
    "whisper_atlas": "Whisper Atlas",
    "wealth_blueprint": "Wealth Blueprint",
    "inner_archetypes": "Inner Archetypes",
}


# ───────── 로깅 ─────────
def get_logger(name: str = "yt_3ch_daily") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    log_file = LOG_DIR / f"{name}.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S"))
    logger.addHandler(sh)
    return logger


# ───────── secrets ─────────
def load_secrets() -> dict[str, str]:
    env: dict[str, str] = {}
    if not SECRETS_PATH.exists():
        return env
    for line in SECRETS_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


# ───────── 채널별 작업 폴더 ─────────
def channel_dirs(channel_key: str) -> dict[str, Path]:
    base = STORAGE_ROOT / channel_key
    today = datetime.date.today().isoformat()
    work = base / today
    for sub in ("assets", "audio", "images", "output"):
        (work / sub).mkdir(parents=True, exist_ok=True)
    return {
        "base": base,
        "work": work,
        "assets": work / "assets",
        "audio": work / "audio",
        "images": work / "images",
        "output": work / "output",
    }


# ───────── Pollinations Flux (Free) ─────────
def pollinations_image(prompt: str, dest: Path,
                        width: int = 1920, height: int = 1080,
                        seed: int | None = None, model: str = "flux") -> Path:
    """
    Pollinations.ai 무료 Flux 이미지. 키 불필요. (AI Side Hustle 패턴 동일)
    """
    if dest.exists() and dest.stat().st_size > 5_000:
        return dest
    q = urllib.parse.quote(prompt)
    seed_q = f"&seed={seed}" if seed is not None else ""
    url = (
        f"https://image.pollinations.ai/prompt/{q}"
        f"?width={width}&height={height}&nologo=true&model={model}{seed_q}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 KunStudio/1.0"})
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
                f.write(r.read())
            if dest.exists() and dest.stat().st_size > 5_000:
                return dest
        except Exception as e:
            last_err = e
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f"pollinations failed: {last_err}")


# ───────── 자체 생성 무저작권 사운드 ─────────
def synth_noise(dest: Path, duration_sec: int = 300,
                 color: str = "pink", volume: float = 0.5) -> Path:
    """
    ffmpeg lavfi 로 화이트/핑크/브라운 노이즈 자체 생성. 저작권 0%.
      color: "white" | "pink" | "brown"
    """
    if dest.exists() and dest.stat().st_size > 10_000:
        return dest
    src = {
        "white": "anoisesrc=color=white",
        "pink":  "anoisesrc=color=pink",
        "brown": "anoisesrc=color=brown",
    }.get(color, "anoisesrc=color=pink")
    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi",
        "-i", f"{src}:amplitude={volume}:r=44100",
        "-t", str(duration_sec),
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(dest),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dest


def mix_two_audios(a: Path, b: Path, dest: Path,
                    a_vol: float = 0.7, b_vol: float = 0.5) -> Path:
    """두 오디오 amix (자연 사운드 레이어링용)."""
    cmd = [
        FFMPEG, "-y",
        "-i", str(a), "-i", str(b),
        "-filter_complex",
        f"[0:a]volume={a_vol}[a0];[1:a]volume={b_vol}[a1];[a0][a1]amix=inputs=2:duration=shortest",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(dest),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dest


# ───────── 영상 헬퍼 ─────────
def loop_audio_to_hours(short_audio: Path, dest_audio: Path, hours: float) -> Path:
    """짧은 5분 mp3 → N시간 stream_loop."""
    total = int(hours * 3600)
    cmd = [
        FFMPEG, "-y",
        "-stream_loop", "-1",
        "-i", str(short_audio),
        "-t", str(total),
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(dest_audio),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dest_audio


def make_static_video(image: Path, audio: Path, dest_mp4: Path,
                       resolution: str = "1920x1080") -> Path:
    """단일 이미지 + 오디오 → mp4. (Whisper Atlas long-form 용)

    resolution: "WxH" 포맷 (예: "1920x1080"). 내부적으로 scale 의 ':' 포맷으로 변환.
    """
    if "x" in resolution:
        w, h = resolution.lower().split("x")
    else:
        w, h = "1920", "1080"
    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", str(image),
        "-i", str(audio),
        "-vf", (
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1"
        ),
        "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast", "-crf", "28",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(dest_mp4),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"ffmpeg make_static_video failed (rc={res.returncode}):\n"
            f"  cmd: {' '.join(cmd[:6])} ...\n"
            f"  stderr: {res.stderr[-1500:]}"
        )
    return dest_mp4


def ken_burns_clip(image: Path, dest_mp4: Path, seconds: int = 12,
                    portrait: bool = True, fps: int = 30) -> Path:
    """
    Ken Burns zoompan. portrait=True 면 1080x1920 (Shorts), False 면 1920x1080.
    """
    if portrait:
        scale = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        size = "1080x1920"
    else:
        scale = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
        size = "1920x1080"
    d_frames = seconds * fps
    vf = f"{scale},zoompan=z='min(zoom+0.0008,1.15)':d={d_frames}:s={size}:fps={fps}"
    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", str(image),
        "-vf", vf,
        "-t", str(seconds),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
        "-pix_fmt", "yuv420p",
        str(dest_mp4),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dest_mp4


def concat_clips_with_audio(clips: list[Path], audio: Path, dest_mp4: Path) -> Path:
    """concat 데모필 + 오디오 mux."""
    list_txt = dest_mp4.with_suffix(".list.txt")
    list_txt.write_text(
        "\n".join(f"file '{c.as_posix()}'" for c in clips),
        encoding="utf-8",
    )
    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_txt),
        "-i", str(audio),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(dest_mp4),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dest_mp4


# ───────── Gumroad affiliate footer (auto-injected into descriptions) ─────────
GUMROAD_FOOTER_BY_CHANNEL = {
    "whisper_atlas": (
        "\n\n📥 Sleep & Mindfulness Resources:\n"
        "Saju Diary — 12-month Korean self-knowledge workbook\n"
        "→ https://ghdejr.gumroad.com/l/qcjtu?utm_source=youtube&utm_campaign=whisper_atlas\n"
        "(Educational journal, not a fortune-telling product.)\n\n"
        "🎵 Pair with: Sori Atlas — Sleep & Ambient playlist\n"
        "→ https://www.youtube.com/playlist?list=PLI_ZAqNV4FUjwbfrFLyJ7ZvO9TPKiP37C"
    ),
    "wealth_blueprint": (
        "\n\n📥 Resources mentioned (Educational only — not financial advice):\n"
        "Saju Diary — 12-month Korean four-pillars workbook\n"
        "→ https://ghdejr.gumroad.com/l/qcjtu?utm_source=youtube&utm_campaign=wealth_blueprint\n\n"
        "🎵 Background music: Sori Atlas — Lofi Study playlist\n"
        "→ https://www.youtube.com/playlist?list=PLI_ZAqNV4FUgUP5FJ6CN-BC5RAvI7sEt7"
    ),
    "inner_archetypes": (
        "\n\n📥 Personality & self-knowledge resources:\n"
        "Saju Diary — Korean four-pillars 12-month workbook\n"
        "→ https://ghdejr.gumroad.com/l/qcjtu?utm_source=youtube&utm_campaign=inner_archetypes\n"
        "(Personality models are lenses, not diagnoses.)\n\n"
        "🎵 Reflective BGM: Sori Atlas — Lofi & Ambient\n"
        "→ https://www.youtube.com/@soriatlas"
    ),
    # healing_sleep_realm 폐기됨 (2026-04-29) — Sori Atlas의 "Sleep & Ambient" 재생목록으로 통합
    # Sori Atlas는 D:\scripts\suno_yt_pipeline.py로 자체 footer 처리
}

def _add_gumroad_footer(description: str, channel_key: str) -> str:
    """Append channel-specific Gumroad affiliate footer (idempotent)."""
    footer = GUMROAD_FOOTER_BY_CHANNEL.get(channel_key, "")
    if not footer or "ghdejr.gumroad.com" in (description or ""):
        return description
    # YouTube description hard limit ~5000 chars
    combined = (description or "").rstrip() + footer
    return combined[:4900]


# ───────── upload-post 통합 ─────────
def upload_to_channel(video_path: Path, channel_key: str,
                       title: str, description: str,
                       dry_run: bool = False,
                       max_retry: int = 3) -> tuple[bool, str]:
    """upload_post_client.post_to_channel 래퍼.

    SSL EOF / 타임아웃 등 일시적 네트워크 에러 시 max_retry 만큼 재시도.
    description 에 채널별 Gumroad 어필리에이트 footer 자동 삽입.
    """
    import time as _time
    log = get_logger()
    if channel_key not in CHANNEL_KEYS:
        return False, f"unknown channel_key={channel_key}"
    description = _add_gumroad_footer(description, channel_key)
    if dry_run:
        log.info(f"[DRY-RUN] would upload {video_path.name} → {channel_key} ({title[:60]!r})")
        return True, "dry-run"
    sys.path.insert(0, str(SRC_DIR))
    try:
        from upload_post_client import post_to_channel  # type: ignore
    except Exception as e:
        return False, f"import upload_post_client failed: {e}"

    last_resp = ""
    for attempt in range(1, max_retry + 1):
        ok, resp = post_to_channel(str(video_path), channel_key,
                                    title=title[:100], description=description)
        last_resp = str(resp)[:400]
        log.info(f"upload {channel_key} attempt {attempt}/{max_retry} ok={ok} resp={last_resp[:200]}")
        if ok:
            return True, last_resp
        # 비동기 백그라운드 처리 응답이면 재시도 X (실제론 OK)
        if "Upload initiated successfully in background" in last_resp:
            log.info(f"[INFO] {channel_key} 비동기 백그라운드 업로드 — OK 처리")
            return True, last_resp
        # SSL EOF / timeout 등 retryable 에러는 재시도
        retryable = any(s in last_resp for s in [
            "_ssl.c", "EOF occurred", "timed out", "Connection reset",
            "BadStatusLine", "RemoteDisconnected", "503", "502", "429",
        ])
        if not retryable or attempt >= max_retry:
            break
        wait = 10 * attempt  # 10s, 20s, 30s
        log.info(f"  retryable error, waiting {wait}s before retry")
        _time.sleep(wait)
    return False, last_resp


# ───────── self-test ─────────
if __name__ == "__main__":
    log = get_logger()
    env = load_secrets()
    log.info(f"secrets loaded: {len(env)} keys")
    log.info(f"upload-post key: {'OK' if env.get('UPLOADPOST_API_KEY') else 'MISSING'}")
    log.info(f"ffmpeg: {'OK' if Path(FFMPEG).exists() else 'MISSING'}")
    log.info(f"storage root: {STORAGE_ROOT}")
    for k, label in CHANNEL_KEYS.items():
        d = channel_dirs(k)
        log.info(f"  {k} ({label}) → {d['work']}")
