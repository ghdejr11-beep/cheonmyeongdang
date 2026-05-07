# -*- coding: utf-8 -*-
"""CEO Daily Briefing — 2026-05-07 12:10 (점심 브리핑)
10개 메시지: 요약+TOP10 / 7개 부서 상세 / 법무+데이터 / 수집부
"""
import os, json, urllib.request, urllib.parse, time

# Load secrets
secrets_path = 'C:/Users/hdh02/Desktop/cheonmyeongdang/.secrets'
for line in open(secrets_path, encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)
token = os.environ['TELEGRAM_BOT_TOKEN']
chat_id = os.environ['TELEGRAM_CHAT_ID']

def send_tg(msg):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = urllib.parse.urlencode({
        'chat_id': chat_id,
        'text': msg,
        'disable_web_page_preview': 'true',
    }).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

DATE = '2026-05-07'
TIME = '12:10'

# ================================================================
# 메시지 1: 요약 + TOP 10 해야할일
# ================================================================
msg1 = f"""📊 CEO 브리핑 | {DATE} {TIME}
(글로벌 SaaS 라이브 D+1, 점심 브리핑)

💰 어제(5/6) 팀별 수익 (unified_revenue.py)
🔮 천명당: ₩0 (V2 PG/PayPal collector 미연결, 실수익 누락 가능)
📚 전자책 (KDP/Gumroad): ₩0 (KDP scraper no_data — 세션 만료 의심)
📺 미디어 (AdMob/YT): ₩0 (impression 미발생)
🎮 게임 (HexDrop): ₩0 (1.3 비공개 테스트만)
💼 세무: ₩0 (프로토타입, 출시 전)
🛡️ 보험: ₩0 (API 심사대기)
🗺️ 여행 (KORLENS): ₩0 (Etsy 리스팅, AID 코미션 대기)
💰 어제 합계: ₩0 / 7일 평균 ₩0 / 30일 누적 ₩0

⚠️ 매출 0의 진짜 원인 = 트래픽/유입 단계 (인프라는 살아있음)
⚠️ 누락 채널: PayPal, Etsy, V2 PG, Lemon Squeezy → collector 추가 필요

🏆 오늘 해야할 일 TOP 10 (수익 직결순)
1. KDP scraper 'no_data' 진단·복구 — 매출 0 원인 1순위, 토큰 갱신 + 셀렉터 점검 (auto)
2. PayPal collector 추가 — Smart Buttons 어제 라이브, 진짜 매출 발생 가능성 가장 높음 (auto)
3. Etsy collector 추가 — KORLENS 글로벌 리스팅, 어제 매출 누락 가능 (auto)
4. 천명당 V2 PG 매출 합산 endpoint — DB 자체 집계 (auto)
5. Pinterest 핀 5개 추가 발행 — 글로벌 트래픽 leading indicator (auto)
6. SEO 블로그 4개 언어 발행 (글로벌 v3.5 indexing 가속) — auto
7. 인플라 50건 reply monitor v2 강화 → 응답 분류·대응 자동화 (auto)
8. KORLENS Klook AID 120494 commission 트래킹 dashboard (auto)
9. 게임 dev: Tetris AI 대결 v2 — Mini-app 등록 준비 (auto)
10. 토스/갤럭시아 우편 회신 진행상황 점검 — 평일 우편 가능, 사용자 확인만 (USER)
"""

