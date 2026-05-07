# -*- coding: utf-8 -*-
"""
TOP 3 large card PNG (1920x1080) for monitor side display.
Output: docs/top3_actions_2026_05_07.png
"""
import os
import io
from PIL import Image, ImageDraw, ImageFont
import qrcode

ROOT = r"C:\Users\hdh02\Desktop\cheonmyeongdang"
OUT = os.path.join(ROOT, "docs", "top3_actions_2026_05_07.png")

FONT_REG = r"C:\Windows\Fonts\malgun.ttf"
FONT_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"

W, H = 1920, 1080
BG = (15, 23, 42)        # slate-900
BG_CARD = (30, 41, 59)   # slate-800
TEXT_LIGHT = (241, 245, 249)
TEXT_MUTED = (148, 163, 184)
ACCENT_GREEN = (34, 197, 94)
ACCENT_GOLD = (251, 191, 36)

TOP3 = [
    {
        "rank": 1, "color": (220, 38, 38),  # red-600
        "title": "K-Startup AI리그 신청",
        "subtitle": "PMS 가입 + 신청서 제출",
        "time": "60분",
        "revenue": "₩5천만 ~ 5억",
        "deadline": "5/20 마감 (D-13)",
        "url": "https://pms.k-startup.go.kr",
        "guide": "docs/grant_application_oneliners.md",
    },
    {
        "rank": 2, "color": (234, 88, 12),  # orange-600
        "title": "Play Console v1.3.1 배포",
        "subtitle": "AAB 20% rollout",
        "time": "5분",
        "revenue": "₩14,500 / 월 정기결제",
        "deadline": "ASAP (검토 1~2일)",
        "url": "https://play.google.com/console",
        "guide": "docs/play_console_oneliners.md",
    },
    {
        "rank": 3, "color": (250, 204, 21),  # yellow-400
        "title": "AppSumo Lifetime Deal 제출",
        "subtitle": "Submit Your Tool 폼",
        "time": "20분",
        "revenue": "$5K ~ $15K (첫 30일)",
        "deadline": "ASAP (검토 5~14일)",
        "url": "https://appsumo.com/partners/list-your-product/",
        "guide": "docs/appsumo_submit_oneliners.md",
    },
]


def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def make_qr_pil(url, box_size=8):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ===== Header =====
    draw.rectangle([0, 0, W, 110], fill=(2, 6, 23))
    draw.text((60, 25), "TOP 3 ACTIONS — 2026.05.07", font=font(48), fill=TEXT_LIGHT)
    draw.text((60, 80), "오늘 90분 투자 → 90일 기댓값 ₩6,000만 ~ 7천만 unlock", font=font(20, bold=False), fill=ACCENT_GOLD)
    draw.text((W - 60, 50), "천명당 · 쿤스튜디오", font=font(22), fill=TEXT_MUTED, anchor="rm")

    # ===== 3 cards stacked =====
    card_top = 140
    card_h = 290
    card_gap = 15
    card_x = 40
    card_w = W - 80

    for i, item in enumerate(TOP3):
        y = card_top + i * (card_h + card_gap)

        # card bg
        draw.rounded_rectangle([card_x, y, card_x + card_w, y + card_h], radius=18, fill=BG_CARD)

        # left color band
        draw.rounded_rectangle([card_x, y, card_x + 14, y + card_h], radius=18, fill=item["color"])
        draw.rectangle([card_x + 8, y, card_x + 14, y + card_h], fill=item["color"])

        # rank big number
        draw.text((card_x + 50, y + 30), str(item["rank"]), font=font(180), fill=item["color"])

        # title
        title_x = card_x + 230
        draw.text((title_x, y + 35), item["title"], font=font(48), fill=TEXT_LIGHT)
        draw.text((title_x, y + 100), item["subtitle"], font=font(24, bold=False), fill=TEXT_MUTED)

        # metrics row
        metric_y = y + 160
        # time
        draw.text((title_x, metric_y), "소요시간", font=font(16, bold=False), fill=TEXT_MUTED)
        draw.text((title_x, metric_y + 22), item["time"], font=font(34), fill=TEXT_LIGHT)
        # revenue
        rev_x = title_x + 220
        draw.text((rev_x, metric_y), "매출 잠재", font=font(16, bold=False), fill=TEXT_MUTED)
        draw.text((rev_x, metric_y + 22), item["revenue"], font=font(34), fill=ACCENT_GREEN)
        # deadline
        dl_x = title_x + 620
        draw.text((dl_x, metric_y), "마감", font=font(16, bold=False), fill=TEXT_MUTED)
        draw.text((dl_x, metric_y + 22), item["deadline"], font=font(34), fill=item["color"])

        # bottom line - URL + guide
        draw.text((title_x, y + 240), item["url"], font=font(18, bold=False), fill=(125, 211, 252))
        draw.text((title_x, y + 263), "Guide: " + item["guide"], font=font(14, bold=False), fill=TEXT_MUTED)

        # QR code on right
        qr_pil = make_qr_pil(item["url"], box_size=8)
        # resize QR
        qr_size = 230
        qr_resized = qr_pil.resize((qr_size, qr_size), Image.NEAREST)
        # white frame
        frame = 12
        draw.rounded_rectangle(
            [card_x + card_w - qr_size - frame * 2 - 30, y + 30,
             card_x + card_w - 30, y + 30 + qr_size + frame * 2],
            radius=8, fill=(255, 255, 255)
        )
        img.paste(qr_resized, (card_x + card_w - qr_size - frame - 30, y + 30 + frame))
        # QR caption
        qr_caption_x = card_x + card_w - qr_size // 2 - frame - 30
        draw.text((qr_caption_x, y + 30 + qr_size + frame * 2 + 5), "스캔 → 즉시 이동", font=font(14), fill=TEXT_MUTED, anchor="mt")

    # ===== Footer =====
    footer_y = H - 50
    draw.text((60, footer_y), "완료 후: 클로드에게 \"#1 완료\" / \"#2 완료\" / \"#3 완료\" → 후속 자동화 가동",
              font=font(18), fill=TEXT_LIGHT)
    draw.text((W - 60, footer_y), "전체 13건: docs/USER_ACTIONS_2026_05_07.md",
              font=font(16, bold=False), fill=TEXT_MUTED, anchor="rm")

    img.save(OUT, "PNG", optimize=True)
    print(f"PNG saved: {OUT}")
    print(f"Size: {os.path.getsize(OUT)} bytes ({W}x{H})")


if __name__ == "__main__":
    main()
