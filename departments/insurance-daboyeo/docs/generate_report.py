#!/usr/bin/env python3
"""
AZ금융-보맵 그룹 내 설계사 전용 도구 제안서 생성기
대상: 에즈금융서비스 경영진/검토자
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

NAVY = HexColor('#1e3a5f')
BLUE = HexColor('#2563eb')
GRAY = HexColor('#4a5568')
LIGHT_GRAY = HexColor('#cbd5e0')
VERY_LIGHT = HexColor('#f7fafc')
GREEN = HexColor('#047857')
AMBER = HexColor('#b45309')
RED = HexColor('#b91c1c')
GOLD = HexColor('#c9a84c')
PURPLE = HexColor('#7c3aed')


def draw_header(c, page_num, total_pages):
    c.setFont('MalgunBd', 9)
    c.setFillColor(NAVY)
    c.drawString(M, H - 14*mm, 'AZ금융-보맵 그룹 내 설계사 전용 도구 제안서')
    c.setFillColor(GRAY)
    c.setFont('Malgun', 9)
    c.drawRightString(W - M, H - 14*mm, f'{page_num} / {total_pages}')
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.4)
    c.line(M, H - 17*mm, W - M, H - 17*mm)


def draw_footer(c):
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.4)
    c.line(M, 15*mm, W - M, 15*mm)
    c.setFont('Malgun', 8)
    c.setFillColor(GRAY)
    c.drawString(M, 10*mm, '제안자: 홍덕훈 | AZ금융(에즈금융서비스) 소속 설계사')
    c.drawRightString(W - M, 10*mm, datetime.datetime.now().strftime('%Y-%m-%d'))


def draw_box(c, x, y, w, h, color=VERY_LIGHT, border=LIGHT_GRAY, radius=3, line_width=0.8):
    c.setFillColor(color)
    c.setStrokeColor(border)
    c.setLineWidth(line_width)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)


def draw_h1(c, y, number, text):
    c.setFillColor(NAVY)
    c.setFont('MalgunBd', 17)
    c.drawString(M, y, f'{number}. {text}')
    c.setStrokeColor(NAVY)
    c.setLineWidth(2)
    c.line(M, y - 3*mm, M + 55*mm, y - 3*mm)
    return y - 11*mm


def draw_h2(c, y, text, color=BLUE):
    c.setFillColor(color)
    c.setFont('MalgunBd', 12)
    c.drawString(M, y, f'■ {text}')
    return y - 7*mm


def draw_body(c, y, text, size=10, indent=0, color=black, leading=None):
    c.setFillColor(color)
    c.setFont('Malgun', size)
    if leading is None: leading = size + 3
    for line in text.split('\n'):
        c.drawString(M + indent, y, line)
        y -= leading
    return y


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


TOTAL_PAGES = 7


def page1_cover(c):
    """표지"""
    c.setFillColor(NAVY)
    c.rect(0, H - 100*mm, W, 100*mm, fill=1, stroke=0)

    c.setFillColor(GOLD)
    c.rect(W/2 - 35*mm, H - 55*mm, 70*mm, 1, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont('MalgunBd', 28)
    c.drawCentredString(W/2, H - 45*mm, 'AZ금융 - 보맵 그룹 시너지')

    c.setFillColor(HexColor('#cbd5e0'))
    c.setFont('Malgun', 13)
    c.drawCentredString(W/2, H - 60*mm, '설계사 전용 고객 관리 도구 제안')

    c.setFillColor(GOLD)
    c.setFont('MalgunBd', 18)
    c.drawCentredString(W/2, H - 85*mm, '『보험다보여』 SELLERSIDE')

    box_y = H/2 - 60*mm
    draw_box(c, M, box_y, W - 2*M, 75*mm, color=VERY_LIGHT)

    c.setFont('MalgunBd', 13)
    c.setFillColor(NAVY)
    c.drawString(M + 10*mm, box_y + 63*mm, '[ 제안 요지 ]')

    c.setFont('Malgun', 10.5)
    c.setFillColor(black)
    lines = [
        'AZ금융(에즈금융서비스)은 2022년 보맵(주) 지분 40% 이상을 확보한',
        '보맵의 최대주주입니다. 보맵 앱은 대중(B2C) 서비스로 포지셔닝되어 있으며,',
        '그룹 내에 설계사(B2B) 전용 도구는 부재한 상황입니다.',
        '',
        '본 제안은 AZ금융 소속 설계사 홍덕훈이 자체 개발한',
        '「보험다보여 Sellerside」의 그룹 자산화 및 전사 배포를 제안드립니다.',
        '',
        '보맵(B2C, 마이데이터 대중 서비스)와 상호 보완 관계로,',
        'AZ금융 설계사의 고객 관리 효율과 고객 유지율 향상에 기여할 수 있습니다.',
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
    c.setFillColor(NAVY)
    c.drawCentredString(W/2, footer_y + 12*mm, '제안자 : 홍 덕 훈 (HONG DEOKHUN)')
    c.setFont('Malgun', 10)
    c.setFillColor(GRAY)
    c.drawCentredString(W/2, footer_y + 6*mm, 'AZ금융(에즈금융서비스) 소속 설계사')
    c.drawCentredString(W/2, footer_y, '생명보험 / 손해보험 모집인 자격 보유')
    c.drawCentredString(W/2, footer_y - 6*mm, f'제안일 : {datetime.datetime.now().strftime("%Y년 %m월 %d일")}')

    c.showPage()


def page2_group_position(c):
    """그룹 내 포지셔닝"""
    draw_header(c, 2, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '1', 'AZ금융 - 보맵 그룹 내 포지셔닝')
    y -= 2*mm

    y = draw_h2(c, y, '1.1  그룹 구조')
    draw_box(c, M, y - 30*mm, W - 2*M, 28*mm, color=VERY_LIGHT)
    c.setFont('MalgunBd', 11)
    c.setFillColor(NAVY)
    c.drawString(M + 6*mm, y - 7*mm, 'AZ금융(에즈금융서비스)')
    c.setFont('Malgun', 9.5)
    c.setFillColor(GRAY)
    c.drawString(M + 6*mm, y - 13*mm, '독립 GA · 38개 보험사 계약 · 전국 16개 지점')
    c.setFont('MalgunBd', 11)
    c.setFillColor(NAVY)
    c.drawString(M + 6*mm, y - 21*mm, '  └ 보맵(주)  [ 2022년 지분 40%+ 확보, 최대주주 ]')
    c.setFont('Malgun', 9.5)
    c.setFillColor(GRAY)
    c.drawString(M + 6*mm, y - 27*mm, '  └ 마이데이터 사업자 · 대중(B2C) 보험 관리 플랫폼')
    y -= 36*mm

    y = draw_h2(c, y, '1.2  서비스 레이어 분석')

    # 테이블
    draw_box(c, M, y - 4*mm, W - 2*M, 6*mm, color=NAVY, border=NAVY)
    c.setFont('MalgunBd', 9.5)
    c.setFillColor(white)
    c.drawString(M + 6*mm, y - 1.5*mm, '구분')
    c.drawString(M + 45*mm, y - 1.5*mm, '보맵 (기존)')
    c.drawString(M + 105*mm, y - 1.5*mm, '보험다보여 Sellerside (제안)')
    y -= 7*mm

    rows = [
        ('타겟', '일반 대중 (B2C)', 'AZ금융 설계사 + 담당 고객'),
        ('접근 방식', '앱스토어 다운로드', '설계사가 고객에게 전용 링크 공유'),
        ('주요 기능', '마이데이터 보험 조회·관리', '설계사별 고객 관리 · 청구 안내'),
        ('수익 모델', '광고 · 앱 내 전환', 'AZ 설계사 업무 효율화'),
        ('설계사 표시', '앱 내 랜덤 매칭', '고정 담당 설계사 1:1'),
        ('보맵과 관계', '-', '상호 보완 (대중 vs 전담)'),
    ]
    c.setFont('Malgun', 9)
    for i, (a, b, d) in enumerate(rows):
        bg = VERY_LIGHT if i % 2 == 0 else white
        c.setFillColor(bg)
        c.rect(M, y - 4*mm, W - 2*M, 5.5*mm, fill=1, stroke=0)
        c.setFillColor(black)
        c.setFont('MalgunBd', 9)
        c.drawString(M + 6*mm, y - 1.5*mm, a)
        c.setFont('Malgun', 9)
        c.drawString(M + 45*mm, y - 1.5*mm, b)
        c.drawString(M + 105*mm, y - 1.5*mm, d)
        y -= 5.5*mm

    y -= 5*mm
    y = draw_h2(c, y, '1.3  핵심 메시지')
    draw_box(c, M, y - 28*mm, W - 2*M, 26*mm, color=HexColor('#fef3c7'), border=GOLD)
    c.setFont('MalgunBd', 11)
    c.setFillColor(NAVY)
    c.drawString(M + 6*mm, y - 7*mm, '「 보맵 = 대중 B2C / 보험다보여 Sellerside = 설계사 B2B2C 」')
    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    msg_lines = [
        '본 도구는 보맵과 경쟁하지 않습니다. 보맵이 커버하지 못하는',
        'B2B (설계사 업무) + B2C (담당 고객) 영역을 보완합니다.',
        '',
        '기존 보맵 유저의 유입을 가로채지 않으며, AZ금융 설계사가 자기 고객에게만 공유합니다.',
    ]
    ly = y - 13*mm
    for line in msg_lines:
        c.drawString(M + 6*mm, ly, line)
        ly -= 5*mm

    draw_footer(c)
    c.showPage()


def page3_features(c):
    """주요 기능"""
    draw_header(c, 3, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '2', '핵심 기능')
    y -= 2*mm

    y = draw_h2(c, y, '2.1  고객용 앱 (B2C, 담당 설계사 자동 연결)')
    features_c = [
        '전 보험사 실시간 연동 (생명·손해·실손·상해 통합 / 가족 계약 포함)',
        '본인 가입 보험만 우선 표시 (미가입 34개 숨김 / 토글로 확장)',
        '중복 보장 감지 + 월 절약액 계산',
        '보장 공백 분석 및 맞춤 추천',
        '보험료 계산기 (실시간 시뮬레이션)',
        '청구 서류 자동 안내 (8종 케이스)',
        '담당 설계사 1:1 연결 (전화 / 문자 / 카톡)',
        '갱신 및 만기 알림',
        '고객센터·불만접수 (AI 자동 분류 + 24시간 답변)',
    ]
    y = draw_numbered(c, y, features_c)
    y -= 3*mm

    y = draw_h2(c, y, '2.2  설계사용 앱 (B2B, 고객 관리 대시보드)')
    features_a = [
        '본인 프로필 설정 (사번 · 이름 · 연락처 · 지점)',
        '본인 전용 고객 링크 자동 생성 (URL + QR)',
        '고객 관리 대시보드 (건수 · 월 보험료 · 갱신 예정)',
        '고객별 보장 분석 (중복 · 공백 · 리스크 점수)',
        '청구 서류 안내 (설계사 상담 참고용)',
        '가입 전 건강 분석 (CODEF 마이헬스웨이 API 계약 진행 중)',
        '상담 일정 관리',
        '피드백·개선제안 (9종 카테고리 · AI 자동 분류)',
    ]
    y = draw_numbered(c, y, features_a)
    y -= 3*mm

    y = draw_h2(c, y, '2.3  설계사별 개인화 구조')
    draw_box(c, M, y - 42*mm, W - 2*M, 40*mm, color=VERY_LIGHT)
    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    flow = [
        '[1] 설계사가 앱 설치 후 사번 · 이름 · 연락처 입력',
        '[2] 본인 전용 고객용 링크 자동 생성 (예: .../?a=<encoded>)',
        '[3] 설계사가 담당 고객에게 링크 공유 (카톡 · 문자 · 명함 QR)',
        '[4] 고객이 링크 접속 → 자동으로 해당 설계사로 연결',
        '[5] 고객 앱 상단에 담당 설계사 정보 고정 배너',
        '[6] 고객이 상담 신청 → 바로 담당 설계사에게 연결',
    ]
    ly = y - 7*mm
    for line in flow:
        c.drawString(M + 6*mm, ly, line)
        ly -= 5.5*mm

    draw_footer(c)
    c.showPage()


def page4_synergy(c):
    """그룹 시너지"""
    draw_header(c, 4, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '3', 'AZ금융 - 보맵 그룹 시너지')
    y -= 2*mm

    y = draw_h2(c, y, '3.1  AZ금융에 미치는 효과')
    effects_az = [
        '전국 16개 지점 · 설계사 전원 사용 가능한 공통 업무 도구',
        '설계사별 고객 관리 표준화 → 영업 효율 증가',
        '고객 유지율 상승 (1:1 담당 설계사 연결로 이탈 방지)',
        '신규 고객 유입 채널 증가 (설계사가 지인·기존 고객에게 링크 공유)',
        'IT 개발비 0원 (설계사 본인 개발, 그룹 자산화 시 인계 가능)',
    ]
    y = draw_numbered(c, y, effects_az)
    y -= 3*mm

    y = draw_h2(c, y, '3.2  보맵에 미치는 효과 및 약점 보완', color=PURPLE)
    effects_bm = [
        '설계사 영역 신규 진출 (기존 보맵은 B2C만 커버)',
        '보맵 플랫폼 신뢰도 상승 (AZ 설계사 공식 도구로 확장 시)',
        '설계사 유입으로 보맵 DB 풀 확장 가능',
        '사용자 불만 해소: "가족 계약 조회 불완전 · 타사 미연동" (구글플레이 리뷰)',
        '데이터 연계 시 B2B2C 통합 플랫폼으로 진화',
    ]
    y = draw_numbered(c, y, effects_bm)
    y -= 3*mm

    y = draw_h2(c, y, '3.3  설계사 개인에게 미치는 효과', color=GREEN)
    effects_ag = [
        '본인 브랜드(이름 · 사번) 노출 강화 → 고객 신뢰 증대',
        '청구 서류 안내 시간 단축 (기존 대비 70% 감소 예상)',
        '고객 관리 엑셀 · 수기 메모 대체',
        '월별 갱신 · 만기 자동 알림으로 재계약률 향상',
    ]
    y = draw_numbered(c, y, effects_ag)

    draw_footer(c)
    c.showPage()


def page5_legal(c):
    """법적 검토"""
    draw_header(c, 5, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '4', '법적 검토')
    y -= 2*mm

    y = draw_h2(c, y, '4.1  보험업법 제87조 관점')
    draw_box(c, M, y - 24*mm, W - 2*M, 22*mm, color=VERY_LIGHT)
    c.setFont('MalgunBd', 10)
    c.setFillColor(NAVY)
    c.drawString(M + 6*mm, y - 7*mm, '「 보험설계사의 등록 - 타 보험사 모집 제한 」')
    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    c.drawString(M + 6*mm, y - 13*mm, '본 도구는 AZ금융 소속 설계사가 AZ금융 계약 범위 내에서')
    c.drawString(M + 6*mm, y - 18*mm, '고객을 관리하는 도구이므로 제87조에 저촉되지 않습니다.')
    y -= 30*mm

    y = draw_h2(c, y, '4.2  합법적 기능 (정보 제공 · 관리 도구)')
    y = draw_bullet(c, y, [
        '가입자 본인의 보험 현황 시각화 (마이데이터 기반)',
        '보장 공백 · 중복 분석 (의사결정 보조)',
        '청구 서류 안내 (약관 · 공개 정보 기반)',
        '담당 설계사 1:1 연결 (등록 설계사에게만)',
        '실손24 및 보험사 청구 페이지 링크 제공',
    ])
    y -= 3*mm

    y = draw_h2(c, y, '4.3  배제되는 기능 (법적 리스크 차단)', color=RED)
    draw_box(c, M, y - 28*mm, W - 2*M, 26*mm, color=HexColor('#fef2f2'), border=RED)
    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    exclude = [
        'AZ금융 미계약 보험사 상품 모집 (제87조 저촉)',
        '보험금 청구 대행 (손해사정사 라이선스 필요)',
        '타 설계사 연결 (AZ 설계사에게만 연결)',
        '플랫폼 자체 금전 · 결제 처리',
    ]
    ly = y - 7*mm
    for line in exclude:
        c.drawString(M + 6*mm, ly, '·')
        c.drawString(M + 10*mm, ly, line)
        ly -= 5.5*mm
    y -= 34*mm

    y = draw_h2(c, y, '4.4  개인정보 보호')
    y = draw_bullet(c, y, [
        '사용자 동의 후에만 보험 정보 조회',
        '간편인증 (공동인증서 등) 본인 인증',
        '민감정보 (주민번호 · 질병명) 서버 저장 금지',
        'SSL/TLS 암호화 · 사용자 요청 시 24시간 내 데이터 삭제',
    ])

    draw_footer(c)
    c.showPage()


def page6_tech(c):
    """기술 구성 + 보안"""
    draw_header(c, 6, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '5', '기술 구성 및 보안')
    y -= 2*mm

    y = draw_h2(c, y, '5.1  기술 스택')
    y = draw_bullet(c, y, [
        '프론트엔드:  HTML · CSS · JavaScript (반응형 SPA)',
        '백엔드:  Vercel Serverless Functions (Node.js)',
        '데이터 소스:  내보험다보여 API (금감원/생손보협회)',
        '호스팅:  GitHub Pages (정적) + Vercel (API)',
        '설계사 개인화:  URL 파라미터 + Base64 인코딩 프로필',
    ])
    y -= 3*mm

    y = draw_h2(c, y, '5.2  확장 가능성')
    draw_box(c, M, y - 36*mm, W - 2*M, 34*mm, color=VERY_LIGHT)
    c.setFont('Malgun', 9.5)
    c.setFillColor(black)
    ext = [
        '현 단계:  개인 설계사 운영 (MVP / Beta)',
        '2단계:  AZ금융 공식 채택 시 사내 SSO 연동 (사번 기반 자동 로그인)',
        '3단계:  보맵 API 연동 (B2B2C 통합 생태계)',
        '4단계:  AWS 이전 + K-ISMS 인증 획득 (대규모 운영)',
        '5단계:  AI 기반 추천 엔진 도입 (Claude / OpenAI)',
    ]
    ly = y - 7*mm
    for line in ext:
        c.drawString(M + 6*mm, ly, '·')
        c.drawString(M + 10*mm, ly, line)
        ly -= 5.5*mm
    y -= 42*mm

    y = draw_h2(c, y, '5.3  현재 진행 상황')
    status = [
        '[완료]  고객용 앱 MVP (설계사 URL 파라미터 인식 · 미가입 숨김 UX)',
        '[완료]  설계사용 앱 MVP (프로필 설정 · 링크 생성 · QR · 고객 관리)',
        '[완료]  청구 서류 자동 안내 (8종 케이스)',
        '[완료]  고객용 + 설계사용 양쪽 고객센터·피드백 시스템 (AI 자동 분류)',
        '[완료]  마케팅 랜딩 페이지 (B2C+B2B 통합 소개 · 실 스크린샷 10장)',
        '[완료]  Vercel API 서버 구축 (텔레그램 프록시 · 사전예약 · 티켓 접수)',
        '[완료]  경쟁사 차별화 포지셔닝 (전 보험사 실시간 연동 카피)',
        '[진행]  CODEF API 정식 계약 협의 (2026-04-17 신청, 3영업일 승인 예정)',
        '[진행]  마이헬스웨이 건강정보 연동 (CODEF 상품 추가 예정)',
        '[진행]  경쟁사 수집부 가동 (보맵 · 굿리치 · 레몬클립 일별 모니터링)',
        '[대기]  AZ금융 승인 및 전사 배포 검토',
        '[대기]  토스 앱인토스 미니앱 등록 (승인 후)',
    ]
    y = draw_bullet(c, y, status)

    draw_footer(c)
    c.showPage()


def page7_request(c):
    """검토 요청"""
    draw_header(c, 7, TOTAL_PAGES)
    y = H - 28*mm

    y = draw_h1(c, y, '6', '검토 및 협의 요청 사항')
    y -= 2*mm

    draw_box(c, M, y - 80*mm, W - 2*M, 78*mm, color=VERY_LIGHT, border=BLUE, line_width=1.5)
    c.setFont('MalgunBd', 13)
    c.setFillColor(BLUE)
    c.drawString(M + 8*mm, y - 9*mm, '「 검토 및 협의를 요청드리는 사항 」')

    c.setFont('Malgun', 10.5)
    c.setFillColor(black)
    requests = [
        '본 도구의 전사(全社) 배포 여부 검토',
        '보맵과의 역할 분리 및 통합 로드맵 협의',
        'AZ금융 공식 브랜드 · 로고 사용 범위',
        '사내 SSO 연동 · 사번 인증 체계 구축 가능 여부',
        '그룹 자산화 시 인계 조건 및 보상 체계',
    ]
    ry = y - 19*mm
    for i, req in enumerate(requests, 1):
        c.setFont('MalgunBd', 10.5)
        c.setFillColor(NAVY)
        c.drawString(M + 12*mm, ry, f'{i}.')
        c.setFont('Malgun', 10.5)
        c.setFillColor(black)
        c.drawString(M + 20*mm, ry, req)
        ry -= 9*mm

    c.setFont('Malgun', 9.5)
    c.setFillColor(GRAY)
    c.drawString(M + 8*mm, ry - 3*mm, '※ 본 도구는 회사 승인 없이는 대외 공개하지 않으며, 승인 범위 내에서만 운영합니다.')

    y -= 92*mm

    # 데모 링크
    draw_box(c, M, y - 36*mm, W - 2*M, 34*mm, color=VERY_LIGHT)
    c.setFont('MalgunBd', 10)
    c.setFillColor(NAVY)
    c.drawString(M + 6*mm, y - 7*mm, '「 데모 사이트 (검토용) 」')
    c.setFont('Malgun', 8.5)
    c.setFillColor(BLUE)
    c.drawString(M + 6*mm, y - 14*mm, '[소개]')
    c.drawString(M + 22*mm, y - 14*mm, 'https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/landing.html')
    c.drawString(M + 6*mm, y - 20*mm, '[고객용]')
    c.drawString(M + 22*mm, y - 20*mm, 'https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/index.html')
    c.drawString(M + 6*mm, y - 26*mm, '[설계사용]')
    c.drawString(M + 22*mm, y - 26*mm, 'https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/agent.html')
    c.setFont('Malgun', 8.5)
    c.setFillColor(GRAY)
    c.drawString(M + 6*mm, y - 32*mm, '※ 소개 페이지에서 기능·차별화 개요 확인 후, 고객용/설계사용 앱을 체험하실 수 있습니다.')
    y -= 44*mm

    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.5)
    c.line(M, y, W - M, y)
    y -= 12*mm

    c.setFont('Malgun', 11)
    c.setFillColor(black)
    c.drawCentredString(W/2, y, '검토 의견을 기다리겠습니다.')
    y -= 6*mm
    c.drawCentredString(W/2, y, '감사합니다.')
    y -= 18*mm

    c.setFont('MalgunBd', 12)
    c.setFillColor(NAVY)
    c.drawRightString(W - M - 30*mm, y, '제안자 : 홍 덕 훈')
    c.setFont('Malgun', 9.5)
    c.setFillColor(GRAY)
    c.drawRightString(W - M - 30*mm, y - 6*mm, 'AZ금융(에즈금융서비스) 소속 설계사')
    c.drawRightString(W - M - 30*mm, y - 11*mm, '생명보험 · 손해보험 자격증 보유')
    c.drawRightString(W - M - 30*mm, y - 16*mm, 'ghdejr11@gmail.com')

    c.setStrokeColor(LIGHT_GRAY)
    c.rect(W - M - 25*mm, y - 15*mm, 18*mm, 18*mm, stroke=1, fill=0)
    c.setFont('Malgun', 8)
    c.setFillColor(LIGHT_GRAY)
    c.drawCentredString(W - M - 16*mm, y - 7*mm, '(인)')

    draw_footer(c)
    c.showPage()


def main():
    # 기존 파일 제목 변경
    old_path = Path(__file__).parent / '보험다보여_GADP_승인요청서.pdf'
    new_path = Path(__file__).parent / 'AZ금융_보맵그룹_설계사도구_제안서.pdf'

    c = canvas.Canvas(str(new_path), pagesize=A4)

    page1_cover(c)
    page2_group_position(c)
    page3_features(c)
    page4_synergy(c)
    page5_legal(c)
    page6_tech(c)
    page7_request(c)

    c.save()

    # 기존 잘못된 PDF 삭제
    if old_path.exists():
        old_path.unlink()

    print(f'[OK] PDF 생성 완료: {new_path}')
    print(f'     파일 크기: {new_path.stat().st_size / 1024:.1f} KB')
    print(f'     페이지 수: {TOTAL_PAGES}쪽')
    print(f'     타이틀: AZ금융-보맵 그룹 시너지 제안서')


if __name__ == '__main__':
    main()
