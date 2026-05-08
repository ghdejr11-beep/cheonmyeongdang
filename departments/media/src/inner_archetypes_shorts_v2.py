#!/usr/bin/env python3
"""
Inner Archetypes — YouTube Shorts 자동 생성 v2 (매일 6편 강화).

= 기존 inner_archetypes_pipeline.py (long-form 5~7분, 화/금) 보완 =

흐름 (요약):
  1. mbti_content_pool.json 로드 → 오늘 6편 prompt 결정 (날짜+슬롯 결정적)
  2. 슬롯별로:
     a. 스크립트 30~50초 (Claude → fallback)
     b. edge-tts 음성 (en-US-AndrewNeural / -5%)
     c. Pollinations Flux 1080x1920 이미지 1장
     d. ffmpeg ken_burns 9:16 + drawtext 타이틀 오버레이
     e. Upload-Post → @innerarchetypes-y4y (categoryId 27 Education,
        containsSyntheticMedia=true, #Shorts)
  3. 처리 기록 D:\\scripts\\inner_archetypes_shorts_done.json

매일 6편 = 16 MBTI × 30일 = 480 unique slot
오전 3편 (08:30) + 오후 3편 (14:30) ← schtask 2개로 분리

매출 직결:
  - description 자동: 천명당 사주 cross-sell + Saju Diary Gumroad 어필
  - end card 멘션: "내 MBTI 알아보기 → 천명당 무료 사주"
  - Sori Atlas BGM 채널 cross-promo

법적 안전:
  - "이 성격은 우울증" 같은 진단 표현 X (DISCLAIMER 자동 삽입)
  - synthetic media 라벨 ON (categoryId 27, containsSyntheticMedia=true)
  - 인용 시 framework 출처 자동 표기

사용:
    python inner_archetypes_shorts_v2.py --slot morning  # 오전 3편 (slot 0,1,2)
    python inner_archetypes_shorts_v2.py --slot evening  # 오후 3편 (slot 3,4,5)
    python inner_archetypes_shorts_v2.py --slot all      # 6편
    python inner_archetypes_shorts_v2.py --dry-run       # 업로드 X
    python inner_archetypes_shorts_v2.py --slot 0        # 특정 슬롯 1개만
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

from yt_channel_common import (  # type: ignore
    get_logger, load_secrets, channel_dirs,
    pollinations_image, FFMPEG, upload_to_channel,
)

CHANNEL_KEY = "inner_archetypes"
POOL_PATH = Path(r"D:\scripts\mbti_content_pool.json")
RECORD_PATH = Path(r"D:\scripts\inner_archetypes_shorts_done.json")
KFONT = "C\\:/Windows/Fonts/malgun.ttf"

# 매출 직결 — 천명당 + Saju Diary cross-sell
CROSS_SELL_FOOTER = (
    "\n\n📥 한국식 사주로 내 MBTI 더 깊이 알기:\n"
    "천명당 — 무료 사주 분석 + 일운 (앱)\n"
    "→ https://cheonmyeongdang.com?utm_source=youtube&utm_campaign=inner_archetypes_shorts\n\n"
    "📔 Saju Diary — 12-month Korean self-knowledge workbook\n"
    "→ https://ghdejr.gumroad.com/l/qcjtu?utm_source=youtube&utm_campaign=inner_archetypes_shorts\n\n"
    "🎵 Reflective BGM: Sori Atlas\n"
    "→ https://www.youtube.com/@soriatlas\n\n"
    "DISCLAIMER: Educational content based on personality frameworks. NOT a "
    "medical, psychiatric, or therapeutic diagnosis. Personality models are "
    "lenses for self-reflection, not absolute truths."
)

DEFAULT_TAGS = [
    "MBTI", "Personality", "PersonalityTest", "Psychology",
    "Shorts", "MBTITypes", "16Personalities", "MBTIShorts",
    "SelfDiscovery", "InnerArchetypes",
]

# ──────────────────────── pool loader ────────────────────────

def load_pool() -> dict:
    if not POOL_PATH.exists():
        raise FileNotFoundError(f"content pool missing: {POOL_PATH}")
    return json.loads(POOL_PATH.read_text(encoding="utf-8"))


def load_record() -> dict:
    if RECORD_PATH.exists():
        try:
            return json.loads(RECORD_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_record(rec: dict):
    RECORD_PATH.write_text(
        json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ──────────────────────── slot 결정 ────────────────────────

def pick_slot_jobs(slot_indices: list[int]) -> list[dict]:
    """오늘 날짜·슬롯 인덱스 기반 결정적 6편 선택.

    Returns: [{slot, type_key, type_meta, theme_key, theme_tpl,
               rival_key (옵션), rival_meta, dim (옵션), is_comparison}]
    """
    pool = load_pool()
    types: dict = pool["types"]
    type_keys = list(types.keys())  # 16
    daily_themes: dict = pool["daily_themes"]
    theme_templates: dict = pool["theme_templates"]
    dims = pool["comparison_dimensions"]

    today = datetime.date.today()
    day_of_month = today.day  # 1~31
    day_in_cycle = ((day_of_month - 1) % 30) + 1  # 1~30
    cycle_seed = (today.year * 10000 + today.month * 100 + day_in_cycle)

    base_theme_key = daily_themes[str(day_in_cycle)]

    # 슬롯별 테마 다양화: day theme가 base, slot 인덱스로 다른 테마 6개 회전
    # (기존: 6슬롯 모두 단일 테마 → 매출 다양성/시청자 흥미 떨어짐)
    theme_rotation = [
        "core_motivation", "shadow_warning", "money_pattern",
        "career_fit", "love_compatibility", "growth_practice",
    ]

    # 결정적 셔플 — 중복 없이 슬롯별 type 선택.
    # day별 시드로 16 type을 셔플한 뒤, slot 인덱스로 슬라이스.
    # day가 다르면 셔플 순서가 달라 30일 사이클 동안 모든 type이 골고루 등장.
    rng_seed = cycle_seed
    shuffled_keys = list(type_keys)
    for i in range(len(shuffled_keys) - 1, 0, -1):
        rng_seed = (rng_seed * 1103515245 + 12345) & 0x7FFFFFFF
        j = rng_seed % (i + 1)
        shuffled_keys[i], shuffled_keys[j] = shuffled_keys[j], shuffled_keys[i]

    jobs: list[dict] = []
    for slot in slot_indices:
        type_key = shuffled_keys[slot % len(shuffled_keys)]
        type_meta = types[type_key]

        # 슬롯별 테마: day별로 시작점을 회전시켜 같은 슬롯이 매일 다른 테마
        theme_offset = (cycle_seed + slot) % len(theme_rotation)
        slot_theme_key = theme_rotation[theme_offset]
        # day가 comparison_vs인 날은 일부 슬롯에 비교 강제 (기존 호환)
        if base_theme_key == "comparison_vs" and slot % 2 == 0:
            slot_theme_key = "comparison_vs"
        theme_tpl = theme_templates[slot_theme_key]

        # 비교 모드용 보조 해시 (같은 type이라도 rival/dim 다르게)
        h = int(
            hashlib.sha1(f"{cycle_seed}_{slot}".encode()).hexdigest(), 16
        )

        is_comparison = slot_theme_key == "comparison_vs"
        rival_key = None
        rival_meta = None
        dim_obj = None
        if is_comparison:
            rival_idx = (h >> 8) % len(type_meta["rivals"])
            rival_key = type_meta["rivals"][rival_idx]
            rival_meta = types.get(rival_key) or {"label": rival_key, "ko": rival_key}
            dim_obj = dims[(h >> 16) % len(dims)]

        jobs.append({
            "slot": slot,
            "day_in_cycle": day_in_cycle,
            "type_key": type_key,
            "type_meta": type_meta,
            "theme_key": slot_theme_key,
            "theme_tpl": theme_tpl,
            "rival_key": rival_key,
            "rival_meta": rival_meta,
            "dim": dim_obj,
            "is_comparison": is_comparison,
        })
    return jobs


# ──────────────────────── 스크립트 빌더 ────────────────────────

def build_title(job: dict) -> str:
    tpl = job["theme_tpl"]
    type_meta = job["type_meta"]
    title = tpl["title_en"]
    repl = {
        "{LABEL}": type_meta["label"],
        "{TYPE}": job["type_key"],
        "{CORE}": type_meta["core"],
        "{SHADOW}": type_meta["shadow"],
        "{GROWTH}": type_meta["growth"],
    }
    if job["is_comparison"] and job["rival_meta"] and job["dim"]:
        repl["{RIVAL_LABEL}"] = job["rival_meta"]["label"]
        repl["{RIVAL}"] = job["rival_key"]
        repl["{DIM}"] = job["dim"]["dim"]
        repl["{DIM_KO}"] = job["dim"]["ko"]
    for k, v in repl.items():
        title = title.replace(k, v)
    return title[:90]


def build_script(job: dict, env: dict, log) -> str:
    """Claude (Haiku) 스크립트 — 30~50초 분량 (~80~120 단어).

    실패 시 theme_tpl의 hook+body 템플릿으로 fallback.
    """
    type_meta = job["type_meta"]
    type_key = job["type_key"]
    tpl = job["theme_tpl"]
    theme_key = job["theme_key"]

    # Fallback (템플릿 기반)
    fallback = tpl["hook"] + " " + tpl["body"]
    repl = {
        "{LABEL}": type_meta["label"],
        "{TYPE}": type_key,
        "{CORE}": type_meta["core"],
        "{SHADOW}": type_meta["shadow"],
        "{GROWTH}": type_meta["growth"],
        "{STRENGTH}": type_meta["core"],
    }
    if job["is_comparison"] and job["rival_meta"] and job["dim"]:
        repl["{RIVAL_LABEL}"] = job["rival_meta"]["label"]
        repl["{RIVAL}"] = job["rival_key"]
        repl["{DIM}"] = job["dim"]["dim"]
        repl["{DIM_KO}"] = job["dim"]["ko"]
    for k, v in repl.items():
        fallback = fallback.replace(k, v)

    key = env.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        log.info("  no ANTHROPIC_API_KEY → fallback")
        return fallback

    extra_ctx = ""
    if job["is_comparison"] and job["rival_meta"] and job["dim"]:
        extra_ctx = (
            f"\nCOMPARISON: {type_key} vs {job['rival_key']} on dimension '{job['dim']['dim']}'.\n"
            f"  - {type_key} brings: {type_meta['core']}\n"
            f"  - {job['rival_key']} brings: {job['rival_meta'].get('core', 'opposite traits')}\n"
        )

    prompt = (
        f"Write a YouTube SHORT script of ABOUT 90 to 110 words "
        f"(spoken in 35 to 50 seconds).\n\n"
        f"FRAMEWORK: MBTI 16 Personalities\n"
        f"TYPE: {type_meta['label']} ({type_key})\n"
        f"THEME: {theme_key}\n"
        f"CORE motivation: {type_meta['core']}\n"
        f"SHADOW: {type_meta['shadow']}\n"
        f"GROWTH: {type_meta['growth']}\n"
        f"{extra_ctx}\n"
        "Structure:\n"
        "  - Sentence 1 (HOOK, 7 sec): a specific, contrarian opening that "
        "stops the scroll. NO 'Hey guys' or generic intros.\n"
        "  - Body (25 to 35 sec): 2 to 3 punchy lines that deliver real insight.\n"
        "  - CTA (5 sec): 'Comment your type' or 'Tag a friend who is X'.\n\n"
        "Hard rules:\n"
        "  - Educational framing only. NO medical or psychiatric language.\n"
        "  - Never claim 100% accuracy. Personality is a 'lens', not 'truth'.\n"
        "  - Plain spoken English, no markdown, no emojis.\n"
        "  - Do NOT include stage directions or speaker labels.\n"
        "  - Do NOT exceed 110 words."
    )
    import urllib.request
    for model in ("claude-haiku-4-5", "claude-sonnet-4-6"):
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps({
                    "model": model,
                    "max_tokens": 350,
                    "system": "You are a sharp narrator for a viral MBTI YouTube Shorts channel. Frank but not mean.",
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
            text = data["content"][0]["text"].strip()
            if 200 < len(text) < 1500:
                return text
        except Exception as e:
            log.info(f"  Claude {model} failed: {e}")
    log.info("  → fallback template script")
    return fallback


# ──────────────────────── 음성 ────────────────────────

def synth_voice(text: str, out_mp3: Path, env: dict, log) -> Path:
    try:
        sys.path.insert(0, str(Path(
            r"D:\cheonmyeongdang\departments\media\youtube\shared"
        )))
        from tts import synthesize  # type: ignore
        synthesize(text, out_mp3, voice="en-US-AndrewNeural", rate="-5%")
        log.info(f"  voice: edge-tts → {out_mp3.name}")
        return out_mp3
    except Exception as e:
        log.info(f"  edge-tts failed: {e} → ElevenLabs fallback")
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


# ──────────────────────── 이미지 ────────────────────────

def build_image_prompt(job: dict) -> str:
    type_meta = job["type_meta"]
    base_style = (
        "ethereal symbolic illustration, dreamlike pastel watercolor, "
        "abstract symbolic figure silhouette, jungian symbolism, "
        "vertical 9:16 cinematic, no text, no faces clearly visible"
    )
    if job["is_comparison"] and job["rival_meta"]:
        return (
            f"split composition contrasting {type_meta['label']} and "
            f"{job['rival_meta']['label']} archetypes, two opposing "
            f"symbolic figures meeting in the middle, {base_style}"
        )
    return (
        f"{type_meta['label']} archetype mood, abstract symbolic figure, "
        f"essence of {type_meta['core']}, {base_style}"
    )


# ──────────────────────── 영상 ────────────────────────

def _ffmpeg_safe_text(s: str) -> str:
    """drawtext 안전 escape."""
    s = s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "")
    s = re.sub(r"[\"\[\]]", "", s)
    return s


def render_short(
    img: Path, audio: Path, title_overlay: str, type_key: str,
    out_mp4: Path, log,
) -> Path:
    """1080x1920 ken_burns + 타이틀 + #Shorts 안전 길이."""
    safe_title = _ffmpeg_safe_text(title_overlay[:60])
    safe_type = _ffmpeg_safe_text(type_key)
    # 60초 안전 (Shorts 최대 60초)
    seconds = 58
    fps = 30
    d_frames = seconds * fps
    scale = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    vf = (
        f"{scale},zoompan=z='min(zoom+0.0008,1.18)':d={d_frames}:s=1080x1920:fps={fps},"
        f"drawtext=fontfile='{KFONT}':text='{safe_type}':"
        f"fontcolor=white:fontsize=180:x=(w-text_w)/2:y=120:"
        f"box=1:boxcolor=0x000000@0.55:boxborderw=24,"
        f"drawtext=fontfile='{KFONT}':text='{safe_title}':"
        f"fontcolor=white:fontsize=58:x=(w-text_w)/2:y=h-360:"
        f"box=1:boxcolor=0x000000@0.65:boxborderw=22"
    )
    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", str(img),
        "-i", str(audio),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(out_mp4),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"ffmpeg render_short failed (rc={res.returncode}):\n"
            f"  stderr: {res.stderr[-1500:]}"
        )
    return out_mp4


