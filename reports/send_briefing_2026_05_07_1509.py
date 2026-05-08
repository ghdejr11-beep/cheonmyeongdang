# -*- coding: utf-8 -*-
"""
CEO 브리핑 — 2026-05-07 15:09 (목)
하루 5회 자동 브리핑 중 PM 사이클 보고. 메시지 10개로 분할 발송.
"""
import os, json, urllib.request, urllib.parse, time

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

# ================================================================
# 메시지 1: CEO 브리핑 요약 + TOP 10
# ================================================================
msg1 = """📊 CEO 브리핑 | 2026-05-07 15:09 (목)

💰 팀별 수익 (어제 5/6 기준)
🔮 천명당: ₩0 (글로벌 v3.5 라이브 D+1)
📚 전자책: $0 (KDP no_data, 토큰 점검 필요)
📺 미디어: ₩0 (YT/AdMob 정상 수집, 매출 0)
🎮 게임: ₩0 (HexDrop 1.3 라이브)
💼 세무: ₩0 (세금N혜택 라이브, 종소세 D-24)
🛡️ 보험: ₩0 (서비스소개서 작성완료)
🗺️ 여행: ₩0 (KORLENS 글로벌 launch 직후)
💰 총: ₩0 / 30일 누적 ₩0

🔔 결정적 D-day
- 종소세 D-24 (5/31 마감) ← 매년 5월 골든타임
- KoDATA 등록 D-1 (5/8 시작) ← KORLENS round2
- Etsy KORLENS 리스팅 D+1
- 천명당 PayPal Smart Buttons D+1 첫 결제 대기

🏆 오늘 해야할 일 TOP 10 (수익 직결 우선)
1. #1 종소세 자동 분개 MVP — 세금N혜택 베타 페이지. CSV→Claude분개→PDF. 5/31까지 ₩300만~₩3,000만 단발 잠재. 8h
2. #7 AI 프롬프트팩 5 SKU (K-Saju/MBTI/타로/꿈/관상) — Gumroad 출시, 천명당 자산 즉시 재활용. 6h
3. KoDATA 메일 발송 (find@kodata.co.kr) — D-1 트리거. 자동 작성 가능
4. Etsy 한국 사주 영문 리스팅 20건 — Claude 영문 변환. K-컬처 유럽 호응. 6h
5. PayPal collector 추가 — Smart Buttons 라이브이므로 매출 가능성 1순위 채널
6. KDP scraper no_data 진단 — 셀렉터/토큰 만료 점검
7. Reddit/Quora draft 5/8부터 daily publish 시작 — 30+40 자산 풀 채움 완료
8. Beehiiv issue #6 사전 review (7/8 publish)
9. #6 간이지급 알림 봇 베타 — 세금N혜택 확장 ₩9,900/월/법인
10. Vibe Coding 한국어 부트캠프 콘텐츠 패키지 — Lovable $300M ARR 검증 시장 진입

📅 다음 자동 사이클: 21:00 / 다음 사용자 turn 시 우선 인터뷰: KDP 토큰 + PayPal collector 키"""

