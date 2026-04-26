# -*- coding: utf-8 -*-
"""
Pinterest 종 핀 자동 생성 (1200x1800, 2:3)

- 같은 상품에 톤만 다른 핀 3개 (a/b/c 변형)
- 상단 30% 헤드라인 (톤별 카피 다르게)
- 중앙 50% 핵심 시각 (큰 숫자)
- 하단 20% CTA (Gumroad URL)

출력: prompts/pinterest/{slug}_a.png, _b.png, _c.png
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "pinterest"
OUT.mkdir(exist_ok=True)

PIN_W, PIN_H = 1200, 1800

FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"

GUMROAD_BASE = "kunstudio.gumroad.com"

# 카테고리 (regenerate_thumbnails.py 와 동일 정의)
CATEGORIES = [
    ("sns",         "SNS 콘텐츠",     "SNS CONTENT",     100, "sns"),
    ("youtube",     "유튜브",         "YOUTUBE",         100, "sns"),
    ("business",    "비즈니스",       "BUSINESS",        100, "business"),
    ("data",        "데이터 분석",    "DATA ANALYSIS",   100, "business"),
    ("design",      "디자인",         "DESIGN",          100, "creative"),
    ("copywriting", "카피라이팅",     "COPYWRITING",     100, "creative"),
    ("blog",        "블로그",         "BLOG WRITING",    100, "writing"),
    ("language",    "외국어",         "LANGUAGES",       100, "writing"),
    ("email",       "이메일",         "EMAIL",           100, "productivity"),
    ("allinone",    "올인원 9팩",     "ALL-IN-ONE",      900, "productivity"),
]

PALETTES = {
    "sns":          {"bg": (10, 10, 10),     "accent": (255, 214, 10),  "text": (255, 255, 255), "sub": (255, 214, 10)},
    "business":     {"bg": (30, 58, 95),     "accent": (201, 169, 97),  "text": (255, 255, 255), "sub": (201, 169, 97)},
    "creative":     {"bg": (109, 40, 217),   "accent": (236, 72, 153),  "text": (255, 255, 255), "sub": (255, 230, 245)},
    "writing":      {"bg": (6, 167, 125),    "accent": (255, 255, 255), "text": (255, 255, 255), "sub": (200, 240, 220)},
    "productivity": {"bg": (29, 78, 216),    "accent": (255, 214, 10),  "text": (255, 255, 255), "sub": (255, 214, 10)},
}

# 변형 톤 (a/b/c) — 같은 카테고리에 카피만 다르게
# 토큰: {kr} = 카테고리 한글, {n} = 갯수
TONES = {
    "a": {  # benefit-focused
        "label": "BENEFIT",
        "headline": "{kr}",
        "headline2": "5분만에 끝낸다",
        "cta": "지금 받기 →",
    },
    "b": {  # curiosity / question
        "label": "CURIOSITY",
        "headline": "다들 {kr}을",
        "headline2": "AI에 맡기는 이유",
        "cta": "프롬프트 보러가기 →",
    },
    "c": {  # urgency / number
        "label": "VALUE",
        "headline": "{kr} 프롬프트",
        "headline2": "{n}개 평생 소장",
        "cta": "할인가로 받기 →",
    },
}


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD, size=size)


def draw_centered(draw, text, f, fill, cx, cy):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2 - bbox[0], cy - th // 2 - bbox[1]), text, font=f, fill=fill)


def draw_text_left(draw, text, f, fill, x, y):
    bbox = draw.textbbox((0, 0), text, font=f)
    draw.text((x - bbox[0], y - bbox[1]), text, font=f, fill=fill)


def make_pin(slug, name_kr, name_en, count, palette_key, variant: str) -> Image.Image:
    palette = PALETTES[palette_key]
    tone = TONES[variant]

    img = Image.new("RGB", (PIN_W, PIN_H), palette["bg"])
    draw = ImageDraw.Draw(img)

    # 상단 30% (0 ~ 540): 헤드라인
    # 톤 라벨 (작게, accent)
    f_label = font(36)
    draw_centered(draw, f"{tone['label']} · {name_en}", f_label, palette["sub"], PIN_W // 2, 110)

    # 헤드라인 2줄 (각 줄을 가로 88% 안에 들어가도록 자동 축소)
    h1 = tone["headline"].format(kr=name_kr, n=count)
    h2 = tone["headline2"].format(kr=name_kr, n=count)
    target_hw = int(PIN_W * 0.88)

    def fit_font(text, start=96, floor=48):
        size = start
        while size > floor:
            f = font(size)
            bbox = draw.textbbox((0, 0), text, font=f)
            if (bbox[2] - bbox[0]) <= target_hw:
                return f
            size -= 4
        return font(floor)

    f_h1 = fit_font(h1)
    f_h2 = fit_font(h2)
    draw_centered(draw, h1, f_h1, palette["text"], PIN_W // 2, 260)
    draw_centered(draw, h2, f_h2, palette["accent"], PIN_W // 2, 380)

    # 중앙 50% (540 ~ 1440): 큰 숫자 (가로 80% 안에 들어가도록 자동 축소)
    num_str = str(count)
    target_w = int(PIN_W * 0.78)
    f_num_size = 720 if len(num_str) <= 3 else 560
    while f_num_size > 200:
        f_num = font(f_num_size)
        bbox = draw.textbbox((0, 0), num_str, font=f_num)
        if (bbox[2] - bbox[0]) <= target_w:
            break
        f_num_size -= 20
    draw_centered(draw, num_str, f_num, palette["accent"], PIN_W // 2, 990)

    # 숫자 아래 라벨
    f_sub = font(60)
    label = "PROMPTS" if slug != "allinone" else "PROMPTS PACK"
    draw_centered(draw, label, f_sub, palette["text"], PIN_W // 2, 1370)

    # 하단 20% (1440 ~ 1800): CTA
    # 디바이더
    draw.line([(120, 1500), (PIN_W - 120, 1500)], fill=palette["sub"], width=4)

    f_cta = font(72)
    draw_centered(draw, tone["cta"], f_cta, palette["accent"], PIN_W // 2, 1600)

    f_url = font(40)
    url = f"{GUMROAD_BASE}/l/{slug}"
    draw_centered(draw, url, f_url, palette["text"], PIN_W // 2, 1720)

    return img


def main():
    total = 0
    for cat in CATEGORIES:
        slug = cat[0]
        for v in ("a", "b", "c"):
            img = make_pin(*cat, variant=v)
            out = OUT / f"{slug}_{v}.png"
            img.save(out, "PNG", optimize=True)
            total += 1
    print(f"[done] {total} Pinterest pins generated in {OUT}")


if __name__ == "__main__":
    main()
