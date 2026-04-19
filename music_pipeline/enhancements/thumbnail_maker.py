"""썸네일 자동 생성기.

YouTube 썸네일은 CTR 의 70% 를 결정한다. 현재 auto_watcher.py /
lyrics_watcher.py 는 썸네일을 지정하지 않아 YouTube 가 자동 프레임
스냅샷을 쓰는데, 이는 Ken Burns 중간 프레임이라 구도가 엉망이다.

이 모듈은 스타일별 프리셋으로 1280x720 썸네일을 합성한다:
  - 배경: 기존 영상용 bg 이미지 (있으면) 또는 그라데이션 자동 생성
  - 장르 라벨 (큰 영문)
  - 후킹 카피 (한글 1줄)
  - 시즌·시간 태그

업로드 후 `thumbnails.set()` API 로 첨부.

사용:
    from music_pipeline.enhancements.thumbnail_maker import make_thumbnail

    thumb_path = make_thumbnail(
        out_path="thumb.png",
        style_name="lofi",
        hook_kr="공부할 때 듣는 로파이",
        duration_label="8 HOURS",
        bg_image_path="bg.png",  # 선택
    )
    # youtube_service.thumbnails().set(videoId=..., media_body=thumb_path).execute()
"""

from __future__ import annotations

import os
import random
from pathlib import Path


try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: F401
except ImportError:
    Image = None  # type: ignore

W, H = 1280, 720

# 장르별 컬러 프리셋 (youtube_uploader.STYLE_KEYWORDS 와 싱크)
THUMBNAIL_PRESETS = {
    "lofi": {
        "bg_gradient": [(25, 20, 40), (55, 35, 75)],
        "accent": (200, 160, 255),
        "label_en": "LO-FI",
        "label_color": (220, 190, 255),
        "hook_color": (240, 240, 250),
    },
    "sleep": {
        "bg_gradient": [(5, 5, 25), (15, 20, 50)],
        "accent": (100, 140, 220),
        "label_en": "SLEEP",
        "label_color": (150, 180, 240),
        "hook_color": (220, 230, 245),
    },
    "rain": {
        "bg_gradient": [(15, 20, 25), (30, 45, 55)],
        "accent": (120, 170, 190),
        "label_en": "RAIN",
        "label_color": (170, 200, 220),
        "hook_color": (230, 240, 245),
    },
    "meditation": {
        "bg_gradient": [(10, 20, 15), (25, 50, 40)],
        "accent": (100, 190, 140),
        "label_en": "MEDITATION",
        "label_color": (150, 210, 175),
        "hook_color": (235, 245, 240),
    },
    "jazz": {
        "bg_gradient": [(30, 18, 10), (65, 40, 20)],
        "accent": (210, 170, 100),
        "label_en": "JAZZ",
        "label_color": (230, 195, 140),
        "hook_color": (245, 230, 210),
    },
    "study": {
        "bg_gradient": [(15, 15, 30), (35, 35, 65)],
        "accent": (150, 180, 255),
        "label_en": "STUDY",
        "label_color": (180, 200, 255),
        "hook_color": (230, 235, 250),
    },
    "classical": {
        "bg_gradient": [(10, 10, 15), (30, 25, 40)],
        "accent": (220, 200, 160),
        "label_en": "CLASSICAL",
        "label_color": (230, 215, 180),
        "hook_color": (245, 240, 225),
    },
    "electronic": {
        "bg_gradient": [(10, 5, 20), (50, 15, 80)],
        "accent": (255, 50, 200),
        "label_en": "SYNTHWAVE",
        "label_color": (255, 120, 220),
        "hook_color": (250, 235, 250),
    },
    "pop": {
        "bg_gradient": [(20, 10, 25), (55, 20, 60)],
        "accent": (255, 120, 180),
        "label_en": "K-POP BALLAD",
        "label_color": (255, 160, 200),
        "hook_color": (250, 235, 245),
    },
    "general": {
        "bg_gradient": [(13, 13, 13), (35, 35, 45)],
        "accent": (200, 200, 200),
        "label_en": "PLAYLIST",
        "label_color": (220, 220, 220),
        "hook_color": (240, 240, 240),
    },
}


