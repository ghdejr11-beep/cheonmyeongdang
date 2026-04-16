#!/usr/bin/env python3
"""
세금N혜택 홍보 콘텐츠 30개 자동 생성
- 인스타/페북/쓰레드/카카오/텔레그램 모든 채널용
- 각 캡션 + 해시태그 + 이미지 텍스트 오버레이
- 메타 Business Suite Planner에 일괄 업로드용 JSON + CSV
"""
import os
import json
import csv
from datetime import datetime, timedelta

OUTPUT = os.path.join(os.path.dirname(__file__), 'tax_content_output')
os.makedirs(OUTPUT, exist_ok=True)

LANDING = "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/tax/src/"

# 콘텐츠 테마 5개 × 포스트 6개 = 30개
CONTENT = [
    # ========== 테마 1: 후킹 / 놀라움 (숫자 강조) ==========
    {
        "type": "hook",
        "caption": """작년 당신이 세금을 얼마나 더 냈는지 아시나요?

프리랜서 평균 환급액: 49만원
크리에이터 평균 환급액: 38만원
자영업자 평균 환급액: 52만원

종합소득세 신고 D-44
지금 1분이면 확인 가능합니다.

수수료 0원 조회 → 링크 프로필""",
        "image_title": "작년 평균 환급액",
        "image_big": "32만원",
        "image_sub": "프리랜서 · 자영업자 · 크리에이터",
        "hashtags": "#종합소득세 #세금환급 #프리랜서 #1인사업자 #세금N혜택 #환급금 #절세",
    },
    {
        "type": "hook",
        "caption": """📊 3.3% 원천징수가 모여 쌓인 돈

연수입 3천만원 프리랜서 기준
→ 1년에 약 99만원 원천징수
→ 실제 세금 약 50만원 (경비 공제 후)
→ **약 49만원 환급 가능**

1분만 투자하면 확인됩니다.""",
        "image_title": "3.3% 원천징수",
        "image_big": "49만원 환급",
        "image_sub": "연수입 3,000만원 기준",
        "hashtags": "#프리랜서세금 #3점3환급 #원천징수환급 #종합소득세 #세금N혜택",
    },
    {
        "type": "hook",
        "caption": """🔥 종합소득세 신고 D-44

5/31 마감까지 44일 남았습니다.

지금까지 환급받지 않은 세금이 있다면
지금이 마지막 기회입니다.

무료 조회 → 프로필 링크""",
        "image_title": "종합소득세 마감",
        "image_big": "D-44",
        "image_sub": "2026년 5월 31일까지",
        "hashtags": "#종합소득세신고 #D44 #세금마감 #세금환급 #세금N혜택",
    },
    {
        "type": "hook",
        "caption": """⚠️ 모르면 손해 보는 3.3% 환급

프리랜서·유튜버·강사 등
원천징수 3.3% 떼고 받으셨다면

신고 안 하면 → 국가가 가져갑니다
신고 하면 → 최대 80%까지 돌려받을 수 있어요

5/31 전에 꼭 확인하세요.""",
        "image_title": "프리랜서 3.3%",
        "image_big": "최대 80% 환급",
        "image_sub": "신고 안 하면 국가에게 귀속",
        "hashtags": "#프리랜서 #3점3 #세금환급 #종합소득세 #프리랜서절세",
    },
    {
        "type": "hook",
        "caption": """💰 유튜버 A씨: 환급액 172만원

연 수입 4,500만원
편집비·장비비 등 경비 1,800만원
3.3% 원천징수액 147만원

→ 실제 세액 계산 결과 172만원 환급!

혼자 계산 어려우면 무료 자동 계산""",
        "image_title": "유튜버 A씨 사례",
        "image_big": "172만원 환급",
        "image_sub": "연수입 4,500만원",
        "hashtags": "#유튜버세금 #크리에이터세금 #부업세금 #세금환급 #세금N혜택",
    },
    {
        "type": "hook",
        "caption": """📈 숨은 세금 환급금 있나요?

홈택스 로그인 → 복잡함
세무사 방문 → 상담료 5~10만원
**세금N혜택** → 1분 무료 조회

수수료 0원, 회원가입 X""",
        "image_title": "세무 서비스 비교",
        "image_big": "수수료 0원",
        "image_sub": "타 서비스 대비 10~20% 절감",
        "hashtags": "#세무사비교 #세금앱 #수수료0 #세금환급 #세금N혜택",
    },

    # ========== 테마 2: 대상별 어필 ==========
    {
        "type": "target",
        "caption": """💼 프리랜서라면 꼭 확인하세요

경비처리 가능한 것들:
✓ 업무용 노트북, 모니터
✓ 통신비 70%
✓ 교육비, 도서비
✓ 카페 작업 시 음료비 (한도 있음)

연 수입 3천만원 → 약 49만원 환급""",
        "image_title": "프리랜서 필수",
        "image_big": "49만원",
        "image_sub": "평균 환급액",
        "hashtags": "#프리랜서 #1인사업자 #프리랜서경비 #세금환급",
    },
    {
        "type": "target",
        "caption": """🏪 자영업자·소상공인 맞춤

✓ 매입 원가 전액 경비처리
✓ 임대료, 관리비
✓ 직원 급여, 4대보험
✓ 사업용 차량 리스·렌트
✓ 노란우산공제 최대 500만원 소득공제

매출 1억 400만원 이하면 간이과세자 전환 검토""",
        "image_title": "자영업자 절세 가이드",
        "image_big": "500만원",
        "image_sub": "노란우산공제 최대 소득공제",
        "hashtags": "#자영업자 #소상공인 #절세 #종합소득세",
    },
    {
        "type": "target",
        "caption": """🎬 유튜버·크리에이터

경비처리 가능:
✓ 카메라, 마이크, 조명 장비
✓ 편집 프로그램 구독료 (프리미어·파이널컷)
✓ 촬영 장소 대여비
✓ 외주 편집비 (원천징수 3.3%)

해외 애드센스 수입도 종합소득세 신고 필수""",
        "image_title": "크리에이터 절세",
        "image_big": "장비 100% 경비",
        "image_sub": "카메라·마이크·편집",
        "hashtags": "#유튜버 #크리에이터 #애드센스 #부업세금",
    },
    {
        "type": "target",
        "caption": """🛵 배달 라이더 절세

✓ 오토바이·자전거 구입비
✓ 수리비, 주유비, 보험료
✓ 휴대폰 요금 (업무용 70%)
✓ 배달가방, 헬멧 등 장비

단순경비율 약 79.4% 적용 가능""",
        "image_title": "배달 라이더",
        "image_big": "79.4%",
        "image_sub": "단순경비율 인정",
        "hashtags": "#배달라이더 #쿠팡이츠 #배민 #배달세금",
    },
    {
        "type": "target",
        "caption": """💻 직장인 부업러

본업 월급 외 부업 수입은
따로 종합소득세 신고해야 해요.

✓ 블로그 광고료
✓ 유튜브 애드센스
✓ 쿠팡파트너스·애드포스트
✓ 과외비, 원고료

3.3% 떼고 받은 건 환급 가능!""",
        "image_title": "직장인 부업",
        "image_big": "부수입 신고",
        "image_sub": "종합소득세 확정신고",
        "hashtags": "#직장인부업 #부수입 #애드센스 #부업세금",
    },
    {
        "type": "target",
        "caption": """🛡️ 보험설계사 경비처리

✓ 교통비, 차량유지비
✓ 고객 접대비 (증빙 필수)
✓ 업무용 정장, 명함
✓ 사무용품, 문구류

단순경비율 약 48.1% 적용""",
        "image_title": "보험설계사",
        "image_big": "48.1%",
        "image_sub": "단순경비율 인정",
        "hashtags": "#보험설계사 #fp #보험영업 #보험설계사세금",
    },

    # ========== 테마 3: 교육 / 정보 ==========
    {
        "type": "edu",
        "caption": """📚 종합소득세란?

1년 동안 번 소득 전부 합쳐서
한 번에 신고·납부하는 세금.

신고 기간: 매년 5월 1일 ~ 31일
대상: 사업소득·근로소득·이자·배당·연금·기타

납부 늦으면 가산세 붙으니
무조건 5월 내 신고하세요!""",
        "image_title": "종합소득세란?",
        "image_big": "5/1 ~ 5/31",
        "image_sub": "매년 5월 신고",
        "hashtags": "#종합소득세 #세금기초 #소득세신고 #세테크",
    },
    {
        "type": "edu",
        "caption": """📖 환급 vs 추징

환급: 미리 낸 세금 > 실제 세금
→ 차액을 돌려받음 (💰)

추징: 미리 낸 세금 < 실제 세금
→ 차액을 더 내야 함 (💸)

프리랜서는 대부분 환급!
안 하면 국가가 그대로 가져감.""",
        "image_title": "환급 vs 추징",
        "image_big": "프리랜서 = 환급",
        "image_sub": "안 하면 국가 귀속",
        "hashtags": "#환급 #추징 #세금환급 #프리랜서환급",
    },
    {
        "type": "edu",
        "caption": """🧮 경비처리란?

"사업을 위해 쓴 돈"을
수입에서 빼주는 제도.

경비 많이 인정받을수록
→ 세금 줄어듦
→ 환급액 증가

하지만 증빙 없으면 인정 안 돼요!
카드 명세서, 현금영수증 보관 필수""",
        "image_title": "경비처리",
        "image_big": "증빙이 핵심",
        "image_sub": "카드·현금영수증",
        "hashtags": "#경비처리 #절세 #세금환급 #증빙",
    },
    {
        "type": "edu",
        "caption": """📌 간이과세자 vs 일반과세자

간이과세자 (매출 1억 400만원 미만)
✓ 세금계산서 발행 불가
✓ 세율 낮음 (1.5~4%)
✓ 부가세 환급 못 받음

일반과세자 (매출 1억 400만원 이상)
✓ 세금계산서 발행 가능
✓ 세율 10%
✓ 부가세 환급 가능""",
        "image_title": "간이 vs 일반",
        "image_big": "1억 400만원",
        "image_sub": "기준 매출",
        "hashtags": "#간이과세자 #일반과세자 #부가세 #사업자",
    },
    {
        "type": "edu",
        "caption": """⏰ 세금 캘린더 2026

1월 25일: 부가세 확정신고
4월 30일: 법인세 신고 (12월 결산)
5월 31일: 종합소득세 신고 ⚠️
7월 25일: 부가세 예정신고
8월 31일: 법인세 중간예납
1월 25일(익년): 부가세 확정신고

알림 놓치면 가산세!""",
        "image_title": "세금 캘린더",
        "image_big": "5/31",
        "image_sub": "종합소득세 마감",
        "hashtags": "#세금캘린더 #세금일정 #부가세 #종합소득세",
    },
    {
        "type": "edu",
        "caption": """📝 신고하지 않으면?

무신고 가산세: 납부세액의 20%
과소신고 가산세: 차액의 10%
납부지연 가산세: 연 8.03%

"나는 환급이니 안 해도 돼"
→ 환급 못 받고 끝!

수수료 0원 무료 조회""",
        "image_title": "미신고 페널티",
        "image_big": "가산세 20%",
        "image_sub": "무신고 시 부과",
        "hashtags": "#가산세 #신고필수 #세금신고 #종합소득세",
    },

    # ========== 테마 4: 서비스 차별점 ==========
    {
        "type": "uniq",
        "caption": """🆚 타 서비스와 비교

타 서비스:
× 환급액의 10~20% 수수료
× 가입 필수
× 개인정보 서버 저장

세금N혜택:
✓ 수수료 0원
✓ 회원가입 불필요
✓ 주민번호 서버 미저장

왜 무료? 도서·광고 제휴로 운영""",
        "image_title": "세금N혜택 차별점",
        "image_big": "수수료 0원",
        "image_sub": "가입 없이 1분 조회",
        "hashtags": "#세금앱 #세무서비스 #세금환급 #세금N혜택",
    },
    {
        "type": "uniq",
        "caption": """🔒 개인정보 보안 원칙

✓ 주민번호 256비트 암호화 전송
✓ 서버에 저장 안 함
✓ 한국신용정보원 인증 API(CODEF)
✓ 카카오·토스·네이버·PASS 간편인증

공동인증서(공인인증서) 필요 없음""",
        "image_title": "보안 원칙",
        "image_big": "256-bit 암호화",
        "image_sub": "서버 미저장",
        "hashtags": "#개인정보보호 #보안 #세금앱 #codef",
    },
    {
        "type": "uniq",
        "caption": """⚡ 1분 조회 프로세스

Step 1: 카카오톡 본인인증 (20초)
Step 2: 홈택스 자동 연동 (30초)
Step 3: 환급금 즉시 표시 (10초)

총 소요: 1분
필요: 스마트폰 하나""",
        "image_title": "1분 프로세스",
        "image_big": "60초",
        "image_sub": "간편인증 → 조회",
        "hashtags": "#1분세금 #간편세금 #카카오인증 #세금N혜택",
    },
    {
        "type": "uniq",
        "caption": """💬 AI 세무 상담 24시간

"유튜브 수입도 신고해야 해?"
"노트북 산 건 경비 처리 돼?"
"3.3% 얼마나 환급받을 수 있어?"

실제 세무사 기준으로 학습한 AI가
24시간 즉답해드립니다.

세금N혜택 AI 상담 탭""",
        "image_title": "AI 세무 상담",
        "image_big": "24시간",
        "image_sub": "즉답 가능",
        "hashtags": "#AI세무 #세무상담 #세금AI #세금N혜택",
    },
    {
        "type": "uniq",
        "caption": """🏛️ 정부 지원금 자동 매칭

소상공인 디지털 전환 지원 최대 400만원
청년 창업 사업화 지원 최대 1억원
고용촉진 장려금 최대 720만원
노란우산공제 연 500만원 소득공제

내 사업에 맞는 지원금 자동 추천""",
        "image_title": "정부 지원금",
        "image_big": "1억원",
        "image_sub": "청년 창업 최대",
        "hashtags": "#정부지원금 #소상공인지원 #창업지원 #세금N혜택",
    },
    {
        "type": "uniq",
        "caption": """📱 웹·앱 선택 가능

모바일·PC 어디서든 웹으로 즉시 사용
or
Android 앱 다운로드 (Play Store)

회원가입 없이 링크만 눌러도 시작 가능""",
        "image_title": "웹 + 앱",
        "image_big": "설치 불필요",
        "image_sub": "링크 클릭만",
        "hashtags": "#모바일세금 #세금웹 #세금앱 #세금N혜택",
    },

    # ========== 테마 5: 긴급 CTA ==========
    {
        "type": "cta",
        "caption": """🔥 지금 바로 조회하세요

종합소득세 마감 D-44
2026년 5월 31일까지

1분 투자 → 평균 32만원 환급 확인

무료로 확인하기 → 프로필 링크""",
        "image_title": "지금 시작",
        "image_big": "D-44",
        "image_sub": "마감 임박",
        "hashtags": "#지금시작 #세금환급 #종합소득세 #세금N혜택",
    },
    {
        "type": "cta",
        "caption": """💰 환급액이 얼마일지 궁금하다면

1분이면 확인 가능합니다.

✓ 카카오톡 인증
✓ 홈택스 자동 연동
✓ 5년치 환급금 조회
✓ 수수료 0원

클릭 → 프로필 링크""",
        "image_title": "환급액 확인",
        "image_big": "1분",
        "image_sub": "조회 완료",
        "hashtags": "#환급금조회 #세금환급 #무료 #세금N혜택",
    },
    {
        "type": "cta",
        "caption": """⏰ 이번 달 내 꼭 하세요

5월 31일 자정 이후엔
환급 신청 불가능.

1년 기다려야 함.
(가산세 위험도 있음)

수수료 없이 1분 확인 →""",
        "image_title": "5월 31일",
        "image_big": "마감 엄수",
        "image_sub": "1년 기다려야",
        "hashtags": "#5월31일 #세금마감 #종합소득세 #세금N혜택",
    },
    {
        "type": "cta",
        "caption": """🎯 친구·가족과 공유하세요

주변에 프리랜서·자영업자·유튜버가 있다면
이 링크 한번 보여주세요.

대부분 환급 대상자인데 몰라서
매년 수십만원씩 버리고 있습니다.

공유하기 →""",
        "image_title": "공유하기",
        "image_big": "수십만원",
        "image_sub": "매년 버려지는 돈",
        "hashtags": "#공유 #프리랜서 #자영업자 #세금환급",
    },
    {
        "type": "cta",
        "caption": """💡 오늘의 꿀팁

"환급 조회" + "환급 신청"은 다릅니다.

조회만 한다고 자동으로 입금 X
반드시 신청까지 완료해야 받을 수 있어요.

세금N혜택에선 조회 → 신청까지 원클릭!""",
        "image_title": "조회 ≠ 신청",
        "image_big": "신청 필수",
        "image_sub": "조회만으론 X",
        "hashtags": "#세금환급 #신청필수 #세금N혜택",
    },
    {
        "type": "cta",
        "caption": """🚀 세금N혜택 런칭 기념

✨ 신규 런칭 이벤트 ✨
→ 평생 수수료 0원 약속
→ 신고 마감 전까지 무제한 재조회
→ 세금 캘린더 자동 알림 무료

지금 시작하세요 → 프로필 링크""",
        "image_title": "런칭 기념",
        "image_big": "평생 무료",
        "image_sub": "수수료 0원 약속",
        "hashtags": "#런칭 #이벤트 #세금N혜택 #무료세무",
    },
]