# ================================================================
# 메시지 2: 🔮 천명당팀
# ================================================================
msg2 = """🔮 천명당팀 상세 보고 | 2026-05-07

💰 수익 현황
- 어제 (5/6) 수익: ₩0 (글로벌 v3.5 라이브 D+1)
- 누적 수익: ₩0 (라이브 직후, 매출 lag 7~30일 정상 구간)
- 수익 경로: PayPal Smart Buttons (USD) + 토스/갤럭시아 (KRW) + 카카오페이 (KRW)
- 6 SKU 라이브: ₩2,900~₩29,900 + 정기결제 2종

📋 현재 진행상황
- 천명당 v3.5 글로벌 SaaS 라이브 D+1 (5/6 출시) ✅
- 4 언어 (ko/en/ja/zh) × 6 페이지 ✅
- 결제·매직링크·AI Q&A 챗 ✅
- 매월 1일 운세 / PDF 30p / 시각화 차트 4종 ✅
- AAB 빌드 자동 ✅
- 11 schtask 정상 가동 ✅
- 50 인플루언서 outreach 진행 ✅
- VC 3 pitch (Antler/Kakao/D2SF) 송부 완료
- Beehiiv 10 issue 풀 (D+9주 publish) 사전 작성 완료
- Reddit 30 / Quora 40 draft 풀 채움 완료
- 카카오 사주봇 월렛 908652 실행중
- 앱인토스 사업자 검토중

⚠️ 문제점
- D+1 매출 ₩0 (인지 단계 정상이나 acquisition lag 단축 필요)
- PayPal collector 미구축 (라이브 채널 매출 자동 합산 X)
- KDP 토큰 만료 추정 (no_data) → 다음 사이클 진단
- 인플루언서 outreach 응답률 추적 v2 강화 필요

🔧 개선 가능성
- PayPal collector 추가 → 매출 가시성 100% 회복 (예상 +2h)
- AI 프롬프트팩 5 SKU 추가 → Gumroad 즉시 출시 (예상 +6h, 월 ₩50~₩500만)
- Etsy 한국 사주 영문 리스팅 20건 → K-컬처 유럽 호응 (예상 +6h, 월 ₩100~₩1,000만)
- D+3/+7/+14 winback 메일 시퀀스 모니터 강화 → LTV +50%

🎯 앞으로 진행 방향
- 이번 주: PayPal collector + Etsy 20 리스팅 + Gumroad 5 SKU
- 다음 주: D+30 종합 매출 분석 + 인플루언서 응답률 리포트
- 이번 달: 첫 결제 ₩100만 돌파, 종합풀이 정기결제 100명 확보"""

# ================================================================
# 메시지 3: 📺 미디어팀
# ================================================================
msg3 = """📺 미디어팀 상세 보고 | 2026-05-07

💰 수익 현황
- 어제 (5/6) AdMob: ₩0 / YouTube: ₩0
- Sori Atlas 24/7 라이브 (Suno 음원, Hetzner CX22 ₩7,000/월)
- K-Wisdom 채널 (@kunstudio_kr) 운영중 — Whisper Atlas 폐기 후 피벗

📋 현재 진행상황
- YT 5채널 활성: whisper_atlas / wealth_blueprint / inner_archetypes / ai_sidehustle / Sori Atlas (5재생목록)
- Upload-Post $192/년 결제, 5/5 한도 사용 중
- TikTok 워밍업 4/24~4/29 완료, 프로필 kunstudio
- Bluesky (@kunstudio) + Discord 웹훅 실발행 검증 완료
- Postiz 셀프호스트 (Railway Hobby $5/월) 텔레그램 연결
- Pinterest 3핀 + KORLENS 2블로그 + Klook AID 120494 (commission live)
- multi_poster.py post_instagram() 직접 사용 (Postiz Instagram OAuth 포기)
- KunStudio_KWisdom_Daily schtask 매일 07:00

⚠️ 문제점
- YouTube Studio 채널 정보 자동 입력 완료, 사용자 1클릭 "게시"만 남음 (5/1 인계)
- AdMob 매출 0 — 앱 사용자 base 부족
- Pinterest 3핀 publish 후 트래픽 미전환 (CTA 강화 필요)
- AI Side Hustle 신규 제목으로 재등록 대기 (BLOCKED 후 다음주)

🔧 개선 가능성
- Reddit/Quora 30+40 draft 5/8부터 daily publish → SEO 트래픽 확보
- Beehiiv 5주치 사전 작성 완료 → 자동 publish 시퀀스
- KORLENS Etsy + Sori Atlas BGM affiliate cross-link → 다채널 매출
- Coupang Partners 어필리에이트 inject (15만원 누적 시 자동 승인)

🎯 앞으로 진행 방향
- 이번 주: Reddit/Quora 자동 publish + Beehiiv issue #6 review
- 다음 주: K-콘텐츠 영문 SEO 50 게시물 자동 + Affiliate 30% 강화
- 이번 달: 5채널 평균 구독 1,000 돌파 + AdMob 첫 ₩10,000 매출"""

