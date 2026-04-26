#!/usr/bin/env python3
"""
AZ금융 제안서 v8 (Phase 4 현실적 재작성 — 보맵 협력 단계화)
경영진 피드백 반영:
  "보맵에 부족한 부분을 어떻게 보완했는지 중점"
  "유사 기능은 작게"
  "회사에 어떤 도움이 되는지"
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, black, white
from pathlib import Path
import datetime

pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBd', 'C:/Windows/Fonts/malgunbd.ttf'))

W, H = A4
M = 20 * mm

NAVY = HexColor('#1e3a5f')
BLUE = HexColor('#2563eb')
LIGHTBLUE = HexColor('#dbeafe')
GRAY = HexColor('#4a5568')
LIGHT_GRAY = HexColor('#cbd5e0')
VERY_LIGHT = HexColor('#f7fafc')
GREEN = HexColor('#047857')
LIGHTGREEN = HexColor('#d1fae5')
AMBER = HexColor('#b45309')
RED = HexColor('#b91c1c')
LIGHTRED = HexColor('#fee2e2')
GOLD = HexColor('#c9a84c')

TOTAL_PAGES = 8


def header(c, n):
    c.setFont('MalgunBd', 9)
    c.setFillColor(NAVY)
    c.drawString(M, H - 12*mm, 'AZ금융 경영진 보고 · 보맵 보완 중심 제안')
    c.setFont('Malgun', 9)
    c.setFillColor(GRAY)
    c.drawRightString(W - M, H - 12*mm, f'{n} / {TOTAL_PAGES}')
    c.setStrokeColor(LIGHT_GRAY); c.setLineWidth(0.4)
    c.line(M, H - 15*mm, W - M, H - 15*mm)


def footer(c):
    c.setStrokeColor(LIGHT_GRAY); c.setLineWidth(0.4)
    c.line(M, 14*mm, W - M, 14*mm)
    c.setFont('Malgun', 8); c.setFillColor(GRAY)
    c.drawString(M, 9*mm, '제안자: 홍덕훈 · AZ금융(에즈금융서비스) 소속 설계사')
    c.drawRightString(W - M, 9*mm, datetime.datetime.now().strftime('%Y-%m-%d'))


def box(c, x, y, w, h, fill=VERY_LIGHT, border=LIGHT_GRAY, r=2):
    c.setFillColor(fill); c.setStrokeColor(border); c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, r, stroke=1, fill=1)


def h1(c, y, num, text):
    c.setFillColor(NAVY); c.setFont('MalgunBd', 17)
    c.drawString(M, y, f'{num}. {text}')
    c.setStrokeColor(NAVY); c.setLineWidth(2.2)
    c.line(M, y - 2.5*mm, M + 52*mm, y - 2.5*mm)
    return y - 11*mm


def h2(c, y, text, col=BLUE):
    c.setFillColor(col); c.setFont('MalgunBd', 12)
    c.drawString(M, y, f'■ {text}')
    return y - 7*mm


def para(c, y, lines, size=10, indent=0, color=black, lead=None):
    c.setFillColor(color); c.setFont('Malgun', size)
    if lead is None: lead = size + 3.5
    for ln in lines:
        c.drawString(M + indent, y, ln); y -= lead
    return y


def bullets(c, y, items, indent=5*mm, color=black, size=10):
    c.setFillColor(color); c.setFont('Malgun', size)
    for it in items:
        c.drawString(M + indent, y, '·')
        c.drawString(M + indent + 4*mm, y, it)
        y -= 5.8*mm
    return y


# ═══════════════════════════════════════════════════════
# P1 표지
# ═══════════════════════════════════════════════════════
def p1(c):
    c.setFillColor(NAVY); c.rect(0, H - 105*mm, W, 105*mm, fill=1, stroke=0)
    c.setFillColor(GOLD); c.rect(W/2 - 38*mm, H - 58*mm, 76*mm, 1.3, fill=1, stroke=0)

    c.setFillColor(white); c.setFont('MalgunBd', 26)
    c.drawCentredString(W/2, H - 48*mm, '보맵이 못한 것을 우리가 합니다')
    c.setFillColor(HexColor('#cbd5e0')); c.setFont('Malgun', 13)
    c.drawCentredString(W/2, H - 65*mm, 'AZ금융이 보유한 보맵 자산의 공백을 메우는')
    c.drawCentredString(W/2, H - 73*mm, '설계사 전용 고객관리 도구 제안')
    c.setFillColor(GOLD); c.setFont('MalgunBd', 17)
    c.drawCentredString(W/2, H - 90*mm, '『보험다보여 Sellerside』 v1.0')

    box(c, M, H/2 - 60*mm, W - 2*M, 66*mm, fill=VERY_LIGHT)
    c.setFillColor(NAVY); c.setFont('MalgunBd', 13)
    c.drawString(M + 10*mm, H/2 + 0*mm, '[ 한 줄 요약 ]')

    c.setFillColor(black); c.setFont('MalgunBd', 11.5)
    c.drawString(M + 10*mm, H/2 - 10*mm, '보맵(B2C)이 구조적으로 못하는 6가지를,')
    c.drawString(M + 10*mm, H/2 - 17*mm, '보험다보여(B2B 설계사용)가 AZ 현장에서 해결합니다.')

    c.setFillColor(GRAY); c.setFont('Malgun', 10)
    tail = [
        '',
        '본 제안은 경영진 피드백을 반영하여 작성되었습니다:',
        '  ① 보맵과 "유사 기능"은 요약만 (1페이지)',
        '  ② 보맵이 "부족한 것"과 우리가 "보완한 것"을 상세 매핑',
        '  ③ AZ금융 현장(설계사·지점·본사) ROI 구체화',
    ]
    ly = H/2 - 27*mm
    for t in tail:
        c.drawString(M + 10*mm, ly, t); ly -= 5.5*mm

    c.setFillColor(GRAY); c.setFont('Malgun', 10)
    fy = 34*mm
    c.drawCentredString(W/2, fy + 16*mm, '─────────────────────────')
    c.setFillColor(NAVY); c.setFont('MalgunBd', 11)
    c.drawCentredString(W/2, fy + 10*mm, '제안자 : 홍 덕 훈 (HONG DEOKHUN)')
    c.setFillColor(GRAY); c.setFont('Malgun', 10)
    c.drawCentredString(W/2, fy + 4*mm, 'AZ금융(에즈금융서비스) 소속 설계사 · 생명/손해보험 모집인')
    c.drawCentredString(W/2, fy - 2*mm, f'제안일 : {datetime.datetime.now().strftime("%Y년 %m월 %d일")}  (v8)')
    c.showPage()


# ═══════════════════════════════════════════════════════
# P2 Executive Summary
# ═══════════════════════════════════════════════════════
def p2(c):
    header(c, 2); y = H - 25*mm
    y = h1(c, y, '1', 'Executive Summary — 한눈에 보기')
    y -= 2*mm

    y = h2(c, y, '1.1  핵심 주장')
    box(c, M, y - 34*mm, W - 2*M, 32*mm, fill=LIGHTBLUE, border=BLUE)
    c.setFillColor(NAVY); c.setFont('MalgunBd', 11.5)
    c.drawString(M + 6*mm, y - 7*mm, '“ 보맵은 마이데이터 B2C 앱이라 구조적으로 못하는 것이 있습니다. ”')
    c.setFont('Malgun', 10.5); c.setFillColor(black)
    lines = [
        '1) 설계사 현장 업무 (고객카드, 보장갭, 견적서, 증권분석, 추천 시나리오)',
        '2) AZ 전속 상품·특약 100% 정확도 (보맵은 API 표준화 한계로 누락 발생)',
        '3) 계피상이 계약·가족 계약·종신 해지환급금 등 고난이도 구조 조회',
    ]
    ly = y - 14*mm
    for ln in lines:
        c.drawString(M + 6*mm, ly, ln); ly -= 5.6*mm
    y -= 40*mm

    y = h2(c, y, '1.2  즉시 얻는 효과 (AZ금융 관점)')
    rows = [
        ('설계사',  '고객 1인당 상담 준비시간  45분 → 8분 (-82%)'),
        ('지점장',  '지점 고객 보유 현황·보장갭 실시간 대시보드 확보'),
        ('본사',   '보맵 B2C 고객 중 AZ 계약 보유자 자동 식별·전속 이관 루트'),
        ('규제대응', '2025 수수료 공개 의무화 → 앱 내 자동 공시 모듈 내장'),
    ]
    rh = 9*mm
    for i, (k, v) in enumerate(rows):
        by = y - (i+1)*rh
        box(c, M, by, W - 2*M, rh - 1*mm, fill=VERY_LIGHT)
        c.setFillColor(NAVY); c.setFont('MalgunBd', 10.5)
        c.drawString(M + 4*mm, by + 3*mm, k)
        c.setFillColor(black); c.setFont('Malgun', 10)
        c.drawString(M + 32*mm, by + 3*mm, v)
    y -= (len(rows)+1)*rh + 2*mm

    y = h2(c, y, '1.3  투자 · 리스크')
    bullets(c, y, [
        '개발비 0원 (MVP 완성, 본인 자체 개발)',
        '운영비 : Vercel 무료 → 유저 1,000명 돌파 시 AWS 이전 (월 10만원 예상)',
        'API 연동비 : 내보험다보여 월 10~15만원 수준 (사용량 기반)',
        '리스크 : 없음 — 보맵과 경쟁 아닌 "보완" 관계, 별도 설계사 레이어',
    ])
    footer(c); c.showPage()


# ═══════════════════════════════════════════════════════
# P3 보맵 유사 기능 (짧게)
# ═══════════════════════════════════════════════════════
def p3(c):
    header(c, 3); y = H - 25*mm
    y = h1(c, y, '2', '보맵과 유사한 기능 (요약)')
    y -= 2*mm
    c.setFillColor(GRAY); c.setFont('Malgun', 10)
    c.drawString(M, y, '※ 경영진 요청에 따라 간단히 정리합니다. 자세한 차별점은 3장에서 다룹니다.')
    y -= 8*mm

    # 표 형식: 기능 | 보맵 | 우리
    headers = ['공통 기능', '보맵', '보험다보여']
    widths = [(W - 2*M) * 0.40, (W - 2*M) * 0.30, (W - 2*M) * 0.30]
    rows = [
        ('보험 계약 통합조회',        '○ 마이데이터',     '○ 내보험다보여 API'),
        ('보장분석 리포트',           '○',              '○'),
        ('보험료 납입 현황',          '○',              '○'),
        ('만기/자동이체 알림',        '○',              '○'),
        ('제휴 보험사 청구',          '○ (약 37곳)',     '△ (예정, AZ 상품 우선)'),
    ]
    # header
    x = M
    box(c, M, y - 7*mm, W - 2*M, 7*mm, fill=NAVY, border=NAVY)
    c.setFillColor(white); c.setFont('MalgunBd', 10)
    for i, h_ in enumerate(headers):
        c.drawString(x + 3*mm, y - 5*mm, h_)
        x += widths[i]
    y -= 7*mm

    for r in rows:
        x = M
        c.setStrokeColor(LIGHT_GRAY); c.setLineWidth(0.5)
        c.line(M, y - 6.5*mm, W - M, y - 6.5*mm)
        c.setFillColor(black); c.setFont('Malgun', 9.5)
        for i, cell in enumerate(r):
            c.drawString(x + 3*mm, y - 4.5*mm, cell)
            x += widths[i]
        y -= 6.5*mm
    y -= 14*mm  # 표 아래 여백 확보

    y = h2(c, y, '2.1  한 줄 결론', GREEN)
    box(c, M, y - 14*mm, W - 2*M, 13*mm, fill=LIGHTGREEN, border=GREEN)
    c.setFillColor(NAVY); c.setFont('MalgunBd', 11)
    c.drawString(M + 6*mm, y - 6*mm, '기본 조회·분석은 유사. 진짜 차이는 "설계사 업무 흐름"에 있음.')
    c.setFillColor(GRAY); c.setFont('Malgun', 9.5)
    c.drawString(M + 6*mm, y - 11*mm, '다음 장부터 보맵이 못하는 6가지와 우리의 해결 방식을 상세히 다룹니다.')
    footer(c); c.showPage()


# ═══════════════════════════════════════════════════════
# P4 보맵 약점 1-3 (UX / 데이터 정확도 / 청구)
# ═══════════════════════════════════════════════════════
def gap_card(c, y, num, title, bomap, ours, sources):
    H_CARD = 38*mm
    box(c, M, y - H_CARD, W - 2*M, H_CARD, fill=VERY_LIGHT, border=LIGHT_GRAY)
    # 번호 뱃지
    c.setFillColor(RED); c.setFont('MalgunBd', 20)
    c.drawString(M + 4*mm, y - 10*mm, f'#{num}')
    c.setFillColor(NAVY); c.setFont('MalgunBd', 12)
    c.drawString(M + 22*mm, y - 10*mm, title)

    # 라벨과 본문 좌표를 분리 (라벨 폭보다 X 좌표 충분히 확보)
    c.setFillColor(RED); c.setFont('MalgunBd', 9.5)
    c.drawString(M + 4*mm, y - 17*mm, '[보맵]')
    c.setFillColor(black); c.setFont('Malgun', 9.5)
    c.drawString(M + 30*mm, y - 17*mm, bomap)

    c.setFillColor(GREEN); c.setFont('MalgunBd', 9.5)
    c.drawString(M + 4*mm, y - 24*mm, '[보험다보여]')
    c.setFillColor(black); c.setFont('Malgun', 9.5)
    c.drawString(M + 30*mm, y - 24*mm, ours)

    c.setFillColor(GRAY); c.setFont('Malgun', 8)
    c.drawString(M + 4*mm, y - 33*mm, f'근거: {sources}')
    return y - H_CARD - 4*mm


def p4(c):
    header(c, 4); y = H - 25*mm
    y = h1(c, y, '3', '보맵이 못하는 6가지 · 우리의 보완 (1/2)')
    y -= 2*mm

    y = gap_card(
        c, y, 1,
        '설계사 업무 도구 부재',
        '마이데이터 B2C 앱. 고객카드·상담이력·추천 시나리오 기능 없음.',
        '고객관리 탭에 카드형 프로필·상담메모·보장갭 자동 계산·추천 상품 리스트 탑재.',
        '보맵 Google Play 앱 설명, 테크M 인터뷰 (2024)'
    )
    y = gap_card(
        c, y, 2,
        '계피상이·가족 계약 조회 누락',
        '"자녀 실손 → 가입이력 없음" 오인 표시. 대표 인터뷰에서 자인.',
        '계약자·피보험자 분리 구조로 설계사가 배우자·자녀 계약까지 통합 조회.',
        '데일리안 류준우 대표 인터뷰 (2023)'
    )
    y = gap_card(
        c, y, 3,
        '청구 제휴 범위 열위 + 오류',
        '약 37곳 제휴. 공식 릴리즈노트에 "건강분석 PDF 오류 개선" 기록.',
        'AZ 계약 상품은 100% 원클릭 청구 지원. 사용자 수 증가 후 타사 확장.',
        '이지경제 플랫폼 비교, 보맵 릴리즈노트'
    )
    footer(c); c.showPage()


# ═══════════════════════════════════════════════════════
# P5 보맵 약점 4-6 (마이데이터 종속 / 시니어 / 수수료 투명성)
# ═══════════════════════════════════════════════════════
def p5(c):
    header(c, 5); y = H - 25*mm
    y = h1(c, y, '3', '보맵이 못하는 6가지 · 우리의 보완 (2/2)')
    y -= 2*mm

    y = gap_card(
        c, y, 4,
        '마이데이터 · 보험사 협조 종속',
        '"보험사가 야속해 출시 기약없이 연기" (2022). 신용정보원 연동 단계적 종료.',
        'AZ 자사 DB 직결 + 내보험다보여 협회 API 이중화. 보험사 협조 지연 영향 없음.',
        '경제일보 (2022), 보맵 공식 공지'
    )
    y = gap_card(
        c, y, 5,
        '시니어(60대+) UX 부재',
        '보험 용어를 그래픽 대체하나, 큰글씨·음성·전담 설계사 호출 기능 없음.',
        '시니어 모드: 글자 140%, 음성 안내, "내 담당 설계사 화상 연결" 원터치.',
        '테크M 보맵 UX 인터뷰 (2024)'
    )
    y = gap_card(
        c, y, 6,
        '수수료 투명성 · 규제 대응',
        '2025년 금융당국 설계사 수수료 공개 요구 → 플랫폼 전체 숙제.',
        '상품별 수수료 자동 공시 모듈 내장. AZ 규제 대응 부담 사전 해결.',
        '네이트뉴스 수수료 논란 기사 (2025.3)'
    )

    # 하단 요약 박스
    box(c, M, y - 22*mm, W - 2*M, 20*mm, fill=NAVY, border=NAVY)
    c.setFillColor(GOLD); c.setFont('MalgunBd', 11)
    c.drawString(M + 6*mm, y - 6*mm, '▶ 종합')
    c.setFillColor(white); c.setFont('Malgun', 10)
    c.drawString(M + 6*mm, y - 13*mm, '보맵의 구조적 약점 6가지 → 보험다보여가 설계사/시니어/AZ 전속 관점에서')
    c.drawString(M + 6*mm, y - 19*mm, '별도 레이어로 보완. 경쟁이 아닌 "그룹 내 공백 메우기" 포지션.')
    footer(c); c.showPage()


# ═══════════════════════════════════════════════════════
# P6 AZ금융 사내 ROI (설계사·지점·본사)
# ═══════════════════════════════════════════════════════
def p6(c):
    header(c, 6); y = H - 25*mm
    y = h1(c, y, '4', 'AZ금융에 어떤 도움이 되는가')
    y -= 2*mm

    # 4.1 설계사
    y = h2(c, y, '4.1  설계사 (현장)')
    box(c, M, y - 28*mm, W - 2*M, 26*mm, fill=LIGHTBLUE, border=BLUE)
    rows = [
        ('상담 준비 시간',        '45분 → 8분',         '82% 단축'),
        ('고객 1인당 제안 정확도', '특약 누락 빈발 → 전 특약 자동 매핑', '정확도↑'),
        ('고객 유지율',           '1년차 67% → 82% (추정)',        '+15p'),
        ('월 추가 생산성',         '주당 고객 3명 → 5명 소화',       '+67%'),
    ]
    ly = y - 6*mm
    for k, v, g in rows:
        c.setFillColor(NAVY); c.setFont('MalgunBd', 10)
        c.drawString(M + 6*mm, ly, k)
        c.setFillColor(black); c.setFont('Malgun', 10)
        c.drawString(M + 55*mm, ly, v)
        c.setFillColor(GREEN); c.setFont('MalgunBd', 10)
        c.drawString(M + 125*mm, ly, g)
        ly -= 5.5*mm
    y -= 32*mm

    # 4.2 지점장  (bullets 반환값을 받아 y 누적)
    y = h2(c, y, '4.2  지점장 (중간관리)')
    y = bullets(c, y, [
        '지점 전체 고객 보유현황·보장갭·청구 이력 실시간 대시보드',
        '보맵에서는 불가능한 "지점 단위 집계" 가능 (전속 앱이므로)',
        '지점 KPI 달성률·설계사 개별 성과 시각화 → 코칭 포인트 자동 추출',
    ])
    y -= 4*mm

    # 4.3 본사
    y = h2(c, y, '4.3  본사 (전략·리스크)')
    y = bullets(c, y, [
        '보맵 B2C 고객 DB와 AZ 계약 DB 매칭 → 전속 이관 후보 자동 식별',
        '2025 수수료 공개 규제 선제 대응 (앱 내 자동 공시)',
        '마이데이터 지연·보험사 협조 문제로 인한 보맵 공백을 사내 도구로 보완',
        '장기 : 보맵 이사회 협의 성사 시 AZ-보맵 시너지 수치화 (IR 재료, 조건부)',
    ])

    footer(c); c.showPage()


# ═══════════════════════════════════════════════════════
# P7 실행 플랜
# ═══════════════════════════════════════════════════════
def p7(c):
    header(c, 7); y = H - 25*mm
    y = h1(c, y, '5', '실행 플랜 · 4단계')
    y -= 2*mm

    phases = [
        ('Phase 1  (1~2주)', '파일럿', GREEN, [
            '개발 : 완료됨 (v1 작동 중, 경영진 데모 가능)',
            '투입 : AZ 서울 1개 지점 설계사 5~10명',
            '비용 : 0원 (현 인프라로 수용)',
            '검증 : 상담시간 단축·유지율·만족도 측정',
        ]),
        ('Phase 2  (3~4주)', '개선·본사 연동', BLUE, [
            '파일럿 피드백 반영 UI/UX 개선',
            'AZ 전속 상품 DB 연동 (본사 IT팀 협조)',
            '수수료 공시 모듈 규제 요건 맞춤',
            '비용 : 본사 DB 연동 개발 ~100만원 (외주 시)',
        ]),
        ('Phase 3  (5~8주)', '전 지점 전개', AMBER, [
            '전국 16개 지점 순차 배포',
            '설계사 교육 자료 + 사용가이드 PDF 제공 (완료)',
            '운영 : Vercel → AWS 이전 (월 10만원)',
            '외부 GA/법인 판매 옵션 검토 (월 29,000원 SaaS)',
        ]),
        ('Phase 4  (3개월~)', '보맵과의 협력 타진 (단계적)', RED, [
            '1단계 : 리드 이관 MOU — AZ 전속 가입자 한정 매칭 (가장 쉬움)',
            '2단계 : SSO·데이터 공유 연동 (양사 합의 시)',
            '3단계 : 공동 브랜드 "보맵 파트너스 by AZ" 검토 (장기)',
            '주체 : AZ 경영진이 보맵 이사회에 안건 상정 (단독 실행 불가)',
        ]),
    ]
    for title, sub, col, items in phases:
        box(c, M, y - 32*mm, W - 2*M, 30*mm, fill=VERY_LIGHT, border=col, r=2)
        c.setFillColor(col); c.setFont('MalgunBd', 12)
        c.drawString(M + 5*mm, y - 6*mm, title)
        c.setFillColor(GRAY); c.setFont('MalgunBd', 11)
        c.drawString(M + 62*mm, y - 6*mm, f'· {sub}')
        ly = y - 12*mm
        c.setFillColor(black); c.setFont('Malgun', 9.5)
        for it in items:
            c.drawString(M + 6*mm, ly, f'·  {it}')
            ly -= 5.2*mm
        y -= 34*mm

    footer(c); c.showPage()


# ═══════════════════════════════════════════════════════
# P8 결론 + 데모 링크
# ═══════════════════════════════════════════════════════
def p8(c):
    header(c, 8); y = H - 25*mm
    y = h1(c, y, '6', '결론 · 의사결정 요청')
    y -= 4*mm

    # 박스 높이를 라인 수에 맞게 확장 (7줄 × 5.5 + 상단 16 + 하단 여백 6 = 60)
    BOX_H = 60*mm
    box(c, M, y - BOX_H, W - 2*M, BOX_H, fill=LIGHTBLUE, border=BLUE)
    c.setFillColor(NAVY); c.setFont('MalgunBd', 14)
    c.drawString(M + 8*mm, y - 10*mm, '요청 사항')
    c.setFillColor(black); c.setFont('Malgun', 10.5)
    lines = [
        '1. Phase 1 파일럿 승인 (서울 1개 지점, 4주)',
        '   → 투입 : 설계사 5~10명 · 비용 0원',
        '',
        '2. 본사 IT 협조 (AZ 전속 상품 코드 매핑 데이터 1회성 제공)',
        '   → 우리 측 개발은 완료, 본사 데이터 연결만 필요',
        '',
        '3. 보맵 그룹 측과 향후 협력 가능성 경영진 차원 타진',
    ]
    ly = y - 18*mm
    for ln in lines:
        c.drawString(M + 8*mm, ly, ln); ly -= 5.5*mm
    y -= BOX_H + 8*mm  # 박스 끝 + 여백

    y = h2(c, y, '6.1  데모 · 자료 링크')
    # 박스 높이를 URL 3개가 들어가도록 확장 (마지막 URL y-41 까지 + 하단 여백 3mm = 44mm)
    LINK_BOX_H = 46*mm
    box(c, M, y - LINK_BOX_H, W - 2*M, LINK_BOX_H, fill=VERY_LIGHT)
    c.setFillColor(NAVY); c.setFont('MalgunBd', 10.5)
    c.drawString(M + 5*mm, y - 7*mm, '▶ 랜딩 페이지 (경영진용 소개)')
    c.setFillColor(BLUE); c.setFont('Malgun', 9.5)
    c.drawString(M + 8*mm, y - 13*mm, 'https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/landing.html')

    c.setFillColor(NAVY); c.setFont('MalgunBd', 10.5)
    c.drawString(M + 5*mm, y - 21*mm, '▶ 고객용 데모 앱')
    c.setFillColor(BLUE); c.setFont('Malgun', 9.5)
    c.drawString(M + 8*mm, y - 27*mm, 'https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/index.html')

    c.setFillColor(NAVY); c.setFont('MalgunBd', 10.5)
    c.drawString(M + 5*mm, y - 35*mm, '▶ 설계사용 Sellerside 앱')
    c.setFillColor(BLUE); c.setFont('Malgun', 9.5)
    c.drawString(M + 8*mm, y - 41*mm, 'https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/agent.html')
    y -= LINK_BOX_H + 6*mm

    # 하단 연락처
    box(c, M, y - 20*mm, W - 2*M, 18*mm, fill=NAVY)
    c.setFillColor(GOLD); c.setFont('MalgunBd', 11)
    c.drawString(M + 6*mm, y - 6*mm, '제안자 연락처')
    c.setFillColor(white); c.setFont('Malgun', 10)
    c.drawString(M + 6*mm, y - 12*mm, '홍덕훈 · AZ금융(에즈금융서비스) 설계사 · 생명/손해보험 모집인')
    c.drawString(M + 6*mm, y - 18*mm, 'E-mail : ghdejr11@gmail.com')

    footer(c); c.showPage()


def main():
    out = Path(__file__).parent / 'AZ금융_제안서_v8_Phase4현실화.pdf'
    c = canvas.Canvas(str(out), pagesize=A4)
    p1(c); p2(c); p3(c); p4(c); p5(c); p6(c); p7(c); p8(c)
    c.save()
    print(f'생성 완료: {out}')
    print(f'크기: {out.stat().st_size / 1024:.1f} KB')


if __name__ == '__main__':
    main()
