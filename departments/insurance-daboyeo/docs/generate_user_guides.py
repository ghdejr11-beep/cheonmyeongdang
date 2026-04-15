#!/usr/bin/env python3
"""
보험다보여 앱 사용자 가이드 PDF 생성기
- 고객용 가이드 (고객에게 배포)
- 설계사용 가이드 (AZ금융 설계사에게 배포)
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color, black, white
from pathlib import Path
import datetime

pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBd', 'C:/Windows/Fonts/malgunbd.ttf'))

W, H = A4
M = 22 * mm

# 고객용 색상 (블루 계열 - 신뢰)
C_NAVY = HexColor('#1e3a5f')
C_BLUE = HexColor('#2563eb')
C_LIGHT = HexColor('#dbeafe')

# 설계사용 색상 (퍼플 계열 - 프로페셔널)
A_PURPLE = HexColor('#7c3aed')
A_DARK = HexColor('#4c1d95')
A_LIGHT = HexColor('#ede9fe')

# 공통
GRAY = HexColor('#4a5568')
LIGHT_GRAY = HexColor('#cbd5e0')
VERY_LIGHT = HexColor('#f7fafc')
GREEN = HexColor('#047857')
AMBER = HexColor('#b45309')
RED = HexColor('#b91c1c')
GOLD = HexColor('#c9a84c')


# ═══════════════════════════════════════════════════════
# 공통 유틸
# ═══════════════════════════════════════════════════════

def draw_header(c, page_num, total_pages, title, color):
    c.setFont('MalgunBd', 9)
    c.setFillColor(color)
    c.drawString(M, H - 14*mm, title)
    c.setFillColor(GRAY)
    c.setFont('Malgun', 9)
    c.drawRightString(W - M, H - 14*mm, f'{page_num} / {total_pages}')
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.4)
    c.line(M, H - 17*mm, W - M, H - 17*mm)


def draw_footer(c, subtitle):
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.4)
    c.line(M, 15*mm, W - M, 15*mm)
    c.setFont('Malgun', 8)
    c.setFillColor(GRAY)
    c.drawString(M, 10*mm, subtitle)
    c.drawRightString(W - M, 10*mm, datetime.datetime.now().strftime('%Y-%m-%d'))


def draw_box(c, x, y, w, h, color=VERY_LIGHT, border=LIGHT_GRAY, radius=3, line_width=0.8):
    c.setFillColor(color)
    c.setStrokeColor(border)
    c.setLineWidth(line_width)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)


def draw_h1(c, y, number, text, main_color):
    c.setFillColor(main_color)
    c.setFont('MalgunBd', 17)
    c.drawString(M, y, f'{number}. {text}')
    c.setStrokeColor(main_color)
    c.setLineWidth(2)
    c.line(M, y - 3*mm, M + 55*mm, y - 3*mm)
    return y - 11*mm


def draw_h2(c, y, text, color):
    c.setFillColor(color)
    c.setFont('MalgunBd', 12)
    c.drawString(M, y, f'■ {text}')
    return y - 7*mm


def draw_bullet(c, y, items, indent=5*mm, color=black, size=10):
    c.setFillColor(color)
    c.setFont('Malgun', size)
    for item in items:
        c.drawString(M + indent, y, '·')
        c.drawString(M + indent + 4*mm, y, item)
        y -= 5.8*mm
    return y


def draw_numbered(c, y, items, indent=5*mm, color=black, size=10):
    c.setFillColor(color)
    c.setFont('Malgun', size)
    for i, item in enumerate(items, 1):
        c.setFont('MalgunBd', size)
        c.drawString(M + indent, y, f'{i}.')
        c.setFont('Malgun', size)
        c.drawString(M + indent + 7*mm, y, item)
        y -= 5.8*mm
    return y


def draw_step(c, y, num, title, desc, color):
    """단계별 설명 박스"""
    # 원형 번호
    c.setFillColor(color)
    c.circle(M + 6*mm, y - 4*mm, 5*mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('MalgunBd', 12)
    c.drawCentredString(M + 6*mm, y - 6*mm, str(num))

    # 제목
    c.setFillColor(color)
    c.setFont('MalgunBd', 12)
    c.drawString(M + 16*mm, y - 3*mm, title)

    # 설명
    c.setFillColor(black)
    c.setFont('Malgun', 10)
    lines = desc.split('\n')
    ly = y - 10*mm
    for line in lines:
        c.drawString(M + 16*mm, ly, line)
        ly -= 5.2*mm

    return ly - 4*mm


# ═══════════════════════════════════════════════════════
# 고객용 가이드 PDF
# ═══════════════════════════════════════════════════════

def customer_page1_cover(c):
    """고객용 표지"""
    c.setFillColor(C_NAVY)
    c.rect(0, H - 100*mm, W, 100*mm, fill=1, stroke=0)

    c.setFillColor(GOLD)
    c.rect(W/2 - 35*mm, H - 55*mm, 70*mm, 1, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont('MalgunBd', 38)
    c.drawCentredString(W/2, H - 48*mm, '보 험 다 보 여')

    c.setFillColor(C_LIGHT)
    c.setFont('Malgun', 13)
    c.drawCentredString(W/2, H - 63*mm, '내 보험을 한눈에 · 담당 설계사 1:1 연결')

    c.setFillColor(GOLD)
    c.setFont('MalgunBd', 20)
    c.drawCentredString(W/2, H - 85*mm, '고객 사용 가이드')

    # 중앙 박스
    box_y = H/2 - 60*mm
    draw_box(c, M, box_y, W - 2*M, 75*mm, color=C_LIGHT)

    c.setFont('MalgunBd', 13)
    c.setFillColor(C_NAVY)
    c.drawString(M + 10*mm, box_y + 63*mm, '[ 보험다보여란? ]')

    c.setFont('Malgun', 10.5)
    c.setFillColor(black)
    lines = [
        '여러 보험에 가입하셨나요?',
        '어떤 보장이 중복되는지, 부족한 부분이 뭔지 헷갈리시나요?',
        '',
        '보험다보여는 38개 보험사 정보를 한 곳에 모아',
        '내 보험 현황을 명확하게 보여주는 서비스입니다.',
        '',
        '앱 설치 필요 없이 링크만 있으면 바로 사용 가능하며,',
        '모든 기능이 무료이고 수수료가 없습니다.',
    ]
    ly = box_y + 53*mm
    for line in lines:
        c.drawString(M + 10*mm, ly, line)
        ly -= 6*mm

    c.setFont('Malgun', 10.5)
    c.setFillColor(GRAY)
    footer_y = 38*mm
    c.drawCentredString(W/2, footer_y + 18*mm, '─────────────────────────')
    c.setFont('MalgunBd', 11)
    c.setFillColor(C_NAVY)
    c.drawCentredString(W/2, footer_y + 12*mm, '『 보험이 복잡해지지 않도록 』')
    c.setFont('Malgun', 10)
    c.setFillColor(GRAY)
    c.drawCentredString(W/2, footer_y + 5*mm, '담당 설계사가 끝까지 책임지고 관리합니다')
    c.drawCentredString(W/2, footer_y - 3*mm, f'버전 1.0  ·  {datetime.datetime.now().strftime("%Y년 %m월")}')

    c.showPage()


def customer_page2_features(c):
    """고객용 주요 기능"""
    draw_header(c, 2, 5, '보험다보여 고객 사용 가이드', C_NAVY)
    y = H - 28*mm

    y = draw_h1(c, y, '1', '무엇을 할 수 있나요?', C_NAVY)
    y -= 2*mm

    features = [
        ('🏠', '내 보험 현황', '가입된 모든 보험을 한눈에 확인', '가입 보험 · 월 납입료 · 갱신 예정일을 자동으로 정리'),
        ('🛡️', '보장 분석', '중복 보장 · 부족한 보장을 자동 분석', '예: 암 진단비가 2곳에서 중복 → 월 절약 가능액 제시'),
        ('⚖️', '보험사 비교', '38개 보험사 상품을 나란히 비교', '보험료 · 보장 범위 · 갱신 주기를 한 화면에'),
        ('🧮', '보험료 계산기', '가상 시뮬레이션으로 미리 계산', '나이 · 성별 · 조건 입력 → 예상 보험료 즉시 확인'),
        ('📋', '청구 서류 안내', '청구에 필요한 서류를 상황별로 안내', '통원 · 입원 · 수술 등 8가지 케이스별 필요서류 리스트'),
        ('👔', '담당 설계사', '궁금한 점은 바로 연결', '전화 · 문자 · 카카오톡으로 담당 설계사와 1:1 상담'),
    ]

    for icon, title, desc, detail in features:
        # 카드 박스
        draw_box(c, M, y - 24*mm, W - 2*M, 22*mm, color=VERY_LIGHT, line_width=0.6)

        # 아이콘 (이모지 대신 색 박스)
        c.setFillColor(C_BLUE)
        c.roundRect(M + 4*mm, y - 18*mm, 14*mm, 14*mm, 3, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont('MalgunBd', 14)
        c.drawCentredString(M + 11*mm, y - 10*mm, title[:2])

        # 제목
        c.setFillColor(C_NAVY)
        c.setFont('MalgunBd', 12)
        c.drawString(M + 22*mm, y - 7*mm, title)

        # 설명
        c.setFillColor(black)
        c.setFont('Malgun', 10)
        c.drawString(M + 22*mm, y - 13*mm, desc)
        c.setFillColor(GRAY)
        c.setFont('Malgun', 9)
        c.drawString(M + 22*mm, y - 19*mm, detail)

        y -= 26*mm

    draw_footer(c, '고객 사용 가이드')
    c.showPage()


def customer_page3_howto(c):
    """사용 방법"""
    draw_header(c, 3, 5, '보험다보여 고객 사용 가이드', C_NAVY)
    y = H - 28*mm

    y = draw_h1(c, y, '2', '어떻게 시작하나요?', C_NAVY)
    y -= 2*mm

    y = draw_h2(c, y, '2.1  3단계로 시작하기', C_BLUE)

    y = draw_step(c, y, 1, '담당 설계사에게 받은 링크로 접속',
        '카카오톡 · 문자로 받은 링크를 클릭하면 됩니다.\n앱 설치 필요 없이 웹브라우저에서 바로 실행됩니다.', C_BLUE)

    y = draw_step(c, y, 2, '상단에 담당 설계사가 자동으로 표시됩니다',
        '『홍길동 설계사 · 강남지점 · 010-1234-5678』 형태로\n화면 상단에 항상 고정 표시되어 바로 연결 가능합니다.', C_BLUE)

    y = draw_step(c, y, 3, '원하는 메뉴를 선택하여 사용',
        '좌측 메뉴에서 내 보험 현황 · 보장 분석 · 청구 안내 등\n원하는 기능을 선택하여 바로 사용하실 수 있습니다.', C_BLUE)

    y -= 3*mm
    y = draw_h2(c, y, '2.2  담당 설계사에게 문의하는 방법', C_BLUE)

    draw_box(c, M, y - 36*mm, W - 2*M, 34*mm, color=C_LIGHT)
    c.setFont('MalgunBd', 11)
    c.setFillColor(C_NAVY)
    c.drawString(M + 6*mm, y - 7*mm, '화면 상단 『담당 설계사』 배너에서 선택')

    methods = [
        '전화 — 『📞 전화』 버튼 → 담당 설계사에게 바로 전화 연결',
        '문자 — 『💬 문자』 버튼 → 기본 메시지 자동 입력',
        '메뉴 — 좌측 『설계사 연결』 → 상담 내용 상세 입력',
    ]
    c.setFont('Malgun', 10)
    c.setFillColor(black)
    ly = y - 14*mm
    for m in methods:
        c.drawString(M + 6*mm, ly, '·')
        c.drawString(M + 10*mm, ly, m)
        ly -= 6*mm

    draw_footer(c, '고객 사용 가이드')
    c.showPage()


def customer_page4_claim(c):
    """청구 서류 안내 사용법"""
    draw_header(c, 4, 5, '보험다보여 고객 사용 가이드', C_NAVY)
    y = H - 28*mm

    y = draw_h1(c, y, '3', '보험금 청구 서류 안내 사용법', C_NAVY)
    y -= 2*mm

    y = draw_h2(c, y, '3.1  간단한 3단계', C_BLUE)

    y = draw_step(c, y, 1, '『보험금 청구』 메뉴 클릭',
        '좌측 메뉴에서 『📋 보험금 청구』를 선택합니다.', C_BLUE)

    y = draw_step(c, y, 2, '내 상황을 선택합니다',
        '통원 · 입원 · 수술 · 응급실 · 암 진단 · 교통사고 · 골절 · 뇌/심장\n8가지 상황 중 해당되는 것을 선택하세요.', C_BLUE)

    y = draw_step(c, y, 3, '필요한 서류와 청구 방법 확인',
        '청구 가능한 보험 · 필요 서류 · 예상 지급 범위를 확인합니다.\n실손24 바로가기 · 각 보험사 청구 페이지 링크도 제공됩니다.', C_BLUE)

    y -= 3*mm
    y = draw_h2(c, y, '3.2  실손24 앱 연동 (정부 공식)', C_BLUE)
    draw_box(c, M, y - 30*mm, W - 2*M, 28*mm, color=VERY_LIGHT, border=GREEN)
    c.setFont('MalgunBd', 11)
    c.setFillColor(GREEN)
    c.drawString(M + 6*mm, y - 7*mm, '실손보험 청구는 실손24 앱이 가장 편리합니다')
    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    c.drawString(M + 6*mm, y - 14*mm, '2024년 10월부터 정부(보험개발원)가 운영하는 실손24 앱을 통해')
    c.drawString(M + 6*mm, y - 20*mm, '병원에서 보험사로 서류를 전자 전송할 수 있습니다.')
    c.drawString(M + 6*mm, y - 26*mm, '앱 내 『실손24 바로가기』 버튼을 누르면 자동 연결됩니다.')

    draw_footer(c, '고객 사용 가이드')
    c.showPage()


def customer_page5_faq(c):
    """자주 묻는 질문 + 안내"""
    draw_header(c, 5, 5, '보험다보여 고객 사용 가이드', C_NAVY)
    y = H - 28*mm

    y = draw_h1(c, y, '4', '자주 묻는 질문 (FAQ)', C_NAVY)
    y -= 2*mm

    faqs = [
        ('Q. 서비스 비용이 있나요?',
         'A. 완전 무료입니다. 수수료 · 광고 · 결제 일체 없습니다.'),
        ('Q. 제 정보는 안전한가요?',
         'A. 모든 통신은 SSL 암호화되며, 민감 정보는 서버에 저장되지 않습니다.'),
        ('Q. 앱을 설치해야 하나요?',
         'A. 아니요. 링크만 있으면 브라우저에서 바로 사용 가능합니다.'),
        ('Q. 담당 설계사가 누군지 어떻게 확인하나요?',
         'A. 화면 상단 배너에서 이름 · 사번 · 지점 · 연락처를 확인할 수 있습니다.'),
        ('Q. 다른 보험사 상품도 가입할 수 있나요?',
         'A. 담당 설계사에게 문의하시면 AZ금융 계약 38개 보험사 상품을 안내받을 수 있습니다.'),
        ('Q. 실손24와 이 앱의 차이는 무엇인가요?',
         'A. 실손24는 정부 실손보험 청구 앱, 본 앱은 내 보험 전체를 통합 관리하는 도구입니다.'),
    ]

    for q, a in faqs:
        draw_box(c, M, y - 16*mm, W - 2*M, 14*mm, color=VERY_LIGHT, line_width=0.6)
        c.setFont('MalgunBd', 10)
        c.setFillColor(C_NAVY)
        c.drawString(M + 6*mm, y - 5*mm, q)
        c.setFont('Malgun', 9.5)
        c.setFillColor(black)
        c.drawString(M + 6*mm, y - 12*mm, a)
        y -= 18*mm

    y -= 4*mm
    # 안내사항
    draw_box(c, M, y - 28*mm, W - 2*M, 26*mm, color=HexColor('#fef3c7'), border=GOLD)
    c.setFont('MalgunBd', 11)
    c.setFillColor(C_NAVY)
    c.drawString(M + 6*mm, y - 7*mm, '[ 중요 안내 ]')
    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    notes = [
        '본 서비스는 청구 대행이 아닌 정보 안내 · 관리 도구입니다.',
        '실제 보험 청구는 가입자 본인이 보험사에 직접 신청해야 합니다.',
        '보장 분석 · 추천 결과는 참고 자료이며 전문 상담이 필요할 수 있습니다.',
    ]
    ly = y - 13*mm
    for n in notes:
        c.drawString(M + 6*mm, ly, '·')
        c.drawString(M + 10*mm, ly, n)
        ly -= 5.5*mm

    draw_footer(c, '고객 사용 가이드')
    c.showPage()


def generate_customer_guide():
    output = Path(__file__).parent / '보험다보여_고객_사용가이드.pdf'
    c = canvas.Canvas(str(output), pagesize=A4)
    customer_page1_cover(c)
    customer_page2_features(c)
    customer_page3_howto(c)
    customer_page4_claim(c)
    customer_page5_faq(c)
    c.save()
    return output


# ═══════════════════════════════════════════════════════
# 설계사용 가이드 PDF
# ═══════════════════════════════════════════════════════

def agent_page1_cover(c):
    """설계사용 표지"""
    c.setFillColor(A_DARK)
    c.rect(0, H - 100*mm, W, 100*mm, fill=1, stroke=0)

    c.setFillColor(GOLD)
    c.rect(W/2 - 35*mm, H - 55*mm, 70*mm, 1, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont('MalgunBd', 32)
    c.drawCentredString(W/2, H - 48*mm, '보험다보여 SELLERSIDE')

    c.setFillColor(A_LIGHT)
    c.setFont('Malgun', 13)
    c.drawCentredString(W/2, H - 63*mm, 'AZ금융 설계사 전용 고객 관리 도구')

    c.setFillColor(GOLD)
    c.setFont('MalgunBd', 20)
    c.drawCentredString(W/2, H - 85*mm, '설계사 사용 가이드')

    box_y = H/2 - 60*mm
    draw_box(c, M, box_y, W - 2*M, 75*mm, color=A_LIGHT)

    c.setFont('MalgunBd', 13)
    c.setFillColor(A_DARK)
    c.drawString(M + 10*mm, box_y + 63*mm, '[ 설계사님께 ]')

    c.setFont('Malgun', 10.5)
    c.setFillColor(black)
    lines = [
        '본 도구는 AZ금융 소속 설계사가 담당 고객을',
        '효율적으로 관리하기 위한 B2B 전용 도구입니다.',
        '',
        '1. 사번을 입력하여 본인 프로필을 설정하고',
        '2. 본인 전용 고객용 링크를 생성하여',
        '3. 담당 고객에게 카톡 · 문자 · 명함 QR로 공유하면',
        '4. 고객이 링크로 접속 시 본인이 자동으로 담당 설계사로 표시됩니다.',
        '',
        '보맵(B2C 대중 서비스)과 상호 보완 관계입니다.',
    ]
    ly = box_y + 53*mm
    for line in lines:
        c.drawString(M + 10*mm, ly, line)
        ly -= 6*mm

    c.setFont('Malgun', 10.5)
    c.setFillColor(GRAY)
    footer_y = 38*mm
    c.drawCentredString(W/2, footer_y + 18*mm, '─────────────────────────')
    c.setFont('MalgunBd', 11)
    c.setFillColor(A_DARK)
    c.drawCentredString(W/2, footer_y + 12*mm, '『 고객에게 먼저 다가가는 설계사가 됩니다 』')
    c.setFont('Malgun', 10)
    c.setFillColor(GRAY)
    c.drawCentredString(W/2, footer_y + 5*mm, '영업 효율 × 고객 신뢰 동시 확보')
    c.drawCentredString(W/2, footer_y - 3*mm, f'버전 1.0  ·  {datetime.datetime.now().strftime("%Y년 %m월")}')

    c.showPage()


def agent_page2_setup(c):
    """설계사용 초기 설정"""
    draw_header(c, 2, 6, '보험다보여 Sellerside 설계사 사용 가이드', A_DARK)
    y = H - 28*mm

    y = draw_h1(c, y, '1', '첫 시작 — 프로필 설정', A_DARK)
    y -= 2*mm

    y = draw_h2(c, y, '1.1  프로필 입력 항목', A_PURPLE)
    y = draw_bullet(c, y, [
        '사번 (설계사 코드) — 필수',
        '이름 — 필수',
        '연락처 — 필수 (고객이 전화/문자 시 연결됨)',
        '이메일 — 선택',
        '소속 지점 — 선택 (예: 서울 강남지점)',
        '카카오톡 ID — 선택',
        '자격증 및 소개 — 선택 (예: 10년 경력 · 연 500건 상담)',
    ])
    y -= 3*mm

    y = draw_h2(c, y, '1.2  설정 방법', A_PURPLE)

    y = draw_step(c, y, 1, '설계사용 앱 접속',
        '『설계사용 URL』로 접속합니다.\n웹브라우저에서 바로 열 수 있으며 앱 설치 불필요.', A_PURPLE)

    y = draw_step(c, y, 2, '좌측 메뉴 → 『내 프로필 설정』',
        '좌측 사이드바에서 『내 프로필 설정』을 클릭합니다.', A_PURPLE)

    y = draw_step(c, y, 3, '정보 입력 후 『저장하기』',
        '필수 항목을 입력하고 저장하면 사이드바에\n본인 이름과 사번이 자동으로 표시됩니다.', A_PURPLE)

    draw_footer(c, '설계사 사용 가이드')
    c.showPage()


def agent_page3_sharelink(c):
    """고객 링크 생성/공유"""
    draw_header(c, 3, 6, '보험다보여 Sellerside 설계사 사용 가이드', A_DARK)
    y = H - 28*mm

    y = draw_h1(c, y, '2', '본인 전용 고객 링크 생성/공유', A_DARK)
    y -= 2*mm

    y = draw_h2(c, y, '2.1  링크 생성 방법', A_PURPLE)

    y = draw_step(c, y, 1, '좌측 메뉴 → 『고객 링크 공유』',
        '프로필 설정 완료 후 『고객 링크 공유』 메뉴 접근.', A_PURPLE)

    y = draw_step(c, y, 2, '자동 생성된 링크 확인',
        '본인 프로필이 암호화되어 포함된 URL이 자동 생성됩니다.\n예: .../index.html?a=<encoded_profile>', A_PURPLE)

    y = draw_step(c, y, 3, '공유 방법 선택',
        '『링크 복사』 · 『카카오톡 공유』 · 『문자 공유』 · QR 코드', A_PURPLE)

    y -= 3*mm
    y = draw_h2(c, y, '2.2  공유 채널별 활용법', A_PURPLE)

    channels = [
        ('카카오톡', '담당 고객 단체방 · 개별 채팅에 링크 공유'),
        ('문자', '신규 고객 · 장년층 고객에게 문자로 전송'),
        ('QR 코드', '명함 뒷면 · 매장 입구에 부착 → 스캔 시 바로 연결'),
        ('이메일', '서명에 링크 포함 → 자연스러운 노출'),
        ('대면', '고객 미팅 시 QR 코드 스캔 요청 → 현장 연결'),
    ]

    # 테이블
    draw_box(c, M, y - 4*mm, W - 2*M, 6*mm, color=A_DARK, border=A_DARK)
    c.setFont('MalgunBd', 9.5)
    c.setFillColor(white)
    c.drawString(M + 6*mm, y - 1.5*mm, '채널')
    c.drawString(M + 40*mm, y - 1.5*mm, '활용 방법')
    y -= 7*mm

    c.setFont('Malgun', 9.5)
    for i, (ch, desc) in enumerate(channels):
        bg = VERY_LIGHT if i % 2 == 0 else white
        c.setFillColor(bg)
        c.rect(M, y - 4*mm, W - 2*M, 5.5*mm, fill=1, stroke=0)
        c.setFillColor(black)
        c.setFont('MalgunBd', 9.5)
        c.drawString(M + 6*mm, y - 1.5*mm, ch)
        c.setFont('Malgun', 9)
        c.drawString(M + 40*mm, y - 1.5*mm, desc)
        y -= 5.5*mm

    y -= 5*mm
    # 팁
    draw_box(c, M, y - 22*mm, W - 2*M, 20*mm, color=HexColor('#fef3c7'), border=GOLD)
    c.setFont('MalgunBd', 11)
    c.setFillColor(A_DARK)
    c.drawString(M + 6*mm, y - 7*mm, '[ 활용 팁 ]')
    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    c.drawString(M + 6*mm, y - 13*mm, '· 고객이 링크로 접속 시 자동으로 본인이 담당 설계사로 표시됩니다.')
    c.drawString(M + 6*mm, y - 19*mm, '· 대중 광고 · 앱스토어 공개 금지 (1:1 고객 관리용)')

    draw_footer(c, '설계사 사용 가이드')
    c.showPage()


def agent_page4_dashboard(c):
    """고객 관리 대시보드"""
    draw_header(c, 4, 6, '보험다보여 Sellerside 설계사 사용 가이드', A_DARK)
    y = H - 28*mm

    y = draw_h1(c, y, '3', '고객 관리 대시보드', A_DARK)
    y -= 2*mm

    y = draw_h2(c, y, '3.1  대시보드 주요 지표', A_PURPLE)
    y = draw_bullet(c, y, [
        '총 관리 고객 수 · 활성 고객 수',
        '이번 달 전체 보험료 합계',
        '중복 보장 고객 수 (정리 대상)',
        '보장 공백 고객 수 (추가 가입 제안 대상)',
        '갱신 예정 고객 수 (재계약 기회)',
    ])
    y -= 3*mm

    y = draw_h2(c, y, '3.2  고객별 보장 분석', A_PURPLE)
    y = draw_bullet(c, y, [
        '좌측 메뉴 『내 고객 관리』로 이동',
        '고객 카드 클릭 시 상세 보장 현황 팝업',
        '중복 보장 · 보장 공백 자동 하이라이트',
        '리스크 점수로 우선 상담 대상 식별',
    ])
    y -= 3*mm

    y = draw_h2(c, y, '3.3  권장 활용 시나리오', A_PURPLE)
    scenarios = [
        ('갱신 예정 고객 대응',
         '매월 1일 대시보드 확인 → 갱신 예정 고객 리스트업 → 사전 연락'),
        ('중복 보장 정리 제안',
         '중복 보장 감지 알림 → 고객에게 구조조정 제안 → 절약분 재투자 유도'),
        ('보장 공백 보완 영업',
         '공백 영역 자동 탐지 → 맞춤 상품 제안 → 추가 가입 유도'),
        ('청구 지원',
         '고객 청구 문의 → 청구 서류 안내 DB 활용 → 신속 응대'),
    ]

    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    for scenario, desc in scenarios:
        c.setFont('MalgunBd', 10)
        c.setFillColor(A_DARK)
        c.drawString(M + 4*mm, y, '◆ ' + scenario)
        c.setFont('Malgun', 9.5)
        c.setFillColor(black)
        c.drawString(M + 4*mm, y - 5*mm, '   → ' + desc)
        y -= 11*mm

    draw_footer(c, '설계사 사용 가이드')
    c.showPage()


def agent_page5_claim(c):
    """청구 서류 안내 기능"""
    draw_header(c, 5, 6, '보험다보여 Sellerside 설계사 사용 가이드', A_DARK)
    y = H - 28*mm

    y = draw_h1(c, y, '4', '청구 서류 안내 DB 활용', A_DARK)
    y -= 2*mm

    y = draw_h2(c, y, '4.1  8가지 상황별 즉시 참조', A_PURPLE)
    y = draw_bullet(c, y, [
        '통원 · 입원 · 수술 · 응급실 · 암 · 교통사고 · 골절 · 뇌/심장',
        '각 상황별 필요 서류 · 예상 지급 범위 · 청구 경로 즉시 확인',
        '고객 문의 시 통화 중 실시간 참조 가능',
    ])
    y -= 3*mm

    y = draw_h2(c, y, '4.2  복잡 케이스 체크리스트', A_PURPLE)
    draw_box(c, M, y - 55*mm, W - 2*M, 53*mm, color=A_LIGHT)
    c.setFont('MalgunBd', 10)
    c.setFillColor(A_DARK)
    c.drawString(M + 6*mm, y - 7*mm, '다음 사항을 고객 상담 시 반드시 확인하세요')
    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    checks = [
        '중복 보장 확인 (실손 중복 불가 · 상해/질병은 중복 가능)',
        '자손보험 vs 실손보험 청구 순서 (자손 먼저)',
        '암 조직검사 결과 코드 (C00~C97 · D00~D48)',
        '뇌/심장 질환 코드 (I60~I69 뇌 · I20~I25 심장)',
        '후유장해 진단 시점 (치료 종결 6개월 이후)',
        '청구 소멸시효 (3년 이내)',
        '약관상 대기기간 (암보험 90일 등)',
        '고지의무 위반 여부 (가입 2년 이내 특히 주의)',
    ]
    ly = y - 14*mm
    for chk in checks:
        c.drawString(M + 6*mm, ly, '□')
        c.drawString(M + 12*mm, ly, chk)
        ly -= 5.5*mm

    y -= 60*mm

    # 주의
    draw_box(c, M, y - 20*mm, W - 2*M, 18*mm, color=HexColor('#fef2f2'), border=RED)
    c.setFont('MalgunBd', 10)
    c.setFillColor(RED)
    c.drawString(M + 6*mm, y - 7*mm, '[ 주의 ]')
    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    c.drawString(M + 6*mm, y - 13*mm, '본 기능은 설계사 참고용이며, 실제 청구는 고객이 보험사에 직접 신청합니다.')
    c.drawString(M + 6*mm, y - 18*mm, '청구 대행은 손해사정사 자격이 필요하므로 엄격히 배제됩니다.')

    draw_footer(c, '설계사 사용 가이드')
    c.showPage()


def agent_page6_tips(c):
    """영업 팁 + 자주 묻는 질문"""
    draw_header(c, 6, 6, '보험다보여 Sellerside 설계사 사용 가이드', A_DARK)
    y = H - 28*mm

    y = draw_h1(c, y, '5', '영업 활용 팁 & FAQ', A_DARK)
    y -= 2*mm

    y = draw_h2(c, y, '5.1  매출 증대 활용법', A_PURPLE)
    tips = [
        '첫 상담 시 링크 전달 → 고객이 24시간 내 접속할 확률 80%+',
        '고객의 보장 공백 분석 결과를 캡처 → 상담 자료로 활용',
        '월 1회 『보험 리뷰 알림』 발송 → 자연스러운 재접촉',
        '갱신 예정일 1개월 전 자동 알림 → 재계약률 30% 상승 가능',
        '청구 문의 시 즉답률 상승 → 고객 충성도 향상',
    ]
    y = draw_numbered(c, y, tips)
    y -= 3*mm

    y = draw_h2(c, y, '5.2  자주 묻는 질문', A_PURPLE)

    faqs = [
        ('Q. 다른 설계사가 내 링크를 복사해서 쓰면?',
         'A. 링크에 본인 프로필이 암호화되어 고정되므로 무관합니다.'),
        ('Q. 고객이 다른 링크로도 들어갈 수 있나요?',
         'A. 마지막으로 접속한 링크의 설계사가 담당으로 저장됩니다.'),
        ('Q. 회사 승인 없이 운영해도 되나요?',
         'A. 회사 승인 전에는 본인 담당 고객 1:1 용도로만 사용 권장.'),
        ('Q. 앱인토스 · 앱스토어에 올라가나요?',
         'A. 현재는 웹 기반. 회사 승인 후 앱인토스 배포 예정.'),
        ('Q. 데이터는 어디에 저장되나요?',
         'A. 사용자 디바이스(localStorage)에만 저장. 서버 저장 없음.'),
    ]

    for q, a in faqs:
        draw_box(c, M, y - 16*mm, W - 2*M, 14*mm, color=VERY_LIGHT, line_width=0.6)
        c.setFont('MalgunBd', 10)
        c.setFillColor(A_DARK)
        c.drawString(M + 6*mm, y - 5*mm, q)
        c.setFont('Malgun', 9.5)
        c.setFillColor(black)
        c.drawString(M + 6*mm, y - 12*mm, a)
        y -= 18*mm

    draw_footer(c, '설계사 사용 가이드')
    c.showPage()


def generate_agent_guide():
    output = Path(__file__).parent / '보험다보여Sellerside_설계사_사용가이드.pdf'
    c = canvas.Canvas(str(output), pagesize=A4)
    agent_page1_cover(c)
    agent_page2_setup(c)
    agent_page3_sharelink(c)
    agent_page4_dashboard(c)
    agent_page5_claim(c)
    agent_page6_tips(c)
    c.save()
    return output


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    customer = generate_customer_guide()
    agent = generate_agent_guide()

    print('[OK] 2개 PDF 생성 완료')
    print(f'  1) 고객용 가이드: {customer.name}')
    print(f'     - 크기: {customer.stat().st_size / 1024:.1f} KB · 5쪽')
    print(f'  2) 설계사용 가이드: {agent.name}')
    print(f'     - 크기: {agent.stat().st_size / 1024:.1f} KB · 6쪽')


if __name__ == '__main__':
    main()
