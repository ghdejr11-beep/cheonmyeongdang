#!/usr/bin/env python3
"""
4채널 YouTube 배너(2048x1152) + 프로필(800x800) 자동 생성.
Pollinations Flux 무료 API 사용 — API 키 불요.

출력 경로:
  D:\\documents\\쿤스튜디오\\yt_branding\\<channel>\\banner.jpg
  D:\\documents\\쿤스튜디오\\yt_branding\\<channel>\\profile.jpg
"""
import os
import urllib.parse
import urllib.request
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(r"D:\documents\쿤스튜디오\yt_branding")
OUT.mkdir(parents=True, exist_ok=True)

CHANNELS = {
    "healing_sleep_realm": {
        "title": "Healing Sleep Realm",
        "banner_prompt": (
            "cinematic dreamy night sky, crescent moon over misty mountains, "
            "soft purple and deep blue gradients, floating stars and nebula, "
            "tranquil lake reflection, ambient glow, minimalist logo space in center, "
            "sleep and meditation aesthetic, ultra wide banner composition, 4k, serene, calming"
        ),
        "profile_prompt": (
            "minimalist crescent moon and single star on deep purple gradient background, "
            "soft glow, centered circular composition, sleep meditation icon, "
            "clean modern, spiritual aesthetic, no text"
        ),
    },
    "whisper_atlas": {
        "title": "Whisper Atlas",
        "banner_prompt": (
            "aurora borealis over frozen misty landscape, old vintage world map overlay, "
            "soft teal and pink gradients, whispering sound waves visualization, "
            "ultra wide cinematic banner, ASMR aesthetic, ethereal, mysterious, 4k"
        ),
        "profile_prompt": (
            "minimalist sound wave shaped like globe, soft teal and pink gradient, "
            "centered circular composition, ASMR icon, clean modern, no text"
        ),
    },
    "wealth_blueprint": {
        "title": "Wealth Blueprint",
        "banner_prompt": (
            "architectural blueprint style with gold stacks, upward arrow chart, "
            "navy blue and gold color scheme, wealth growth concept, "
            "ultra wide banner, professional financial aesthetic, "
            "clean minimal lines, premium look, 4k"
        ),
        "profile_prompt": (
            "minimalist gold coin stack with upward arrow on navy blue background, "
            "centered circular composition, finance icon, clean professional, no text"
        ),
    },
    "inner_archetypes": {
        "title": "Inner Archetypes",
        "banner_prompt": (
            "jungian shadow self concept, split face half light half dark, "
            "ancient mandala and tree of life symbols, deep black with gold accents, "
            "mythological archetypes, ultra wide cinematic banner, "
            "psychological depth aesthetic, spiritual mystical, 4k"
        ),
        "profile_prompt": (
            "minimalist mandala merged with tree silhouette, "
            "gold on deep black background, centered circular composition, "
            "jungian archetype icon, clean mystical, no text"
        ),
    },
}


def gen(prompt, width, height, out_path):
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width={width}&height={height}&nologo=true&model=flux&enhance=true&seed=42"
    req = urllib.request.Request(url, headers={"User-Agent": "KunStudio-YtBranding/1.0"})
    print(f"  -> {out_path.name} ({width}x{height})")
    with urllib.request.urlopen(req, timeout=120) as r:
        out_path.write_bytes(r.read())
    print(f"     saved {out_path.stat().st_size // 1024}KB")


def main():
    for slug, cfg in CHANNELS.items():
        print(f"\n=== {cfg['title']} ===")
        cdir = OUT / slug
        cdir.mkdir(parents=True, exist_ok=True)
        gen(cfg["banner_prompt"], 2048, 1152, cdir / "banner.jpg")
        gen(cfg["profile_prompt"], 800, 800, cdir / "profile.jpg")
    print(f"\n완료. 출력: {OUT}")


if __name__ == "__main__":
    main()
