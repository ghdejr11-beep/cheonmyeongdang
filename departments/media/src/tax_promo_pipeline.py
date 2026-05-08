#!/usr/bin/env python3
"""
tax_promo_pipeline.py — 세금N혜택 5월 31일 마감 마케팅 자동 파이프라인.

산출물 (D:\\kunstudio-promo):
  tax_shorts/    : 5개 쇼츠 mp4 (1080x1920, 30~45초)
  tax_cards/     : 5개 카드뉴스 zip (각 6~8 슬라이드 1080x1350)
  tax_assets/    : 중간 산출물 (이미지, TTS, 자막)

발행 큐:
  departments/media/src/tax_promo_queue.json
  - 5월 1일~31일 매일 1개 발행 (총 31회)
  - 5쇼츠 + 5카드뉴스 = 10개를 31일 분산 (반복 사용)
  - 각 발행 시 multi_poster.send_all_direct() 호출
  - 쿠팡 자동 inject는 multi_poster 측에서 5회당 1회 처리

사용:
  python tax_promo_pipeline.py build      # 5쇼츠 + 5카드뉴스 생성
  python tax_promo_pipeline.py queue      # 발행 큐 JSON 생성
  python tax_promo_pipeline.py post-today # 오늘 분 1개 발행
  python tax_promo_pipeline.py all        # build + queue
"""
from __future__ import annotations
import os
import sys
import json
import time
import shutil
import zipfile
import urllib.request
import urllib.parse
import subprocess
import datetime
import wave
import struct
import math
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ───────── 경로 ─────────
PROJECT_ROOT = Path(r"D:\cheonmyeongdang")
SECRETS_PATH = PROJECT_ROOT / ".secrets"
SRC_DIR = PROJECT_ROOT / "departments" / "media" / "src"
LOG_DIR = PROJECT_ROOT / "departments" / "media" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

PROMO_ROOT = Path(r"D:\kunstudio-promo")
SHORTS_DIR = PROMO_ROOT / "tax_shorts"
CARDS_DIR = PROMO_ROOT / "tax_cards"
ASSETS_DIR = PROMO_ROOT / "tax_assets"
for d in (SHORTS_DIR, CARDS_DIR, ASSETS_DIR):
    d.mkdir(parents=True, exist_ok=True)

QUEUE_FILE = SRC_DIR / "tax_promo_queue.json"
LOG_FILE = LOG_DIR / "tax_promo.log"

FFMPEG = r"C:\Users\hdh02\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

LANDING = "https://tax-n-benefit-api.vercel.app"
HASHTAGS_BASE = "#종합소득세 #종소세 #환급 #프리랜서 #N잡러 #5월마감"
LEGAL_NOTE = "광고 · 세금N혜택 마케팅"

# 광고/홍보에 거론 금지 — 시비/소송 RISK (사용자 규칙 5/1)
# 본인 제품(천명당/세금N혜택 등)은 OK. 타사 실명만 차단.
FORBIDDEN_BRANDS = (
    "삼쩜삼", "자비스", "트리플3", "쎈택스", "토스인컴",
    "Samsung", "BTS", "Squid Game",
)


def assert_no_forbidden(text: str, label: str = "content") -> None:
    """발행 직전 호출. 금지어 발견 시 raise → schtask 중단."""
    if not text:
        return
    found = [b for b in FORBIDDEN_BRANDS if b in text]
    if found:
        raise RuntimeError(
            f"[GUARD] forbidden brand in {label}: {found}. "
            f"see CLAUDE.md feedback_no_specific_company_names rule."
        )


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