# ================================================================
# 메시지 2: 천명당팀
# ================================================================
msg2 = f"""🔮 천명당팀 상세 보고 | {DATE}

💰 수익 현황
- 어제(5/6) 수익: ₩0 (V2 PG / PayPal collector 미연결 = 실수익 누락 가능)
- 누적 수익: 추적 불가 (V2 PG endpoint 미합산)
- 수익 경로: PayPal Smart Buttons (글로벌 라이브 5/3) / V2 KR PG / 광고 (AdMob 미발생)
- 매출 unlock 잠재: ₩2.5억~수십억 (4언어 SaaS 인플라 50명 outreach 중)

📋 현재 진행상황
- v3.5 글로벌 SaaS 라이브 (5/6, ko/en/ja/zh 4언어 × 6페이지)
- PayPal Smart Buttons 라이브 (5/3, confirm-payment.js)
- V2 KR PG 라이브 (한국결제네트웍스+갤럭시아+카카오페이)
- AppSumo / RapidAPI / Etsy 가이드 작성 완료 (5/6)
- VC 3 pitch deck (Antler / Kakao Ventures / D2SF) 완료
- 11개 schtask 가동 중 (briefing/blog/SNS/replies)
- 인플라 50명 outreach 발송 완료 (5/6)
- Play Console 비공개 테스트 검토 중
- 카카오 사주봇 실행 중 (월렛 908652)
- 앱인토스 사업자 검토 중

⚠️ 문제점
- V2 PG / PayPal 매출 unified_revenue.py 미합산 → 진짜 매출 0인지 확인 불가
- 인플라 50명 응답률 미상 (monitor v2 강화 진행 중)
- 4언어 SEO 인덱싱 lag (글로벌 라이브 D+1, 트래픽 7~30일 후 가시화)
- AppSumo / RapidAPI 가이드만 있고 실제 리스팅 안 됨

🔧 개선 가능성
- PayPal/Etsy/V2 collector 추가 → 진짜 매출 노출 (오늘 자동 처리, +₩? 가시화)
- Pinterest 핀 일 5개 → 30일간 트래픽 +20% 추정
- 인플라 답장 자동 분류 + 대응 → conversion 2배
- AppSumo 리스팅 실제 등록 → LTD 매출 $10K~$50K 추정
- VC pitch 발송 (Antler 5/15 D-Day 마감 추정) → 시드 unlock

🎯 앞으로 진행 방향
- 이번 주: collector 4채널 추가 + Pinterest 핀 30개 + 인플라 reply monitor v2 라이브
- 다음 주: AppSumo 실제 리스팅 + RapidAPI 등록 + VC 3사 pitch 발송
- 이번 달: 글로벌 MRR ₩100만 돌파 (PayPal+V2 합산), AppSumo LTD 첫 매출
"""

# ================================================================
# 메시지 3: 미디어팀
# ================================================================
msg3 = f"""📺 미디어팀 상세 보고 | {DATE}

💰 수익 현황
- 어제(5/6) AdMob 수익: ₩0 (impression 0, app 트래픽 미발생)
- YouTube 수익: ₩0 (videoCount=0 채널 다수)
- Pinterest 트래픽: 어제 핀 3개 발행 (KORLENS), 클릭 데이터 추적 중
- 어필리에이트 (Klook AID 120494): commission live, 매출 0 (D+1)

📋 현재 진행상황
- 활성 5채널: Whisper Atlas / Wealth Blueprint / Inner Archetypes / AI Side Hustle / Sori Atlas
- Sori Atlas 신규: Suno Pro 음원 + Hetzner VPS 24/7 송출 준비 (5재생목록)
- K-Wisdom 채널 (피벗) 글로벌 K-콘텐츠 채널 가동
- Upload-Post $192/년 결제, 5/5 프로필 한도 사용 중
- Postiz 셀프호스트 가동 (Railway, $5/월), 텔레그램+Bluesky 연결
- KORLENS 2 블로그 + Pinterest 3 핀 어제 발행 (5/6)
- TikTok 워밍업 4/24~4/29 완료, kunstudio 프로필 활성

⚠️ 문제점
- Whisper Atlas videoCount=0 (YouTube 2026 AI slop 정책 영향, K-Wisdom으로 피벗)
- Postiz Instagram OAuth 포기 (multi_poster.py post_instagram() 직접 사용)
- AdMob impression 0 = 천명당/HexDrop 앱 트래픽 미발생 (앱 출시·노출 부족)
- YouTube 5채널 수익화 임계 (구독 1000명+ 시청 4000h) 미달

🔧 개선 가능성
- Sori Atlas Lofi 24/7 송출 → AdSense + Suno 트래픽 unlock 추정 ₩30만/월
- Pinterest 핀 자동 발행 일 5개 → KORLENS 글로벌 SEO trafic +200%
- 어필리에이트 다채널 (Klook+Booking+Amazon Associate) → commission +3채널
- TikTok Shorts EN 자동 발행 (departments/tiktok_shorts_en) → bilingual 트래픽
- YouTube Shorts MrBeast-style hook → CTR +50% 목표

🎯 앞으로 진행 방향
- 이번 주: Sori Atlas Hetzner VPS 송출 시작 (CX22 ₩7,000/월), Pinterest 핀 30개
- 다음 주: TikTok Shorts EN 일 3개 발행 자동화, AdMob app 신규 1개 (HexDrop 1.3)
- 이번 달: 5채널 중 1채널 수익화 임계 돌파, 어필리에이트 첫 commission 발생
"""