# ================================================================
# 메시지 4: 🛡️ 보험팀
# ================================================================
msg4 = """🛡️ 보험다보여팀 상세 보고 | 2026-05-07

💰 수익 현황
- 어제 (5/6) 수익: ₩0
- 누적: ₩0 (API 심사 단계, 매출 미발생)

📋 현재 진행상황
- insurance_app.html 라이브 ✅
- 보험상품정보 API 심사 서류 준비완료 ✅
- 서비스소개서 작성완료 ✅
- 사업자등록증 / privacy / terms 정합성 통과
- 광고홍보 시 특정 보험사명 거론 금지 룰 적용 (Samsung/현대해상 등 일반화)

⚠️ 문제점
- API 심사 회신 미수령 (4/29 신청 후 D+8)
- 보험설계사 license 보유 X → 비교/검색만 가능, 권유는 법적 X
- 보험업법 광고 사전심의 필요 가능성 → 변호사 사전 자문 필요

🔧 개선 가능성
- API 회신 대기 중 SEO 콘텐츠 사전 작성 → "암보험 비교 2026" 등 long-tail 30건
- 보험 비교 글 + Coupang Partners (보험사 외 일반 상품) cross-link
- 천명당 사주풀이 + 건강 운 → 보험 제안 cross-sell 채널 가능

🎯 앞으로 진행 방향
- 이번 주: API 심사 회신 대기 (자동 모니터 메일)
- 다음 주: 회신 통과 시 비교 페이지 라이브 + SEO 30 게시물
- 이번 달: 첫 비교 lead 100건 확보 + 어필리에이트 conversion 측정"""

# ================================================================
# 메시지 5: 📚 전자책팀
# ================================================================
msg5 = """📚 전자책팀 상세 보고 | 2026-05-07

💰 수익 현황
- 어제 (5/6) KDP: $0 (no_data, 셀렉터/토큰 만료 추정)
- 누적: 0건 (실제 매출 자동 집계 불가 상태)
- 27 KDP 책 등록 / BookK ISBN 발급 형식 차단 룰 적용

📋 현재 진행상황
- KDP 27책 활성 (저자명 Deokgu Studio 통일)
- Gumroad 4종 (B2B 콘텐츠) + Mega Bundle $29.99
- Gumroad cross-link git ffaebbc 적용
- AI Side Hustle 재등록 대기 (BLOCKED 후 다음주)
- Cover Verifier (다이어리/플래너/캘린더 등 BookK 차단 형식 자동 거부)

⚠️ 문제점
- KDP scraper no_data — 셀렉터 변경 또는 토큰 만료
- 매출 자동 집계 X (5/7 PM 사이클 기준)
- KDP 풀 자동화 금지 룰 (Selenium anti-bot RISK) → 클립보드 헬퍼까지만
- Gumroad sales feed 0건 (트래픽 부족)

🔧 개선 가능성
- KDP scraper 토큰 재발급 + 셀렉터 점검 (예상 +2h, 매출 가시성 회복)
- AI 프롬프트팩 5 SKU Gumroad 출시 (천명당 자산 재활용, 월 ₩50~₩500만 잠재)
- 한국 사주 마스터 Notion 워크스페이스 ($19-29) Gumroad+Etsy 듀얼 (+30~50% 매출)
- Vibe Coding 한국어 부트캠프 패키지 ($49) — Lovable $300M ARR 검증 시장

🎯 앞으로 진행 방향
- 이번 주: KDP scraper 진단 + Gumroad 5 SKU 출시
- 다음 주: Etsy 듀얼 출시 + Mega Bundle 시즌2
- 이번 달: KDP 매출 첫 $50 + Gumroad 월 $200 돌파"""

