#!/usr/bin/env python3
"""
Wealth Blueprint — 부 마인드셋 / 부자 습관 / 영어 자기계발 쇼츠 (60초).
스타일: Mel Robbins / Naval Ravikant / James Clear (인용 + 짧은 해설).

⚠️ 법적 안전:
  - 메모리 규칙: 보험업법 / 투자 권유 위반 컨텐츠 X
  - "이 종목 사세요", "월 X% 수익" 등 금융 자문 표현 절대 금지
  - 마인드셋 / 습관 / 영어 표현 학습 프레이밍 으로 한정
  - 모든 영상 description 에 "Educational only, not financial advice" 디스클레이머

파이프라인:
  1. 오늘의 quote 선택 (Naval/Mel/Clear/Buffett 격언, public domain or fair-use 짧은 인용)
  2. Claude (Haiku 폴백 → Sonnet) 으로 60초 해설 스크립트 생성
  3. edge-tts (무료) 또는 ElevenLabs (Free 한도) 음성
  4. Pollinations Flux 9:16 이미지 5장 (Ken Burns)
  5. concat + 자막 SRT 임베드 (영어/한국어 듀얼)
  6. (옵션) Upload-Post → YouTube wealth_blueprint
"""
from __future__ import annotations
import argparse
import datetime
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

from yt_channel_common import (  # type: ignore
    get_logger, load_secrets, channel_dirs,
    pollinations_image,
    ken_burns_clip, concat_clips_with_audio,
    upload_to_channel, FFMPEG,
)

CHANNEL_KEY = "wealth_blueprint"

# Public-domain & widely-quoted single-line aphorisms (fair-use 짧은 인용)
# 투자 권유 표현 0%, 마인드셋·습관 한정.
QUOTES = [
    {
        "en": "You will never change your life until you change something you do daily.",
        "ko": "매일 하는 행동을 바꾸지 않으면 인생은 절대 바뀌지 않는다.",
        "author": "John C. Maxwell",
        "theme": "habits",
    },
    {
        "en": "Seek wealth, not money or status. Wealth is assets that earn while you sleep.",
        "ko": "돈과 지위가 아니라 부를 추구하라. 부는 당신이 자는 동안에도 돈을 버는 자산이다.",
        "author": "Naval Ravikant",
        "theme": "mindset",
    },
    {
        "en": "You do not rise to the level of your goals. You fall to the level of your systems.",
        "ko": "당신은 목표의 수준으로 올라가는 게 아니라, 시스템의 수준으로 떨어진다.",
        "author": "James Clear",
        "theme": "habits",
    },
    {
        "en": "If you do not find a way to make money while you sleep, you will work until you die.",
        "ko": "자는 동안 돈 버는 법을 찾지 못하면, 죽을 때까지 일해야 한다.",
        "author": "Warren Buffett",
        "theme": "mindset",
    },
    {
        "en": "Discipline equals freedom.",
        "ko": "규율이 곧 자유다.",
        "author": "Jocko Willink",
        "theme": "discipline",
    },
    {
        "en": "Compound interest is the eighth wonder of the world.",
        "ko": "복리는 세계 8대 불가사의다.",
        "author": "Albert Einstein (attributed)",
        "theme": "mindset",
    },
    {
        "en": "The first principle is that you must not fool yourself, and you are the easiest person to fool.",
        "ko": "첫 번째 원칙은 자신을 속이지 않는 것이다. 가장 속이기 쉬운 사람이 바로 자신이다.",
        "author": "Richard Feynman",
        "theme": "mindset",
    },
]


def pick_quote() -> dict:
    return QUOTES[datetime.date.today().toordinal() % len(QUOTES)]


def claude_haiku_or_sonnet(prompt: str, env: dict, log) -> str | None:
    """Haiku 우선 시도, 실패 시 Sonnet. 둘 다 실패하면 None (폴백 사용)."""
    import urllib.request
    key = env.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        log.info("  no ANTHROPIC_API_KEY → skipping Claude, using fallback script")
        return None
    for model in ("claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929"):
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps({
                    "model": model,
                    "max_tokens": 600,
                    "system": (
                        "You are a YouTube Shorts script writer for a wealth-mindset "
                        "channel. Write in plain spoken English. Educational framing only. "
                        "NEVER recommend specific stocks, crypto, or investment products. "
                        "NEVER promise income amounts. No medical or legal advice."
                    ),
                    "messages": [{"role": "user", "content": prompt}],
                }).encode(),
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
            return data["content"][0]["text"].strip()
        except Exception as e:
            log.info(f"  Claude {model} failed: {e}")
    return None


def fallback_script(q: dict) -> str:
    """Claude 호출 실패 시 templated 스크립트 (60초 분량)."""
    return (
        f"Here is a thought worth a minute of your day. {q['author']} said this. "
        f"Quote. {q['en']} End quote. "
        "Read it again slowly. "
        "Most of us spend years chasing motivation when what we really need is a small "
        "system that runs whether we feel like it or not. "
        "Pick one tiny action you can repeat every single day. Just one. "
        "Two minutes. Maybe three. "
        "Then show up tomorrow and do it again. That is the entire blueprint. "
        "If this hit home, follow for one mindset reset every morning."
    )