# ================================================================
# 메시지 4: 보험다보여팀
# ================================================================
msg4 = f"""🛡️ 보험다보여팀 상세 보고 | {DATE}

💰 수익 현황
- 어제(5/6) 수익: ₩0 (서비스 미출시, API 심사대기)
- 수익 모델: 보험 비교 후 가입 시 commission (보험사 제휴)
- 예상 단가: 1건 가입당 ₩30,000~₩100,000 commission

📋 현재 진행상황
- insurance_app.html (랜딩 페이지) 완성
- API 심사 서류 준비 완료 (보험연구원·보험개발원)
- 서비스 소개서 작성 완료
- CODEF 정식 신청 대기 (4/17)
- 보험업법 사전 체크 (4/24 메모리, 법적 리스크 회피 강제)

⚠️ 문제점
- API 심사 lag (보험연구원·개발원 심사 1~3개월 소요 추정)
- CODEF 정식 신청 진행 status 불투명 (4/17 이후 상태 확인 필요)
- 보험업법 sales 자격증 (보험설계사) 미보유 → 비교만 가능, 직접 판매 불가
- 보험사 제휴 미체결 (commission 협상 단계 X)

🔧 개선 가능성
- API 심사 가속 (담당자 follow-up 메일 자동 발송) → 1~2개월 단축
- 보험설계사 자격증 취득 (사용자) → 직접 판매 unlock
- 비교 콘텐츠 SEO 블로그 50개 발행 → 트래픽 검증 후 제휴 협상력 ↑
- KAKAO 알림톡 비교 결과 자동 푸시 → conversion 2~3배

🎯 앞으로 진행 방향
- 이번 주: CODEF 신청 status 확인, 담당자 follow-up 메일 발송 (auto)
- 다음 주: 보험 비교 SEO 블로그 10개 발행 (trafic 검증)
- 이번 달: API 심사 통과 후 보험사 1곳 제휴 (협상 시작)
"""

# ================================================================
# 메시지 5: 전자책팀
# ================================================================
msg5 = f"""📚 전자책팀 상세 보고 | {DATE}

💰 수익 현황
- 어제(5/6) 수익: ₩0 (KDP scraper no_data, 실수익 누락 가능)
- 추정 누적: KDP 27책 출간, Gumroad 4종 라이브
- Gumroad cross-link git ffaebbc 완료 (5/5)
- Mega Bundle $29.99 라이브 (5/1)

📋 현재 진행상황
- KDP 27책 출간 완료
- Gumroad 4종 라이브 (B2B 가이드 3종 + Mega Bundle)
- BookK ISBN 발급 형식 (다이어리/플래너 등) 100% 반려 → KDP만 사용
- KDP 풀 자동화 금지 (anti-bot RISK), 클립보드 헬퍼까지만
- 표지 일괄 수정 완료 (4/19)
- D+30 winback 메일 시퀀스 가동 (5/1)

⚠️ 문제점
- KDP scraper 'no_data' (5/6) → 세션 만료 의심, 매출 진단 불가
- KDP 27책 중 누가 실제 매출 발생하는지 trafic 데이터 없음 (책별 royalty 추적 X)
- Gumroad 4종 conversion 수치 추적 미설정
- 베스트셀러 카테고리 미등극 → 노출 부족

🔧 개선 가능성
- KDP scraper 토큰 갱신 → 매출 가시화 (오늘 자동 처리)
- KDP 책별 dashboard (성과 top 5 / bottom 5) → top에 광고비 집중
- Gumroad GA4 + UTM → conversion funnel 가시화
- KDP A+ Content 미적용 책 → A+ 추가 시 conversion +10~30%
- 베스트셀러 키워드 리서치 (Helium 10 등) → 카테고리 진입

🎯 앞으로 진행 방향
- 이번 주: KDP scraper 복구 + 책별 매출 dashboard
- 다음 주: 상위 5책 A+ Content 추가, Gumroad GA4 연결
- 이번 달: KDP 신규 5권 출간, Gumroad MRR ₩30만 돌파
"""

