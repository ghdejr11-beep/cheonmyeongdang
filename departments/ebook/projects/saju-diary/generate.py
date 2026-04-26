"""
사주일기 (Saju Diary) - 표지 + 본문 PDF 생성기
- 표지: 보라(#6D28D9) + 라벤더(#C4B5FD)
- 본문: 365일 daily diary + 사주 키워드 + 30p 입문 가이드 = 395p
- 한국어 폰트: 맑은고딕 / Pretendard / Noto Sans KR 자동 탐색
"""
from __future__ import annotations
import math
import os
from datetime import date, timedelta
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE = Path(__file__).parent
PRIMARY = HexColor("#6D28D9")
SECONDARY = HexColor("#C4B5FD")
ACCENT_DARK = HexColor("#3C1A78")

W, H = 8.5 * inch, 11 * inch  # trim
W_BLEED, H_BLEED = 8.75 * inch, 11.25 * inch  # cover with bleed

# 한국어 폰트 등록
KR_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\NanumGothic.ttf",
    r"C:\Windows\Fonts\Pretendard-Regular.ttf",
]

def register_korean_font():
    for cand in KR_FONT_CANDIDATES:
        if Path(cand).exists():
            try:
                pdfmetrics.registerFont(TTFont("KR", cand))
                # Bold variant
                bold_cand = cand.replace(".ttf", "bd.ttf")
                if Path(bold_cand).exists():
                    pdfmetrics.registerFont(TTFont("KR-Bold", bold_cand))
                else:
                    pdfmetrics.registerFont(TTFont("KR-Bold", cand))
                return True
            except Exception as e:
                print(f"  font load failed ({cand}): {e}")
    return False

HAS_KR = register_korean_font()
KR = "KR" if HAS_KR else "Helvetica"
KR_B = "KR-Bold" if HAS_KR else "Helvetica-Bold"


# ==========================================
# 표지 (cover.pdf)
# ==========================================
def make_cover():
    out = BASE / "cover.pdf"
    c = canvas.Canvas(str(out), pagesize=(W_BLEED, H_BLEED))
    # 배경 (보라 그라데이션 느낌은 단색 + 별)
    c.setFillColor(PRIMARY)
    c.rect(0, 0, W_BLEED, H_BLEED, fill=1, stroke=0)
    # 외곽 라벤더 보더
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(2)
    m = 0.5 * inch
    c.rect(m, m, W_BLEED - 2*m, H_BLEED - 2*m, fill=0, stroke=1)
    # 별자리 별 (랜덤 시드)
    import random
    random.seed(42)
    c.setFillColor(SECONDARY)
    for _ in range(60):
        sx = random.uniform(m + 5, W_BLEED - m - 5)
        sy = random.uniform(m + 5, H_BLEED - m - 5)
        sz = random.uniform(0.8, 2.5)
        c.circle(sx, sy, sz, fill=1, stroke=0)
    # 큰 별 4개 코너
    for cx, cy in [(W_BLEED*0.18, H_BLEED*0.82), (W_BLEED*0.82, H_BLEED*0.85),
                    (W_BLEED*0.15, H_BLEED*0.18), (W_BLEED*0.85, H_BLEED*0.2)]:
        draw_star(c, cx, cy, 12, 5, 5, SECONDARY)
    # 중앙 한자 命 자리에 한글 큰 타이틀 (한자 자제 - 2026 트렌드)
    c.setFillColor(white)
    c.setFont(KR_B, 78)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.55, "사주일기")
    # 부제
    c.setFillColor(SECONDARY)
    c.setFont(KR, 20)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.48, "365일 자기성찰 다이어리")
    c.setFont(KR, 14)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.44, "매일 사주 키워드와 함께")
    # 데코 라인
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(2)
    c.line(W_BLEED*0.3, H_BLEED*0.41, W_BLEED*0.7, H_BLEED*0.41)
    # 2026 표시
    c.setFillColor(white)
    c.setFont(KR_B, 24)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.32, "2026")
    c.setFont(KR, 12)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.29, "병오년 BYEONG-O")
    # 저자명
    c.setFillColor(SECONDARY)
    c.setFont(KR_B, 13)
    c.drawCentredString(W_BLEED/2, 0.65*inch, "Deokgu Studio")
    c.save()
    print(f"  [saju-diary] cover.pdf -> {os.path.getsize(out)/1024:.0f} KB")


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


