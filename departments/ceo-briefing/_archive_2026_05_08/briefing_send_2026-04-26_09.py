# -*- coding: utf-8 -*-
"""CEO 브리핑 09:00 (2026-04-26 토)"""
import os, json, time, urllib.request, urllib.parse

# Load secrets
for line in open('C:/Users/hdh02/Desktop/cheonmyeongdang/.secrets', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)

token = os.environ['TELEGRAM_BOT_TOKEN']
chat_id = os.environ['TELEGRAM_CHAT_ID']

def send_tg(msg):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = urllib.parse.urlencode({'chat_id': chat_id, 'text': msg}).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

DATE = "2026-04-26"
TIME = "09:00"

# ============== 메시지 1: 요약 + TOP 10 ==============
msg1 = f"""📊 CEO 브리핑 | {DATE} {TIME}

💰 팀별 수익 (어제~오늘)
🔮 천명당: ₩0 (Play 미출시·인앱 0건)
📚 전자책 (KDP): 데이터 없음 (CSV 수동 다운필요)
📺 미디어 (YT 4채널): $0.02 ≈ ₩28 / 누적조회 460,141 / 구독 2,323 / 어제 +11
🎮 게임 (HexDrop): ₩0 (비공개 테스트)
💼 세무: ₩0 (Vercel CODEF 연동 대기)
🛡️ 보험: ₩0 (GADP 보류)
🗺️ 여행지도: ₩0 (placeholder)
🛒 쿠팡 파트너스: 에러 (cp949 인코딩 - 수정 필요)
💰 총: ₩28 (실현) + 누적 자산 형성 중

🏆 오늘 해야할 일 TOP 10 (수익 빠른 순)
1. 세금N혜택 카피 "9.9% + 환급 0원시 100% 환불" 변경 (2시간) — 삼쩜삼 부정여론 흡수, 전환 2-3배
2. 천명당 9,900원 무제한 구독 SKU 추가 — 1000명×9900 = 990만/월 (포스텔러 검증 모델)
3. HexDrop 1.3 정식 출시 클릭 (Play Console) — 광고매출 즉시 발생
4. KDP 신규 3권 업로드 (사주일기/운세노트/프롬프트워크북) — 월 150-500만 잠재
5. Gumroad 8상품 노출 (텔레그램·X·인스타 SNS자동 가동중) — 누적 0건 → 첫 매출
6. 한국어 B2B 프롬프트팩 3종 (병원/세무/법률) 크티 등록 — 한국어 시장 진공
7. CODEF service_no 000007456002 Vercel env 연동 + tax-cert-all API — 환급 대행 첫 사용자
8. 천명당 v1.3 비공개 테스터 피드백 수집 + 정식출시 결정
9. YT 3채널 (Whisper/Wealth/Inner) 일일 자동 dry-run → live 전환 — 1k 구독 빠르게
10. 보험팀 GADP 겸업 결정 (법적 리스크 점검) — 결정 안 하면 5번째 부서 사장

자세한 부서 보고 → 메시지 2~10"""

# ============== 메시지 2: 천명당팀 ==============
msg2 = f"""🔮 천명당팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: 카카오페이/토스페이/광고 (모두 미가동)

📋 현재 진행상황
- v1.1 내부 테스트 출시 완료 (4/11)
- 무료/유료 사주 15개 섹션 완성
- 카카오 사주봇 실행중 (월렛 908652)
- 토스 인앱결제 허가 완료
- Play Console: 비공개 테스트 검토중
- 앱인토스: 사업자 검토중
- 꿈해몽: 데이터 239개 (350+ 확장 필요 - 치아/시험/전남친 등 미커버)
- 바이오리듬 좌우분할 UI 개선중

⚠️ 문제점
- Play Store 정식 출시 미완료 → 매출 0
- 인앱결제 SKU/구독 화면 미구현
- 명리학 감수자 표시 정책 미확정 (4/24 자제 결정 메모 있음)

🔧 개선 가능성
- 9,900원/월 무제한 구독 SKU 추가 → 1000명×9900 = 990만원/월 (포스텔러/헬로우봇 검증)
- 광고 NO + 무제한 정책 카피 → 점신/포스텔러 광고불만 흡수
- GPT 1:1 사주 건당 2,900원 → 100~500만/월 잠재
- 19,900원 프리미엄 상담권 (헬로우봇 26,000원 대비 30% 저렴)

🎯 앞으로 진행 방향
- 이번 주: 비공개 테스터 피드백 마감 + 정식 출시 결정
- 다음 주: 9,900원 구독 SKU 출시 + 카피 "광고 NO" 강조
- 이번 달: 첫 100명 유료 구독자 확보 → 월 100만 돌파"""