# ================================================================
# 메시지 6: 🎮 게임팀
# ================================================================
msg6 = """🎮 게임팀 상세 보고 | 2026-05-07

💰 수익 현황
- 어제 (5/6) HexDrop 매출: ₩0 (Play 라이브)
- 누적: ₩0 (베타 테스트 단계)
- 사주팡 게임 50% MVP

📋 현재 진행상황
- HexDrop 1.3 비공개 테스트 게시 완료 (4/10) ✅
- HexDrop Billing 통합 완료
- 테트리스 AI 대결 게임 완성
- 사주팡 게임 MVP 50%
- BETA FLOW ₩63,000 (4/26 완료)

⚠️ 문제점
- HexDrop 1.3 출시 클릭 사용자 액션 미완 (4/24~ 보류)
- Play Console MCP Chrome hidden file input 트리거 불가 → 사용자 직접 업로드 필수
- 매출 자동 집계 채널 X
- 글로벌 마케팅 채널 0

🔧 개선 가능성
- HexDrop 1.3 정식 출시 → AdMob 활성 (사용자 1클릭만 필요)
- 사주팡 MVP 100% 완성 → 천명당 cross-promotion (사주풀이 후 게임 추천)
- Vibe Coding 콘텐츠 패키지 모바일 데모로 활용 가능
- 게임팀 9시 사이클 인기 캐주얼 게임 리서치 → HTML5+JS 신규 게임 매월 1편

🎯 앞으로 진행 방향
- 이번 주: HexDrop 1.3 사용자 출시 클릭 (1건만 남음)
- 다음 주: 사주팡 100% + Play 베타 등록
- 이번 달: HexDrop AdMob 첫 ₩50,000 + 사주팡 베타 1,000명"""

# ================================================================
# 메시지 7: 💼 세무팀
# ================================================================
msg7 = """💼 세무팀 상세 보고 | 2026-05-07

💰 수익 현황
- 어제 (5/6) 수익: ₩0 (라이브, 매출 미발생)
- 종소세 D-24 (5/31 마감) — 매년 5월 골든타임 진입

📋 현재 진행상황
- 세금N혜택 100% 출시 ✅
- 기획서 완성 (수수료 0% 모델) ✅
- 프로토타입 완성 ✅
- modoo.or.kr Tech Track 신청 완료 (4/19)
- 광고비 14% click fraud 탐지 niche 후보

⚠️ 문제점
- 매출 자동 집계 채널 X (현재 자체 PG 라이브 X)
- 광고/홍보 X → 자연 트래픽 부족
- 종소세 기능 모듈 미완 (5/31 D-24 골든타임)

🔧 개선 가능성
- ⭐ #1 종소세 자동 분개 MVP (8h) — D-24 골든타임. CSV→Claude→PDF. 단발 ₩9,900~₩29,000 / SaaS ₩4,900/월. **5/31까지 ₩300만~₩3,000만 잠재**
- #6 간이지급명세서 알림 봇 (10h) — B2B SaaS ₩9,900/월/법인. 1,000법인 = ₩990만/월
- #8 자영업자 위기 진단 봇 — ₩19,900/단발. 폐업률 9%대 중후반 시장
- #10 건설/제조 진행률 매출 자동 — B2B ₩99,000/월/현장

🎯 앞으로 진행 방향
- 이번 주: ⭐ 종소세 자동 분개 MVP 8h 안에 베타 + SEO "프리랜서 종소세" 무경쟁 키워드
- 다음 주: 간이지급 알림 봇 베타 + 카카오 알림톡 연동
- 이번 달: 종소세 단발 매출 ₩300만 달성 + B2B SaaS 첫 100법인 확보"""

# ================================================================
# 메시지 8: 🗺️ 여행지도팀 (KORLENS)
# ================================================================
msg8 = """🗺️ 여행지도팀 (KORLENS) 상세 보고 | 2026-05-07

💰 수익 현황
- 어제 (5/6) Etsy 글로벌 launch 직후, 수익 ₩0
- Klook AID 120494 commission live ✅
- Coupang Partners 15만원 누적 시 자동 승인 대기

📋 현재 진행상황
- KORLENS 현지인 픽 라이브 (Vercel default 도메인)
- Supabase + Google OAuth 연동 ✅
- 카카오 KOE205 해결 ✅
- Etsy KORLENS 리스팅 5/6 글로벌 launch
- KoDATA 등록 D-1 (5/8 시작) — round2 신청 양식 폴더 보관
- KoDATA find@kodata.co.kr 메일 ID 19df70fe428c7e65 (회신 5/12경 예상)
- 관광 AI 신청 5/20 마감

⚠️ 문제점
- Etsy 리스팅 D+1 매출 ₩0 (acquisition 단계 정상)
- 관광 AI 사업계획서 round2 폴더 보관 상태, 메일 발송 D-day 5/12 이전 필수
- 지도 데이터 placeholder 상태 (실제 콘텐츠 부족)

🔧 개선 가능성
- ⭐ Etsy 한국 사주 영문 리스팅 20건 추가 (6h) — 천명당 자산 재활용, 월 ₩100~₩1,000만 잠재
- KORLENS Pinterest+SEO K-pop/K-drama/K-food 트래픽 흡수
- 정부지원 관광AI(KORLENS) 신청 — 5/20 마감 D-13
- Sori Atlas BGM affiliate cross-link

🎯 앞으로 진행 방향
- 이번 주: KoDATA 5/8 트리거 + Etsy 20 리스팅 + Pinterest 핀 30
- 다음 주: 관광 AI 신청 + KoDATA 회신 모니터
- 이번 달: KORLENS Etsy 첫 매출 + Klook commission 첫 정산"""

