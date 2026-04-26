# -*- coding: utf-8 -*-
"""
digital-products 썸네일 일괄 재생성 (v2 — 숫자 임팩트형, 1280x720)

- 카테고리별 색상 통일 + 큰 숫자 + 카테고리명 + "PROMPTS" 라벨
- 기존 thumbnail_*.png 파일명 그대로 덮어쓰기
- 백업: prompts/backup_pre_v2/ 로 기존 파일 이동
"""

import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backup_pre_v2"

# 1280x720
W, H = 1280, 720

# 폰트 후보 (Windows 기본). 굵은 sans-serif → Korean 지원
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"
FONT_NOTO = "C:/Windows/Fonts/NotoSansKR-VF.ttf"

# 카테고리 정의
# (slug, 한글명, 영문명, count, palette_key)
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

# 카테고리 색상 (배경, 강조, 텍스트, 서브텍스트)
PALETTES = {
    "sns":          {"bg": (10, 10, 10),     "accent": (255, 214, 10),  "text": (255, 214, 10),  "sub": (255, 255, 255)},
    "business":     {"bg": (30, 58, 95),     "accent": (201, 169, 97),  "text": (201, 169, 97),  "sub": (245, 245, 245)},
    "creative":     {"bg": (109, 40, 217),   "accent": (236, 72, 153),  "text": (255, 255, 255), "sub": (255, 200, 230)},
    "writing":      {"bg": (6, 167, 125),    "accent": (255, 255, 255), "text": (255, 255, 255), "sub": (200, 240, 220)},
    "productivity": {"bg": (29, 78, 216),    "accent": (255, 214, 10),  "text": (255, 214, 10),  "sub": (255, 255, 255)},
}


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def draw_centered(draw: ImageDraw.ImageDraw, text: str, font, fill, cx: int, cy: int):
    """주어진 (cx, cy)에 텍스트의 중심이 오도록 그린다."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = cx - tw // 2 - bbox[0]
    y = cy - th // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)


def draw_text_left(draw, text, font, fill, x: int, y: int):
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text((x - bbox[0], y - bbox[1]), text, font=font, fill=fill)


def draw_text_right(draw, text, font, fill, x_right: int, y: int):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((x_right - tw - bbox[0], y - bbox[1]), text, font=font, fill=fill)


def make_thumbnail(slug: str, name_kr: str, name_en: str, count: int, palette: dict) -> Image.Image:
    img = Image.new("RGB", (W, H), palette["bg"])
    draw = ImageDraw.Draw(img)

    # 좌측 강조 바 (카테고리별 accent)
    bar_w = 14
    draw.rectangle([(60, 80), (60 + bar_w, H - 80)], fill=palette["accent"])

    # 상단: 카테고리 한글명 (작게)
    try:
        f_top_kr = load_font(FONT_BOLD, 44)
    except OSError:
        f_top_kr = load_font(FONT_NOTO, 44)
    draw_text_left(draw, name_kr, f_top_kr, palette["sub"], 110, 90)

    # 상단 우측: 영문명 (작게)
    f_top_en = load_font(FONT_BOLD, 30)
    draw_text_right(draw, name_en, f_top_en, palette["accent"], W - 60, 100)

    # 중앙: 거대한 숫자 (50% 차지)
    num_str = str(count)
    # 숫자 폰트는 가능한 가장 큼. 캔버스 높이의 약 65%
    num_size = 460 if len(num_str) <= 3 else 380
    f_num = load_font(FONT_BOLD, num_size)
    draw_centered(draw, num_str, f_num, palette["accent"], W // 2, H // 2 + 10)

    # 숫자 배경에 살짝 그림자/테두리 효과를 위해 외곽선 두 번 (과도한 효과는 생략)

    # 하단: "PROMPTS" 라벨
    f_label = load_font(FONT_BOLD, 56)
    label = "PROMPTS" if slug != "allinone" else "PROMPTS PACK"
    draw_centered(draw, label, f_label, palette["sub"], W // 2, H - 80)

    # 하단 좌측: 브랜드
    f_brand = load_font(FONT_BOLD, 24)
    draw_text_left(draw, "kunstudio.co", f_brand, palette["sub"], 110, H - 50)

    # 하단 우측: 슬러그 (작게)
    draw_text_right(draw, f"#{slug}", f_brand, palette["sub"], W - 60, H - 50)

    return img


def verify_image(path: Path) -> tuple[bool, str]:
    try:
        with Image.open(path) as im:
            if im.mode != "RGB":
                return False, f"mode={im.mode} (expected RGB)"
            if im.size != (W, H):
                return False, f"size={im.size} (expected {W}x{H})"
            return True, f"OK mode={im.mode} size={im.size}"
    except Exception as e:
        return False, f"open fail: {e}"


def backup_existing():
    BACKUP.mkdir(exist_ok=True)
    moved = 0
    for slug, *_ in CATEGORIES:
        src = ROOT / f"thumbnail_{slug}.png"
        if src.exists():
            dst = BACKUP / src.name
            if dst.exists():
                dst.unlink()
            shutil.move(str(src), str(dst))
            moved += 1
    return moved


def generate_one(idx: int, total: int, slug, name_kr, name_en, count, palette_key):
    palette = PALETTES[palette_key]
    img = make_thumbnail(slug, name_kr, name_en, count, palette)
    out = ROOT / f"thumbnail_{slug}.png"
    img.save(out, "PNG", optimize=True)
    return out


def main():
    print(f"[i] backup → {BACKUP}")
    moved = backup_existing()
    print(f"[i] moved {moved} existing thumbnails to backup")

    # 1) 첫 번째 생성 후 검증
    first = CATEGORIES[0]
    out = generate_one(1, len(CATEGORIES), *first)
    ok, msg = verify_image(out)
    print(f"[verify] {out.name}: {msg}")
    if not ok:
        raise SystemExit(f"[!] verification failed for {out}: {msg}")

    # 2) 나머지 일괄 생성
    for i, cat in enumerate(CATEGORIES[1:], start=2):
        out = generate_one(i, len(CATEGORIES), *cat)
        print(f"  [{i:02d}/{len(CATEGORIES):02d}] {out.name}")

    # 최종 카운트
    files = sorted(ROOT.glob("thumbnail_*.png"))
    print(f"[done] {len(files)} thumbnails generated in {ROOT}")
    print(f"[done] backup: {BACKUP} ({moved} files)")


if __name__ == "__main__":
    main()
