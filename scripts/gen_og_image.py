# -*- coding: utf-8 -*-
"""Generate Open Graph (og:image) for cheonmyeongdang.vercel.app
Output: og.png (1200x630), og.jpg (compressed)
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630

# Colors
BG = (8, 10, 16)         # #080a10
BG2 = (13, 16, 32)        # #0d1020
GOLD = (201, 168, 76)     # #c9a84c
GOLD2 = (232, 201, 122)   # #e8c97a
GOLD3 = (245, 230, 176)
TEXT = (232, 224, 208)
TEXT2 = (168, 152, 128)

# Resolve font paths
def find_font(candidates):
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

# Korean serif (for 한자/한국어)
KR_SERIF = find_font([
    r"C:\Windows\Fonts\batang.ttc",
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
])
KR_SANS = find_font([
    r"C:\Windows\Fonts\NotoSansKR-VF.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\gulim.ttc",
])

print(f"KR_SERIF: {KR_SERIF}")
print(f"KR_SANS: {KR_SANS}")


def f(path, size):
    return ImageFont.truetype(path, size)


def draw_radial_bg():
    """Dark gradient + slight vignette."""
    base = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG2)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    cx, cy = W // 2, H // 2
    # Soft radial vignette via concentric ellipses
    for r in range(max(W, H), 0, -8):
        alpha = int(255 * (r / max(W, H)) * 0.55)
        md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    base = Image.composite(overlay, base, mask.filter(ImageFilter.GaussianBlur(80)))
    return base


def draw_stars(draw, n=180, seed=7):
    """Sparse star/dot pattern."""
    rng = random.Random(seed)
    for _ in range(n):
        x = rng.randint(0, W)
        y = rng.randint(0, H)
        size = rng.choice([1, 1, 1, 2, 2, 3])
        bright = rng.choice([90, 110, 140, 180, 220])
        draw.ellipse([x, y, x + size, y + size], fill=(bright, bright, bright))
    # A few golden bright dots
    rng2 = random.Random(seed + 17)
    for _ in range(18):
        x = rng2.randint(0, W)
        y = rng2.randint(0, H)
        s = rng2.choice([2, 3, 4])
        draw.ellipse([x, y, x + s, y + s], fill=GOLD2)


def draw_corner_ornament(draw):
    """Simple gold border lines + corner brackets."""
    pad = 28
    line = GOLD
    # Outer thin border
    draw.rectangle([pad, pad, W - pad, H - pad], outline=line, width=2)
    # Inner thin frame
    pad2 = pad + 10
    draw.rectangle([pad2, pad2, W - pad2, H - pad2], outline=(120, 100, 50), width=1)
    # Corner accents
    L = 32
    for (cx, cy) in [(pad, pad), (W - pad, pad), (pad, H - pad), (W - pad, H - pad)]:
        draw.line([(cx - L, cy), (cx + L, cy)], fill=GOLD2, width=3)
        draw.line([(cx, cy - L), (cx, cy + L)], fill=GOLD2, width=3)


def text_w(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def main():
    img = draw_radial_bg()
    draw = ImageDraw.Draw(img)
    draw_stars(draw)
    draw_corner_ornament(draw)

    # Top tag line
    tag_font = f(KR_SANS, 28)
    tag = "天命堂  |  CHEONMYEONGDANG"
    tw, th = text_w(draw, tag, tag_font)
    draw.text(((W - tw) / 2, 80), tag, font=tag_font, fill=GOLD2)

    # Decorative divider
    cx = W // 2
    draw.line([(cx - 110, 130), (cx + 110, 130)], fill=GOLD, width=2)
    draw.ellipse([cx - 4, 126, cx + 4, 134], fill=GOLD2)

    # Hero - hanja
    hanja_font = f(KR_SERIF, 220)
    hanja = "天命堂"
    hw, hh = text_w(draw, hanja, hanja_font)
    hx = (W - hw) / 2
    hy = 165
    # Soft glow (multiple offsets)
    for ox, oy, a in [(-3, -3, GOLD), (3, 3, (60, 50, 20)), (0, 4, (40, 32, 12))]:
        draw.text((hx + ox, hy + oy), hanja, font=hanja_font, fill=a)
    draw.text((hx, hy), hanja, font=hanja_font, fill=GOLD2)

    # Subtitle Korean
    sub_font = f(KR_SANS, 44)
    sub = "천명당"
    sw, sh = text_w(draw, sub, sub_font)
    draw.text(((W - sw) / 2, hy + hh + 18), sub, font=sub_font, fill=TEXT)

    # Service line
    svc_font = f(KR_SANS, 30)
    svc = "무료 사주  ·  관상  ·  손금  ·  타로  ·  꿈해몽  ·  운세"
    vw, vh = text_w(draw, svc, svc_font)
    draw.text(((W - vw) / 2, hy + hh + 75), svc, font=svc_font, fill=TEXT2)

    # Bottom URL
    url_font = f(KR_SANS, 24)
    url = "cheonmyeongdang.vercel.app"
    uw, uh = text_w(draw, url, url_font)
    draw.text((W - uw - 60, H - uh - 50), url, font=url_font, fill=GOLD)

    # Bottom-left badge
    badge_font = f(KR_SANS, 22)
    badge = "AI 운세 · 100% 무료"
    draw.text((60, H - 75), badge, font=badge_font, fill=TEXT2)

    # Save
    out_png = os.path.join(ROOT, "og.png")
    out_jpg = os.path.join(ROOT, "og.jpg")
    img.save(out_png, "PNG", optimize=True)
    img.convert("RGB").save(out_jpg, "JPEG", quality=85, optimize=True)
    print(f"Wrote: {out_png}  ({os.path.getsize(out_png)//1024} KB)")
    print(f"Wrote: {out_jpg}  ({os.path.getsize(out_jpg)//1024} KB)")


if __name__ == "__main__":
    main()