def _find_font(candidates: list[str], size: int):
    """여러 경로 중 존재하는 폰트 로드."""
    if Image is None or ImageFont is None:
        return None
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def _get_bold_korean_font(size: int):
    return _find_font(
        [
            r"C:\Windows\Fonts\malgunbd.ttf",
            r"C:\Windows\Fonts\malgun.ttf",
            "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        ],
        size,
    )


def _get_bold_english_font(size: int):
    return _find_font(
        [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\Montserrat-Bold.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
        ],
        size,
    )


def _draw_gradient_bg(draw, gradient: list[tuple[int, int, int]]):
    c1, c2 = gradient
    for y in range(H):
        r_ = y / H
        r = int(c1[0] + (c2[0] - c1[0]) * r_)
        g = int(c1[1] + (c2[1] - c1[1]) * r_)
        b = int(c1[2] + (c2[2] - c1[2]) * r_)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def _draw_vignette(img):
    """가장자리 어둡게 (중앙 집중).
    라디얼 마스크 생성 후 어두운 레이어를 합성.
    """
    # 라디얼 알파 마스크
    mask = Image.new("L", (W, H), 0)
    mdraw = ImageDraw.Draw(mask)
    cx, cy = W // 2, H // 2
    max_r = int(((W / 2) ** 2 + (H / 2) ** 2) ** 0.5)
    for r in range(max_r, 0, -8):
        ratio = r / max_r
        alpha = int(170 * (ratio ** 2))
        mdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(dark, img, mask)


def make_thumbnail(
    out_path: str,
    style_name: str = "general",
    hook_kr: str = "",
    duration_label: str = "",
    bg_image_path: str | None = None,
) -> str | None:
    """썸네일 합성해서 저장. 성공 시 경로 반환, 실패 시 None."""
    if Image is None:
        print("[thumbnail_maker] Pillow 미설치 — 설치: pip install Pillow")
        return None

    preset = THUMBNAIL_PRESETS.get(style_name) or THUMBNAIL_PRESETS["general"]

    # 배경
    if bg_image_path and os.path.exists(bg_image_path):
        try:
            bg = Image.open(bg_image_path).convert("RGB")
            # 1280x720 으로 커버 크롭
            iw, ih = bg.size
            if iw / ih > W / H:
                new_h, new_w = H, int(H * iw / ih)
            else:
                new_w, new_h = W, int(W * ih / iw)
            bg = bg.resize((new_w, new_h), Image.LANCZOS)
            left, top = (new_w - W) // 2, (new_h - H) // 2
            bg = bg.crop((left, top, left + W, top + H))
            # 어둡게
            overlay = Image.new("RGB", (W, H), (0, 0, 0))
            bg = Image.blend(bg, overlay, alpha=0.45)
        except Exception:
            bg = Image.new("RGB", (W, H), preset["bg_gradient"][0])
            _draw_gradient_bg(ImageDraw.Draw(bg), preset["bg_gradient"])
    else:
        bg = Image.new("RGB", (W, H), preset["bg_gradient"][0])
        _draw_gradient_bg(ImageDraw.Draw(bg), preset["bg_gradient"])

    # 장식 점/액센트
    draw = ImageDraw.Draw(bg)
    random.seed(hash(style_name) % 10000)
    accent = preset["accent"]
    for _ in range(60):
        x = random.randint(0, W)
        y = random.randint(0, H)
        sz = random.uniform(0.5, 2.5)
        bright = random.uniform(0.2, 0.6)
        cr = int(accent[0] * bright)
        cg = int(accent[1] * bright)
        cb = int(accent[2] * bright)
        draw.ellipse([x - sz, y - sz, x + sz, y + sz], fill=(cr, cg, cb))

    bg = _draw_vignette(bg)
    draw = ImageDraw.Draw(bg)

    # 1. 장르 라벨 (상단 왼쪽 작게) — 2026 카페뮤직BGM 공식
    label_font = _get_bold_english_font(42)
    if label_font:
        label = preset["label_en"]
        draw.text((60, 50), label, font=label_font, fill=preset["label_color"])
        # 라벨 언더라인
        label_bbox = draw.textbbox((60, 50), label, font=label_font)
        draw.rectangle(
            [60, label_bbox[3] + 6, label_bbox[2], label_bbox[3] + 12],
            fill=preset["accent"],
        )

    # 2. 시간 라벨 (상단 오른쪽)
    if duration_label:
        dur_font = _get_bold_english_font(56)
        if dur_font:
            dbbox = draw.textbbox((0, 0), duration_label, font=dur_font)
            dw = dbbox[2] - dbbox[0]
            dx = W - dw - 60
            dy = 50
            # 배경 박스
            pad = 16
            draw.rectangle(
                [dx - pad, dy - pad, dx + dw + pad, dy + (dbbox[3] - dbbox[1]) + pad],
                fill=(0, 0, 0, 180),
            )
            draw.text((dx, dy), duration_label, font=dur_font, fill=(255, 255, 255))

    # 3. 메인 후킹 카피 (한글 중앙 하단) — CTR 의 핵심
    if hook_kr:
        # 길이에 따라 크기 자동 조정
        target_w = W - 120
        size = 92
        hook_font = _get_bold_korean_font(size)
        while hook_font and size > 40:
            bbox = draw.textbbox((0, 0), hook_kr, font=hook_font)
            tw = bbox[2] - bbox[0]
            if tw <= target_w:
                break
            size -= 6
            hook_font = _get_bold_korean_font(size)

        if hook_font:
            bbox = draw.textbbox((0, 0), hook_kr, font=hook_font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = (W - tw) // 2
            ty = H - th - 120
            # 그림자
            for off in [(5, 5), (3, 3)]:
                draw.text(
                    (tx + off[0], ty + off[1]), hook_kr, font=hook_font,
                    fill=(0, 0, 0),
                )
            # 외곽선
            for dx in (-2, -1, 0, 1, 2):
                for dy in (-2, -1, 0, 1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    draw.text(
                        (tx + dx, ty + dy), hook_kr, font=hook_font,
                        fill=(0, 0, 0),
                    )
            # 메인
            draw.text((tx, ty), hook_kr, font=hook_font, fill=preset["hook_color"])

    # 채널 워터마크 (하단 오른쪽 작게)
    wm_font = _get_bold_english_font(24)
    if wm_font:
        draw.text((W - 200, H - 50), "@덕구네 · 2026", font=wm_font, fill=(180, 180, 180))

    try:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        bg.save(out_path, "PNG", optimize=True)
        return out_path
    except Exception as e:
        print(f"[thumbnail_maker] 저장 실패: {e}")
        return None


# ============================================================
# 제목/후킹 자동 생성
# ============================================================
HOOK_TEMPLATES = {
    "lofi": [
        "공부할 때 듣는 로파이",
        "집중 2배 되는 비트",
        "새벽에 듣는 차분한 음악",
        "잠 안 올 때 이 플레이리스트",
    ],
    "sleep": [
        "5분 안에 잠드는 수면 음악",
        "꿀잠 자는 법",
        "불면증에 듣는 음악",
        "뇌가 쉬는 소리",
    ],
    "rain": [
        "비 오는 밤 힐링",
        "빗소리로 잠들기",
        "카페에서 듣는 빗소리",
        "스트레스 녹이는 빗소리",
    ],
    "jazz": [
        "카페에서 일할 때",
        "주말 아침 재즈",
        "한적한 카페 분위기",
        "작업할 때 재즈",
    ],
    "study": [
        "집중력 올리는 음악",
        "시험 공부 BGM",
        "4시간 집중 세션",
        "과제할 때 듣는 음악",
    ],
    "pop": [
        "이별 후 듣는 발라드",
        "눈물이 멈추지 않는 노래",
        "감성 충만 K-발라드",
        "AI가 만든 이별 노래",
    ],
    "meditation": [
        "마음 가라앉히는 명상",
        "불안할 때 듣는 음악",
        "하루 10분 명상",
        "생각 많을 때",
    ],
    "classical": [
        "공부할 때 클래식",
        "집중되는 피아노",
        "아침에 듣는 클래식",
        "편안한 피아노 음악",
    ],
    "electronic": [
        "밤에 듣는 신스웨이브",
        "운전할 때 드라이빙 뮤직",
        "90s 레트로 감성",
        "깊은 밤 일렉트로닉",
    ],
    "general": [
        "이 플레이리스트면 충분",
        "한 번 들으면 빠져요",
        "잔잔한 하루 BGM",
    ],
}


def pick_hook_kr(style_name: str, seed: int | None = None) -> str:
    """스타일에 맞는 한글 후킹 카피 하나 선택."""
    hooks = HOOK_TEMPLATES.get(style_name) or HOOK_TEMPLATES["general"]
    if seed is not None:
        random.seed(seed)
    return random.choice(hooks)


if __name__ == "__main__":
    if Image is None:
        print("⚠️  Pillow 미설치라 self-test 스킵")
    else:
        out = make_thumbnail(
            out_path="/tmp/thumb_lofi_test.png",
            style_name="lofi",
            hook_kr="공부할 때 듣는 로파이",
            duration_label="8 HOURS",
        )
        assert out and os.path.exists(out)
        size = os.path.getsize(out)
        print(f"✓ thumbnail_maker.py 자체 테스트 통과")
        print(f"샘플 썸네일: {out} ({size/1024:.1f} KB)")

        # 후킹 카피
        hook = pick_hook_kr("jazz", seed=1)
        assert hook in HOOK_TEMPLATES["jazz"]
        print(f"샘플 후킹 (jazz): {hook}")
