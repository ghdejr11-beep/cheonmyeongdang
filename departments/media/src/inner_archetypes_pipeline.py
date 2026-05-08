#!/usr/bin/env python3
"""
Inner Archetypes — MBTI / 에니어그램 / 칼 융 12원형 long-form (5~10분).
주 2회 (화/금) 발행.

파이프라인:
  1. 오늘의 archetype 선택 (12원형 12종 + MBTI 16종 + Enneagram 9종 = 37 토픽 풀)
  2. Claude (Haiku 우선) 으로 5~7분 분량 (~900-1200 단어) 스크립트 생성
  3. edge-tts (무료) 또는 ElevenLabs (Free) 음성
  4. Pollinations Flux 6~8장 (16:9, 일러스트 스타일)
  5. concat + Ken Burns + 텍스트 오버레이 없이 description 에만 챕터링
  6. (옵션) Upload-Post → YouTube inner_archetypes

법적 안전:
  - "이 성격은 우울증" 같은 의료 진단 표현 X
  - 인용 시 출처 명시 (Carl Jung / Riso-Hudson / MBTI Foundation)
  - "당신의 성격을 100% 맞췄다" 같은 단정 표현 X (educational framing)
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
    upload_to_channel,
)

CHANNEL_KEY = "inner_archetypes"

# 12원형 (Carl Jung / Carol S. Pearson)
JUNG_12 = [
    ("Innocent", "순수한 자아", "trust, optimism, simple joy"),
    ("Sage", "현자", "truth seeker, knowledge, wisdom"),
    ("Explorer", "탐험가", "freedom, authenticity, adventure"),
    ("Outlaw", "반항아", "rebellion, revolution, breaking rules"),
    ("Magician", "마법사", "transformation, vision, manifesting"),
    ("Hero", "영웅", "courage, mastery, proving worth"),
    ("Lover", "연인", "intimacy, passion, beauty"),
    ("Jester", "광대", "joy, humor, playfulness"),
    ("Everyman", "보통사람", "belonging, fairness, realism"),
    ("Caregiver", "양육자", "service, compassion, generosity"),
    ("Ruler", "지배자", "control, leadership, responsibility"),
    ("Creator", "창조자", "artistry, imagination, self-expression"),
]

# MBTI 16
MBTI_16 = [
    "INTJ Architect", "INTP Logician", "ENTJ Commander", "ENTP Debater",
    "INFJ Advocate", "INFP Mediator", "ENFJ Protagonist", "ENFP Campaigner",
    "ISTJ Logistician", "ISFJ Defender", "ESTJ Executive", "ESFJ Consul",
    "ISTP Virtuoso", "ISFP Adventurer", "ESTP Entrepreneur", "ESFP Entertainer",
]

# Enneagram 9
ENNEAGRAM_9 = [
    "Type 1 The Reformer", "Type 2 The Helper", "Type 3 The Achiever",
    "Type 4 The Individualist", "Type 5 The Investigator", "Type 6 The Loyalist",
    "Type 7 The Enthusiast", "Type 8 The Challenger", "Type 9 The Peacemaker",
]


def pick_topic() -> tuple[str, str, str]:
    """요일·주차 기반 로테이션. (kind, label, key) 반환."""
    today = datetime.date.today()
    iso_week = today.isocalendar().week
    weekday = today.weekday()  # 0=Mon

    # 화(1)/금(4) 발행 — 화: Jung 12원형, 금: MBTI/Enneagram 교대
    if weekday <= 2:  # 화요일 (또는 dry_run any day)
        idx = iso_week % len(JUNG_12)
        en, ko, traits = JUNG_12[idx]
        return ("Jung 12 Archetypes", f"The {en} ({ko})", f"jung_{en.lower()}")
    else:
        if iso_week % 2 == 0:
            idx = iso_week % len(MBTI_16)
            return ("MBTI", MBTI_16[idx], f"mbti_{MBTI_16[idx].split()[0].lower()}")
        else:
            idx = iso_week % len(ENNEAGRAM_9)
            return ("Enneagram", ENNEAGRAM_9[idx], f"enn_{idx+1}")


def claude_long_script(kind: str, label: str, env: dict, log) -> str | None:
    import urllib.request
    key = env.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return None
    prompt = (
        f"Write a YouTube long-form script (5 to 7 minutes spoken, about "
        f"900 to 1100 words) about the personality archetype below.\n\n"
        f"FRAMEWORK: {kind}\n"
        f"ARCHETYPE: {label}\n\n"
        "Structure (no markdown headings, but use natural section transitions):\n"
        "1. Hook (15 sec) — paint the inner experience of this type.\n"
        "2. Core motivation (1 min) — what drives them, deepest fear.\n"
        "3. Strengths (1.5 min) — three concrete strengths with examples.\n"
        "4. Shadow side (1.5 min) — three pitfalls and how they show up.\n"
        "5. Growth path (1.5 min) — three concrete practices.\n"
        "6. Closing (30 sec) — invite viewer to subscribe for the next archetype.\n\n"
        "Hard rules:\n"
        "- Educational framing only. NO medical or psychiatric diagnoses. "
        "  Never say 'you have a disorder' or 'this means depression'.\n"
        "- Cite the framework's lineage briefly (Carl Jung / Pearson / Riso-Hudson "
        "  / MBTI Foundation) when relevant.\n"
        "- Never claim 100% accuracy of personality models. Frame as 'lens', not 'truth'.\n"
        "- Plain spoken English, no markdown, no emojis.\n"
        "- Do NOT include stage directions."
    )
    for model in ("claude-haiku-4-5-20251001", "claude-sonnet-4-6"):
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps({
                    "model": model,
                    "max_tokens": 3500,
                    "system": "You are a thoughtful narrator for a personality-psychology YouTube channel.",
                    "messages": [{"role": "user", "content": prompt}],
                }).encode(),
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read())
            return data["content"][0]["text"].strip()
        except Exception as e:
            log.info(f"  Claude {model} failed: {e}")
    return None


def fallback_script(kind: str, label: str) -> str:
    return (
        f"Welcome back. Today we explore {label} from the {kind} framework. "
        "Personality models are lenses, not absolute truths, so listen for the parts "
        "that resonate and leave the rest. "
        "Every archetype carries a core motivation, a recurring fear, and a "
        "set of gifts that look like strengths from the outside but feel like "
        "obligations from the inside. "
        "We will walk through three strengths, three blind spots, and three "
        "specific practices that move this type toward integration. "
        "Take notes if something lands hard. "
        "If this kind of slow, honest psychological work helps you, subscribe "
        "and turn on notifications, because we publish a new archetype every "
        "Tuesday and Friday. Thank you for being here."
    )


def synth_voice(text: str, out_mp3: Path, env: dict, log) -> Path:
    try:
        sys.path.insert(0, str(Path(r"D:\cheonmyeongdang\departments\media\youtube\shared")))
        from tts import synthesize  # type: ignore
        # 명상 톤 — Andrew (낮고 차분)
        synthesize(text, out_mp3, voice="en-US-AndrewNeural", rate="-5%")
        log.info(f"  voice: edge-tts → {out_mp3.name}")
        return out_mp3
    except Exception as e:
        log.info(f"  edge-tts failed: {e}, trying ElevenLabs")
    import urllib.request
    key = env.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise RuntimeError("no ELEVENLABS_API_KEY for fallback")
    voice_id = "JBFqnCBsd6RMkjVDRZzb"
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps({
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.6, "similarity_boost": 0.7},
        }).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as r, open(out_mp3, "wb") as f:
        f.write(r.read())
    return out_mp3


def image_prompts(kind: str, label: str) -> list[str]:
    base_style = ("ethereal symbolic illustration, dreamlike soft pastel watercolor, "
                  "no text, 16:9 cinematic, jungian symbolism, no people faces clearly visible")
    return [
        f"{label} archetype mood, abstract symbolic figure silhouette, {base_style}",
        f"Inner landscape representing {label}, surreal symbolic terrain, {base_style}",
        f"Tarot-card-style emblem for {label}, mystical, {base_style}",
        f"Shadow side of {label} archetype, twilight mood, {base_style}",
        f"Light side of {label} archetype, dawn mood, {base_style}",
        f"Integration journey of {label}, bridge from shadow to light, {base_style}",
    ]


def run(dry_run: bool = False) -> Path:
    log = get_logger()
    env = load_secrets()
    dirs = channel_dirs(CHANNEL_KEY)
    kind, label, slug = pick_topic()
    log.info(f"=== Inner Archetypes | {kind} · {label} | dry_run={dry_run} ===")

    # 1. 스크립트
    script = claude_long_script(kind, label, env, log)
    if not script:
        log.info("  using fallback script")
        script = fallback_script(kind, label)
    (dirs["output"] / f"{slug}.txt").write_text(script, encoding="utf-8")
    log.info(f"  script: {len(script)} chars (~{len(script.split())} words)")

    # 2. TTS
    audio = dirs["audio"] / f"{slug}.mp3"
    synth_voice(script, audio, env, log)

    # 3. 이미지 6장
    prompts = image_prompts(kind, label)
    imgs = []
    seed_base = datetime.date.today().toordinal() * 10
    for i, p in enumerate(prompts, 1):
        dest = dirs["images"] / f"{slug}_img_{i}.png"
        log.info(f"  image {i}/{len(prompts)}: {p[:55]}...")
        pollinations_image(p, dest, width=1920, height=1080, seed=seed_base + i)
        imgs.append(dest)

    # 4. Ken Burns clips — 영상 길이 = 오디오 길이에 맞게 분배
    # ffprobe 없이도 안전하게: 6장 × 60초 = 6분 (long-form 5~7분 타깃에 맞음)
    per_clip_sec = 60
    clips = []
    for i, img in enumerate(imgs, 1):
        clip = dirs["output"] / f"_kb_{slug}_{i}.mp4"
        ken_burns_clip(img, clip, seconds=per_clip_sec, portrait=False)
        clips.append(clip)
        log.info(f"  clip {i}/{len(imgs)} ({per_clip_sec}s)")

    # 5. concat + audio (-shortest 가 오디오 길이에 맞춰 자동 컷)
    out = dirs["output"] / f"{slug}.mp4"
    log.info(f"  render → {out.name}")
    concat_clips_with_audio(clips, audio, out)
    log.info(f"  size: {out.stat().st_size/1024/1024:.2f} MB")

    title = f"{label} — Deep Dive | {kind}"
    description = (
        f"A slow, honest exploration of {label} from the {kind} framework.\n\n"
        "Chapters:\n"
        "0:00 Hook\n"
        "0:15 Core motivation\n"
        "1:15 Strengths\n"
        "2:45 Shadow side\n"
        "4:15 Growth path\n"
        "5:45 Closing\n\n"
        "#Personality #Archetypes #CarlJung #MBTI #Enneagram #Psychology #SelfDiscovery\n\n"
        "DISCLAIMER: Educational content based on personality frameworks. NOT a "
        "medical, psychiatric, or therapeutic diagnosis. Personality models are "
        "lenses for self-reflection, not absolute truths."
    )
    ok, resp = upload_to_channel(out, CHANNEL_KEY, title[:100], description, dry_run=dry_run)
    log.info(f"  upload ok={ok} ({resp[:140]})")
    log.info(f"=== Inner Archetypes done ===")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="콘텐츠만 생성, 업로드 X")
    args = ap.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