# ============== 메시지 3: 미디어팀 ==============
msg3 = f"""📺 미디어팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: $0.02 (CPM 추정)
- 누적 조회수: 460,141 / 구독 2,323
- 채널별:
  · Whisper Atlas (922구독, 340,159조회, 어제+8) - 베스트 [Idol Imagine] 107,211조회
  · Inner Archetypes (1,150구독, 87,843조회) - Carl Jung 시리즈
  · Wealth Blueprint (251구독, 32,139조회, 어제+3) - Credit Card 영상 918조회
  · Healing Sleep Realm (0구독, 0조회 - 신규)

📋 현재 진행상황
- YT 3채널 자동 파이프라인 dry-run 통과 (Whisper/Wealth/Inner)
- AI Side Hustle 쇼츠 매일 06:00 자동 (4/23 첫 영상 Gh3WSv0mZeM 성공, Pollinations Flux)
- Postiz Railway 셀프호스팅 ($5/월) - 텔레그램 연결됨, 6채널 단일 API
- KunStudio Bluesky(@kunstudio)+Discord 웹훅 검증 완료
- TikTok 워밍업 4/24~4/29 (Upload-Post $192/년 결제)
- 텔레그램 자동 홍보 매일 10·20시 가동
- KORLENS 콘텐츠 통합 완료
- fal.ai API 발급 완료
- 음성합성: ElevenLabs $5 결제 완료 (4/27 키 발급) + 대체 후보 보고서 D:\KunStudio_IP\
- 쿠팡 파트너스 단축링크 교체 TODO 남음

⚠️ 문제점
- X Tweet 발송 유료 ($100/월) 미가입
- IG/틱톡/YouTube 자동 미연결 (Postiz로 해결중)
- AI Side Hustle 채널 BLOCKED → 다음주 재등록 대기
- 어제 +11 조회 = 글로벌 viral 부재

🔧 개선 가능성
- TikTok 4/29 연결시 단일채널 일평균 1만 조회 가능 (kunstudio 프로필)
- Whisper Atlas K-pop 컨텐츠 viral 확장 (107k 조회 영상 패턴 복제)
- Bluesky/Discord/텔레그램 동시 발송 → 노출 3배
- 쿠팡 파트너스 15만 누적 시 자동 승인 → 매 SNS포스팅 링크 삽입

🎯 앞으로 진행 방향
- 이번 주: TikTok 워밍업 D-3 (4/29 연결) + AI Side Hustle 재등록 준비
- 다음 주: Postiz 6채널 단일 API 가동 → 일 발행 수 6배
- 이번 달: 누적 조회 100만 돌파 + 쇼츠 편집툴 결제 결정"""

# ============== 메시지 4: 보험팀 ==============
msg4 = f"""🛡️ 보험다보여팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: B2B SaaS 29,000원/월 (미가동)

📋 현재 진행상황
- 고객용/설계사용 데모 배포 완료
- API 심사 서류 준비 완료
- 서비스 소개서 작성 완료
- landing.html + 자산 5종 (overview/recommend/healthcheck/coverage 등) 추가됨 (어제 11건 편집)
- insurance_app.html 프로토타입 가동

⚠️ 문제점
- GADP 겸업 승인 필요 (법적 리스크) → 4/17부터 BLOCKED
- 보험업법 검토 미완료 (CLAUDE.md 법적 리스크 회피 최우선 룰 적용)
- B2B SaaS 사전등록 페이지 미완성

🔧 개선 가능성
- 보맵·굿리치는 소비자용만 → B2B2C 공백 정확히 노림
- 5기능 번들 (고객관리+계약조회+보장분석+청구자동화+견적서) → 29,000원/월
- 200~1,000만/월 잠재 (수익성 TOP10 #2)
- 보험설계사 100명 사전등록 검증 후 본 개발

🎯 앞으로 진행 방향
- 이번 주: GADP 겸업 결정 (법무팀 자문 필요) → 진행 or 사장 결정
- 다음 주: 결정 시 사전등록 랜딩 + Stripe/토스 결제 폼
- 이번 달: 결정에 따라 보험설계사 100명 검증 or 부서 종료"""

