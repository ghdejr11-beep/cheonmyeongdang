#!/usr/bin/env python3
"""
Whisper Atlas — 수면 ASMR / 화이트노이즈 / 자연 사운드 long-form.
(Healing Sleep Realm 보완 채널, 매일 1영상)

파이프라인:
  1. 오늘 토픽 선택 (rain / wind / forest / ocean / fireplace / brown noise 등)
  2. Pollinations Flux → 정적 풍경 이미지 1장 (1920x1080)
  3. ffmpeg lavfi anoisesrc / mix → 5분 짧은 사운드 (저작권 0%)
  4. stream_loop → 1h / 3h / 8h variants
  5. 최종 mp4 (단일 이미지 + 루프 오디오)
  6. (옵션) Upload-Post → YouTube whisper_atlas

음원 정책:
  - freesound.org CC0 다운로드 자산이 있으면 우선 사용 (assets/cc0_<topic>.mp3)
  - 없으면 ffmpeg lavfi anoisesrc (white/pink/brown) 자체 생성 → 저작권 0%
  - 메모리 규칙: 저작권 음원 절대 사용 금지

CLI:
  python whisper_atlas_pipeline.py --dry-run                # 1h 만 생성, 업로드 X
  python whisper_atlas_pipeline.py --hours 1,3              # 1h+3h, dry run 아님
  python whisper_atlas_pipeline.py --topic rain --hours 8   # 강제 토픽
"""
from __future__ import annotations
import argparse
import datetime
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

from yt_channel_common import (  # type: ignore
    get_logger, load_secrets, channel_dirs,
    pollinations_image, synth_noise, mix_two_audios,
    loop_audio_to_hours, make_static_video,
    upload_to_channel,
)

CHANNEL_KEY = "whisper_atlas"

# 7개 토픽 (요일 로테이션)
TOPICS = [
    {
        "slug": "rain_forest",
        "title_tpl": "Rain on Forest {hours} Hours · Deep Sleep · No Ads",
        "image_prompt": "Cinematic dense rainforest in heavy rain, soft mist, twilight, no people, ultrawide 16:9, calming, photorealistic, low saturation",
        "noise": ("pink", 0.55),
        "secondary": None,  # CC0 rain layer if available later
        "tags": ["sleep", "rain", "asmr", "forest", "white noise", "8 hours"],
    },
    {
        "slug": "ocean_waves",
        "title_tpl": "Gentle Ocean Waves {hours} Hours · Sleep & Relax · No Ads",
        "image_prompt": "Cinematic moonlit calm ocean shore at night, soft waves, distant horizon, no people, ultrawide 16:9, deep blue tones",
        "noise": ("brown", 0.5),
        "secondary": None,
        "tags": ["sleep", "ocean", "waves", "asmr", "white noise"],
    },
    {
        "slug": "wind_mountain",
        "title_tpl": "Soft Mountain Wind {hours} Hours · Relax · No Ads",
        "image_prompt": "Misty alpine mountain ridge at dawn, soft wind blown grass, no people, cinematic ultrawide 16:9, muted palette",
        "noise": ("white", 0.4),
        "secondary": ("pink", 0.3),
        "tags": ["sleep", "wind", "mountain", "asmr", "white noise"],
    },
    {
        "slug": "fireplace",
        "title_tpl": "Cozy Fireplace Crackle {hours} Hours · Warm Sleep · No Ads",
        "image_prompt": "Warm cozy stone fireplace with soft glowing fire, dark cabin interior, no people, cinematic 16:9, amber tones",
        "noise": ("brown", 0.55),
        "secondary": ("pink", 0.25),
        "tags": ["sleep", "fireplace", "asmr", "cozy", "winter"],
    },
    {
        "slug": "stream_creek",
        "title_tpl": "Forest Stream Sounds {hours} Hours · Sleep & Focus · No Ads",
        "image_prompt": "Gentle forest creek with mossy stones, soft sunlight through trees, no people, cinematic 16:9, photorealistic",
        "noise": ("pink", 0.5),
        "secondary": None,
        "tags": ["sleep", "stream", "water", "nature", "asmr"],
    },
    {
        "slug": "brown_noise_pure",
        "title_tpl": "Brown Noise {hours} Hours · ADHD Focus & Sleep · No Ads",
        "image_prompt": "Minimal soft gradient cosmic dust dark brown to black, abstract dreamy 16:9, no text",
        "noise": ("brown", 0.7),
        "secondary": None,
        "tags": ["brown noise", "focus", "adhd", "sleep", "study"],
    },
    {
        "slug": "night_crickets",
        "title_tpl": "Summer Night Crickets {hours} Hours · Peaceful Sleep · No Ads",
        "image_prompt": "Peaceful summer countryside at night, fireflies, soft moonlight, no people, cinematic ultrawide 16:9",
        "noise": ("pink", 0.4),
        "secondary": ("white", 0.2),
        "tags": ["sleep", "crickets", "night", "summer", "asmr"],
    },
]


