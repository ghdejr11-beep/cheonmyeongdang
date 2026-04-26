# -*- coding: utf-8 -*-
"""
B2B 한국어 프롬프트팩 3종 — 썸네일(1280x720) + Pinterest 핀 3종(1200x1800) 일괄 생성

- clinic-marketing-pack (병원 마케팅)
- tax-advisor-pack (세무 답변)
- legal-firstconsult-pack (법률 1차상담)

각 팩별 출력:
- {pack}/thumbnail.png  (1280x720, 숫자 임팩트형)
- {pack}/pinterest_pins/{slug}_a.png   (Benefit 톤)
- {pack}/pinterest_pins/{slug}_b.png   (Curiosity 톤)
- {pack}/pinterest_pins/{slug}_c.png   (Value 톤)
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent

# 1280x720 썸네일
TH_W, TH_H = 1280, 720
# 1200x1800 핀
PIN_W, PIN_H = 1200, 1800

FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"
FONT_NOTO = "C:/Windows/Fonts/NotoSansKR-VF.ttf"


# 카테고리 정의 (slug, 폴더명, 한글 카테고리, 영문, 갯수, palette key)
PACKS = [
    ("clinic",  "clinic-marketing-pack",   "병원 마케팅",   "CLINIC MARKETING",  100, "clinic"),
    ("tax",     "tax-advisor-pack",        "세무 답변",     "TAX ADVISOR",       100, "tax"),
    ("legal",   "legal-firstconsult-pack", "법률 1차상담",  "LEGAL CONSULT",     100, "legal"),
]

# 팔레트 (의료=청록 / 세무=네이비골드 / 법률=다크블루)
PALETTES = {
    "clinic": {"bg": (16, 78, 110),    "accent": (89, 217, 196), "text": (255, 255, 255), "sub": (220, 245, 240)},
    "tax":    {"bg": (24, 40, 72),     "accent": (218, 178, 102),"text": (255, 255, 255), "sub": (244, 228, 196)},
    "legal":  {"bg": (15, 23, 42),     "accent": (203, 161, 53), "text": (255, 255, 255), "sub": (220, 220, 230)},
}

# Pinterest 톤
TONES = {
    "a": {"label": "BENEFIT",   "h1": "{kr} 자동화", "h2": "30분 만에 끝낸다",     "cta": "지금 받기 →"},
    "b": {"label": "CURIOSITY", "h1": "{kr} 카톡",   "h2": "원장님이 직접 안 쓰는 이유","cta": "프롬프트 보러가기 →"},
    "c": {"label": "VALUE",     "h1": "{kr}",       "h2": "{n}개 평생 소장",       "cta": "할인가로 받기 →"},
}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size=size)
    except OSError:
        return ImageFont.truetype(FONT_NOTO, size=size)


def draw_centered(draw, text, f, fill, cx, cy):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2 - bbox[0], cy - th // 2 - bbox[1]), text, font=f, fill=fill)


def draw_text_left(draw, text, f, fill, x, y):
    bbox = draw.textbbox((0, 0), text, font=f)
    draw.text((x - bbox[0], y - bbox[1]), text, font=f, fill=fill)


def draw_text_right(draw, text, f, fill, x_right, y):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text((x_right - tw - bbox[0], y - bbox[1]), text, font=f, fill=fill)


# ───────────────────────────── THUMBNAIL ─────────────────────────────

def make_thumbnail(slug, name_kr, name_en, count, palette):
    img = Image.new("RGB", (TH_W, TH_H), palette["bg"])
    draw = ImageDraw.Draw(img)

    # 좌측 강조 바
    draw.rectangle([(60, 80), (74, TH_H - 80)], fill=palette["accent"])

    # 상단 좌측: 한글 카테고리
    f_top_kr = font(FONT_BOLD, 44)
    draw_text_left(draw, name_kr, f_top_kr, palette["sub"], 110, 90)

    # 상단 우측: 영문
    f_top_en = font(FONT_BOLD, 30)
    draw_text_right(draw, name_en, f_top_en, palette["accent"], TH_W - 60, 100)

    # B2B 라벨 (작은 강조 박스)
    f_b2b = font(FONT_BOLD, 24)
    bbox = draw.textbbox((0, 0), "B2B 한국어", font=f_b2b)
    bw, bh = bbox[2] - bbox[0] + 32, bbox[3] - bbox[1] + 16
    draw.rectangle([(110, 160), (110 + bw, 160 + bh)], fill=palette["accent"])
    draw_text_left(draw, "B2B 한국어", f_b2b, palette["bg"], 126, 168)

    # 중앙: 큰 숫자
    num_str = str(count)
    num_size = 460 if len(num_str) <= 3 else 380
    f_num = font(FONT_BOLD, num_size)
    draw_centered(draw, num_str, f_num, palette["accent"], TH_W // 2, TH_H // 2 + 30)

    # 하단: PROMPTS 라벨
    f_label = font(FONT_BOLD, 56)
    draw_centered(draw, "PROMPTS", f_label, palette["sub"], TH_W // 2, TH_H - 90)

    # 하단 좌측 브랜드
    f_brand = font(FONT_BOLD, 24)
    draw_text_left(draw, "kunstudio.co", f_brand, palette["sub"], 110, TH_H - 50)

    # 하단 우측 #slug
    draw_text_right(draw, f"#{slug}", f_brand, palette["sub"], TH_W - 60, TH_H - 50)

    return img


# ───────────────────────────── PINTEREST PIN ─────────────────────────

def make_pin(slug, name_kr, name_en, count, palette, tone_key):
    tone = TONES[tone_key]
    img = Image.new("RGB", (PIN_W, PIN_H), palette["bg"])
    draw = ImageDraw.Draw(img)

    # 상단 30% — 헤드라인
    # 라벨 박스
    f_label = font(FONT_BOLD, 38)
    label_text = tone["label"]
    bbox = draw.textbbox((0, 0), label_text, font=f_label)
    bw, bh = bbox[2] - bbox[0] + 40, bbox[3] - bbox[1] + 20
    draw.rectangle([(80, 100), (80 + bw, 100 + bh)], fill=palette["accent"])
    draw_text_left(draw, label_text, f_label, palette["bg"], 100, 110)

    # 헤드라인 1
    h1 = tone["h1"].format(kr=name_kr, n=count)
    f_h1 = font(FONT_BOLD, 100)
    draw_text_left(draw, h1, f_h1, palette["text"], 80, 230)

    # 헤드라인 2
    h2 = tone["h2"].format(kr=name_kr, n=count)
    f_h2 = font(FONT_BOLD, 80)
    draw_text_left(draw, h2, f_h2, palette["accent"], 80, 360)

    # 중앙 50% — 큰 숫자
    f_num = font(FONT_BOLD, 600)
    draw_centered(draw, str(count), f_num, palette["accent"], PIN_W // 2, PIN_H // 2 + 80)

    # PROMPTS 라벨
    f_pr = font(FONT_BOLD, 80)
    draw_centered(draw, "PROMPTS", f_pr, palette["text"], PIN_W // 2, PIN_H // 2 + 380)

    # 하단 20% — CTA
    cta = tone["cta"]
    f_cta = font(FONT_BOLD, 56)
    cta_y = PIN_H - 220
    bbox = draw.textbbox((0, 0), cta, font=f_cta)
    cw, ch = bbox[2] - bbox[0] + 80, bbox[3] - bbox[1] + 40
    cx = (PIN_W - cw) // 2
    draw.rectangle([(cx, cta_y), (cx + cw, cta_y + ch)], fill=palette["accent"])
    draw_centered(draw, cta, f_cta, palette["bg"], PIN_W // 2, cta_y + ch // 2)

    # 브랜드
    f_brand = font(FONT_BOLD, 36)
    draw_centered(draw, "kunstudio.gumroad.com", f_brand, palette["sub"], PIN_W // 2, PIN_H - 80)

    return img


# ───────────────────────────── MAIN ─────────────────────────

def verify(path: Path, expected_size):
    with Image.open(path) as im:
        if im.mode != "RGB":
            return False, f"mode={im.mode}"
        if im.size != expected_size:
            return False, f"size={im.size}"
        return True, f"OK {im.size}"


def main():
    total_files = 0
    for slug, folder, name_kr, name_en, count, pkey in PACKS:
        pack_dir = ROOT / folder
        pin_dir = pack_dir / "pinterest_pins"
        pin_dir.mkdir(parents=True, exist_ok=True)
        palette = PALETTES[pkey]

        # 썸네일
        th = make_thumbnail(slug, name_kr, name_en, count, palette)
        th_path = pack_dir / "thumbnail.png"
        th.save(th_path, "PNG", optimize=True)
        ok, msg = verify(th_path, (TH_W, TH_H))
        print(f"[thumbnail] {th_path.name}: {msg}")
        total_files += 1

        # Pinterest 핀 3종
        for tone_key in ("a", "b", "c"):
            pin = make_pin(slug, name_kr, name_en, count, palette, tone_key)
            pin_path = pin_dir / f"{slug}_{tone_key}.png"
            pin.save(pin_path, "PNG", optimize=True)
            ok, msg = verify(pin_path, (PIN_W, PIN_H))
            print(f"  [pin {tone_key}] {pin_path.name}: {msg}")
            total_files += 1

    print(f"\n[done] {total_files} files generated across {len(PACKS)} packs")


if __name__ == "__main__":
    main()