# ============== 메시지 5: 전자책팀 ==============
msg5 = f"""📚 전자책팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: $0 (KDP CSV 수동 다운필요)
- 누적 수익: 검증 미완료
- Gumroad: 8상품 등록, 누적 0건 (🚨 노출/마케팅 부재)
  · 퇴사 후 1인 사업 플레이북
  · 클로드 코드 실전 가이드
  · 2026 AI 부업 수익 리포트
  · 노션 템플릿 50개
  · Claude·ChatGPT 1,000개 프롬프트팩
  · AI 부업 시스템 PREMIUM
  · AI로 월 500만원 자동화
  · AI 부업 시작 가이드 (무료 샘플)

📋 현재 진행상황
- KDP 10/20권 심사중 + 디지털 상품 10종 생성
- 어제 459건 편집 (kdp_description.html 4종, aplus 자산 등)
- 신규 3권 준비: ai-prompt-workbook, fortune-notebook, saju-diary, zodiac-mandala-coloring
- 표지 일괄 수정 (4/19) - Deokgu Studio 저자명 통일
- 4/24 WebP25% 변환 작업 완료

⚠️ 문제점
- Gumroad 8상품 누적 판매 0건 → 노출/마케팅 부재
- KDP 표지 거절 위험 (템플릿 텍스트 금지/spine 0.5인치 룰)
- KDP 2025 크리스마스 계정정지 사건 → 신뢰도 하락 (Gumroad 병행 안전망 필요)
- 한국어 시장 미진출

🔧 개선 가능성
- Gumroad 노출: 미디어부 SNS 4채널 자동연동 (일일 1포스팅) → 첫 매출
- KDP 한국어 사주일기/저널/프롬프트워크북 시리즈화 → Amazon Best Seller 카테고리 (Journals/Coloring/Logbooks)
- 150~500만원/월 잠재 (수익성 TOP10 #5)
- KDP 3권 신규 업로드 즉시 가능

🎯 앞으로 진행 방향
- 이번 주: KDP 신규 3권 업로드 + Gumroad SNS 자동 홍보 가동
- 다음 주: 한국어 저널 시리즈 5권 출시
- 이번 달: KDP 20권 완료 + Gumroad 첫 100건 매출"""

# ============== 메시지 6: 게임팀 ==============
msg6 = f"""🎮 게임팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0 (비공개 테스트 단계)
- 광고매출 미가동 (AdMob Publisher ID 미설정)

📋 현재 진행상황
- HexDrop 1.3 비공개 테스트 게시 완료 (4/10)
- 테트리스 AI 대결 게임 완성
- 어제 mtime 변화 0건 (개발 정체)
- 천명당 미니앱 .ait 빌드 완료 (앱인토스 등록 대기)
- 테스터 피드백 수집중

⚠️ 문제점
- HexDrop 1.3 정식 출시 미완료 → 매출 0
- AAB 업로드는 사용자 수동 (MCP Chrome hidden file input 트리거 불가)
- AdMob Publisher ID 미설정 → 광고 매출 불가
- QA 부족

🔧 개선 가능성
- HexDrop 1.3 정식 출시 클릭 1회 → 즉시 광고 매출 발생
- AdMob Publisher ID 등록 후 .secrets에 ADMOB_PUBLISHER_ID 저장
- 테트리스 AI 대결 → 글로벌 캐주얼 시장 (인기 카테고리)
- 새 캐주얼 게임 매주 1개 (HTML5+JS, 9시 실행 자동)

🎯 앞으로 진행 방향
- 이번 주: HexDrop 1.3 정식 출시 클릭 + AdMob 등록
- 다음 주: 천명당 미니앱 앱인토스 콘솔 등록 (사업자 검토 통과시)
- 이번 달: 신규 게임 4개 + AAB 업로드 자동화 우회법 탐색"""

# ============== 메시지 7: 세무팀 ==============
msg7 = f"""💼 세무팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0 (베타 단계)
- 누적 수익: ₩0
- 수익 모델: 9.9% 환급 수수료 (삼쩜삼 20% / 토스 15-20% 사이 가격공격)

📋 현재 진행상황
- 종소세 계산기 완성 + Vercel 배포 (tax-n-benefit-api.vercel.app)
- CODEF 프로덕션 승인됨 (4/22 확인)
- service_no: 000007456002, authorities PUBLIC 포함 전체
- 어제 32건 편집 (index.html, app_subsidy/coaching/chat 자산)
- index_v_pre_top1_copy.html 카피 작업중
- support.js TODO: Claude Agent SDK 분류 재판정 + auto_fix PR

⚠️ 문제점
- Vercel env 미연동 (CODEF_CLIENT_ID/SECRET/PUBLIC_KEY 추가 필요)
- /v1/kr/public/nt/proof-issue/tax-cert-all API 미연동
- 메인 카피 미수정 (수익성 TOP10 #1 = 카피 한 줄로 매출 점프)

🔧 개선 가능성 (★★★ 최우선)
- 카피 변경: "9.9% 정액 + 환급 0원시 100% 환불 보장" → 전환율 2-3배
- 추정 매출: 500~3,000만/월 (수익성 TOP10 #1, 페인 TOP3 동시 해결)
- 부가가치 번들: 환급+병원비+통신비 (구독형) → 200~800만/월
- 1단계 Vercel MVP → 유저 1000명/월매출 100만 넘으면 AWS 이전

🎯 앞으로 진행 방향
- 이번 주 (★★★): 카피 변경 + Vercel env 추가 + tax-cert-all 연동
- 다음 주: 결제 라우터 (토스페이) + 환불 보장 정책 페이지
- 이번 달: 첫 100명 환급 처리 → 월 500만 돌파 (가장 빠른 매출원)"""

