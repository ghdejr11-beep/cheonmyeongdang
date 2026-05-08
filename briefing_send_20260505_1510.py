# -*- coding: utf-8 -*-
"""CEO 브리핑 - 2026-05-05 15:10 KST (Tuesday)"""
import os, json, time, urllib.request, urllib.parse

for line in open(r'D:\cheonmyeongdang\.secrets', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)

token = os.environ['TELEGRAM_BOT_TOKEN']
chat = os.environ['TELEGRAM_CHAT_ID']

def send(msg):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    # Telegram limit ~4096
    if len(msg) > 4000:
        # split by lines
        parts = []
        cur = ''
        for ln in msg.split('\n'):
            if len(cur) + len(ln) + 1 > 3800:
                parts.append(cur)
                cur = ln
            else:
                cur = (cur + '\n' + ln) if cur else ln
        if cur:
            parts.append(cur)
    else:
        parts = [msg]
    results = []
    for p in parts:
        data = urllib.parse.urlencode({'chat_id': chat, 'text': p, 'disable_web_page_preview': 'true'}).encode()
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=20) as r:
            results.append(json.loads(r.read()).get('ok'))
        time.sleep(0.3)
    return all(results)

D = '2026-05-05'
T = '15:10'

# ============ MSG 1 : 요약 + TOP 10 ============
msg1 = f"""📊 CEO 브리핑 | {D} {T} (화)

💰 팀별 수익 (D-1, 5/4 월)
🔮 천명당: ₩0 (PayPal Smart Buttons 라이브 / 결제 0건)
📚 전자책: $0 (KDP 27책 / Gumroad 4종 매출 0)
📺 미디어: ₩0 (AdSense 1~2주 검토중)
🎮 게임: ₩0 (HexDrop 1.3 비공개 / 사주팡 50% MVP)
💼 세무: ₩0 (세금N혜택 라이브 / 신청 트래픽 0)
🛡️ 보험: ₩0 (API 심사 서류 / 미런칭)
🗺️ 여행: ₩0 (KORLENS 라이브 / 결제 0)
💰 합계: ₩0 / 4월 누적도 0원 위기 11일째

🚨 핵심 리스크
- 두 달간 매출 0 → PayPal 라이브 후 첫 결제도 미발생 (5/3~5/5)
- 광고/트래픽 펀넬 부재 (PayPal 버튼 있어도 클릭이 0)
- 한국 PG 우편(갤럭시아) 5/4 (월) 발송 마감 → 발송 여부 확인 필요

🏆 오늘 해야할 일 TOP 10 (수익 직결 우선)
1. Pinterest English Pin 10장 자동 업로드 — Pinterest는 SEO처럼 누적, 무료, 글로벌 도달. 천명당/세금N혜택/KORLENS 각 3~4장. 비용 0
2. Gumroad 4종 Discount Code "FIRST50" 50% 발행 + Reddit 소액 게시 — 첫 매출 brake 목적. 비용 0
3. Ko-fi Tip Jar 다국어 페이지 점검 + 천명당/세무 SNS bio 링크 갱신 — 0% 수수료 첫 매출 채널
4. PayPal 결제 1건 시뮬레이션 (테스트 카드) — confirm-payment.js 로그 확인. 결제 funnel dead 여부 진단
5. Google Sheets→PayPal Subscription 결제 alert hookup 점검 — 첫 결제 발생시 즉시 알림 수신 보장
6. KDP 27책 중 매출 0 책 8권 키워드/카테고리 재최적화 (제목 변경 X) — 알고 검색 노출 증대
7. KORLENS 영문 SEO 블로그 3편 자동 생성+발행 (미디어부 cron) — 비용 0, Google index 누적
8. 갤럭시아/토스 우편 5/4 (월) 발송 여부 확인 → 미발송이면 5/5 (화) 오늘 발송 준비 (사용자 액션)
9. Suno 음원 4트랙 자동 생성→Sori Atlas YouTube/Spotify(Distrokid) 동시 업로드 — Sori Atlas 24/7 라이브 + 음원 monetize
10. Lemon Squeezy 가맹점 가입 시작 (PayPal 백업, 한국 사업자 OK) — 결제 채널 다양화 매출 +20% 추정"""