# ──────────────────────── description ────────────────────────

def build_description(job: dict, script: str) -> str:
    type_meta = job["type_meta"]
    title = build_title(job)
    if job["is_comparison"] and job["rival_meta"] and job["dim"]:
        head = (
            f"{job['type_key']} vs {job['rival_key']} — who wins at "
            f"{job['dim']['dim']}?\n\n"
        )
    else:
        head = f"{type_meta['label']} — {job['theme_key'].replace('_', ' ')}\n\n"
    body = head + script.strip() + "\n\n"
    tag_line = "#" + " #".join(DEFAULT_TAGS[:8]) + " #" + job["type_key"]
    return (body + tag_line + CROSS_SELL_FOOTER)[:4900]


# ──────────────────────── 메인 슬롯 처리 ────────────────────────

def process_slot(job: dict, env: dict, log, dirs: dict, dry_run: bool) -> dict:
    type_key = job["type_key"]
    slot = job["slot"]
    today = datetime.date.today().isoformat()
    slug_parts = [today, f"slot{slot}", type_key.lower(), job["theme_key"]]
    if job["is_comparison"]:
        slug_parts.append(f"vs_{(job['rival_key'] or '').lower()}")
    slug = "_".join(slug_parts)
    log.info(f"=== [SHORT slot {slot}] {type_key} · {job['theme_key']}"
             f"{' vs ' + (job['rival_key'] or '') if job['is_comparison'] else ''} ===")

    # 1. 스크립트
    script = build_script(job, env, log)
    (dirs["output"] / f"{slug}.txt").write_text(script, encoding="utf-8")
    log.info(f"  script: {len(script)} chars (~{len(script.split())} words)")

    # 2. 음성
    audio = dirs["audio"] / f"{slug}.mp3"
    synth_voice(script, audio, env, log)

    # 3. 이미지
    img = dirs["images"] / f"{slug}.png"
    seed = (datetime.date.today().toordinal() * 100) + slot
    pollinations_image(build_image_prompt(job), img, width=1080, height=1920, seed=seed)
    log.info(f"  image: {img.name}")

    # 4. 렌더
    title = build_title(job)
    out_mp4 = dirs["output"] / f"{slug}.mp4"
    render_short(img, audio, title, type_key, out_mp4, log)
    size_mb = out_mp4.stat().st_size / 1024 / 1024
    log.info(f"  render: {out_mp4.name} ({size_mb:.2f} MB)")

    # 5. 업로드
    description = build_description(job, script)
    full_title = (title + " #Shorts")[:100]
    if dry_run:
        log.info(f"  [DRY-RUN] would upload: {full_title!r}")
        return {"slot": slot, "ok": True, "dry_run": True, "mp4": str(out_mp4)}

    ok, resp = upload_to_channel(out_mp4, CHANNEL_KEY, full_title, description, dry_run=False)
    log.info(f"  upload ok={ok} resp={str(resp)[:200]}")

    video_id = None
    if ok and isinstance(resp, str):
        m = re.search(r"['\"](?:post_id|videoId)['\"]:\s*['\"]([\w\-]{11})['\"]", resp)
        if m:
            video_id = m.group(1)

    return {
        "slot": slot, "ok": ok, "dry_run": False, "mp4": str(out_mp4),
        "video_id": video_id, "title": full_title, "type": type_key,
        "theme": job["theme_key"],
    }