# ============== 메시지 8: 여행지도팀 ==============
msg8 = f"""🗺️ 여행지도팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 모델: 미정 (placeholder 상태)

📋 현재 진행상황
- placeholder 상태
- 어제 4건 편집 (logs/poi_2026-04-26.json, korlens 통합, landing.html)
- KORLENS 콘텐츠 통합 - 외국인 관광 데이터 자동 수집중
- 2026 관광데이터 공모전 출품 완료 (4/18) - 별도 KORLENS 부서

📋 KORLENS 별도 보고
- Vercel 배포 완료 + AI 큐레이터 챗봇 가동
- 카카오 KOE205 해결 완료 (4/22)
- Supabase + Google OAuth 연동중
- 공모전 예비심사 5월 예정 → 통과시 개발 지원금 + 컨설팅

⚠️ 문제점
- 여행지도 부서 자체는 placeholder 단계 (구체적 제품 없음)
- 수익 모델 미정의

🔧 개선 가능성
- KORLENS 외국인 모드 UI 영문화 v2 → 글로벌 트래픽 흡수
- 여행지도와 KORLENS 통합 → 한 부서로 합쳐 효율화
- 공모전 11월 시상식 통과시 정부 지원금 + 미디어 노출

🎯 앞으로 진행 방향
- 이번 주: 여행지도 부서 정체성 결정 (KORLENS 통합 or 별도 제품)
- 다음 주: KORLENS 영문화 v2 작업
- 이번 달: 5월 예비심사 결과 대기 + 외국인 트래픽 검증"""

# ============== 메시지 9: 지원부서 (법무 + 데이터) ==============
msg9 = f"""⚖️ 법무정책부: privacy.html ✅ / terms.html ✅
- 사업자 등록 완료 (홍덕훈 / 쿤스튜디오 / 경주 / 간이과세 / SW개발업)
- 인앱결제·광고·토스페이 모두 가능
- 보험팀 GADP 겸업 → 보험업법 검토 BLOCKED 상태
- KDP 표지 거절방지 룰 (템플릿 텍스트 금지, spine 0.5인치)
- 자동화 개인정보 배제 룰 (브랜드명만 사용)

📊 데이터분석부: GA4 (G-90Y8GPVX1F) 설치 완료
- 부서별 mtime 변화 (어제):
  · ebook 459건 (KDP description 일괄 수정)
  · digital-products 109건 (legal/tax 핀터레스트 핀)
  · media 38건 (YT 4채널 토큰/스크립트)
  · tax 32건 (index.html, 자산)
  · insurance 11건 (landing 자산)
  · ceo-briefing 7건 (autofix)
  · security 5건 (uptime monitor)
  · travelmap 4건 (poi/korlens)
  · korlens 3건 (icon)
  · cheonmyeongdang 2건 (dreams 로그)
  · intelligence 1건 (revenue_pain)
  · secretary 1건 (edit_queue)
  · game 0건 ⚠️ (정체)

⚠️ 데이터 이슈
- 쿠팡 파트너스 cp949 인코딩 에러 - 수정 필요
- KDP CSV 자동 다운 미연동 - 수익 데이터 공백
- AdMob Publisher ID 미설정 - 광고 매출 측정 불가
- Play 서비스 계정 JSON 미저장 - Play Console 매출 측정 불가
- Vercel Analytics API 연동 TODO (intelligence/sales_collector.py)"""

