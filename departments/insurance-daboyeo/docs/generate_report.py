#!/usr/bin/env python3
"""
보험다보여 서비스 소개 및 GADP 승인 요청 PDF 생성기
대상: GADP 소속 상관/검토자
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color, black, white
from pathlib import Path
import datetime

# 한글 폰트 등록
pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBd', 'C:/Windows/Fonts/malgunbd.ttf'))

W, H = A4
M = 20 * mm  # 마진

# 색상
NAVY = HexColor('#1a365d')
BLUE = HexColor('#2563eb')
GRAY = HexColor('#4a5568')
LIGHT_GRAY = HexColor('#e2e8f0')
GREEN = HexColor('#059669')
AMBER = HexColor('#d97706')
RED = HexColor('#dc2626')
BG_LIGHT = HexColor('#f7fafc')


def draw_header(c, page_num, total_pages):
    """헤더 + 페이지 번호"""
    c.setFont('MalgunBd', 10)
    c.setFillColor(NAVY)
    c.drawString(M, H - 15*mm, '보험다보여 서비스 소개 및 승인 요청')
    c.setFillColor(GRAY)
    c.setFont('Malgun', 9)
    c.drawRightString(W - M, H - 15*mm, f'{page_num} / {total_pages}')
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.5)
    c.line(M, H - 17*mm, W - M, H - 17*mm)


def draw_footer(c):
    """푸터"""
    c.setFont('Malgun', 8)
    c.setFillColor(GRAY)
    c.drawString(M, M/2, '쿤스튜디오 | 대표: 홍덕훈 | 사업자등록: 552-59-00848')
    c.drawRightString(W - M, M/2, datetime.datetime.now().strftime('%Y-%m-%d'))


def draw_box(c, x, y, w, h, color=BG_LIGHT, border=LIGHT_GRAY, radius=3):
    c.setFillColor(color)
    c.setStrokeColor(border)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)


def draw_h1(c, y, text, color=NAVY):
    c.setFillColor(color)
    c.setFont('MalgunBd', 18)
    c.drawString(M, y, text)
    c.setStrokeColor(color)
    c.setLineWidth(2)
    c.line(M, y - 3*mm, M + 40*mm, y - 3*mm)
    return y - 10*mm


def draw_h2(c, y, text, color=BLUE):
    c.setFillColor(color)
    c.setFont('MalgunBd', 14)
    c.drawString(M, y, '▎ ' + text)
    return y - 7*mm


def draw_body(c, y, text, size=10, indent=0, color=black):
    """여러 줄 한글 텍스트"""
    c.setFillColor(color)
    c.setFont('Malgun', size)
    lines = text.split('\n')
    for line in lines:
        c.drawString(M + indent, y, line)
        y -= (size + 3)
    return y


def draw_bullet(c, y, items, indent=5*mm, color=black):
    c.setFillColor(color)
    c.setFont('Malgun', 10)
    for item in items:
        c.drawString(M + indent, y, '•')
        c.drawString(M + indent + 4*mm, y, item)
        y -= 5.5*mm
    return y


# ─── 페이지 렌더링 ───
TOTAL_PAGES = 6


def page1_cover(c):
    """표지"""
    # 배경 그라데이션 (상단)
    c.setFillColor(NAVY)
    c.rect(0, H - 90*mm, W, 90*mm, fill=1, stroke=0)

    # 타이틀
    c.setFont('MalgunBd', 36)
    c.setFillColor(white)
    c.drawCentredString(W/2, H - 45*mm, '보험다보여')
    c.setFont('Malgun', 14)
    c.drawCentredString(W/2, H - 55*mm, '고객을 위한 보험 통합 관리 플랫폼')

    # 부제
    c.setFont('MalgunBd', 20)
    c.setFillColor(HexColor('#c9a84c'))
    c.drawCentredString(W/2, H - 75*mm, 'GADP 서비스 승인 요청')

    # 중앙 박스
    box_y = H/2 - 50*mm
    draw_box(c, M, box_y, W - 2*M, 70*mm, color=BG_LIGHT)

    c.setFont('MalgunBd', 14)
    c.setFillColor(NAVY)
    c.drawString(M + 10*mm, box_y + 58*mm, '📋 보고서 개요')

    c.setFont('Malgun', 11)
    c.setFillColor(black)
    lines = [
        '본 문서는 GADP 소속 설계사 홍덕훈이 개인적으로 개발한',
        '보험 정보 통합 관리 서비스 「보험다보여」의 서비스 구조와',
        '법적 검토 사항을 정리한 자료입니다.',
        '',
        '본 서비스 운영 및 공개에 앞서 회사의 검토와 승인을',
        '정식으로 요청드립니다.',
    ]
    ly = box_y + 48*mm
    for line in lines:
        c.drawString(M + 10*mm, ly, line)
        ly -= 6*mm

    # 하단 정보
    c.setFont('Malgun', 11)
    c.setFillColor(GRAY)
    footer_y = 40*mm
    c.drawCentredString(W/2, footer_y + 12*mm, '작성자: 홍덕훈 (쿤스튜디오 대표 / GADP 소속 설계사)')
    c.drawCentredString(W/2, footer_y + 6*mm, '자격증: 생명보험 · 손해보험 모집인')
    c.drawCentredString(W/2, footer_y, f'작성일: {datetime.datetime.now().strftime("%Y년 %m월 %d일")}')

    c.showPage()


def page2_overview(c):
    """서비스 개요"""
    draw_header(c, 2, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '1. 서비스 개요')
    y -= 3*mm

    y = draw_h2(c, y, '1.1 서비스명 및 목적')
    draw_box(c, M, y - 24*mm, W - 2*M, 22*mm)
    c.setFont('MalgunBd', 11)
    c.setFillColor(NAVY)
    c.drawString(M + 5*mm, y - 6*mm, '서비스명: 보험다보여 (Insurance Dashboard)')
    c.setFont('Malgun', 10)
    c.setFillColor(black)
    c.drawString(M + 5*mm, y - 13*mm, '목적: 고객의 보험 가입 현황을 한눈에 관리하고,')
    c.drawString(M + 5*mm, y - 18*mm, '        보장 공백·중복을 분석하여 합리적 의사결정을 돕는 정보 제공 서비스')
    y -= 30*mm

    y = draw_h2(c, y, '1.2 타겟 고객')
    y = draw_bullet(c, y, [
        '개인 보험 가입자 (20~60대)',
        '자기 보험 상황을 명확히 알고 싶은 사용자',
        '여러 보험사 상품을 한 곳에서 관리하고 싶은 사용자',
        'GADP 소속 설계사의 기존 고객 (설계사가 상담 보조 도구로 활용)',
    ])
    y -= 3*mm

    y = draw_h2(c, y, '1.3 서비스 구성 (2개 버전)')
    draw_box(c, M, y - 38*mm, W - 2*M, 36*mm)
    c.setFont('MalgunBd', 11)
    c.setFillColor(BLUE)
    c.drawString(M + 5*mm, y - 6*mm, '[A] 고객용 (Customer)')
    c.setFont('Malgun', 9)
    c.setFillColor(black)
    c.drawString(M + 5*mm, y - 12*mm, '• 내 보험 현황 · 보장 분석 · 보험사 비교 · 맞춤 추천 · 보험료 계산기')
    c.drawString(M + 5*mm, y - 17*mm, '• 청구 서류 자동 안내 · 갱신 만기 알림 · 설계사 연결')

    c.setFont('MalgunBd', 11)
    c.setFillColor(HexColor('#7c3aed'))
    c.drawString(M + 5*mm, y - 25*mm, '[B] 설계사용 (Agent - 본인 전용)')
    c.setFont('Malgun', 9)
    c.setFillColor(black)
    c.drawString(M + 5*mm, y - 31*mm, '• 고객 관리 대시보드 · 고객별 보장 분석 · 청구 서류 참고 DB')
    c.drawString(M + 5*mm, y - 36*mm, '• 가입 전 건강분석 · 상담 일정 관리')
    y -= 44*mm

    y = draw_h2(c, y, '1.4 주요 기능 7가지')
    features = [
        '1) 38개 보험사 통합 조회 (내보험다보여 API 연동 예정)',
        '2) 중복 보장 감지 (예: 암 진단비 2곳 중복 시 월 절약액 계산)',
        '3) 보장 공백 분석 (가입 부족 영역 시각화)',
        '4) AI 맞춤 보험 추천 (정보 제공만, 권유 아님)',
        '5) 보험료 계산기 (가상 시뮬레이션)',
        '6) 청구 서류 자동 안내 (상황별 필요 서류 리스트)',
        '7) 실손24 및 각 보험사 청구 페이지 바로가기',
    ]
    y = draw_bullet(c, y, features)

    draw_footer(c)
    c.showPage()


def page3_legal(c):
    """법적 검토"""
    draw_header(c, 3, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '2. 법적 검토 및 업무 범위')
    y -= 3*mm

    y = draw_h2(c, y, '2.1 보험업법 제87조 (보험설계사 등록)')
    info_text = '보험설계사는 소속 보험회사 외의 자를 위하여 모집할 수 없음.\n다만 소비자 정보 제공 및 관리 도구 운영은 모집 행위에 해당하지 않음.'
    y = draw_body(c, y, info_text, size=10, indent=3*mm, color=GRAY)
    y -= 3*mm

    y = draw_h2(c, y, '2.2 본 서비스의 법적 성격')
    draw_box(c, M, y - 40*mm, W - 2*M, 38*mm, color=HexColor('#f0fdf4'), border=GREEN)

    c.setFont('MalgunBd', 11)
    c.setFillColor(GREEN)
    c.drawString(M + 5*mm, y - 6*mm, '✅ 합법 (정보 제공 · 관리 도구)')
    c.setFont('Malgun', 9)
    c.setFillColor(black)
    c.drawString(M + 5*mm, y - 12*mm, '• 가입자 본인의 보험 현황 시각화 → 마이데이터 기반 정보 조회')
    c.drawString(M + 5*mm, y - 17*mm, '• 보장 공백/중복 분석 → 의사결정 보조 도구')
    c.drawString(M + 5*mm, y - 22*mm, '• 청구 서류 안내 → 소비자 편의 제공 (약관·공개정보 기반)')
    c.drawString(M + 5*mm, y - 27*mm, '• 실손24 링크 제공 → 정부 운영 플랫폼 연결')
    c.drawString(M + 5*mm, y - 32*mm, '• 설계사 연결 → 등록된 본인(홍덕훈)에게만 연결')
    c.drawString(M + 5*mm, y - 37*mm, '※ 약관·공개정보에 근거하므로 상담·모집 행위와 무관')
    y -= 46*mm

    y = draw_h2(c, y, '2.3 엄격히 배제하는 업무')
    draw_box(c, M, y - 32*mm, W - 2*M, 30*mm, color=HexColor('#fef2f2'), border=RED)

    c.setFont('MalgunBd', 11)
    c.setFillColor(RED)
    c.drawString(M + 5*mm, y - 6*mm, '❌ 수행하지 않는 업무 (법적 리스크 차단)')
    c.setFont('Malgun', 9)
    c.setFillColor(black)
    c.drawString(M + 5*mm, y - 12*mm, '• 타 보험사 상품 모집 행위 (보험업법 제87조 위반)')
    c.drawString(M + 5*mm, y - 17*mm, '• 보험금 청구 대행 (손해사정사 라이선스 필요)')
    c.drawString(M + 5*mm, y - 22*mm, '• 타 설계사 연결 (본인 제외 다른 설계사 수수료 수취 X)')
    c.drawString(M + 5*mm, y - 27*mm, '• 금전·결제 처리 (현재 정보 제공만, 추후 회사 승인 시 검토)')
    y -= 36*mm

    draw_footer(c)
    c.showPage()


def page4_claim(c):
    """청구 기능 상세"""
    draw_header(c, 4, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '3. 보험금 청구 기능 상세')
    y -= 3*mm

    y = draw_h2(c, y, '3.1 핵심 원칙')
    y = draw_body(c, y,
        '본 기능은 「청구 대행」이 아닌 「정보 제공 및 안내」 서비스입니다.\n'
        '고객이 직접 보험사에 청구하도록 서류 및 프로세스를 안내합니다.',
        size=10, indent=3*mm, color=GRAY)
    y -= 5*mm

    y = draw_h2(c, y, '3.2 처리 흐름')
    flow_items = [
        '1단계: 사용자가 상황 선택 (통원/입원/수술/응급/암/교통사고/골절/뇌심장)',
        '2단계: 진단명 또는 특이사항 입력 (선택)',
        '3단계: 시스템이 해당 상황별 청구 가능 보험 목록 표시',
        '4단계: 각 보험별 필요 서류 · 예상 지급 범위 · 청구 경로 제공',
        '5단계: 실손24 앱 바로가기 또는 보험사 웹사이트 링크 안내',
        '6단계: 복잡 케이스는 「설계사 상담 신청」 버튼으로 연결 (본인)',
    ]
    y = draw_bullet(c, y, flow_items)
    y -= 3*mm

    y = draw_h2(c, y, '3.3 커버 범위 (8종 케이스)')
    cases = [
        ('🏥 통원 치료', '실손 · 상해/질병'),
        ('🛏️ 입원 치료', '실손 · 입원일당 · 상해/질병'),
        ('⚕️ 수술', '실손 · 수술보험'),
        ('🚑 응급실', '실손 · 상해보험'),
        ('🎗️ 암 진단', '암보험 · 실손 · 입원일당 (조직검사 결과 필수 안내)'),
        ('🚗 교통사고', '실손 · 자동차보험 · 운전자보험 (자손/실손 중복 불가 경고)'),
        ('🦴 골절/상해', '실손 · 상해보험 · 후유장해 (6개월 후 재진단 안내)'),
        ('💔 뇌/심장 질환', '진단금 · 실손 · 후유장해 (질병 코드 I63/I21 확인 안내)'),
    ]
    c.setFont('Malgun', 9)
    c.setFillColor(black)
    for case, detail in cases:
        c.setFont('MalgunBd', 9)
        c.drawString(M + 5*mm, y, case)
        c.setFont('Malgun', 9)
        c.drawString(M + 50*mm, y, detail)
        y -= 5.5*mm

    y -= 5*mm
    y = draw_h2(c, y, '3.4 정부 플랫폼 연동 (실손24)')
    y = draw_body(c, y,
        '2024년 10월부터 정부(보험개발원)가 운영하는 「실손24」 앱을 통해\n'
        '병원에서 보험사로 서류를 전자 전송할 수 있음. 본 서비스는 실손24로의\n'
        '링크 제공만 수행하므로 법적 리스크 없음.',
        size=10, indent=3*mm, color=GRAY)

    draw_footer(c)
    c.showPage()


def page5_tech(c):
    """기술 구성 및 데이터 보안"""
    draw_header(c, 5, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '4. 기술 구성 및 보안')
    y -= 3*mm

    y = draw_h2(c, y, '4.1 기술 스택')
    tech = [
        '프론트엔드: HTML/CSS/JavaScript (SPA)',
        '백엔드: Vercel Serverless Functions (Node.js)',
        '데이터 소스: 내보험다보여 API (금감원/생손보협회)',
        '호스팅: GitHub Pages (정적) + Vercel (API)',
        '보안: HTTPS, CORS, 환경변수 암호화',
    ]
    y = draw_bullet(c, y, tech)
    y -= 3*mm

    y = draw_h2(c, y, '4.2 데이터 수집·처리 원칙')
    draw_box(c, M, y - 50*mm, W - 2*M, 48*mm, color=BG_LIGHT)
    c.setFont('MalgunBd', 10)
    c.setFillColor(NAVY)
    c.drawString(M + 5*mm, y - 6*mm, '개인정보보호법 · 신용정보법 준수')
    c.setFont('Malgun', 9)
    c.setFillColor(black)
    points = [
        '• 사용자 동의 후에만 보험 정보 조회',
        '• 간편인증(공동인증서 등)으로 본인 인증',
        '• 원본 데이터는 즉시 파기, 분석 결과만 저장',
        '• 민감정보(주민번호·질병명)는 서버 저장 금지',
        '• SSL/TLS 암호화 통신',
        '• 사용자 동의 없는 데이터 공유/판매 절대 불가',
        '• 사용자 요청 시 24시간 내 데이터 삭제',
    ]
    py = y - 12*mm
    for p in points:
        c.drawString(M + 5*mm, py, p)
        py -= 5*mm
    y -= 56*mm

    y = draw_h2(c, y, '4.3 수익 모델 (현재·향후)')
    y = draw_body(c, y,
        '[현재] 무료 서비스 · 광고 없음 · 수수료 0원\n'
        '[향후] 프리미엄 구독 모델 검토 가능 (회사 승인 후)\n'
        '         - 예: AI 심화 분석 · 세무 연계 · 리포트 PDF 제공',
        size=10, indent=3*mm, color=GRAY)

    draw_footer(c)
    c.showPage()


def page6_request(c):
    """최종 승인 요청"""
    draw_header(c, 6, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '5. 승인 요청 사항')
    y -= 3*mm

    draw_box(c, M, y - 80*mm, W - 2*M, 78*mm, color=BG_LIGHT, border=BLUE)
    c.setFont('MalgunBd', 13)
    c.setFillColor(BLUE)
    c.drawString(M + 6*mm, y - 8*mm, '🙏 검토 및 승인을 요청드리는 사항')
    c.setFont('Malgun', 10)
    c.setFillColor(black)
    requests = [
        '1. 본 서비스의 운영 가능 여부 (GADP 소속 설계사 겸업 관점)',
        '2. GADP 브랜드·회사명 언급 가능 여부 (현재는 설계사 개인 운영)',
        '3. 소속 설계사 신분으로 외부 고객 유입 시 준수 사항',
        '4. 향후 수익 모델 도입 시 회사 정책과의 정합성',
        '5. 서비스명·로고 등 대외 커뮤니케이션 범위',
    ]
    ry = y - 16*mm
    for req in requests:
        c.drawString(M + 10*mm, ry, req)
        ry -= 7*mm

    c.setFont('Malgun', 9)
    c.setFillColor(GRAY)
    c.drawString(M + 6*mm, ry, '※ 상기 사항에 대한 공식 의견을 주시면 반영하여 운영하겠습니다.')

    y -= 90*mm

    # 현재 상태
    y = draw_h2(c, y, '현재 진행 상황')
    status_items = [
        '✅ 데모 사이트 구축 완료 (고객용/설계사용)',
        '⏸️ 정식 런칭 전 회사 승인 대기 중',
        '⏸️ 내보험다보여 API 연동 준비 (승인 후 진행)',
        '⏸️ 토스 앱인토스 미니앱 등록 (승인 후 진행)',
    ]
    y = draw_bullet(c, y, status_items)
    y -= 5*mm

    # 데모 링크
    draw_box(c, M, y - 22*mm, W - 2*M, 20*mm, color=BG_LIGHT)
    c.setFont('MalgunBd', 10)
    c.setFillColor(NAVY)
    c.drawString(M + 5*mm, y - 6*mm, '🔗 데모 사이트 (검토용)')
    c.setFont('Malgun', 9)
    c.setFillColor(BLUE)
    c.drawString(M + 5*mm, y - 12*mm, '[고객용] https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/index.html')
    c.drawString(M + 5*mm, y - 18*mm, '[설계사용] https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/agent.html')
    y -= 30*mm

    # 서명
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.5)
    c.line(M, y, W - M, y)
    y -= 15*mm

    c.setFont('Malgun', 11)
    c.setFillColor(black)
    c.drawCentredString(W/2, y, '담당자의 검토와 회신을 기다리겠습니다. 감사합니다.')
    y -= 15*mm

    c.setFont('MalgunBd', 12)
    c.setFillColor(NAVY)
    c.drawRightString(W - M - 20*mm, y, '작성자: 홍덕훈 (소속 설계사)')
    c.setFont('Malgun', 10)
    c.setFillColor(GRAY)
    c.drawRightString(W - M - 20*mm, y - 6*mm, '쿤스튜디오 대표 · 생명/손해보험 자격증')
    c.drawRightString(W - M - 20*mm, y - 11*mm, 'ghdejr11@gmail.com')

    draw_footer(c)
    c.showPage()


def main():
    output_path = Path(__file__).parent / '보험다보여_GADP_승인요청서.pdf'
    c = canvas.Canvas(str(output_path), pagesize=A4)

    page1_cover(c)
    page2_overview(c)
    page3_legal(c)
    page4_claim(c)
    page5_tech(c)
    page6_request(c)

    c.save()
    print(f'✅ PDF 생성 완료: {output_path}')
    print(f'   파일 크기: {output_path.stat().st_size / 1024:.1f} KB')
    print(f'   페이지 수: 6쪽')


if __name__ == '__main__':
    main()