# ================================================================
# 메시지 6: 게임팀
# ================================================================
msg6 = f"""🎮 게임팀 상세 보고 | {DATE}

💰 수익 현황
- 어제(5/6) 수익: ₩0 (HexDrop 1.3 비공개 테스트만)
- 수익 모델: 인앱결제 + AdMob (천명당 동일 인프라)
- HexDrop 1.3 비공개 테스트 게시 완료 (4/10)

📋 현재 진행상황
- HexDrop 1.3 비공개 테스트 게시 완료
- 사주팡 게임 50% MVP (5/1)
- gem-cascade v_pre (aibattle/bgm/fx/round) 4 변형 개발
- stack-builder v_pre (aibattle/bgm/character/redesign) 4 변형
- tetris-ai-battle 폴더 존재
- 게임 dev 부서 가동 (departments/game)

⚠️ 문제점
- HexDrop 1.3 비공개 테스트만, 정식 출시 전 → 매출 0
- 사주팡 50% MVP 멈춤 → 출시 lag
- gem-cascade / stack-builder v_pre 다수, 출시 결정 미정
- AdMob 광고 단가 불명 (impression 미발생)

🔧 개선 가능성
- HexDrop 1.3 정식 출시 → AdMob impression 첫 발생 (+₩? 미상)
- 사주팡 MVP 완성 → 천명당 cross-sell unlock
- gem-cascade 변형 1개 선택 → 정식 출시 (4 변형 중 best 변형 평가 후)
- 글로벌 출시 (영문 UI) → 시장 10배 확대

🎯 앞으로 진행 방향
- 이번 주: HexDrop 1.3 정식 출시 (사용자 1클릭만 남음)
- 다음 주: 사주팡 MVP 100% 완성, 비공개 테스트 등록
- 이번 달: HexDrop 1.3 + 사주팡 + gem-cascade 1변형 = 3 게임 라이브, AdMob 첫 매출
"""

# ================================================================
# 메시지 7: 세무팀
# ================================================================
msg7 = f"""💼 세무팀 상세 보고 | {DATE}

💰 수익 현황
- 어제(5/6) 수익: ₩0 (서비스 미출시)
- 수익 모델: 수수료 0% (Freemium → 프리미엄 ₩9,900/월)
- 시장: 한국 1인사업자 800만명, 간이과세 70% (사용자 본인도 포함)

📋 현재 진행상황
- 기획서 완성 (수수료 0% 모델)
- 프로토타입 완성 (modoo.or.kr 통한 신청, 5/5 메모리)
- 모두의 창업 4/19 Tech Track 신청 완료 (5/5 발견)
- 정부지원 K-Startup AI리그 / 관광AI 진행 중

⚠️ 문제점
- 프로토타입만, 실제 출시 안 됨 → 매출 0
- 카카오페이 비즈니스 가입 status (사업자등록 보유, 가입 가능)
- 세무 자격 (세무사) 미보유 → "세무 안내·계산기"까지만 가능, "세무대행" 불가
- 경쟁자 (삼쩜삼·자비스) 기존 점유 → 차별화 포인트 약함

🔧 개선 가능성
- 출시 → 1인사업자 SEO 트래픽 unlock (간이과세·종합소득세 키워드)
- 차별화: 수수료 0% + 사주(천명당) cross-sell (시너지 unique)
- 정부지원 K-Startup AI리그 / 관광AI 통과 시 자금 unlock
- 카카오페이 비즈니스 + 알림톡 → conversion 채널 강화

🎯 앞으로 진행 방향
- 이번 주: 프로토타입 → 베타 출시 (랜딩 페이지 라이브)
- 다음 주: SEO 블로그 10개 (종합소득세 5/31 대비)
- 이번 달: 베타 가입자 100명, 정부지원 1개 통과
"""