def log(msg: str) -> None:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ───────── 콘텐츠 정의 (5개 쇼츠/카드뉴스) ─────────
# 핵심 원칙: 광고법 준수
#  - "100% 환불 보장" (사실 — 환급 0원 시) → OK
#  - "100% 환급 보장" → 금지 (불가능 약속)
#  - "3일 안에" → "3영업일 SLA" 정확 표기
#  - 광고/마케팅 표기 명시
CONTENT = [
    {
        "id": "shorts1_price",
        "title": "타 환급 서비스 수수료 20%? 9.9%로 절반에 끝내세요",
        "hook": "타 환급 서비스 수수료\n환급액의 20%",
        "body_lines": [
            "환급 30만원이면",
            "수수료만 6만원",
            "",
            "세금N혜택은 9.9%",
            "30만원 환급 시 → 2.97만원",
            "",
            "절반 이하의 비용으로",
            "동일한 환급 서비스",
        ],
        "cta": "tax-n-benefit-api.vercel.app",
        "scenes": [
            {"prompt": "korean money won banknotes flying mid-air, dramatic blue lighting, photorealistic, 9:16, vertical composition", "subtitle": "타 환급 서비스 수수료 20%"},
            {"prompt": "korean freelancer surprised face looking at smartphone, expressive shock, kdrama style, 9:16 vertical", "subtitle": "환급 30만원이면 6만원"},
            {"prompt": "minimal infographic comparing 20% vs 9.9% percentage chart, clean white background, korean fintech style, 9:16", "subtitle": "세금N혜택은 9.9%"},
            {"prompt": "korean smartphone screen showing tax refund app interface, modern UI, blue accent, 9:16 vertical", "subtitle": "30만원이면 2.97만원"},
            {"prompt": "happy korean person holding cash celebrating savings, warm sunlight, candid style, 9:16 vertical", "subtitle": "절반 이하의 비용"},
        ],
        "caption_x": "타 환급 서비스 수수료 20% 너무 비싸지 않나요?\n\n세금N혜택은 9.9%\n환급 30만원이면 약 3만원 수수료로 끝.\n\n5월 31일 종합소득세 마감 임박.\n👉 tax-n-benefit-api.vercel.app",
        "caption_long": "타 환급 서비스 수수료 부담스러우셨죠?\n\n환급액의 20%, 30만원 환급이면 수수료만 6만원입니다.\n세금N혜택은 9.9% — 30만원 환급 시 약 2.97만원.\n절반 이하 비용으로 동일한 환급 서비스를 이용하실 수 있습니다.\n\n프리랜서·N잡러·크리에이터 모두 가능.\n5월 31일 종합소득세 신고 마감까지 D-DAY 카운트다운 중.\n\n무료 환급액 조회 → tax-n-benefit-api.vercel.app\n\n" + LEGAL_NOTE + "\n\n" + HASHTAGS_BASE + " #수수료비교 #절세",
    },
    {
        "id": "shorts2_refund",
        "title": "환급 0원 나와도 100% 환불 보장",
        "hook": "환급 0원이면\n수수료 0원",
        "body_lines": [
            "환급액 조회 → 무료",
            "신고 진행 → 9.9% 수수료",
            "",
            "만약 환급 0원이라면?",
            "→ 수수료 100% 환불",
            "",
            "리스크 0",
            "안 받으면 손해",
        ],
        "cta": "tax-n-benefit-api.vercel.app",
        "scenes": [
            {"prompt": "korean wallet opening empty inside, soft warm light, minimal photo, 9:16 vertical", "subtitle": "환급 0원이면"},
            {"prompt": "korean hand giving cash refund, focus on money exchange, photorealistic, 9:16 vertical", "subtitle": "수수료 100% 환불"},
            {"prompt": "korean smartphone showing zero risk shield icon, blue glow, modern fintech UI, 9:16 vertical", "subtitle": "리스크 제로"},
            {"prompt": "korean office worker checking tax refund on laptop, relieved smile, soft natural light, 9:16 vertical", "subtitle": "안 받으면 손해"},
            {"prompt": "korean happy customer thumbs up with phone showing refund app, casual style, 9:16 vertical", "subtitle": "지금 무료 조회"},
        ],
        "caption_x": "환급 0원 나오면 어떡해요?\n→ 수수료 100% 환불 보장.\n\n조회는 무료, 신고는 9.9%.\n환급 안 나오면 비용 0원.\n\n👉 tax-n-benefit-api.vercel.app",
        "caption_long": "\"환급 안 나오면 수수료만 날리는 거 아닌가요?\"\n\n걱정 마세요.\n조회는 100% 무료, 신고 진행은 환급액의 9.9%.\n만약 환급액이 0원으로 산정되면 수수료 100% 환불 보장입니다.\n\n리스크는 진짜 0.\n프리랜서·N잡러라면 안 해 볼 이유가 없죠.\n\n무료 조회 → tax-n-benefit-api.vercel.app\n\n" + LEGAL_NOTE + " (수수료 환불 정책은 표준 약관 기준)\n\n" + HASHTAGS_BASE + " #환불보장 #리스크제로",
    },
    {
        "id": "shorts3_deadline",
        "title": "5월 31일 마감 임박 - 3영업일 안에 끝내는 법",
        "hook": "종소세 마감\nD-DAY 임박",
        "body_lines": [
            "5월 31일이 마감",
            "지나면 가산세",
            "",
            "세금N혜택",
            "3영업일 SLA 처리",
            "",
            "지연 시 무료 처리",
            "지금 시작하세요",
        ],
        "cta": "tax-n-benefit-api.vercel.app",
        "scenes": [
            {"prompt": "korean wall calendar showing May 31 circled in red, dramatic ticking clock, 9:16 vertical", "subtitle": "5월 31일 마감"},
            {"prompt": "korean stressed freelancer looking at calendar deadline, anxious expression, dim lighting, 9:16 vertical", "subtitle": "지나면 가산세"},
            {"prompt": "korean smartphone with tax app showing 3 day SLA progress bar, modern UI, blue accent, 9:16 vertical", "subtitle": "3영업일 SLA"},
            {"prompt": "korean professional accountant working efficiently on documents, fast pace, motion blur, 9:16 vertical", "subtitle": "지연 시 무료 처리"},
            {"prompt": "korean clock and tax document with checkmark, deadline met, victory mood, 9:16 vertical", "subtitle": "지금 시작"},
        ],
        "caption_x": "종소세 마감 5월 31일.\n\n지나면 가산세 추가.\n세금N혜택 = 3영업일 SLA, 지연 시 무료.\n\n지금 시작하면 안전합니다.\n👉 tax-n-benefit-api.vercel.app",
        "caption_long": "종합소득세 마감일 = 2026년 5월 31일.\n넘기면 무신고 가산세 + 납부지연 가산세가 추가됩니다.\n\n세금N혜택은 3영업일 SLA로 처리합니다.\n만약 영업일 기준 3일을 초과하면 수수료 무료 처리.\n\n시간 없는 N잡러·프리랜서를 위한 빠른 환급 서비스.\n5월 31일 전에 끝내야 합니다.\n\n👉 tax-n-benefit-api.vercel.app\n\n" + LEGAL_NOTE + "\n\n" + HASHTAGS_BASE + " #5월31일 #마감임박 #SLA",
    },
    {
        "id": "shorts4_average",
        "title": "프리랜서 종소세 환급 평균 27만원 - 안 받으면 손해",
        "hook": "프리랜서 평균\n환급 27만원",
        "body_lines": [
            "원천징수 3.3%",
            "쌓이고 쌓여서",
            "",
            "프리랜서 평균",
            "환급액 약 27만원",
            "",
            "신고 안 하면",
            "그대로 국가행",
        ],
        "cta": "tax-n-benefit-api.vercel.app",
        "scenes": [
            {"prompt": "korean freelancer working on laptop in cafe, candid lifestyle photo, warm light, 9:16 vertical", "subtitle": "프리랜서 환급"},
            {"prompt": "stack of korean won bills falling like leaves, money rain, dramatic light, 9:16 vertical", "subtitle": "평균 27만원"},
            {"prompt": "korean infographic showing 3.3 percent withholding tax bar chart, clean modern, 9:16 vertical", "subtitle": "원천징수 3.3%"},
            {"prompt": "korean person regretful looking at empty wallet, soft tragic light, 9:16 vertical", "subtitle": "신고 안 하면"},
            {"prompt": "korean person celebrating tax refund notification on smartphone, joyful expression, 9:16 vertical", "subtitle": "지금 확인"},
        ],
        "caption_x": "프리랜서 종소세 환급 평균 27만원.\n\n원천징수 3.3%가 1년 쌓이면 큰 돈.\n신고 안 하면 그대로 손해.\n\n무료 조회 → tax-n-benefit-api.vercel.app",
        "caption_long": "프리랜서·N잡러 평균 종소세 환급액 약 27만원 (수입 규모/경비에 따라 차이 있음).\n\n3.3% 원천징수가 1년 동안 쌓인 게 환급 가능한 금액입니다.\n신고 안 하면 그대로 국세청에 남고, 5년 지나면 사라집니다.\n\n무료 조회 1분이면 충분.\n5월 31일 마감 전에 확인하세요.\n\n👉 tax-n-benefit-api.vercel.app\n\n" + LEGAL_NOTE + " (환급액은 개인 수입/경비에 따라 다릅니다)\n\n" + HASHTAGS_BASE + " #환급평균 #프리랜서절세",
    },
    {
        "id": "shorts5_bundle",
        "title": "의료비 + 통신비도 한번에 - 추가 환급 가능",
        "hook": "의료비 + 통신비\n추가 공제",
        "body_lines": [
            "기본 환급 외에",
            "의료비 공제",
            "통신비 공제",
            "월세 공제",
            "",
            "추가로 받을 수 있는",
            "환급액 평균 +15~50만원",
        ],
        "cta": "tax-n-benefit-api.vercel.app",
        "scenes": [
            {"prompt": "korean medical bill receipt and stethoscope on desk, soft warm light, 9:16 vertical", "subtitle": "의료비 공제"},
            {"prompt": "korean smartphone bill on table with money next to it, minimal scene, 9:16 vertical", "subtitle": "통신비 공제"},
            {"prompt": "korean apartment monthly rent contract document with cash, 9:16 vertical", "subtitle": "월세 공제"},
            {"prompt": "korean infographic showing additional refund range bar chart, clean modern UI, 9:16 vertical", "subtitle": "추가 +15~50만원"},
            {"prompt": "korean happy customer with multiple refund notifications on phone, joy, 9:16 vertical", "subtitle": "한번에 처리"},
        ],
        "caption_x": "기본 환급 + 의료비/통신비/월세 공제까지.\n\n추가 환급 평균 15~50만원.\n안 챙기면 손해.\n\n👉 tax-n-benefit-api.vercel.app",
        "caption_long": "기본 종소세 환급 외에 추가로 받을 수 있는 공제 항목들.\n\n• 의료비 세액공제 (총급여 3% 초과분)\n• 통신비 (사업자 등록 시 비용 처리)\n• 월세 세액공제 (총급여 7천만원 이하)\n• 신용카드 사용액 공제\n\n조건/금액별로 추가 환급 평균 15~50만원 가능 (개인차).\n세금N혜택은 이 모든 공제를 한번에 처리해 드립니다.\n\n5월 31일 마감 → tax-n-benefit-api.vercel.app\n\n" + LEGAL_NOTE + " (공제 가능 여부는 개인 상황 따라 다름)\n\n" + HASHTAGS_BASE + " #세액공제 #의료비공제 #월세공제",
    },
]


