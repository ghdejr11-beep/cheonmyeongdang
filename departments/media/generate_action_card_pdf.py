# -*- coding: utf-8 -*-
"""
A4 1-page printable action card PDF.
Source: docs/USER_ACTIONS_2026_05_07.md (TOP 13 actions)
Output: docs/user_actions_2026_05_07_print.pdf
"""
import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode

ROOT = r"C:\Users\hdh02\Desktop\cheonmyeongdang"
OUT = os.path.join(ROOT, "docs", "user_actions_2026_05_07_print.pdf")

# Korean font
FONT_PATH = r"C:\Windows\Fonts\malgun.ttf"
FONT_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"
pdfmetrics.registerFont(TTFont("Malgun", FONT_PATH))
pdfmetrics.registerFont(TTFont("MalgunBd", FONT_BOLD))

# 13 actions
ACTIONS = [
    # (rank, priority_color, title, time, revenue, deadline, url)
    (1, "CRIT", "K-Startup AI리그 PMS 신청서 제출", "60분", "₩5천만~5억", "5/20", "https://pms.k-startup.go.kr"),
    (2, "CRIT", "Play Console v1.3.1 AAB 배포 (20%)", "5분", "₩14,500/월", "ASAP", "https://play.google.com/console"),
    (3, "HIGH", "AppSumo Lifetime Deal 제출", "20분", "$5K~15K (30일)", "ASAP", "https://appsumo.com/partners/list-your-product/"),
    (4, "HIGH", "Etsy + Vela 40 listings push", "25분", "$150~450 (30일)", "ASAP", "https://www.etsy.com/sell"),
    (5, "HIGH", "영문 인플루언서 5명 발송", "30분", "$2.2K~8K LTV", "ASAP", "https://www.instagram.com/elementsastro/"),
    (6, "MED",  "RapidAPI Provider listing", "5분", "$50~500/월", "ASAP", "https://rapidapi.com/auth/sign-up?referral=/provider"),
    (7, "MED",  "Beehiiv 가입 + Issue #1 schedule", "5분", "$500~2K/월 (180일)", "ASAP", "https://beehiiv.com"),
    (8, "MED",  "AdMob OAuth 셋업 (매출 추적)", "5분", "(수동 30분/주 절감)", "ASAP", "https://console.cloud.google.com"),
    (9, "MED",  "관광AI(KORLENS) 신청 (KoDATA 회신후)", "30분", "₩1,100만", "5/20", "https://touraz.kr"),
    (10, "LOW", "PayPal Client Secret rotate (보안)", "5분", "(보안 강화)", "ASAP", "https://developer.paypal.com/dashboard/applications/live"),
    (11, "LOW", "Antler Seoul Cohort 8 pitch", "15분", "$100K~500K 시드", "ASAP", "https://antler.co/apply"),
    (12, "LOW", "Kakao Ventures cold email", "10분", "$200K~1M 시드", "ASAP", "https://kakao.vc"),
    (13, "LOW", "Naver D2SF 신청서 제출", "20분", "$200K~500K 시드", "ASAP", "https://d2startup.com"),
]

PRIORITY_COLORS = {
    "CRIT": colors.HexColor("#dc2626"),  # red
    "HIGH": colors.HexColor("#ea580c"),  # orange
    "MED":  colors.HexColor("#ca8a04"),  # yellow/gold
    "LOW":  colors.HexColor("#16a34a"),  # green
}


def make_qr_image(url, size_px=140):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio


def main():
    c = canvas.Canvas(OUT, pagesize=A4)
    W, H = A4  # 595 x 842 pt

    margin_x = 12 * mm
    y = H - 12 * mm

    # ===== Header =====
    c.setFillColor(colors.HexColor("#0f172a"))
    c.rect(0, H - 22 * mm, W, 22 * mm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("MalgunBd", 18)
    c.drawString(margin_x, H - 11 * mm, "천명당 액션 카드 — 2026.05.07")
    c.setFont("Malgun", 10)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawString(margin_x, H - 17 * mm, "오늘 ~3.5h 투자 → 90일 누적 ₩7,000만~₩2.4억 매출 잠재 unlock")
    # Top 3 highlight
    c.setFont("MalgunBd", 9)
    c.setFillColor(colors.HexColor("#fbbf24"))
    top3_text = "TOP 3 (90분): K-Startup AI리그 + Play Console + AppSumo = ₩6,000만~7천만 기댓값"
    c.drawRightString(W - margin_x, H - 17 * mm, top3_text)

    y = H - 30 * mm

    # ===== Table header =====
    col_x = {
        "check": margin_x,
        "rank": margin_x + 8 * mm,
        "pri": margin_x + 18 * mm,
        "title": margin_x + 32 * mm,
        "time": margin_x + 108 * mm,
        "rev": margin_x + 122 * mm,
        "due": margin_x + 158 * mm,
        "qr": margin_x + 168 * mm,
    }

    c.setFillColor(colors.HexColor("#1e293b"))
    c.rect(margin_x - 2, y - 2, W - 2 * margin_x + 4, 7 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("MalgunBd", 8.5)
    c.drawString(col_x["check"], y + 1.5 * mm, "✓")
    c.drawString(col_x["rank"], y + 1.5 * mm, "#")
    c.drawString(col_x["pri"], y + 1.5 * mm, "우선")
    c.drawString(col_x["title"], y + 1.5 * mm, "액션")
    c.drawString(col_x["time"], y + 1.5 * mm, "시간")
    c.drawString(col_x["rev"], y + 1.5 * mm, "매출 잠재")
    c.drawString(col_x["due"], y + 1.5 * mm, "마감")
    c.drawString(col_x["qr"], y + 1.5 * mm, "QR")

    y -= 8 * mm

    # ===== Rows =====
    row_h = 14 * mm
    for rank, pri, title, time, rev, due, url in ACTIONS:
        # alternating background
        if rank % 2 == 0:
            c.setFillColor(colors.HexColor("#f8fafc"))
            c.rect(margin_x - 2, y - row_h + 2 * mm, W - 2 * margin_x + 4, row_h, fill=1, stroke=0)

        # priority color bar (left edge)
        pcolor = PRIORITY_COLORS[pri]
        c.setFillColor(pcolor)
        c.rect(margin_x - 2, y - row_h + 2 * mm, 2 * mm, row_h, fill=1, stroke=0)

        # checkbox
        c.setStrokeColor(colors.HexColor("#475569"))
        c.setLineWidth(0.8)
        c.rect(col_x["check"] + 1, y - 6 * mm, 4 * mm, 4 * mm, fill=0, stroke=1)

        # rank number (big)
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("MalgunBd", 14)
        c.drawString(col_x["rank"], y - 6 * mm, str(rank))

        # priority badge
        c.setFillColor(pcolor)
        c.setFont("MalgunBd", 8)
        c.drawString(col_x["pri"], y - 5 * mm, pri)

        # title
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("MalgunBd", 9.5)
        # truncate if too long
        max_title_chars = 38
        title_disp = title if len(title) <= max_title_chars else title[:max_title_chars - 1] + "…"
        c.drawString(col_x["title"], y - 5 * mm, title_disp)

        # time
        c.setFont("Malgun", 9)
        c.setFillColor(colors.HexColor("#334155"))
        c.drawString(col_x["time"], y - 5 * mm, time)

        # revenue
        c.setFont("MalgunBd", 8.5)
        c.setFillColor(colors.HexColor("#059669"))
        c.drawString(col_x["rev"], y - 5 * mm, rev)

        # deadline
        c.setFont("MalgunBd", 8.5)
        if due == "5/20":
            c.setFillColor(colors.HexColor("#dc2626"))
        else:
            c.setFillColor(colors.HexColor("#64748b"))
        c.drawString(col_x["due"], y - 5 * mm, due)

        # QR code
        qr_bio = make_qr_image(url)
        from reportlab.lib.utils import ImageReader
        qr_img = ImageReader(qr_bio)
        c.drawImage(qr_img, col_x["qr"], y - row_h + 3 * mm, width=row_h - 2 * mm, height=row_h - 2 * mm, mask='auto')

        y -= row_h

    # ===== Footer =====
    y_footer = 18 * mm
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setLineWidth(0.5)
    c.line(margin_x, y_footer + 6 * mm, W - margin_x, y_footer + 6 * mm)

    c.setFont("MalgunBd", 9)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(margin_x, y_footer + 2 * mm, "완료 후: 클로드에게 한 줄만 — \"#N 완료\" → 후속 자동화 가동")

    c.setFont("Malgun", 8)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(margin_x, y_footer - 2 * mm, "가이드 풀 텍스트: docs/USER_ACTIONS_2026_05_07.md  |  자동화 11종 24/7 가동중")
    c.drawRightString(W - margin_x, y_footer - 2 * mm, "쿤스튜디오 · 552-59-00848 · ghdejr11@gmail.com")

    c.save()
    print(f"PDF saved: {OUT}")
    print(f"Size: {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