def synth_voice(text: str, out_mp3: Path, env: dict, log) -> Path:
    """edge-tts 무료 우선, 실패 시 ElevenLabs Free."""
    # 1) edge-tts (무료, 키 불필요)
    try:
        sys.path.insert(0, str(Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\youtube\shared")))
        from tts import synthesize  # type: ignore
        synthesize(text, out_mp3, voice="en-US-GuyNeural")
        log.info(f"  voice: edge-tts → {out_mp3.name}")
        return out_mp3
    except Exception as e:
        log.info(f"  edge-tts failed: {e}, trying ElevenLabs")

    # 2) ElevenLabs (Free 10K char/월)
    import urllib.request
    key = env.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise RuntimeError("no ELEVENLABS_API_KEY for fallback")
    voice_id = "JBFqnCBsd6RMkjVDRZzb"  # George (영어 남성)
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps({
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r, open(out_mp3, "wb") as f:
        f.write(r.read())
    log.info(f"  voice: ElevenLabs → {out_mp3.name}")
    return out_mp3


def write_dual_subtitle(srt_path: Path, en: str, ko: str, total_seconds: float):
    """간단 듀얼 자막 (전체 길이 1줄, 화면 위 1/4)."""
    def _fmt(t):
        h = int(t // 3600); m = int(t // 60) % 60; s = t % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
    srt_path.write_text(
        "1\n"
        f"{_fmt(0.5)} --> {_fmt(max(2.0, total_seconds - 0.5))}\n"
        f"{ko}\n{en}\n",
        encoding="utf-8",
    )


def run(dry_run: bool = False) -> Path:
    log = get_logger()
    env = load_secrets()
    dirs = channel_dirs(CHANNEL_KEY)
    q = pick_quote()
    slug = f"{q['theme']}_{datetime.date.today().isoformat()}"
    log.info(f"=== Wealth Blueprint | quote={q['author']} theme={q['theme']} dry_run={dry_run} ===")

    # 1. 스크립트
    prompt = (
        f"Write a 55-60 second YouTube Shorts script (about 145 spoken words) "
        f"unpacking this aphorism for a young adult audience aiming to build "
        f"better daily habits and a stronger financial mindset.\n\n"
        f"QUOTE: \"{q['en']}\" — {q['author']}\n\n"
        "Rules:\n"
        "- Hook in first 3 seconds.\n"
        "- 3 concrete daily actions (habit-level, no income claims).\n"
        "- End with: 'Follow for one mindset reset every morning.'\n"
        "- Plain spoken English, no markdown, no stage directions.\n"
        "- Do NOT recommend stocks, crypto, real estate, courses, or any product.\n"
        "- Do NOT promise income amounts or guaranteed outcomes."
    )
    script = claude_haiku_or_sonnet(prompt, env, log)
    if not script:
        script = fallback_script(q)
        log.info("  using fallback script")
    (dirs["output"] / f"{slug}.txt").write_text(script, encoding="utf-8")
    log.info(f"  script: {len(script)} chars")

    # 2. TTS
    audio = dirs["audio"] / f"{slug}.mp3"
    synth_voice(script, audio, env, log)

    # 3. 9:16 이미지 5장
    img_prompts = [
        f"Cinematic young person at sunrise window writing in a journal, soft warm light, 9:16, photoreal, no text",
        f"Minimal aesthetic desk with notebook, coffee, plant, soft daylight, 9:16, photoreal, no text",
        f"Person walking at golden hour silhouette over city skyline, hopeful, 9:16, photoreal, no text",
        f"Close-up hands typing on laptop with soft bokeh background, focused, 9:16, photoreal, no text",
        f"Sunrise over calm mountain ridge, quiet beginning of a day, 9:16, photoreal, no text",
    ]
    imgs = []
    seed_base = datetime.date.today().toordinal()
    for i, p in enumerate(img_prompts, 1):
        dest = dirs["images"] / f"{slug}_img_{i}.png"
        log.info(f"  image {i}: {p[:50]}...")
        pollinations_image(p, dest, width=1080, height=1920, seed=seed_base + i)
        imgs.append(dest)

    # 4. Ken Burns clips
    clips = []
    for i, img in enumerate(imgs, 1):
        clip = dirs["output"] / f"_kb_{slug}_{i}.mp4"
        ken_burns_clip(img, clip, seconds=12, portrait=True)
        clips.append(clip)
        log.info(f"  clip {i}/{len(imgs)} {clip.stat().st_size/1024:.0f}KB")

    # 5. concat + audio
    out = dirs["output"] / f"{slug}.mp4"
    log.info(f"  render → {out.name}")
    concat_clips_with_audio(clips, audio, out)
    log.info(f"  size: {out.stat().st_size/1024/1024:.2f} MB")

    # 자막은 description 에 dual-text 로 포함 (SRT burn-in 은 trade-off 커서 생략)
    title = f"{q['en'][:80]} | {q['author']} #Shorts"
    description = (
        f"{q['en']}\n— {q['author']}\n\n"
        f"한국어: {q['ko']}\n— {q['author']}\n\n"
        "Daily mindset reset. One quote, one minute, one habit.\n\n"
        "#Shorts #Mindset #Habits #SelfImprovement #Wealth #DailyHabits "
        "#Motivation #JamesClear #Naval\n\n"
        "DISCLAIMER: Educational content only. Not financial, legal, medical, or "
        "tax advice. Your results will vary."
    )
    ok, resp = upload_to_channel(out, CHANNEL_KEY, title, description, dry_run=dry_run)
    log.info(f"  upload ok={ok} ({resp[:140]})")
    log.info(f"=== Wealth Blueprint done ===")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="콘텐츠만 생성, 업로드 X")
    args = ap.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
