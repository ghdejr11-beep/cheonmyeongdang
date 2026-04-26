"""
운세노트 (Fortune Notebook) - 표지 + 본문 PDF 생성기
- 12개월 월간 운세 트래커 + 행운 색/숫자/방향 메모
- 한국어 + 영어 듀얼 (글로벌 KDP)
- 보라(#6D28D9) + 라벤더(#C4B5FD)
"""
from __future__ import annotations
import os
import math
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE = Path(__file__).parent
PRIMARY = HexColor("#6D28D9")
SECONDARY = HexColor("#C4B5FD")
ACCENT_DARK = HexColor("#3C1A78")

W, H = 8.5 * inch, 11 * inch
W_BLEED, H_BLEED = 8.75 * inch, 11.25 * inch

KR_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\NanumGothic.ttf",
]


def register_korean_font():
    for cand in KR_FONT_CANDIDATES:
        if Path(cand).exists():
            try:
                pdfmetrics.registerFont(TTFont("KR", cand))
                bold = cand.replace(".ttf", "bd.ttf")
                if Path(bold).exists():
                    pdfmetrics.registerFont(TTFont("KR-Bold", bold))
                else:
                    pdfmetrics.registerFont(TTFont("KR-Bold", cand))
                return True
            except Exception:
                continue
    return False


HAS_KR = register_korean_font()
KR = "KR" if HAS_KR else "Helvetica"
KR_B = "KR-Bold" if HAS_KR else "Helvetica-Bold"

MONTHS_KR = ["1월", "2월", "3월", "4월", "5월", "6월",
             "7월", "8월", "9월", "10월", "11월", "12월"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]


def draw_star(c, cx, cy, r_outer, r_inner, points, color):
    c.setFillColor(color)
    p = c.beginPath()
    for i in range(points * 2):
        angle = math.pi/2 + i * math.pi / points
        r = r_outer if i % 2 == 0 else r_inner
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    p.close()
    c.drawPath(p, fill=1)


def make_cover():
    out = BASE / "cover.pdf"
    c = canvas.Canvas(str(out), pagesize=(W_BLEED, H_BLEED))
    c.setFillColor(PRIMARY)
    c.rect(0, 0, W_BLEED, H_BLEED, fill=1, stroke=0)
    # 보더
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(2)
    m = 0.5 * inch
    c.rect(m, m, W_BLEED - 2*m, H_BLEED - 2*m, fill=0)
    # 무궁화 패턴 (5장 꽃잎 - 기하학적)
    flower_color = HexColor("#FFB6E1")
    centers = [(W_BLEED*0.2, H_BLEED*0.85), (W_BLEED*0.8, H_BLEED*0.85),
               (W_BLEED*0.15, H_BLEED*0.2), (W_BLEED*0.85, H_BLEED*0.18),
               (W_BLEED*0.5, H_BLEED*0.2)]
    for cx, cy in centers:
        for k in range(5):
            ang = math.radians(k * 72 + 90)
            px = cx + 12 * math.cos(ang)
            py = cy + 12 * math.sin(ang)
            c.setFillColor(flower_color)
            c.circle(px, py, 7, fill=1, stroke=0)
        c.setFillColor(HexColor("#FFD700"))
        c.circle(cx, cy, 4, fill=1, stroke=0)
    # 별
    import random
    random.seed(7)
    c.setFillColor(SECONDARY)
    for _ in range(40):
        sx = random.uniform(m, W_BLEED - m)
        sy = random.uniform(m, H_BLEED - m)
        c.circle(sx, sy, random.uniform(0.5, 1.8), fill=1, stroke=0)
    # 큰 별 4개
    for cx, cy in [(W_BLEED*0.5, H_BLEED*0.78), (W_BLEED*0.3, H_BLEED*0.65),
                    (W_BLEED*0.7, H_BLEED*0.65)]:
        draw_star(c, cx, cy, 8, 3.5, 5, HexColor("#FFD700"))
    # 타이틀
    c.setFillColor(white)
    c.setFont(KR_B, 70)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.55, "운세노트")
    c.setFont(KR_B, 28)
    c.setFillColor(SECONDARY)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.49, "FORTUNE NOTEBOOK")
    # 부제
    c.setFont(KR, 16)
    c.setFillColor(white)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.42, "12개월 행운 트래커")
    c.setFont(KR, 13)
    c.setFillColor(SECONDARY)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.39, "Lucky Color  |  Number  |  Direction")
    # 데코 라인
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(2)
    c.line(W_BLEED*0.3, H_BLEED*0.36, W_BLEED*0.7, H_BLEED*0.36)
    # 2026
    c.setFillColor(white)
    c.setFont(KR_B, 22)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.32, "2026  -  병오년")
    # 저자명
    c.setFillColor(SECONDARY)
    c.setFont(KR_B, 13)
    c.drawCentredString(W_BLEED/2, 0.65*inch, "Deokgu Studio")
    c.save()
    print(f"  [fortune-notebook] cover.pdf -> {os.path.getsize(out)/1024:.0f} KB")