# ==========================================
# 본문 (interior.pdf)
# ==========================================
SAJU_KEYWORDS = [
    "정인 - 학문과 안정", "편인 - 직관과 영감", "정관 - 명예와 책임",
    "편관 - 도전과 결단", "정재 - 성실한 재물", "편재 - 큰 흐름의 재물",
    "식신 - 베풂과 풍요", "상관 - 표현과 창의", "비견 - 동료와 경쟁",
    "겁재 - 경쟁과 분배",
    "갑목 - 큰 나무의 기상", "을목 - 부드러운 풀잎",
    "병화 - 태양의 활력", "정화 - 촛불의 정성",
    "무토 - 큰 산의 무게감", "기토 - 옥토의 너그러움",
    "경금 - 강철의 결단", "신금 - 보석의 섬세함",
    "임수 - 큰 바다의 흐름", "계수 - 이슬의 청명함",
    "자수의 지혜", "축토의 인내", "인목의 시작", "묘목의 성장",
    "진토의 변화", "사화의 열정", "오화의 절정", "미토의 결실",
    "신금의 단정", "유금의 빛남", "술토의 마무리", "해수의 깊이",
]


def make_interior():
    out = BASE / "saju_diary.pdf"
    c = canvas.Canvas(str(out), pagesize=(W, H))
    # 마진
    M = 0.75 * inch
    M_INNER = 0.85 * inch  # 제본 측 여유

    # ===== 1. Title page =====
    c.setFillColor(PRIMARY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(KR_B, 56)
    c.drawCentredString(W/2, H*0.6, "사주일기")
    c.setFillColor(SECONDARY)
    c.setFont(KR, 18)
    c.drawCentredString(W/2, H*0.53, "365일 자기성찰 다이어리")
    c.setFont(KR, 13)
    c.drawCentredString(W/2, H*0.5, "매일 사주 키워드와 함께")
    c.setFillColor(white)
    c.setFont(KR_B, 14)
    c.drawCentredString(W/2, H*0.15, "Deokgu Studio")
    c.showPage()

    # ===== 2. 사용 안내 (1p) =====
    page_header(c, "사용 안내")
    body_text(c, M, H - 1.5*inch, [
        "이 다이어리는 365일 동안 매일 한 페이지씩 작성하는 자기성찰 노트입니다.",
        "",
        "각 페이지 구성:",
        "  - 날짜 / 요일 / 날씨",
        "  - 오늘의 사주 키워드 (10간 / 12지 / 십신 순환)",
        "  - 오늘의 운 (간단 메모)",
        "  - 자유 일기 공간",
        "  - 감사 한 줄 / 내일 다짐",
        "",
        "사주 키워드는 학습용이며, 절대적 운명을 의미하지 않습니다.",
        "매일의 키워드를 통해 자신의 하루를 새로운 관점에서 돌아보세요.",
    ])
    c.showPage()

    # ===== 3. 사주 입문 가이드 (28p) =====
    guide_pages = [
        ("사주명리란 무엇인가",
         ["사주(四柱)는 사람이 태어난 연·월·일·시 네 기둥의 천간(天干)과 지지(地支) 8글자로",
          "구성됩니다. 그래서 '사주팔자(四柱八字)'라고 부릅니다.",
          "",
          "명리학은 이 8글자의 음양오행 균형을 살펴 그 사람의 성향, 흐름, 시기를",
          "해석하는 동양 철학의 한 갈래입니다.",
          "",
          "이 책은 학술서가 아닙니다. 매일 사주 키워드 하나를 만나며,",
          "자신의 하루를 새 각도로 바라보는 도구로 사용하세요."]),
        ("음양(陰陽)의 기본",
         ["모든 것은 음과 양의 두 기운으로 나뉩니다.",
          "",
          "양(陽): 밝음, 활동, 외향, 더위, 위로 뻗는 기운",
          "음(陰): 어두움, 휴식, 내향, 추위, 아래로 모이는 기운",
          "",
          "어느 한쪽이 좋고 나쁜 게 아니라, 균형이 중요합니다.",
          "낮(양)이 있으면 밤(음)이 있고, 활동이 있으면 휴식이 필요합니다."]),
        ("오행(五行) - 다섯 기운",
         ["목(木) - 나무: 시작, 성장, 의욕",
          "화(火) - 불: 표현, 열정, 확산",
          "토(土) - 흙: 중심, 안정, 신뢰",
          "금(金) - 쇠: 결단, 정리, 수렴",
          "수(水) - 물: 지혜, 흐름, 휴식",
          "",
          "다섯 기운은 서로 살리고 (상생), 서로 견제합니다 (상극).",
          "한 기운만 강하면 불균형이고, 다섯이 적절히 어우러질 때 건강한 흐름이 됩니다."]),
        ("천간(天干) 10글자",
         ["갑(甲) 을(乙) - 목 (큰 나무, 작은 풀)",
          "병(丙) 정(丁) - 화 (태양, 촛불)",
          "무(戊) 기(己) - 토 (큰 산, 옥토)",
          "경(庚) 신(辛) - 금 (강철, 보석)",
          "임(壬) 계(癸) - 수 (큰 바다, 이슬)",
          "",
          "각 천간은 자신만의 기질을 가집니다.",
          "오늘의 천간 키워드는 그 기질을 한 번 떠올려 보는 시간입니다."]),
        ("지지(地支) 12글자",
         ["자(子) 축(丑) 인(寅) 묘(卯) 진(辰) 사(巳)",
          "오(午) 미(未) 신(申) 유(酉) 술(戌) 해(亥)",
          "",
          "12지지는 띠로도 알려져 있습니다 (쥐, 소, 호랑이...).",
          "각 지지는 시간, 계절, 방향, 동물을 함께 의미합니다.",
          "",
          "오늘의 지지 키워드를 만나면, 그 기운의 흐름을 떠올려 보세요."]),
        ("십신(十神) - 관계의 별",
         ["일간(태어난 날의 천간)을 기준으로 다른 글자를 보는 관계가 십신입니다.",
          "",
          "비견 / 겁재 - 동료, 경쟁자",
          "식신 / 상관 - 표현, 창작",
          "정재 / 편재 - 성실 / 큰 재물",
          "정관 / 편관 - 명예 / 도전",
          "정인 / 편인 - 학문 / 직관",
          "",
          "십신 키워드는 오늘 어떤 관계, 어떤 활동에 집중하면 좋을지 힌트입니다."]),
        ("이 책의 활용법",
         ["1. 매일 한 페이지를 작성하세요. 5분이면 충분합니다.",
          "2. 오늘의 사주 키워드를 읽고, 한 줄로 떠오르는 생각을 적어 보세요.",
          "3. 그날의 사건/감정을 자유롭게 기록하세요.",
          "4. 한 주, 한 달, 한 분기 단위로 다시 읽어 보세요.",
          "5. 사주 키워드와 자신의 패턴이 만나는 지점을 발견할 수 있습니다.",
          "",
          "사주는 운명을 정하지 않습니다. 자신을 비추는 거울일 뿐입니다.",
          "매일의 기록이 모이면, 그것이 곧 당신만의 운입니다."]),
    ]
    for title, lines in guide_pages:
        page_header(c, title)
        body_text(c, M, H - 1.5*inch, lines)
        c.showPage()
        # 추가 빈 노트 페이지 (가이드 챕터마다 노트 1p) - 28p 채우기
        page_header(c, f"{title} - 노트")
        draw_lines(c, M, H - 1.5*inch, M_INNER, M, H - 0.75*inch)
        c.showPage()

    # 가이드 합계 = 7챕터 x 2p = 14p + 사용안내 1p + 타이틀 1p = 16p
    # 365 daily + 14 monthly review = 379p + 16 = 395p

    # ===== 4. 365일 daily pages =====
    start_date = date(2026, 1, 1)
    for day in range(365):
        d = start_date + timedelta(days=day)
        kw_idx = day % len(SAJU_KEYWORDS)
        keyword = SAJU_KEYWORDS[kw_idx]
        weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]
        # 월 시작일에 monthly review 페이지
        if d.day == 1 and day != 0:
            month_review_page(c, d.month, M, M_INNER)
            c.showPage()
        # 데일리 페이지
        daily_page(c, d, weekday_kr, keyword, M, M_INNER)
        c.showPage()
    # 마지막 monthly review (12월)
    month_review_page(c, 13, M, M_INNER, last=True)
    c.showPage()

    c.save()
    print(f"  [saju-diary] saju_diary.pdf -> {os.path.getsize(out)/1024/1024:.1f} MB")