print('len1=', len(msg1))
print(send(msg1))
"""
=== MSG 2: 천명당팀 ===
"""
msg2 = f"""🔮 천명당팀 상세 보고 | {D}

💰 수익 현황
- 어제 수익: ₩0 (5/4 일)
- 누적 수익 (4월): ₩0
- 결제 수단: PayPal Smart Buttons 라이브 (5/3 12:00 검증 완료)
- 한국 PG: 갤럭시아 우편 발송 5/4 마감 → 라이브 미통과
- AdSense: 1~2주 검토중

📋 현재 진행상황
- Vercel: confirm-payment.js PayPal 검증 통과 (5/3 commit)
- PayPal env 3개: PAYPAL_CLIENT_ID / PAYPAL_SECRET / PAYPAL_MODE=live (재등록 완료)
- Notion 6 product: 종합풀이/월회원/신년운세/...
- Ko-fi Tip Jar: 다국어 페이지 라이브
- D+30 winback / D+3, D+7, D+14 후속 메일 시퀀스: cron 분기 라이브
- 카카오 알림톡: 1~3영업일 검토중 (카카오비즈)
- 앱인토스 사업자 검토중 (.ait 빌드 완료)

⚠️ 문제점
- PayPal 라이브 후 첫 결제 0건 → 펀넬 트래픽 부재 (광고비 X 정책)
- index.html 최상단 PayPal 버튼이 모바일에서 fold 아래에 위치 가능성
- 한국어 사이트에 영문 결제만 노출 → 신뢰도 의심
- AdSense·갤럭시아·카카오톡 모두 외부 검토 대기 → 능동적 액션 막힘

🔧 개선 가능성
- Pinterest English Pin 10장/일 자동 → 월 +50~200 도달 (비용 0) → 결제 +1~3건/월 추정
- success.html에 "30일 내 환불" 보증 + 한국어 후기 3개 추가 → 전환율 +30% 추정
- D+0 (가입 즉시) 무료 미니 사주 PDF 메일 → email capture → recurring funnel 구축
- Gumroad 4종 Discount "FIRST50" 50% off → 첫 매출 brake (비용 0)
- 천명당 메인 SEO: "오늘의 사주" / "꿈해몽" 영문 페이지 추가 → 글로벌 organic

🎯 앞으로 진행 방향
- 이번 주 (5/5~5/11): Pinterest 자동 + Discount 발행 + PayPal 시뮬레이션 + 후기 페이지 추가
- 다음 주 (5/12~5/18): Lemon Squeezy 가입 / KOR PG 라이브 통과 시 카카오페이 정기결제 활성
- 이번 달 (5월): 첫 결제 ₩2,900 → ₩30,000 (10건) 목표"""

print('len2=', len(msg2))
print(send(msg2))