def page_header(c, title_kr, title_en):
    c.setFillColor(PRIMARY)
    c.rect(0, H - 0.6*inch, W, 0.6*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(KR_B, 18)
    c.drawString(0.85*inch, H - 0.42*inch, title_kr)
    c.setFont(KR, 11)
    c.setFillColor(SECONDARY)
    c.drawRightString(W - 0.75*inch, H - 0.4*inch, title_en)


def lined(c, x_left, y_top, x_right, count, leading=0.3):
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.setLineWidth(0.4)
    cy = y_top
    for _ in range(count):
        c.line(x_left, cy, x_right, cy)
        cy -= leading * inch
    return cy


def make_interior():
    out = BASE / "fortune_notebook.pdf"
    c = canvas.Canvas(str(out), pagesize=(W, H))
    M = 0.75 * inch
    M_INNER = 0.85 * inch

    # === 1. Title page (1p) ===
    c.setFillColor(PRIMARY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(KR_B, 56)
    c.drawCentredString(W/2, H*0.6, "운세노트")
    c.setFont(KR_B, 22)
    c.setFillColor(SECONDARY)
    c.drawCentredString(W/2, H*0.54, "FORTUNE NOTEBOOK")
    c.setFont(KR, 14)
    c.setFillColor(white)
    c.drawCentredString(W/2, H*0.48, "12-Month Lucky Tracker for 2026")
    c.setFont(KR_B, 13)
    c.setFillColor(SECONDARY)
    c.drawCentredString(W/2, H*0.15, "Deokgu Studio")
    c.showPage()

    # === 2. 사용 안내 (1p) ===
    page_header(c, "사용 안내", "How to Use")
    body = [
        "이 노트는 1년 12개월 동안 매월 자신의 운세 흐름을 기록하는 트래커입니다.",
        "This notebook helps you track your monthly fortune flow for 12 months.",
        "",
        "각 달의 페이지 구성 (Each month):",
        "  1. 이번 달의 행운 색 / 숫자 / 방향  (Lucky color / number / direction)",
        "  2. 이번 달의 다짐 / 목표  (Goals & intentions)",
        "  3. 좋았던 일 / 아쉬웠던 일 트래커  (Wins & lessons tracker)",
        "  4. 운세 키워드 일기  (Fortune keyword journal)",
        "  5. 월말 회고 페이지  (Monthly review)",
        "",
        "TIP: 매주 일요일 저녁 5분만 작성해도 한 달이 보입니다.",
        "TIP: 5 minutes every Sunday evening reveals your monthly pattern.",
        "",
        "Disclaimer: 운세 키워드는 자기성찰 도구이며 절대적 운명을 의미하지 않습니다.",
        "Disclaimer: Fortune keywords are self-reflection tools, not predictions.",
    ]
    c.setFillColor(black)
    cy = H - 1.4*inch
    for line in body:
        c.setFont(KR, 11)
        c.drawString(M_INNER, cy, line)
        cy -= 0.27*inch
    c.showPage()

    # === 3. 연간 비전 페이지 (2p) ===
    page_header(c, "2026 연간 비전", "Annual Vision")
    c.setFillColor(black)
    c.setFont(KR_B, 12)
    cy = H - 1.4*inch
    sections = [
        ("올해의 한 단어 / Word of the Year", 1),
        ("올해 이루고 싶은 3가지 / Top 3 Goals", 4),
        ("올해 버리고 싶은 습관 / Habits to release", 3),
        ("올해의 행운 색깔 / Lucky color this year", 1),
        ("올해의 행운 숫자 / Lucky numbers", 1),
    ]
    for title, lines in sections:
        c.setFont(KR_B, 12)
        c.setFillColor(PRIMARY)
        c.drawString(M_INNER, cy, title)
        cy -= 0.1*inch
        cy = lined(c, M_INNER, cy, W - M, lines, 0.32)
        cy -= 0.3*inch
    c.showPage()

    # 빈 비전 페이지 (drawing space)
    page_header(c, "비전 보드 (자유 공간)", "Vision Board (free space)")
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(1.5)
    c.rect(M_INNER, 1*inch, W - M - M_INNER, H - 2.5*inch, fill=0)
    c.setFillColor(HexColor("#888888"))
    c.setFont(KR, 10)
    c.drawCentredString(W/2, 0.7*inch, "이미지 / 키워드 / 단어를 자유롭게 붙이거나 그려 보세요")
    c.showPage()

    # === 4. 12개월 트래커 (월당 12p x 12 = 144p) ===
    for month in range(12):
        kr = MONTHS_KR[month]
        en = MONTHS_EN[month]

        # 4-1. 월간 표지 (1p)
        c.setFillColor(PRIMARY)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(KR_B, 80)
        c.drawCentredString(W/2, H*0.55, kr)
        c.setFont(KR_B, 22)
        c.setFillColor(SECONDARY)
        c.drawCentredString(W/2, H*0.47, en.upper())
        c.setFont(KR, 14)
        c.setFillColor(white)
        c.drawCentredString(W/2, H*0.4, f"Month {month+1} of 12")
        c.showPage()

        # 4-2. 행운 정보 페이지 (1p)
        page_header(c, f"{kr} 행운 정보", f"{en} Lucky Info")
        c.setFillColor(black)
        cy = H - 1.4*inch
        info_blocks = [
            ("이번 달의 행운 색  /  Lucky Color", "예: 보라, 노랑, 청록  ___________________________"),
            ("이번 달의 행운 숫자  /  Lucky Numbers", "예: 3, 7, 18  ____________________________________"),
            ("이번 달의 행운 방향  /  Lucky Direction", "예: 동남, 북서  __________________________________"),
            ("이번 달의 행운 요일  /  Lucky Weekdays", "예: 화, 금  ______________________________________"),
            ("이번 달의 키워드  /  Keywords", "한 줄로:  _______________________________________"),
        ]
        for t, hint in info_blocks:
            c.setFont(KR_B, 13)
            c.setFillColor(PRIMARY)
            c.drawString(M_INNER, cy, t)
            cy -= 0.28*inch
            c.setFont(KR, 11)
            c.setFillColor(black)
            c.drawString(M_INNER, cy, hint)
            cy -= 0.6*inch
        c.showPage()

        # 4-3. 월간 목표 / 다짐 (1p)
        page_header(c, f"{kr} 다짐", f"{en} Intentions")
        c.setFillColor(black)
        cy = H - 1.4*inch
        for title in ["이번 달 가장 이루고 싶은 일 (Top intention)",
                      "이번 달 새로 시작할 습관 (New habit)",
                      "이번 달 정리하고 싶은 것 (Letting go)"]:
            c.setFont(KR_B, 12)
            c.setFillColor(PRIMARY)
            c.drawString(M_INNER, cy, title)
            cy -= 0.15*inch
            cy = lined(c, M_INNER, cy, W - M, 4, 0.32)
            cy -= 0.3*inch
        c.showPage()

        # 4-4. 주간 트래커 (4p, 주당 1p)
        for week in range(4):
            page_header(c, f"{kr} {week+1}주차", f"{en} Week {week+1}")
            c.setFillColor(black)
            cy = H - 1.4*inch
            c.setFont(KR_B, 12)
            c.setFillColor(PRIMARY)
            c.drawString(M_INNER, cy, "이번 주 운세 키워드 (Keyword)")
            cy -= 0.32*inch
            c.line(M_INNER, cy + 4, W - M, cy + 4)
            cy -= 0.25*inch

            c.setFont(KR_B, 12)
            c.setFillColor(PRIMARY)
            c.drawString(M_INNER, cy, "기뻤던 일  /  Wins")
            cy = lined(c, M_INNER, cy - 0.1*inch, W - M, 4, 0.32)
            cy -= 0.2*inch
            c.setFont(KR_B, 12)
            c.drawString(M_INNER, cy, "아쉬웠던 일  /  Lessons")
            cy = lined(c, M_INNER, cy - 0.1*inch, W - M, 3, 0.32)
            cy -= 0.2*inch
            c.setFont(KR_B, 12)
            c.drawString(M_INNER, cy, "감사한 것  /  Gratitude")
            cy = lined(c, M_INNER, cy - 0.1*inch, W - M, 3, 0.32)
            c.showPage()

        # 4-5. 자유 일기 페이지 (4p)
        for j in range(4):
            page_header(c, f"{kr} 일기 {j+1}/4", f"{en} Journal {j+1}/4")
            c.setStrokeColor(HexColor("#CCCCCC"))
            c.setLineWidth(0.4)
            cy = H - 1.4*inch
            while cy > 0.9*inch:
                c.line(M_INNER, cy, W - M, cy)
                cy -= 0.32*inch
            c.showPage()

        # 4-6. 월말 회고 (1p)
        page_header(c, f"{kr} 회고", f"{en} Review")
        c.setFillColor(black)
        cy = H - 1.4*inch
        review = [
            "이번 달 가장 큰 수확은? (Biggest win)",
            "예상과 달랐던 흐름은? (Unexpected flow)",
            "사용한 행운 색/숫자/방향이 효과 있었나요?",
            "다음 달에 적용할 한 가지는?",
        ]
        for t in review:
            c.setFont(KR_B, 12)
            c.setFillColor(PRIMARY)
            c.drawString(M_INNER, cy, t)
            cy -= 0.12*inch
            cy = lined(c, M_INNER, cy, W - M, 3, 0.32)
            cy -= 0.25*inch
        c.showPage()

    # === 5. 부록 (3p) ===
    appendix_pages = [
        ("12지지와 띠 / 12 Branches",
         ["자(子) 쥐  /  축(丑) 소  /  인(寅) 호랑이  /  묘(卯) 토끼",
          "진(辰) 용  /  사(巳) 뱀  /  오(午) 말  /  미(未) 양",
          "신(申) 원숭이  /  유(酉) 닭  /  술(戌) 개  /  해(亥) 돼지",
          "",
          "자신의 띠를 알면, 매년 운세 흐름을 한 번 더 읽을 수 있습니다."]),
        ("오행과 색 / 5 Elements & Colors",
         ["목(木) - 청록 / Green - 시작과 성장",
          "화(火) - 빨강 / Red - 표현과 활력",
          "토(土) - 노랑 / Yellow - 안정과 신뢰",
          "금(金) - 흰색 / White - 결단과 정리",
          "수(水) - 검정 / Black - 지혜와 흐름"]),
        ("연간 회고 / Year-End Review",
         ["올해 가장 자랑스러운 순간 3가지:",
          "올해 만난 가장 좋은 사람:",
          "올해의 한 단어로 표현:",
          "내년에 가져갈 한 가지:"]),
    ]
    for title_kr, lines in appendix_pages:
        page_header(c, title_kr, "Appendix")
        c.setFillColor(black)
        c.setFont(KR, 12)
        cy = H - 1.4*inch
        for line in lines:
            c.drawString(M_INNER, cy, line)
            cy -= 0.32*inch
        cy -= 0.2*inch
        cy = lined(c, M_INNER, cy, W - M, 6, 0.32)
        c.showPage()

    c.save()
    print(f"  [fortune-notebook] fortune_notebook.pdf -> {os.path.getsize(out)/1024/1024:.1f} MB")


if __name__ == "__main__":
    print("=" * 50)
    print("Generating fortune-notebook book...")
    print(f"Korean font: {'OK' if HAS_KR else 'FAIL'}")
    print("=" * 50)
    make_cover()
    make_interior()
    print("Done.")