def run(slot_indices: list[int], dry_run: bool = False) -> list[dict]:
    log = get_logger("inner_archetypes_shorts_v2")
    env = load_secrets()
    dirs = channel_dirs(CHANNEL_KEY)
    jobs = pick_slot_jobs(slot_indices)
    rec = load_record()
    today = datetime.date.today().isoformat()
    rec.setdefault(today, [])

    results = []
    for job in jobs:
        # 이미 처리한 슬롯은 skip (재실행 안전)
        already = any(r.get("slot") == job["slot"] and r.get("ok") for r in rec[today])
        if already and not dry_run:
            log.info(f"  [SKIP] slot {job['slot']} already done today")
            continue
        try:
            r = process_slot(job, env, log, dirs, dry_run=dry_run)
            results.append(r)
            if not dry_run:
                rec[today].append(r)
                save_record(rec)
        except Exception as e:
            log.info(f"  [ERR] slot {job['slot']}: {e}")
            results.append({"slot": job["slot"], "ok": False, "error": str(e)})

    log.info(f"=== SHORTS v2 done: {sum(1 for r in results if r.get('ok'))}/{len(results)} ===")
    return results


def parse_slots(arg: str) -> list[int]:
    if arg == "morning":
        return [0, 1, 2]
    if arg == "evening":
        return [3, 4, 5]
    if arg == "all":
        return [0, 1, 2, 3, 4, 5]
    if arg.isdigit():
        return [int(arg)]
    raise ValueError(f"invalid --slot: {arg}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", default="all",
                    help="morning(0-2) | evening(3-5) | all | <int>")
    ap.add_argument("--dry-run", action="store_true",
                    help="콘텐츠만 생성, 업로드 X")
    args = ap.parse_args()
    slots = parse_slots(args.slot)
    run(slots, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