# ============== 메시지 10: 수집부 ==============
msg10 = f"""🔍 수집부 보고 | {DATE}
(WebSearch + 4/25 수집부 자체 분석 기반)

😤 사람들이 불편해하는 것 TOP 10
1. 삼쩜삼 "14만원 환급 예상→실제 0원, 수수료 2.9만 날림" — 한국경제 2025-02-16 — 세금N혜택 "환급 0원시 100% 환불" 카피 즉시 가능 — 2시간
2. 토스인컴/삼쩜삼 수수료 15-20% 너무 비쌈 — 루리웹·블라인드 — 9.9% 정액제 가격공격 — 2시간 (카피 동시)
3. 보맵 가족계약 조회 불완전·타사 미연동 — Google Play 리뷰 — 보험설계사 SaaS B2B2C로 우회 — 5일 사전등록
4. 점신 광고 과다로 행운패스 강제 — Google Play 1점 리뷰 다수 — 천명당 광고 NO + 구독 ONLY — 3일 SKU
5. KDP 2025 크리스마스 계정정지 + AI 챗봇 루프 — Trustpilot 1.X점 — KDP 한국어 + Gumroad 병행 — 5일 (Gumroad 노출)
6. SSEM 신고 지연 계속 미뤄짐 (2025.5) — 앱스토어 리뷰 — 세금N혜택 "3영업일 보장 SLA" 정책 — 1주
7. 포스텔러 과금 많이 했는데 사주 안 맞음 — Threads·DC — 명리학 감수자 실명 공개 + 환불 보장 — 1일 (정책 결정 필요)
8. 헬로우봇 월 26,000원 유료 전환 과함 — 앱스토어 — 천명당 19,900원 프리미엄 (30% 저렴) — 3일 (구독 SKU 같이)
9. PromptBase 판매자>구매자, 마켓 포화 — Reddit, godofprompt — 한국어 B2B 시장 (포화 ZERO) — 5일 (3종 등록)
10. 인디해커 60분 답 못달면 안보임 — IndieHackers·X — 미디어부 4채널 자동 응답 봇 — 3일

💰 수익 창출 좋은 모델 TOP 10
1. 세금N혜택 환급 9.9% — 시장 ₩수천억 — 진입장벽 中 — 월 500-3000만 — 삼쩜삼 부정여론 흡수 NOW
2. 보험설계사 SaaS 29,000원/월 — 시장 ₩2000억 (보험인 50만명) — 易 — 200-1000만 — 보맵 B2B 공백
3. 천명당 9,900원 무제한 — 시장 ₩100억(포스텔러 검증) — 易 — 200-1000만 — 광고 NO 차별화
4. 환급+병원비+통신비 번들 구독 — 시장 ₩500억+ — 中 — 200-800만 — 국세청 무료 → 부가가치 공백
5. KDP 한국어 저널/플래너 — 시장 ₩50억(국내) — 易 — 150-500만 — Amazon Best Seller 카테고리 검증
6. GPT 1:1 사주 건당 2,900원 — 점신 행운패스 대체 — 中 — 100-500만 — AI 1:1 공백
7. 크티 프로 구독 9,900원/월 — PromptHero $19.99 한국형 — 難 — 100-500만 — 한국어+더싸게
8. 한국어 B2B 프롬프트팩 (병원/세무/법률) — 시장 ₩수십억 진공 — 中 — 100-400만 — PromptBase 한국어 사례 (월 150-250)
9. 헬로우봇형 프리미엄 상담권 19,900원 — 시장 ₩50억 — 中 — 100-500만 — 30% 저렴
10. 크티 추천·제휴 20% 커미션 — 시장 형성중 — 中 — 50-300만 — PromptBase 모델 한국어 첫진입

★★★ 시너지 ★★★★★ 항목 즉시 실행 우선:
- 1순위: 세금N혜택 9.9% + 환불보장 카피 (수익 #1, 페인 #1+#2+#6 동시)
- 2순위: 천명당 9,900원 무제한 (수익 #3, 페인 #4+#7+#8 동시)
- 3순위: 한국어 B2B 프롬프트팩 (수익 #8, 페인 #9 진공점령)

📌 부가 발견
- 국세청 원클릭 무료 출시 → 단순 환급은 무료. 부가가치 번들로 차별화 필수
- KDP 신뢰도 하락 → Gumroad 병행이 안전망
- Gumroad 매출 1위 카테고리 = Software Development $65.8M (32%) → 크티/프롬프트팩 정확히 매치
- 인디해커 "60분 응답 윈도우" 트렌드 → 자동 응답 봇 가치 상승"""

messages = [msg1, msg2, msg3, msg4, msg5, msg6, msg7, msg8, msg9, msg10]

results = []
for i, msg in enumerate(messages, 1):
    try:
        r = send_tg(msg)
        results.append(f"msg{i}: ok={r.get('ok')} len={len(msg)}")
        time.sleep(0.5)
    except Exception as e:
        results.append(f"msg{i}: ERROR {e}")
        time.sleep(0.5)

print("\n".join(results))
print(f"\nTotal: {len(messages)} messages")