# ───────── Pollinations Flux ─────────
def pollinations_image(prompt: str, dest: Path, width=1080, height=1920, seed=None) -> Path:
    if dest.exists() and dest.stat().st_size > 5_000:
        return dest
    q = urllib.parse.quote(prompt)
    seed_q = f"&seed={seed}" if seed is not None else ""
    url = f"https://image.pollinations.ai/prompt/{q}?width={width}&height={height}&nologo=true&model=flux{seed_q}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 KunStudio/1.0"})
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
                f.write(r.read())
            if dest.exists() and dest.stat().st_size > 5_000:
                return dest
        except Exception as e:
            last = e
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f"pollinations failed: {last}")


# ───────── ElevenLabs TTS (한국어) ─────────
# Multilingual v2 모델은 한국어 지원. 무료 voice_id.
ELEVEN_VOICE_ID = "uyVNoMrnUku1dZyVEXwD"  # Anna Kim (다국어 한국어 무난)
ELEVEN_MODEL = "eleven_multilingual_v2"


def elevenlabs_tts(text: str, dest: Path, env: dict | None = None) -> Path | None:
    """텍스트 → mp3. 실패 시 None 반환 (silence fallback)."""
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    env = env or load_secrets()
    key = env.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        log("[TTS] ELEVENLABS_API_KEY 없음 — silence fallback")
        return None
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    payload = json.dumps({
        "text": text,
        "model_id": ELEVEN_MODEL,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.7},
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, method="POST",
        headers={
            "xi-api-key": key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "User-Agent": "KunStudio-Tax/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
            f.write(r.read())
        if dest.exists() and dest.stat().st_size > 1000:
            log(f"[TTS] OK {dest.name} ({dest.stat().st_size} bytes)")
            return dest
    except Exception as e:
        log(f"[TTS] 실패: {type(e).__name__}: {e}")
    return None


# ───────── 무저작권 BGM (lavfi sine + lowpass) ─────────
def synth_bgm(dest: Path, duration_sec: int = 45, freq: int = 220) -> Path:
    """ffmpeg lavfi 로 부드러운 사인파 + 페이드 BGM 생성."""
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi",
        "-i", f"sine=frequency={freq}:duration={duration_sec}:sample_rate=44100",
        "-f", "lavfi",
        "-i", f"sine=frequency={freq * 1.5:.0f}:duration={duration_sec}:sample_rate=44100",
        "-filter_complex",
        f"[0:a]volume=0.10[a];[1:a]volume=0.05[b];[a][b]amix=inputs=2:duration=shortest,"
        f"lowpass=f=1200,afade=t=in:st=0:d=2,afade=t=out:st={duration_sec-2}:d=2",
        "-c:a", "libmp3lame", "-b:a", "128k",
        str(dest),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dest


def synth_silence(dest: Path, duration_sec: int = 8) -> Path:
    """무음 mp3 (TTS 실패 시 fallback)."""
    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=channel_layout=stereo:sample_rate=44100",
        "-t", str(duration_sec),
        "-c:a", "libmp3lame", "-b:a", "128k",
        str(dest),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dest


# ───────── 자막 SRT 생성 ─────────
def write_srt(dest: Path, segments: list[tuple[float, float, str]]) -> Path:
    """segments: [(start, end, text), ...]"""
    def fmt(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t - int(t)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    lines = []
    for i, (a, b, txt) in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{fmt(a)} --> {fmt(b)}")
        lines.append(txt)
        lines.append("")
    dest.write_text("\n".join(lines), encoding="utf-8")
    return dest


# ───────── 쇼츠 mp4 생성 ─────────
def build_short(content: dict, force: bool = False) -> Path:
    cid = content["id"]
    out = SHORTS_DIR / f"{cid}.mp4"
    if out.exists() and not force:
        log(f"[shorts] skip exists: {out.name}")
        return out
    work = ASSETS_DIR / cid
    work.mkdir(parents=True, exist_ok=True)

    log(f"[shorts] === {cid} 시작 ===")

    # 1) 이미지 5장 생성
    n = len(content["scenes"])
    scene_dur = 8.0  # 8초씩 5장 = 40초
    img_paths = []
    for i, sc in enumerate(content["scenes"]):
        img = work / f"scene_{i:02d}.jpg"
        try:
            pollinations_image(sc["prompt"], img, width=1080, height=1920, seed=1000 + i)
        except Exception as e:
            log(f"[shorts][img{i}] 실패: {e}")
            # 이미 있는 이미지로 fallback
            if not img.exists():
                # 첫 번째 이미지가 있으면 복사 fallback
                if img_paths:
                    shutil.copy(img_paths[-1], img)
                else:
                    raise
        img_paths.append(img)
        log(f"[shorts][img{i}] {img.name}")

    # 2) TTS 한국어 (각 scene_subtitle + 마지막 CTA)
    full_narration = "\n".join([sc["subtitle"] for sc in content["scenes"]] + ["지금 바로 무료 조회하세요."])
    tts_path = work / "narration.mp3"
    env = load_secrets()
    tts_ok = elevenlabs_tts(full_narration, tts_path, env)
    if not tts_ok:
        synth_silence(tts_path, duration_sec=int(n * scene_dur))

    # 3) BGM 생성
    bgm_path = work / "bgm.mp3"
    synth_bgm(bgm_path, duration_sec=int(n * scene_dur + 2))

    # 4) Mix narration + BGM (narration 0.9, BGM 0.15)
    mixed = work / "audio_mix.mp3"
    cmd = [
        FFMPEG, "-y",
        "-i", str(tts_path),
        "-i", str(bgm_path),
        "-filter_complex",
        "[0:a]volume=1.0[a];[1:a]volume=0.18[b];[a][b]amix=inputs=2:duration=longest",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(mixed),
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # 5) SRT 자막 생성
    srt_path = work / "subs.srt"
    segs = []
    for i, sc in enumerate(content["scenes"]):
        start = i * scene_dur
        end = (i + 1) * scene_dur - 0.2
        segs.append((start, end, sc["subtitle"]))
    write_srt(srt_path, segs)

    # 6) ffmpeg: 이미지 5장 → 영상 슬라이드쇼 + 자막 + 음성 + 그라데이션 오버레이
    # concat demuxer 방식: 각 이미지 8초씩
    concat_txt = work / "concat.txt"
    lines = []
    for img in img_paths:
        lines.append(f"file '{img.as_posix()}'")
        lines.append(f"duration {scene_dur}")
    lines.append(f"file '{img_paths[-1].as_posix()}'")  # last image without duration (concat quirk)
    concat_txt.write_text("\n".join(lines), encoding="utf-8")

    # 자막 스타일 (KO 큰글씨 + 검은 배경)
    srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")
    sub_style = (
        "FontName=Malgun Gothic,FontSize=22,Bold=1,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,"
        "BorderStyle=4,Outline=2,Shadow=0,Alignment=2,MarginV=120"
    )

    # 그라데이션 오버레이는 drawbox 로 상하 어둡게 (텍스트 가독성)
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"drawbox=x=0:y=0:w=1080:h=300:color=black@0.4:t=fill,"
        f"drawbox=x=0:y=1620:w=1080:h=300:color=black@0.5:t=fill,"
        f"drawtext=fontfile='C\\:/Windows/Fonts/malgunbd.ttf':"
        f"text='{LEGAL_NOTE}':fontcolor=white@0.85:fontsize=24:"
        f"x=(w-text_w)/2:y=40,"
        f"drawtext=fontfile='C\\:/Windows/Fonts/malgunbd.ttf':"
        f"text='{LANDING.replace(':', chr(92)+chr(58))}':fontcolor=yellow:fontsize=28:"
        f"x=(w-text_w)/2:y=h-90,"
        f"subtitles='{srt_escaped}':force_style='{sub_style}'"
    )

    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-i", str(mixed),
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(out),
    ]
    log(f"[shorts] ffmpeg encoding…")
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        log(f"[shorts] ffmpeg ERROR: {proc.stderr.decode('utf-8', errors='ignore')[-1500:]}")
        raise RuntimeError(f"ffmpeg failed for {cid}")
    log(f"[shorts] DONE {out.name} ({out.stat().st_size // 1024} KB)")
    return out


# ───────── 카드뉴스 PNG 생성 (Pillow) ─────────
def build_cards(content: dict, force: bool = False) -> Path:
    """6슬라이드 카드뉴스 (1080x1350) zip."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

    cid = content["id"]
    out_zip = CARDS_DIR / f"{cid}_cards.zip"
    if out_zip.exists() and not force:
        log(f"[cards] skip exists: {out_zip.name}")
        return out_zip

    work = ASSETS_DIR / f"{cid}_cards"
    work.mkdir(parents=True, exist_ok=True)

    W, H = 1080, 1350
    font_path = "C:/Windows/Fonts/malgunbd.ttf"
    font_path_normal = "C:/Windows/Fonts/malgun.ttf"

    def font(size, bold=True):
        try:
            return ImageFont.truetype(font_path if bold else font_path_normal, size)
        except Exception:
            return ImageFont.load_default()

    def gradient_bg(color_top, color_bot):
        img = Image.new("RGB", (W, H), color_top)
        draw = ImageDraw.Draw(img)
        for y in range(H):
            r = int(color_top[0] + (color_bot[0] - color_top[0]) * y / H)
            g = int(color_top[1] + (color_bot[1] - color_top[1]) * y / H)
            b = int(color_top[2] + (color_bot[2] - color_top[2]) * y / H)
            draw.line([(0, y), (W, y)], fill=(r, g, b))
        return img

    def draw_centered(draw, text, y, fnt, color=(255, 255, 255)):
        bbox = draw.textbbox((0, 0), text, font=fnt)
        w = bbox[2] - bbox[0]
        x = (W - w) // 2
        draw.text((x, y), text, font=fnt, fill=color)
        return y + (bbox[3] - bbox[1])

    def draw_multiline(draw, lines, y_start, fnt, color=(255, 255, 255), gap=18):
        y = y_start
        for ln in lines:
            if not ln.strip():
                y += 30
                continue
            bbox = draw.textbbox((0, 0), ln, font=fnt)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (W - w) // 2
            draw.text((x, y), ln, font=fnt, fill=color)
            y += h + gap
        return y

    color_themes = {
        "shorts1_price": ((24, 50, 110), (10, 24, 60)),       # 진한 블루
        "shorts2_refund": ((20, 110, 70), (10, 60, 40)),      # 그린
        "shorts3_deadline": ((150, 30, 30), (80, 12, 12)),    # 레드
        "shorts4_average": ((130, 90, 30), (70, 40, 10)),     # 골드
        "shorts5_bundle": ((90, 40, 110), (40, 20, 60)),      # 퍼플
    }
    top_color, bot_color = color_themes.get(cid, ((30, 30, 60), (10, 10, 30)))

    slide_paths = []

    # Slide 1: Hook (강한 헤드라인)
    img = gradient_bg(top_color, bot_color)
    draw = ImageDraw.Draw(img)
    # 상단 라벨
    draw.text((40, 40), "세금N혜택", font=font(32), fill=(255, 255, 255, 200))
    draw.text((W - 200, 40), "1/6", font=font(28), fill=(255, 255, 255, 180))
    # 메인 후크
    hook_lines = content["hook"].split("\n")
    y = 380
    f_big = font(110)
    for ln in hook_lines:
        bbox = draw.textbbox((0, 0), ln, font=f_big)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), ln, font=f_big, fill=(255, 230, 80))  # 노랑 강조
        y += 130
    # 하단 화살표
    draw.text((W // 2 - 30, H - 200), "↓", font=font(80), fill=(255, 255, 255))
    p = work / "slide_1.png"
    img.save(p, optimize=True)
    slide_paths.append(p)

    # Slide 2: 문제 정의
    img = gradient_bg(top_color, bot_color)
    draw = ImageDraw.Draw(img)
    draw.text((40, 40), content["title"][:30], font=font(28), fill=(255, 255, 255, 180))
    draw.text((W - 200, 40), "2/6", font=font(28), fill=(255, 255, 255, 180))
    y = draw_centered(draw, "왜 중요한가요?", 200, font(56), (255, 230, 80))
    body1 = content["body_lines"][:4]
    draw_multiline(draw, body1, 360, font(48), (255, 255, 255), gap=16)
    p = work / "slide_2.png"
    img.save(p, optimize=True)
    slide_paths.append(p)

    # Slide 3: 솔루션
    img = gradient_bg(top_color, bot_color)
    draw = ImageDraw.Draw(img)
    draw.text((40, 40), content["title"][:30], font=font(28), fill=(255, 255, 255, 180))
    draw.text((W - 200, 40), "3/6", font=font(28), fill=(255, 255, 255, 180))
    y = draw_centered(draw, "이렇게 해결", 200, font(56), (120, 255, 180))
    body2 = content["body_lines"][4:] if len(content["body_lines"]) > 4 else content["body_lines"]
    draw_multiline(draw, body2, 360, font(46), (255, 255, 255), gap=16)
    p = work / "slide_3.png"
    img.save(p, optimize=True)
    slide_paths.append(p)

    # Slide 4: 차별점 / FAQ
    img = gradient_bg(top_color, bot_color)
    draw = ImageDraw.Draw(img)
    draw.text((40, 40), content["title"][:30], font=font(28), fill=(255, 255, 255, 180))
    draw.text((W - 200, 40), "4/6", font=font(28), fill=(255, 255, 255, 180))
    draw_centered(draw, "세금N혜택 차별점", 180, font(54), (255, 230, 80))
    bullets = [
        "수수료 9.9% (업계 평균 20%의 절반)",
        "환급 0원 시 100% 환불 보장",
        "3영업일 SLA · 지연 시 무료",
        "의료비/통신비/월세 통합 처리",
        "무료 조회 1분 완료",
    ]
    y = 350
    for b in bullets:
        draw.text((80, y), "✓", font=font(38), fill=(120, 255, 180))
        draw.text((140, y), b, font=font(34, bold=False), fill=(255, 255, 255))
        y += 90
    p = work / "slide_4.png"
    img.save(p, optimize=True)
    slide_paths.append(p)

    # Slide 5: 사회적 증거
    img = gradient_bg(top_color, bot_color)
    draw = ImageDraw.Draw(img)
    draw.text((40, 40), content["title"][:30], font=font(28), fill=(255, 255, 255, 180))
    draw.text((W - 200, 40), "5/6", font=font(28), fill=(255, 255, 255, 180))
    draw_centered(draw, "지금 시작하는 이유", 180, font(54), (255, 230, 80))
    reasons = [
        "5월 31일 마감 임박",
        "지나면 가산세 추가",
        "환급금은 5년 지나면 소멸",
        "신고 안 하면 그대로 손해",
    ]
    y = 380
    for r in reasons:
        bbox = draw.textbbox((0, 0), r, font=font(40))
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), r, font=font(40), fill=(255, 255, 255))
        y += 100
    p = work / "slide_5.png"
    img.save(p, optimize=True)
    slide_paths.append(p)

    # Slide 6: CTA
    img = gradient_bg(top_color, bot_color)
    draw = ImageDraw.Draw(img)
    draw.text((40, 40), content["title"][:30], font=font(28), fill=(255, 255, 255, 180))
    draw.text((W - 200, 40), "6/6", font=font(28), fill=(255, 255, 255, 180))
    draw_centered(draw, "지금 무료 조회", 280, font(72), (255, 230, 80))
    draw_centered(draw, "1분이면 됩니다", 400, font(48), (255, 255, 255))
    # URL 박스
    draw.rectangle([60, 720, W - 60, 850], fill=(255, 255, 255), outline=(255, 230, 80), width=4)
    draw_centered(draw, "tax-n-benefit-api.vercel.app", 750, font(40), (10, 24, 60))
    # 광고 표기
    draw.text((40, H - 80), LEGAL_NOTE, font=font(22, bold=False), fill=(255, 255, 255, 180))
    draw.text((W - 220, H - 80), "@kunstudio", font=font(22, bold=False), fill=(255, 255, 255, 180))
    p = work / "slide_6.png"
    img.save(p, optimize=True)
    slide_paths.append(p)

    # zip
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in slide_paths:
            z.write(p, p.name)
    log(f"[cards] DONE {out_zip.name} ({out_zip.stat().st_size // 1024} KB, {len(slide_paths)} slides)")
    return out_zip


# ───────── 발행 큐 생성 ─────────
def build_queue() -> Path:
    """5월 1일 ~ 5월 31일 매일 1개 발행. 31일 = 5쇼츠 + 5카드뉴스 × 약 3 사이클."""
    items = []
    today = datetime.date(2026, 5, 1)
    end = datetime.date(2026, 5, 31)

    # 콘텐츠 풀: 10개 (5 쇼츠 + 5 카드뉴스)
    pool = []
    for c in CONTENT:
        pool.append({"type": "shorts", "id": c["id"], "asset": str(SHORTS_DIR / f"{c['id']}.mp4"),
                     "caption_x": c["caption_x"], "caption_long": c["caption_long"]})
        pool.append({"type": "cards", "id": c["id"] + "_cards", "asset": str(CARDS_DIR / f"{c['id']}_cards.zip"),
                     "caption_x": c["caption_x"], "caption_long": c["caption_long"],
                     "first_slide": str(ASSETS_DIR / f"{c['id']}_cards" / "slide_1.png")})

    d = today
    i = 0
    while d <= end:
        item = dict(pool[i % len(pool)])
        item["date"] = d.isoformat()
        item["scheduled_time"] = "18:00"
        item["status"] = "pending"
        items.append(item)
        d += datetime.timedelta(days=1)
        i += 1

    queue = {
        "campaign": "tax_n_benefit_may_2026",
        "deadline": "2026-05-31",
        "landing": LANDING,
        "legal_note": LEGAL_NOTE,
        "hashtags": HASHTAGS_BASE,
        "channels": ["bluesky", "discord", "mastodon", "x", "threads", "instagram", "telegram"],
        "items": items,
    }
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"[queue] DONE {QUEUE_FILE} ({len(items)} items)")
    return QUEUE_FILE


# ───────── 텔레그램 알림 ─────────
def telegram_notify(msg: str, env: dict | None = None) -> bool:
    env = env or load_secrets()
    tok = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = env.get("TELEGRAM_CHAT_ID", "").strip()
    if not tok or not chat:
        return False
    url = f"https://api.telegram.org/bot{tok}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat, "text": msg[:4000]}).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception as e:
        log(f"[tg] {e}")
        return False


# ───────── 오늘 분 발행 ─────────
def post_today() -> dict:
    if not QUEUE_FILE.exists():
        log("[post] queue 없음 — build_queue() 먼저")
        return {"error": "no queue"}
    queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    today_iso = datetime.date.today().isoformat()
    target = None
    target_idx = None
    for i, item in enumerate(queue["items"]):
        if item["date"] == today_iso and item.get("status") == "pending":
            target = item
            target_idx = i
            break
    if not target:
        log(f"[post] 오늘({today_iso}) 발행할 항목 없음")
        return {"info": "no item today"}

    log(f"[post] {target['type']} {target['id']}")
    # multi_poster 호출
    sys.path.insert(0, str(SRC_DIR))
    try:
        import multi_poster
    except Exception as e:
        log(f"[post] multi_poster import 실패: {e}")
        return {"error": str(e)}

    text = target["caption_long"]
    # GUARD: 금지된 타사 실명 발견 시 발행 차단 (사용자 규칙 5/1)
    assert_no_forbidden(text, label=f"caption_long({target['id']})")
    assert_no_forbidden(target.get("caption_x", ""), label=f"caption_x({target['id']})")
    img_url = None
    if target["type"] == "cards":
        # 카드뉴스 첫 슬라이드를 IG 이미지로 사용
        if Path(target["first_slide"]).exists():
            img_url = target["first_slide"]
    elif target["type"] == "shorts":
        # 쇼츠는 영상 — IG는 첫 프레임 이미지로 대체
        img = ASSETS_DIR / target["id"] / "scene_00.jpg"
        if img.exists():
            img_url = str(img)

    results = multi_poster.send_all_direct(text, image_url=img_url)
    # 텔레그램 별도 (multi_poster에 telegram 없으면)
    telegram_notify(f"[세금N혜택 마케팅 발행] {target['id']}\n{target['caption_x'][:200]}")

    queue["items"][target_idx]["status"] = "posted"
    queue["items"][target_idx]["posted_at"] = datetime.datetime.now().isoformat()
    queue["items"][target_idx]["results"] = {k: bool(v) for k, v in results.items()}
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"[post] results: {results}")
    return results


# ───────── main ─────────
def cmd_build(force: bool = False):
    log("=== build 시작 ===")
    for c in CONTENT:
        try:
            build_short(c, force=force)
        except Exception as e:
            log(f"[build][{c['id']}] shorts FAIL: {type(e).__name__}: {e}")
        try:
            build_cards(c, force=force)
        except Exception as e:
            log(f"[build][{c['id']}] cards FAIL: {type(e).__name__}: {e}")
    log("=== build 완료 ===")


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "all"
    force = "--force" in args
    if cmd == "build":
        cmd_build(force=force)
    elif cmd == "queue":
        build_queue()
    elif cmd == "all":
        cmd_build(force=force)
        build_queue()
    elif cmd == "post-today":
        post_today()
    elif cmd == "test-tts":
        # 짧은 한 문장만 테스트
        env = load_secrets()
        out = ASSETS_DIR / "test_tts.mp3"
        r = elevenlabs_tts("안녕하세요 세금N혜택 테스트입니다", out, env)
        log(f"test-tts → {r}")
    elif cmd == "test-img":
        out = ASSETS_DIR / "test_img.jpg"
        pollinations_image("korean money won banknotes, simple, 9:16 vertical", out, 1080, 1920)
        log(f"test-img → {out} ({out.stat().st_size} bytes)")
    elif cmd == "build-one":
        cid = args[1] if len(args) > 1 else CONTENT[0]["id"]
        c = next((x for x in CONTENT if x["id"] == cid), None)
        if not c:
            log(f"unknown id: {cid}")
            return
        build_short(c, force=force)
        build_cards(c, force=force)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