def generate():
    # 1. JSON (프로그래밍 사용용)
    json_path = os.path.join(OUTPUT, 'tax_content_30.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'link': LANDING, 'posts': CONTENT}, f, ensure_ascii=False, indent=2)
    print(f'[OK] JSON: {json_path}')

    # 2. CSV (Meta Business Suite Planner 일괄 업로드용)
    csv_path = os.path.join(OUTPUT, 'tax_content_30.csv')
    start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['#', 'type', 'publish_date', 'caption', 'image_title', 'image_big', 'image_sub', 'hashtags'])
        for i, p in enumerate(CONTENT):
            publish = start + timedelta(hours=i * 8)  # 하루 3개 간격
            w.writerow([
                i + 1,
                p['type'],
                publish.strftime('%Y-%m-%d %H:%M'),
                p['caption'] + '\n\n링크: ' + LANDING + '\n\n' + p['hashtags'],
                p['image_title'],
                p['image_big'],
                p['image_sub'],
                p['hashtags'],
            ])
    print(f'[OK] CSV: {csv_path}')

    # 3. 개별 캡션 파일 (복붙용)
    for i, p in enumerate(CONTENT):
        path = os.path.join(OUTPUT, f'post_{i+1:02d}_{p["type"]}.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"[타입: {p['type']}]\n")
            f.write(f"[이미지 타이틀: {p['image_title']}]\n")
            f.write(f"[이미지 큰글씨: {p['image_big']}]\n")
            f.write(f"[이미지 서브: {p['image_sub']}]\n\n")
            f.write("─" * 40 + "\n")
            f.write("캡션 (복사해서 인스타/페북에 붙여넣기):\n")
            f.write("─" * 40 + "\n\n")
            f.write(p['caption'])
            f.write('\n\n' + LANDING + '\n\n')
            f.write(p['hashtags'])
    print(f'[OK] 개별 파일 {len(CONTENT)}개')

    # 4. 이미지 자동 생성 (PIL)
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print('[SKIP] PIL 미설치 — 이미지 생략')
        return

    img_dir = os.path.join(OUTPUT, 'images')
    os.makedirs(img_dir, exist_ok=True)

    try:
        FONT_BIG = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 120)
        FONT_TITLE = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 50)
        FONT_SUB = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 36)
        FONT_SMALL = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 26)
    except OSError:
        print('[WARN] 폰트 로드 실패')
        return

    for i, p in enumerate(CONTENT):
        # 1080x1080 (인스타 정사각)
        img = Image.new('RGB', (1080, 1080), '#ffffff')
        draw = ImageDraw.Draw(img)
        # 상단 히어로 영역
        draw.rectangle([(0, 0), (1080, 640)], fill='#dbe9fc')
        # 배지
        draw.rounded_rectangle([(380, 100), (700, 160)], radius=30, fill='#ffffff')
        draw.text((540, 130), '세금N혜택', fill='#3282f6', font=FONT_SMALL, anchor='mm')
        # 타이틀 (작게)
        draw.text((540, 240), p['image_title'], fill='#1a1a1a', font=FONT_TITLE, anchor='mm')
        # 큰 숫자/문구 (중앙 강조)
        draw.text((540, 410), p['image_big'], fill='#3282f6', font=FONT_BIG, anchor='mm')
        # 서브
        draw.text((540, 560), p['image_sub'], fill='#666666', font=FONT_SUB, anchor='mm')
        # 하단 CTA 영역
        draw.rectangle([(0, 900), (1080, 1080)], fill='#3282f6')
        draw.text((540, 970), '수수료 0원 · 1분 조회', fill='#ffffff', font=FONT_TITLE, anchor='mm')
        draw.text((540, 1030), 'ghdejr11-beep.github.io/cheonmyeongdang', fill=(255, 255, 255, 220), font=FONT_SMALL, anchor='mm')

        out_path = os.path.join(img_dir, f'post_{i+1:02d}.jpg')
        img.save(out_path, quality=92)
    print(f'[OK] 이미지 {len(CONTENT)}개 생성 ({img_dir})')

    # 5. 사용 가이드
    guide_path = os.path.join(OUTPUT, '00_README.md')
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(f"""# 세금N혜택 홍보 콘텐츠 30개

## 파일 구조
- `tax_content_30.json` — 전체 데이터 (JSON)
- `tax_content_30.csv` — Meta Business Suite Planner 일괄 업로드용
- `post_01_hook.txt` ~ `post_30_cta.txt` — 개별 복붙용 캡션 (30개)
- `images/post_01.jpg` ~ `images/post_30.jpg` — 1080x1080 이미지 30개

## 사용 순서

### 방법 A: Meta Business Suite Planner (일괄 예약)
1. https://business.facebook.com/latest/planner 접속
2. 세금N혜택 페이지 선택
3. "파일에서 가져오기" → `tax_content_30.csv` 업로드
4. 일정 자동 배치 확인
5. 예약 확정 → 자동 발행

### 방법 B: 수동 업로드 (더 빠름)
1. Meta Business Suite → 콘텐츠 → 게시물 만들기
2. `images/post_01.jpg` 업로드
3. `post_01_hook.txt` 열어서 캡션 복붙
4. 페이스북 + 인스타 동시 선택
5. 게시 또는 예약

### 방법 C: 인스타 스토리
- 이미지 30개를 인스타 스토리 9초씩
- 하루 3개 × 10일 분량

## 콘텐츠 테마 분류
- **hook (6개)** — 환급액 수치로 후킹
- **target (6개)** — 직업별 어필 (프리랜서/자영업/유튜버/배달/직장인/보험)
- **edu (6개)** — 세무 기초 지식
- **uniq (6개)** — 서비스 차별점 (수수료 0원, 보안, AI 상담)
- **cta (6개)** — 긴급 액션 유도

## 발행 추천 주기
- 매일 3개 (오전 9시, 오후 1시, 오후 7시)
- 10일 만에 30개 소진
- D-44 기준 5/20까지 완료 가능

## 채널별 최적화
- **인스타 피드**: 이미지 + 캡션 앞부분 125자
- **인스타 스토리**: 이미지만 (텍스트 겹침 주의)
- **페이스북**: 캡션 길어도 OK
- **쓰레드**: 캡션 500자 제한, 해시태그 생략
- **카카오 비즈채널**: 이미지 + 캡션 (줄바꿈 유지)
- **텔레그램**: HTML 태그 활용 가능
""")
    print(f'[OK] 사용가이드: {guide_path}')


if __name__ == '__main__':
    generate()
    print(f'\n전체 완료. 출력: {OUTPUT}')