"""
=== MSG 3: 미디어팀 ===
"""
msg3 = f"""📺 미디어팀 상세 보고 | {D}

💰 수익 현황
- AdSense: 1~2주 검토중 (5/1~)
- YouTube AdSense 5채널: Whisper Atlas 폐기, 활성 4채널 + Sori Atlas
  · K-Wisdom (@kunstudio): 채널 정보 입력 완료, 게시 1클릭 대기
  · Wealth Blueprint / Inner Archetypes / AI Side Hustle: 자동 파이프라인 가동
  · Sori Atlas: Suno 음원 24/7 라이브 (Hetzner CX22 ₩7,000/월)
- Pinterest / TikTok / Bluesky / Discord: multi_poster.py 활성
- Postiz Railway $5/월: 텔레그램 연결됨

📋 현재 진행상황
- Whisper Atlas: 5/1 폐기 (YouTube 2026 AI slop 정책 위반)
- K-Wisdom: schtask KunStudio_KWisdom_Daily 매일 07:00 등록
- Sori Atlas: 5재생목록 (Sleep/Lofi/Study/Cafe/Rain), Distrokid 1년 $19.99 발행 대기
- Upload-Post $192/년: 5/5 프로필 5/5 한도 사용 중
- AI Side Hustle: 매일 06:00 자동, 첫 영상 4/23 성공 (Gh3WSv0mZeM)

⚠️ 문제점
- AdSense 4번째 거절 → 검토 1~2주 결과 대기, 거절 리스크 존재
- K-Wisdom 채널 게시 안 됨 (사용자 1클릭 대기, 5/1~5/5 5일째)
- Sori Atlas Distrokid 미가입 → Spotify/Apple Music 음원 monetize 못함
- Pinterest English 자동 자동화 미구축 (memory 5/4)

🔧 개선 가능성
- Pinterest English 자동 (Selenium + PIL) 5월 1주차 구축 → 월 도달 +5만 추정
- Sori Atlas Distrokid 1년 $19.99 → Spotify Royalty $5~30/월 시작
- K-Wisdom 게시 후 다음 주 5편 자동 발행 → AdSense 통과 후 첫 광고비
- Threads/Mastodon 자동 추가 (4/29 메모: 글로벌 우선) → 비용 0

🎯 앞으로 진행 방향
- 이번 주: Pinterest 자동 구축 + Distrokid 가입 + K-Wisdom 게시 압박
- 다음 주: AdSense 통과 시 광고 단가 모니터링, 통과 못하면 우회 신청 (다른 채널)
- 이번 달: AdSense 통과 + Sori Atlas 첫 royalty + Pinterest 5만 도달"""

print('len3=', len(msg3))
print(send(msg3))

"""
=== MSG 4: 보험팀 ===
"""
msg4 = f"""🛡️ 보험다보여팀 상세 보고 | {D}

💰 수익 현황
- 누적 수익: ₩0
- 미런칭 (API 심사 서류 단계)

📋 현재 진행상황
- insurance_app.html 라이브
- API 심사 서류 준비완료
- 서비스소개서 작성완료
- 4/22 메모: 미런칭

⚠️ 문제점
- 보험업법 / 광고 표시 의무 규제 RISK (memory: 법적 리스크 회피 최우선)
- API 미보유 (제휴사 심사 통과 필요)
- 단독 가입 유인 부족 (가격비교/혜택 비교 데이터 부재)
- 트래픽 0

🔧 개선 가능성
- Affiliate 30% 모델 (사용자 5/4 메모: 무료/affiliate만)로 전환 → 보험사 직접 제휴 X, 토스보험/캐롯 어필리에이트
- "내 보험 진단 무료 PDF" lead magnet → email 모집 → 이후 affiliate 추천
- 인스타 카드뉴스 5장 시리즈 자동 → 일반화된 표현 ("국내 대표 보험사") + 자동 발행
- 토스보험/리치플래닛 어필리에이트 코드 신청

🎯 앞으로 진행 방향
- 이번 주: Affiliate 가능 보험 플랫폼 3사 리서치 → 가입 신청
- 다음 주: lead magnet PDF 1종 제작 + 인스타 5편 자동
- 이번 달: 첫 affiliate 클릭 / 추천 1건 (₩5,000~30,000)"""

print('len4=', len(msg4))
print(send(msg4))