def page_header(c, title):
    c.setFillColor(PRIMARY)
    c.rect(0, H - 0.5*inch, W, 0.5*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(KR_B, 16)
    c.drawString(0.85*inch, H - 0.32*inch, title)
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(1)
    c.line(0.85*inch, H - 0.55*inch, W - 0.75*inch, H - 0.55*inch)


def body_text(c, x, y, lines, size=11, leading=18):
    c.setFillColor(black)
    c.setFont(KR, size)
    cy = y
    for line in lines:
        c.drawString(x, cy, line)
        cy -= leading


def draw_lines(c, x_left, y_top, x_inner_margin, x_right_margin, page_top):
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.setLineWidth(0.5)
    cy = y_top
    while cy > 0.75 * inch:
        c.line(x_inner_margin, cy, W - x_right_margin, cy)
        cy -= 0.32 * inch


def daily_page(c, d, weekday_kr, keyword, M, M_INNER):
    # 날짜 헤더
    c.setFillColor(PRIMARY)
    c.rect(0, H - 0.6*inch, W, 0.6*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(KR_B, 22)
    date_str = f"{d.year}년 {d.month}월 {d.day}일 ({weekday_kr})"
    c.drawString(M_INNER, H - 0.42*inch, date_str)
    c.setFont(KR, 11)
    c.drawRightString(W - M, H - 0.4*inch, f"Day {d.timetuple().tm_yday}/365")

    # 오늘의 사주 키워드 박스
    box_y = H - 1.4*inch
    c.setFillColor(SECONDARY)
    c.rect(M_INNER, box_y - 0.35*inch, W - M_INNER - M, 0.55*inch, fill=1, stroke=0)
    c.setFillColor(ACCENT_DARK)
    c.setFont(KR_B, 11)
    c.drawString(M_INNER + 0.15*inch, box_y + 0.05*inch, "오늘의 사주 키워드")
    c.setFont(KR_B, 14)
    c.drawString(M_INNER + 0.15*inch, box_y - 0.18*inch, keyword)

    # 날씨 / 컨디션 체크박스
    cy = box_y - 0.6*inch
    c.setFillColor(black)
    c.setFont(KR, 10)
    c.drawString(M_INNER, cy, "날씨:  ☼  ☁  ☂  ❄        컨디션:  ☺  😐  ☹        에너지:  □□□□□")

    # 오늘의 운 메모 (3줄)
    cy -= 0.35*inch
    c.setFont(KR_B, 11)
    c.drawString(M_INNER, cy, "오늘의 운 (한 줄 메모)")
    cy -= 0.05*inch
    c.setStrokeColor(HexColor("#999999"))
    c.setLineWidth(0.5)
    for _ in range(2):
        cy -= 0.3*inch
        c.line(M_INNER, cy, W - M, cy)

    # 자유 일기 공간
    cy -= 0.3*inch
    c.setFillColor(black)
    c.setFont(KR_B, 11)
    c.drawString(M_INNER, cy, "오늘의 일기")
    cy -= 0.05*inch
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.setLineWidth(0.4)
    while cy > 1.6*inch:
        cy -= 0.32*inch
        c.line(M_INNER, cy, W - M, cy)

    # 감사 한 줄 / 내일 다짐
    fy = 1.2*inch
    c.setFillColor(black)
    c.setFont(KR_B, 10)
    c.drawString(M_INNER, fy, "감사 한 줄")
    c.line(M_INNER + 1.0*inch, fy - 2, W*0.55, fy - 2)
    c.drawString(W*0.58, fy, "내일 다짐")
    c.line(W*0.58 + 0.85*inch, fy - 2, W - M, fy - 2)

    # 페이지 번호
    c.setFont(KR, 9)
    c.setFillColor(HexColor("#888888"))
    c.drawCentredString(W/2, 0.5*inch, f"{d.month:02d} . {d.day:02d}")


def month_review_page(c, month, M, M_INNER, last=False):
    c.setFillColor(SECONDARY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(ACCENT_DARK)
    c.setFont(KR_B, 36)
    if last:
        c.drawCentredString(W/2, H*0.85, "한 해의 마무리")
    else:
        c.drawCentredString(W/2, H*0.85, f"{month}월의 회고")

    c.setFont(KR_B, 14)
    cy = H*0.7
    sections = [
        "이번 달 가장 기뻤던 일",
        "이번 달 가장 힘들었던 일",
        "사주 키워드 중 가장 와닿았던 것",
        "다음 달의 다짐",
    ] if not last else [
        "올해 가장 기뻤던 일",
        "올해 가장 성장한 부분",
        "가장 와닿았던 사주 키워드",
        "내년에 이루고 싶은 것",
    ]
    for s in sections:
        c.drawString(M_INNER, cy, s)
        cy -= 0.1*inch
        c.setStrokeColor(ACCENT_DARK)
        c.setLineWidth(0.5)
        for _ in range(3):
            cy -= 0.32*inch
            c.line(M_INNER, cy, W - M, cy)
        cy -= 0.45*inch
        c.setFont(KR_B, 14)


# ==========================================
# Main
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("Generating saju-diary book...")
    print(f"Korean font: {'OK (' + KR + ')' if HAS_KR else 'FAIL - using Helvetica'}")
    print("=" * 50)
    make_cover()
    make_interior()
    print("Done.")