# ================================================================
# 메시지 8: 여행지도팀 (KORLENS)
# ================================================================
msg8 = f"""🗺️ 여행지도팀 (KORLENS) 상세 보고 | {DATE}

💰 수익 현황
- 어제(5/6) 수익: ₩0 (commission lag, AID live D+1)
- 수익 모델: Klook AID 120494 commission (5~10%) + Etsy 리스팅 + 광고
- 매출 unlock 잠재: 글로벌 K-tourism 시장 ₩? (관광AI grant 통과 시 가속)

📋 현재 진행상황
- KORLENS 현지인 픽 구축 (Supabase + Google OAuth)
- Klook AID 120494 commission live (5/6)
- KOE205 카카오 OAuth 해결 (4/22)
- Etsy 리스팅 진행 중
- KoDATA 등록 D-2 (5/12 마감)
- K-Startup 관광AI grant 5/20 마감

⚠️ 문제점
- KOE205 해결됐지만 사용자 Client ID 수정 status 불명
- Etsy 리스팅 actual 등록 status 확인 필요
- KoDATA 사전등록 미시작 (5/12 마감 D-5)
- 관광AI grant 5/20 D-13, 사업계획서 미완성

🔧 개선 가능성
- KoDATA 등록 → 관광AI grant 자격 unlock (₩수천만 grant)
- 관광AI grant 통과 → 글로벌 마케팅 자금 unlock
- Etsy 리스팅 등록 → 글로벌 K-tourism 트래픽 unlock
- Klook AID + Booking AID + Trip.com AID = 3채널 commission

🎯 앞으로 진행 방향
- 이번 주: KoDATA 등록 (D-5), 관광AI 사업계획서 50% (auto draft)
- 다음 주: 관광AI grant 제출 (D-13), Etsy 리스팅 라이브
- 이번 달: 관광AI 통과, 글로벌 SEO 트래픽 첫 매출 commission
"""

# ================================================================
# 메시지 9: 지원부서 (법무 + 데이터분석)
# ================================================================
msg9 = f"""⚖️ 법무정책부 + 📊 데이터분석부 보고 | {DATE}

⚖️ 법무정책부
- privacy.html ✅ (위탁업체 8개 명시)
- terms.html ✅ (천명당)
- 보험업법 사전 체크 (4/24) ✅
- 광고에 특정 업체·연예인·IP 거론 금지 (5/1, Samsung/BTS/Squid Game 등)
- 개인정보 자동화 배제 ✅ (포스트에 본인·고객 PII 삽입 금지)
- 본인 휴대폰 010-4244-6992 마스킹 ✅
- 법인 070-8018-7832 마스킹 ✅
- 남은 이슈:
  · KORLENS / 세금N혜택 / 보험다보여 privacy 페이지 (별 도메인) 미작성 가능성
  · KDP 27책 저작권 표기 일관성 (Deokgu Studio 통일) 점검 필요
  · 글로벌 라이브 (4언어) → GDPR/CCPA 쿠키 동의 미적용 가능성

📊 데이터분석부
- GA4 (G-90Y8GPVX1F) 천명당 ✅
- unified_revenue.py 5채널 collector (admob/youtube/gumroad/kdp/kreatie) 가동
- Vercel Analytics 천명당 ✅
- 누락 collector: PayPal, Etsy, V2 PG, Lemon Squeezy → 4채널 추가 시급
- KDP scraper no_data (5/6) → 진단 필요
- 트래픽: 글로벌 라이브 D+1, 4언어 SEO 인덱싱 7~30일 lag
- 인플라 50건 reply rate 추적 미설정 → monitor v2 강화 중
- conversion funnel: 트래픽 → 결제 → MRR step별 GA4 이벤트 미설정
"""