"""
=== MSG 5: 전자책팀 ===
"""
msg5 = f"""📚 전자책팀 상세 보고 | {D}

💰 수익 현황
- KDP 27책 검토중 / 일부 라이브
- Gumroad 4종 라이브 (₩0)
- Mega Bundle $29.99 라이브
- 누적 수익: $0

📋 현재 진행상황
- BookK ISBN 발급 불가 형식 (다이어리/플래너/캘린더/일기장/스케치북/Q&A/도감/사용설명서) → KDP만 사용 (memory 5/4)
- KDP 책: Deokgu Studio 통일, 표지 일괄 수정 (4/19)
- Gumroad 4종 라이브 / Mega Bundle 라이브
- 환불 자동 응답 + winback 가동

⚠️ 문제점
- 매출 0 → SEO/Pinterest 트래픽 부재
- KDP A+ Content 없음 → 전환율 낮음
- 한국어 책만 → 글로벌 도달 X
- Discount Code 없음 → 첫 결제 brake 부재

🔧 개선 가능성
- Gumroad Discount "FIRST50" 50% off → 첫 매출 (비용 0)
- Pinterest English Pin 10장/Gumroad 책 → 월 +500 도달
- KDP 8권 매출 0 → 키워드/카테고리/A+ 재최적화 (제목 변경 X) → 알고 노출 증대
- Mega Bundle $29.99 영문 SEO 페이지 자동 → Google organic
- Reddit /r/printables, /r/sidehustle, /r/passive_income 게시 (10 카르마 후 합법)

🎯 앞으로 진행 방향
- 이번 주: Discount Code 발행 + Pinterest 자동 + KDP 8권 재최적화
- 다음 주: KDP A+ Content 5권 추가 + Reddit 게시
- 이번 달: 첫 결제 1건 → 월 매출 $30 (10건)"""

print('len5=', len(msg5))
print(send(msg5))

"""
=== MSG 6: 게임팀 ===
"""
msg6 = f"""🎮 게임팀 상세 보고 | {D}

💰 수익 현황
- HexDrop 1.3: 비공개 테스트 게시 완료 (4/10)
- 사주팡: 50% MVP
- 누적 수익: ₩0

📋 현재 진행상황
- HexDrop 1.3: AAB 업로드, 비공개 테스트 단계
- 사주팡: 천명당 cross-sell 게임 50% (사주 기반 매칭)
- 테트리스 AI 대결: 완성, 미런칭
- 8앱 Play 검토 진입 (5/1)
- HexDrop Billing 통합 (5/1)

⚠️ 문제점
- HexDrop 1.3 공개 테스트 미전환 → 비공개 단계 25일째 (4/10~)
- 사주팡 50% MVP 정체 (5/1 이후 진행 X)
- 8앱 검토 결과 대기 → 통과 RISK
- 게임 유저 트래픽 펀넬 부재

🔧 개선 가능성
- HexDrop 1.3 공개 테스트 전환 (사용자 1클릭) → 다운로드 가능 → 광고 매출 시작
- 사주팡 MVP 100% 완성 → 천명당 cross-sell 결제율 +30% 추정
- HexDrop AdMob 광고 ID 활성화 (이미 발급) → 첫 광고비
- 8앱 동시 출시 → 누적 다운로드 10K → 광고비 ₩10,000~50,000/월 추정

🎯 앞으로 진행 방향
- 이번 주: HexDrop 공개 전환 압박 + 사주팡 100% (사주 매칭 로직 30% 추가)
- 다음 주: 8앱 검토 통과 / 거절 시 즉시 우회 신청
- 이번 달: HexDrop AdMob 첫 광고비 + 사주팡 라이브"""

print('len6=', len(msg6))
print(send(msg6))

"""
=== MSG 7: 세무팀 ===
"""
msg7 = f"""💼 세무팀 상세 보고 | {D}

💰 수익 현황
- 세금N혜택 라이브 (modoo.or.kr 4/19 신청 완료)
- 누적 수익: ₩0
- 모두의 창업 4/19 Tech Track 신청 완료

📋 현재 진행상황
- 세금N혜택: 100% 출시 (5/1)
- 기획서 완성 (수수료 0% 모델)
- 프로토타입 완성
- 모두의 창업 신청 완료 → 다른 공모전 집중

⚠️ 문제점
- 트래픽 0 → SEO/광고 펀넬 부재
- 수수료 0% 모델 → 즉시 매출 0
- 글로벌 X (한국 한정)
- B2B 영업 X

🔧 개선 가능성
- "내 세금 환급액 계산" 무료 도구 → email capture → 보험 affiliate 추천
- 인스타 카드뉴스 시리즈 자동 (절세팁 10가지) → 일반화 표현 → 비용 0
- 네이버 SEO 블로그 5편 자동 → "사업자 세금 신고" 키워드
- 세무사 affiliate 가입 (소상공인 매칭) → 매칭 1건 ₩30,000~100,000

🎯 앞으로 진행 방향
- 이번 주: 무료 도구 1종 추가 + 인스타 5편 자동
- 다음 주: 네이버 블로그 5편 + 세무사 affiliate 신청
- 이번 달: 첫 매칭 1건 / 도구 사용 100건"""