def pick_topic(force_slug: str | None = None) -> dict:
    if force_slug:
        for t in TOPICS:
            if t["slug"] == force_slug or t["slug"].startswith(force_slug):
                return t
    idx = datetime.date.today().toordinal() % len(TOPICS)
    return TOPICS[idx]


def build_short_audio(topic: dict, dirs: dict, log) -> Path:
    """5분짜리 사운드 만들기 — primary noise + (optional) secondary mix."""
    audio_dir = dirs["audio"]
    primary = audio_dir / f"primary_{topic['noise'][0]}.mp3"
    log.info(f"  audio: synth {topic['noise'][0]} noise (5min, vol={topic['noise'][1]})")
    synth_noise(primary, duration_sec=300,
                color=topic["noise"][0], volume=topic["noise"][1])
    if topic.get("secondary"):
        sec_color, sec_vol = topic["secondary"]
        secondary = audio_dir / f"secondary_{sec_color}.mp3"
        synth_noise(secondary, duration_sec=300, color=sec_color, volume=sec_vol)
        mixed = audio_dir / "mixed_5min.mp3"
        log.info(f"  audio: mix primary + {sec_color}")
        mix_two_audios(primary, secondary, mixed,
                       a_vol=topic["noise"][1], b_vol=sec_vol)
        return mixed
    return primary


def run(hours_list: list[float], force_topic: str | None = None,
        dry_run: bool = False) -> list[Path]:
    log = get_logger()
    dirs = channel_dirs(CHANNEL_KEY)
    topic = pick_topic(force_topic)
    log.info(f"=== Whisper Atlas | topic={topic['slug']} | hours={hours_list} | dry_run={dry_run} ===")

    # 1. 이미지
    img_path = dirs["images"] / f"{topic['slug']}.png"
    log.info(f"  image: {topic['image_prompt'][:60]}...")
    pollinations_image(topic["image_prompt"], img_path,
                       width=1920, height=1080,
                       seed=datetime.date.today().toordinal())

    # 2. 5분 짧은 사운드
    short_audio = build_short_audio(topic, dirs, log)

    # 3. variants
    outputs = []
    for hrs in hours_list:
        looped_audio = dirs["audio"] / f"loop_{int(hrs)}h.mp3"
        if not looped_audio.exists() or looped_audio.stat().st_size < 1_000_000:
            log.info(f"  loop audio → {hrs}h")
            loop_audio_to_hours(short_audio, looped_audio, hours=hrs)
        else:
            log.info(f"  reuse {looped_audio.name}")

        out_mp4 = dirs["output"] / f"{topic['slug']}_{int(hrs)}h.mp4"
        log.info(f"  render mp4 → {out_mp4.name}")
        make_static_video(img_path, looped_audio, out_mp4, resolution="1920x1080")
        log.info(f"    size: {out_mp4.stat().st_size/1024/1024:.1f} MB")
        outputs.append(out_mp4)

        # 업로드 (dry_run 이면 skip)
        title = topic["title_tpl"].format(hours=int(hrs))
        desc = (
            f"{title}\n\n"
            "10 hours of soothing nature sounds for deep sleep, study and relaxation.\n"
            "No ads in the middle. No copyrighted music. Generated with non-copyright "
            "ambient noise sources.\n\n"
            f"Tags: {', '.join('#'+t.replace(' ','') for t in topic['tags'])}\n\n"
            "DISCLAIMER: This video is for relaxation only and is not medical advice."
        )
        ok, resp = upload_to_channel(out_mp4, CHANNEL_KEY, title, desc, dry_run=dry_run)
        log.info(f"  upload ok={ok} ({resp[:120]})")

    log.info(f"=== Whisper Atlas done · {len(outputs)} files ===")
    return outputs


def parse_hours(s: str) -> list[float]:
    return [float(x) for x in s.split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="콘텐츠만 생성, 업로드 X (1h variant only)")
    ap.add_argument("--hours", default=None,
                    help="콤마구분, 예: 1,3,8 (dry_run 시 무시 → 1h만)")
    ap.add_argument("--topic", default=None,
                    help="강제 토픽 slug (예: rain_forest)")
    args = ap.parse_args()

    if args.dry_run:
        hours = [1.0]
    elif args.hours:
        hours = parse_hours(args.hours)
    else:
        hours = [1.0, 3.0, 8.0]

    run(hours, force_topic=args.topic, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