# ================================================================
# 메시지 9: 지원부서 (법무+데이터분석)
# ================================================================
msg9 = """⚖️ 법무정책부 + 📊 데이터분석부 보고 | 2026-05-07

⚖️ 법무정책부
- privacy.html ✅ / terms.html ✅
- 위탁업체 8개 명시 (privacy)
- 광고에 특정 업체·연예인·IP 거론 금지 룰 적용 (Samsung/BTS/Squid Game 등 시비/소송 RISK)
- 보험업법 광고 사전심의 필요 가능성 (보험팀 라이브 전 자문)
- KDP 풀 자동화 금지 (Selenium anti-bot RISK > ROI)
- API 키 보안 철칙 (.gitignore + 서버 프록시 경유)
- 대법원 2026 판례 모니터링 미구축 → 향후 자동 RSS 추가 검토

📊 데이터분석부
- GA4 (G-90Y8GPVX1F) 설치완료 천명당
- unified_revenue.py 90일 rolling JSON
- 어제 (5/6) 통합 매출 ₩0, 7일 평균 ₩0/일, 30일 누적 ₩0
- Collector 상태:
  · admob: ok / youtube: ok / gumroad: ok
  · kdp: no_data ⚠️ (셀렉터/토큰 만료 추정)
  · kreatie: awaiting_input (수동 입력 채널)
- ⚠️ PayPal collector 미구축 — 라이브 채널 매출 자동 합산 X
- ⚠️ Etsy collector 미구축 — KORLENS 리스팅 매출 가시성 X
- 다음 사이클 처리: KDP 진단 + PayPal collector + Etsy collector 추가"""