print('len7=', len(msg7))
print(send(msg7))

"""
=== MSG 8: 여행지도팀 ===
"""
msg8 = f"""🗺️ 여행지도팀 (KORLENS) 상세 보고 | {D}

💰 수익 현황
- KORLENS 라이브 (korlens.app)
- 누적 수익: ₩0

📋 현재 진행상황
- Supabase + Google OAuth 연동중
- 카카오 KOE205 해결 완료 (4/22)
- 현지인 픽 구축
- 글로벌 외국인 대상 (영문)

⚠️ 문제점
- 매출 0 → 한국 여행 외국인 트래픽 펀넬 부재
- Pinterest/TikTok English 자동 미구축
- 결제 X (현재 무료 서비스)
- 모노타이즈 모델 부재

🔧 개선 가능성
- Pinterest English Pin "Korea Travel" 카테고리 50장/월 자동 → 월 +1만 도달 추정
- 호텔/투어 affiliate (Klook/Trip.com) 30% 가입 → 첫 매출
- Premium tier $4.99/월 (현지인 전용 픽 + 음성가이드) → recurring
- Reddit /r/koreatravel 게시 + answers Quora "Korea travel" 관련 질문

🎯 앞으로 진행 방향
- 이번 주: Klook/Trip.com affiliate 가입 + Pinterest 자동
- 다음 주: Premium tier 페이지 + 첫 affiliate 링크 inject
- 이번 달: 첫 affiliate 매출 ₩10,000~30,000"""

print('len8=', len(msg8))
print(send(msg8))

"""
=== MSG 9: 지원부서 ===
"""
msg9 = f"""⚖️ 지원부서 보고 | {D}

⚖️ 법무정책부
- privacy.html ✅ (위탁업체 8개 명시 완료, 4/29)
- terms.html ✅
- 광고 가이드: 특정 업체·연예인·IP 거론 금지 (5/1)
- KDP 거절 방지 규칙 운영 (표지 텍스트 금지, spine 0.5인치, 저자명 통일)
- 환불 약관 자동 응답 hooked (Gumroad 4종)
- 보험업법 / 광고 표시 의무 규제 모니터링

📊 데이터분석부
- GA4 (G-90Y8GPVX1F) 설치완료 (천명당)
- Google Search Console: 천명당/세금N혜택/KORLENS/HexDrop 등록
- 부서 mtime 자동 추적 (CEO 브리핑 v2)
- pytrends + Product Hunt 자동 (briefing.py)
- 매출 데이터 0건 → GA4 conversion event 점검 필요

🔧 인프라부
- Vercel: 천명당/세금N혜택/KORLENS 배포중 (.vercel.app default 사용, 사용자 5/2 메모: 커스텀 도메인 X)
- Hetzner CX22 ₩7,000/월: Sori Atlas 24/7 송출 (5/2 검증)
- Vercel Hobby 12 함수 한도: confirm-payment.js 통합 운영
- Postiz Railway $5/월: 텔레그램 연결
- Upload-Post $192/년: 5/5 프로필 한도

📞 비서부 (Gmail/AdMob/GitHub PAT/CRON_SECRET 인증 자동)
- 4채널 어필리에이트 가동
- Telegram bot 정상
- 매시간 cron 보고 정상"""

print('len9=', len(msg9))
print(send(msg9))