# ================================================================
# 메시지 10: 수집부 (10 불편 + 10 수익)
# ================================================================
msg10 = f"""🔍 수집부 보고 | {DATE}

(2026 5월 글로벌·국내 트렌드 리서치 기반)

😤 사람들이 불편해하는 것 TOP 10
1. AI 도구 도입 후 통제력 ↓ + 측정 복잡성 ↑ (마케터 62%) — Thunderbit/SaaStr 2026 — Claude: GA4 대시보드 + AI 알림 통합 SaaS — 1주
2. 1인사업자 종합소득세 5/31 마감, 간이과세 70% 헷갈림 — 한국 800만 — Claude: 천명당 + 세금N혜택 cross-sell 자동 안내 — 3일
3. 프리랜서 다국적 결제 환율 손실 (PayPal 4.4%+) — 글로벌 — Claude: Wise/Lemon Squeezy 가이드 SaaS — 2주
4. KDP 자비출판 표지 거절 반복 (다이어리/플래너 100%) — 메모리 4/19 — Claude: KDP 거절 방지 templater 무료 SaaS — 1주
5. 보험 비교 후 가입 시 commission 정보 불투명 — 보험사 제휴 — Claude: 보험다보여 commission 명시 + 비교 — API 심사 후 1주
6. K-tourism 외국인 한국 여행 정보 영문 부족 (Trip Advisor 외) — KORLENS 시장 — Claude: KORLENS Etsy 리스팅 + 영문 SEO 30개 — 2주
7. 사주·운세 외국인 영문/일문/중문 콘텐츠 부족 — 천명당 v3.5 라이브 — Claude: 4 언어 SEO 블로그 일 4개 자동 발행 — auto 진행 중
8. SaaS founder GDPR/CCPA compliance 부담 (data privacy from day one) — bigideasdb — Claude: privacy 자동 생성 SaaS — 1주
9. 자영업자 카카오페이/토스페이 가입 lag (서류 5+ 종) — 5/2 메모리 — Claude: PG 가입 가이드 SaaS + 서류 templater — 1주
10. AI slop YouTube 채널 수익화 거부 (faceless+template+volume) — 메모리 5/1 — Claude: K-Wisdom 차별화 가이드 + 영상 OOH 다각화 SaaS — 2주

💰 수익 창출 좋은 모델 TOP 10
1. AI 마케팅 ROI 대시보드 SaaS — TAM ₩글로벌 SaaS $375.6B / 진입 中 / ₩200만/월 / 2026 마케터 87% AI 사용
2. 1인사업자 세무 자동 (천명당+세금N혜택) — TAM 800만 한국 / 진입 中 / ₩300만/월 / 5/31 마감 임박
3. 프리랜서 글로벌 결제 wrapper (Wise/PayPal/Lemon) — TAM 글로벌 1억+ / 진입 高 / ₩100만/월 / 다국적 환율 pain
4. KDP 표지 거절 방지 templater — TAM 글로벌 KDP 작가 30만 / 진입 低 / ₩50만/월 / unique pain
5. 보험 commission 투명 비교 SaaS — TAM 한국 5천만 / 진입 高 (API) / ₩500만/월 / 제휴 후 폭발
6. KORLENS K-tourism Etsy + Klook 어필리에이트 — TAM 외국인 한국 방문 1700만 / 진입 中 / ₩300만/월 / 글로벌 K-wave
7. 천명당 4언어 사주 SaaS (이미 라이브) — TAM 글로벌 5억 사주/점성술 / 진입 中 / ₩수천만/월 잠재 / D+1 검증 중
8. GDPR/CCPA privacy 자동 생성 SaaS — TAM SaaS founder 100만 / 진입 中 / ₩200만/월 / 규제 강화
9. PG 가입 서류 templater (자영업자) — TAM 한국 800만 / 진입 低 / ₩50만/월 / unique pain
10. K-Wisdom 차별화 YT 채널 컨설팅 + SaaS — TAM YT 크리에이터 5천만 / 진입 高 (콘텐츠 차별화) / ₩100만/월 / 2026 AI slop 정책 회피
"""

# ================================================================
# 발송
# ================================================================
messages = [msg1, msg2, msg3, msg4, msg5, msg6, msg7, msg8, msg9, msg10]
results = []
for i, m in enumerate(messages, 1):
    try:
        r = send_tg(m)
        ok = r.get('ok', False)
        results.append((i, ok, r.get('result', {}).get('message_id', None)))
        print(f"[{i}/10] sent ok={ok} message_id={r.get('result', {}).get('message_id')}")
        time.sleep(1)  # rate limit
    except Exception as e:
        print(f"[{i}/10] FAILED: {e}")
        results.append((i, False, str(e)))

print("\n=== SUMMARY ===")
for i, ok, mid in results:
    print(f"msg {i}: {'OK' if ok else 'FAIL'} {mid}")