# ================================================================
# 메시지 10: 🔍 수집부 보고 (10+10)
# ================================================================
msg10 = """🔍 수집부 보고 | 2026-05-07

😤 사람들이 불편해하는 것 TOP 10
1. 종소세 영수증 OCR + 자동 분개 — 신고 대상자 절반+ 추계신고로 손해 (banksalad/taxnet) — 세금N혜택 CSV→Claude — 8h — 매출 상
2. 간이지급명세서 매월 제출 의무 인지 부재 — 2026 가산세 강화 (clobe.ai) — Hometax 알림 봇 + 카카오 알림톡 — 10h — B2B 중
3. 자영업자 폐업률 9%대 중후반 (소매 16.7%, 음식 15.8%) — 통계 집계 이래 최고 (koreabizreview) — 위기 진단 봇 + 정부지원 매칭 — 16h — 진단 ₩19,900/단발
4. 모바일 기능 격차 — 데스크탑 있는 기능 모바일 없어 주 2-10h 손실 (bigideasdb) — PWA 강화 — 12h — LTV +20%
5. 서비스업 노쇼 자동 복구 도구 부재 — 매년 수천$ 손실 (bigideasdb) — 토스 사전결제 + 카카오 알림톡 — 18h — ₩29,000/월/매장
6. Lovable $300M ARR — 비기술자 vibe coding 폭증 — vibe coding 한국어 부트캠프 패키지 — 20h — $49+₩29K/월 멤버십
7. AI-Made Notion 템플릿 시장 $50M+/년 (Gumroad+Etsy) — 한국 사주 Notion 워크스페이스 — 10h — 월 ₩100~₩500만
8. 간병 가족 공유 캘린더 — 약물/방문 일정 공유 도구 부재 — 가족 케어 공유 SaaS — 24h — ₩4,900/월/가족
9. 건설업 회계 work-in-progress 자동화 부재 — 회계사 매월 수기 (Reddit 다수 불만) — B2B niche ₩99,000/월/현장 — 28h
10. 알뜰폰 매월 프로모션 추적 + 광고비 14% click fraud — 텔레그램/카카오 봇 + Click Fraud Lite — 14h — ₩19,900/월

💰 수익 창출 좋은 모델 TOP 10
1. 종소세 자동 분개 단발 도구 (5월 한정) — 250만+ 잠재 — 진입 하 — ₩300만~₩3,000만 — D-24 골든타임 — 세금N혜택 베타 페이지 즉시
2. AI-Made Notion 템플릿 (한국 사주 버티컬) — Gumroad+Etsy $50M+/년 — 진입 하 — 월 ₩100~₩500만 — 천명당 자산 재활용 — 5 SKU $9-29 듀얼
3. Vibe Coding 한국어 교육 패키지 — Lovable $300M ARR 검증 — 진입 중 — 월 ₩200~₩2,000만 — 검색 6,700% 폭증 — $49+멤버십 ₩29K/월
4. 노쇼 복구 미니 SaaS (헬스장/네일샵) — 한국 무경쟁 — 진입 중 — 월 ₩300만~₩3,000만 — 인프라 라이브 — 100매장=₩290만/월
5. 한국 사주 영문 디지털 (Etsy+Gumroad 듀얼) — Etsy 1순위 — 진입 하 — 월 ₩100~₩1,000만 — K-컬처 유럽 폭증 — 50 리스팅+5 SKU
6. 간이지급명세서 알림 봇 (B2B SaaS) — 한국 법인 100만+ — 진입 중 — 월 ₩200~₩1,500만 — 2026 가산세 강화 — 1,000법인=₩990만/월
7. AI 프롬프트팩 (K-Saju/MBTI/타로/꿈/관상/풍수) — Etsy+Gumroad top — 진입 하 — 월 ₩50~₩500만 — 천명당 6 SKU 검증 — 50p×6packs Gumroad
8. 자영업자 위기 진단 봇 — 폐업 100만+/년 — 진입 중 — 월 ₩200~₩2,000만 — 정부지원 5월 다수 — Vercel+Claude ₩19,900/단발
9. K-콘텐츠 영문 SEO 블로그 (Affiliate 30%) — Pinterest+SEO 폭증 — 진입 하 — 월 ₩50~₩500만 — KORLENS/K-Wisdom/Sori 자산 — 50 게시물/월 자동
10. 건설/제조 진행률 매출 자동 (B2B) — 한국 건설 SaaS 1.78조→3.06조 — 진입 중 — 월 ₩300만~₩3,000만 — 한국 SaaS 글로벌 1% 골든타임 — 30현장=₩297만/월

🚀 7일 액션 플랜 (5/7~5/13)
Day 1 (오늘): #1 종소세 MVP 8h ← 매출 직결 1순위
Day 2 (5/8): #7 AI 프롬프트팩 5 SKU 6h + KoDATA D-day 병렬
Day 3 (5/9): #5 사주 영문 Etsy 리스팅 20건 6h
Day 4 (5/10): #2 한국 사주 Notion 8h
Day 5-6 (5/11-12): #6 간이지급 알림 봇 12h + KoDATA 5/12 메일 마감
Day 7 (5/13): #3 Vibe Coding 한국어 패키지 8h
예상 7일 누적: ₩50만~₩500만 (5월 종소세 단발 ₩300만~₩3,000만 추가)"""

# 발송
messages = [msg1, msg2, msg3, msg4, msg5, msg6, msg7, msg8, msg9, msg10]
results = []
for i, m in enumerate(messages, 1):
    try:
        r = send_tg(m)
        ok = r.get('ok', False)
        results.append((i, ok, r.get('result', {}).get('message_id', None)))
        print(f"[{i}/10] sent ok={ok} chars={len(m)}")
        time.sleep(1.2)
    except Exception as e:
        results.append((i, False, str(e)))
        print(f"[{i}/10] FAIL {e}")

print("===")
print(json.dumps(results, ensure_ascii=False))