"""
=== MSG 10: 수집부 (불편사항 10 + 수익모델 10) ===
"""
msg10 = f"""🔍 수집부 보고 | {D}

😤 사람들이 불편해하는 것 TOP 10 (글로벌+한국)
1. 한국 여행 외국인 — 식당 메뉴 한글만, 번역 X — 출처: Reddit /r/koreatravel — Claude+TTS 영문 메뉴 자동 OCR/번역 PWA — 1주 (KORLENS 통합)
2. KDP 저자 — A+ Content 디자인 어려움 — 출처: KDP 커뮤니티 — Claude HTML→PDF 템플릿 50종 자동 — 3일
3. SaaS 1인 개발자 — 한국 PG 가입 6주 — 출처: 본인 4/22~5/2 — Claude PG 가입 가이드 PDF + Lemon Squeezy 추천 affiliate — 1일
4. 직장인 — 부업 소득 신고 어려움 — 출처: 디시 직업갤 — Claude 부업 세금 계산기 + 신고 가이드 — 5일 (세무팀 통합)
5. 사주 사용자 — 한국 앱은 결제 부담 — 출처: 천명당 후기 — Claude 무료 미니 사주 PDF email magnet — 즉시
6. 영어권 K-pop 팬 — Lyrics 의미 해석 — 출처: Reddit /r/kpop — Claude lyric translator + cultural context PWA — 1주
7. 한국 자영업자 — 폐업 절차 어려움 — 출처: 자영업자 카페 — Claude 폐업 가이드 PDF (KDP 책) — 3일
8. 글로벌 학생 — 한국어 자동 작문 도우미 — 출처: HelloTalk — Claude Korean writing assistant Chrome ext — 1주
9. 사주 1인 사업자 — 자동 분석 도구 부재 — 출처: 본인 천명당 — Claude 사주 분석 API SaaS B2B — 2주
10. 영어권 직장인 — 명상 가이드 한국식 — 출처: Calm 후기 — Claude Sori Atlas Korean Zen Sleep Story 1편/주 — 즉시 (Sori Atlas)

💰 수익 창출 좋은 모델 TOP 10 (지금 시점, 무료/affiliate only)
1. Pinterest Auto Posting Service — 시장규모 $5B — 진입장벽 하 — 월수익 $300~3000 — 한국팀 X, Pinterest English 자동 미구축
2. Korea Travel Affiliate — 시장규모 $80B (한국 인바운드) — 진입장벽 하 — 월수익 ₩50K~500K — KORLENS 라이브 + Klook 30% 미가입
3. KDP Coloring Book Bundle — 시장규모 $200M — 진입장벽 하 — 월수익 $100~1500 — 본인 KDP 27책 / coloring 시리즈 0
4. Distrokid Lofi Music — 시장규모 $25B (스트리밍) — 진입장벽 하 — 월수익 $50~500 — Sori Atlas + Suno Pro 보유
5. Reddit Notion Templates — 시장규모 $200M (Notion) — 진입장벽 하 — 월수익 $50~800 — Gumroad 4종 라이브, Reddit 노출 X
6. Korean Learning Newsletter (Beehiiv) — 시장규모 $1B (이메일) — 진입장벽 하 — 월수익 $100~1500 — beehiiv dept 라이브, 콘텐츠 0
7. Pinterest "Korea Aesthetic" Niche — 시장규모 $5B — 진입장벽 하 — 월수익 $200~2000 — KORLENS·천명당 통합 가능
8. Spotify Sleep Story Affiliate — 시장규모 $50B — 진입장벽 중 — 월수익 $50~500 — Sori Atlas Sleep playlist 통합
9. Korean Tax 1-page Guide (KDP) — 시장규모 $10M — 진입장벽 하 — 월수익 ₩30K~300K — 세금N혜택 통합 KDP
10. Notion Sajun Daily Planner — 시장규모 $200M (Notion) — 진입장벽 하 — 월수익 $30~500 — 천명당 cross-sell, Gumroad 1종 추가

🎯 즉시 액션 (오늘 자동 실행 가능)
- Pinterest 영문 자동 (천명당/KORLENS/세금N혜택) — selenium 미구축 → 5월 1주차 우선
- Klook affiliate 가입 신청 → KORLENS inject
- Distrokid $19.99 Sori Atlas 가입 → Suno 4트랙 업로드
- Gumroad 4종 Discount "FIRST50" 발행

다음 브리핑: 18:00"""

print('len10=', len(msg10))
print(send(msg10))

print('DONE')
