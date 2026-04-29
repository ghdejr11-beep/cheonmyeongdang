# -*- coding: utf-8 -*-
"""CEO 브리핑 텔레그램 발송 - 2026-04-26 18:09"""
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
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {'error': str(e)}

# === 메시지 1: 요약 + TOP 10 ===
msg1 = """📊 CEO 브리핑 | 2026-04-26 18:09

💰 팀별 수익 (당일)
🔮 천명당: ₩0 (Play 비공개 검토중)
📚 전자책: $0 (KDP 심사 10권)
📺 미디어: ₩0 (Bluesky/Discord/Telegram 가동)
🎮 게임: ₩0 (HexDrop 1.3 비공개)
💼 세무: ₩0 (CODEF 프로덕션 승인)
🛡️ 보험: ₩0 (GADP 겸업 승인 대기)
🗺️ 여행: ₩0 (KORLENS 공모전 출품)
💰 총: ₩0 (수익 부서 가동률 80%, 매출 채널 미오픈)

🏆 오늘 해야할 일 TOP 10
1. HexDrop 1.3 정식 출시 클릭 — 비공개 테스트 통과, 정식 전환 1클릭이면 즉시 매출 채널 OPEN
2. 천명당 Play 콘솔 비공개→비공개 트랙 v1.2 AAB 업로드 — 인앱 SKU 6종 활성화
3. KDP 11~13권 업로드 — KDP 거절방지 룰(저자명 Deokgu Studio, 표지 텍스트 금지) 준수
4. Gumroad B2B 디지털 상품 3종 출시 — legal-firstconsult-pack/tax-advisor-pack 등 핀터레스트 핀 완성
5. TikTok 워밍업 D+2/5 — kunstudio 프로필 일일 1회 좋아요·시청 (4/29 연결 예정)
6. Postiz Hobby 가동 검증 — 텔레그램 외 IG/TikTok/YT/X 단일 API 라우팅 확인
7. KORLENS 카카오 OAuth Client ID 수정 — KOE205 해결 후 Supabase 로그인 정식 가동
8. 보험팀 GADP 겸업 보고 — 진행/포기 결정 (법적 리스크 차단)
9. CODEF env Vercel 추가 — CLIENT_ID/SECRET/PUBLIC_KEY → /v1/kr/public/nt/proof-issue/tax-cert-all 연동
10. 데이터분석부 GA4 (G-90Y8GPVX1F) 일일 트래픽 보고 자동화 — 첫 데이터 수집 시점 확정"""

# === 메시지 2: 천명당 ===
msg2 = """🔮 천명당팀 상세 보고 | 2026-04-26

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: 카카오페이/토스페이/광고 (전부 채널 OPEN 전)

📋 현재 진행상황
- Play Console: v1.1 비공개 테스트 검토중
- 카카오 사주봇: 실행중 (월렛 908652)
- 토스 인앱결제: 허가 완료, SKU 6종 미설정
- 앱인토스: 사업자 검토중 (.ait 빌드 완료)
- 꿈해몽 데이터: 239개 (목표 350+, 치아/시험/전남친 등 누락)

⚠️ 문제점
- 매출 채널 0개 — Play 정식 출시 전이라 결제 불가
- 꿈해몽 사전 부족 — 사용자 검색에서 "no result" 다수
- 카카오 사주봇 일일 트래픽 미측정 (광고 매출 추정 불가)

🔧 개선 가능성
- v1.2 AAB 업로드 + SKU 6종 등록 → 결제 채널 즉시 OPEN (예상 첫 매출 7일 내)
- 꿈사전 +120건 일일 1회 자동 추가 (Claude로 batch 생성) → 검색 성공률 60%→90%
- 사주봇 GA4 연결 → 광고 단가 협상 근거

🎯 앞으로 진행 방향
- 이번 주: AAB+SKU 업로드, 꿈사전 350개 돌파
- 다음 주: 정식 출시 클릭, 광고 채널 1개 OPEN
- 이번 달: MAU 1,000 / 첫 인앱 결제 발생"""

# === 메시지 3: 미디어 ===
msg3 = """📺 미디어팀 상세 보고 | 2026-04-26

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0 (쿠팡 파트너스 누적 15만원 도달 시 자동 승인)
- 수익 경로: 쿠팡 파트너스, YT 광고, 제휴

📋 현재 진행상황
- 가동 채널: Bluesky(@kunstudio), Discord 웹훅, Telegram
- AI Side Hustle 쇼츠: 매일 06:00 Pollinations Flux 자동 (첫 영상 Gh3WSv0mZeM, 4/23)
- YT 3채널 (Whisper Atlas/Wealth Blueprint/Inner Archetypes): dry-run 통과, schtasks 등록 대기
- TikTok 워밍업 D+2/5 (4/29 연결 예정)
- Postiz Railway Hobby $5/월 가동중

⚠️ 문제점
- IG OAuth Postiz 버그 (v2.21.6) → multi_poster.py post_instagram() 우회 사용
- X Tweet 발송 유료 ($100/월) → 연기
- 쿠팡 단축링크 미적용 (departments/media/src/coupang_rotator.py TODO)

🔧 개선 가능성
- YT 3채널 schtasks 등록 → 일일 9개 영상 자동 (광고 게재 시 월 30~50만 추정)
- 쿠팡 단축링크 적용 후 매 SNS 포스트 삽입 → 누적 15만원 달성 가속

🎯 앞으로 진행 방향
- 이번 주: YT 3채널 정식 가동, TikTok 연결 (4/29)
- 다음 주: 쿠팡 단축링크 적용
- 이번 달: 쿠팡 파트너스 정식 승인, IG/YT 첫 광고 매출"""

# === 메시지 4: 보험 ===
msg4 = """🛡️ 보험다보여팀 상세 보고 | 2026-04-26

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: 설계사 SaaS 구독, 고객 추천 수수료 (둘 다 미오픈)

📋 현재 진행상황
- 고객용/설계사용 데모 배포 완료
- API 심사 서류 준비완료
- 서비스소개서 작성완료
- landing.html 등 최근 수정 (4/26)

⚠️ 문제점
- GADP 겸업 승인 필요 (법적 리스크) — 보험업법 저촉 시 사업 중단 가능성
- 메모리 규칙: "법적 리스크 회피 최우선" → 진행 보류 상태

🔧 개선 가능성
- GADP 진행 결정 시 → 설계사 100명 대상 SaaS 월 99,000원 = 990만원 MRR 가능
- 보류 결정 시 → "추천만" 모델로 전환, 설계사가 직접 가입자 유치, 우리는 콘텐츠/툴만 제공 (보험업법 회피)

🎯 앞으로 진행 방향
- 이번 주: GADP 겸업 진행/포기 결정 (사용자 결정 사항)
- 다음 주: 결정 따라 콘텐츠 전환 또는 API 심사 제출
- 이번 달: 설계사 1호 유치 또는 사업 피벗"""

# === 메시지 5: 전자책 ===
msg5 = """📚 전자책팀 상세 보고 | 2026-04-26

💰 수익 현황
- 어제 수익: $0
- 누적 수익: $0 (KDP 첫 매출 미발생)
- 수익 경로: KDP 인쇄, Gumroad 디지털, 크티 한국

📋 현재 진행상황
- KDP 10/20권 출판 (심사 대기/통과)
- 디지털 상품 10종 생성 (digital-products/prompts/)
- A+ 콘텐츠 zodiac-mandala-coloring 등 완성
- kdp_description.html 일괄 수정 (4/26)

⚠️ 문제점
- KDP 심사 10권 대기 (거절 위험: 표지 텍스트, spine 여백, 저자명 통일)
- Gumroad 매출 0건 (런칭 후 마케팅 부재)
- 크티 한국 등록 진행 중 (한줄설명/상세설명 누락 반복 위험)

🔧 개선 가능성
- KDP 11~13권 업로드 (거절방지 체크리스트 적용) → 심사 통과율 +30%
- Gumroad B2B 3종 출시 (legal-firstconsult/tax-advisor/saju-diary) → 첫 매출 7일 내 가능
- 크티 11가지 필드 체크리스트 자동화 → 상세설명 누락 0건

🎯 앞으로 진행 방향
- 이번 주: 11~13권 KDP 업로드, Gumroad 3종 출시
- 다음 주: 핀터레스트 핀 일일 6개 자동, 키워드 최적화
- 이번 달: KDP 첫 매출, Gumroad 누적 $500"""

# === 메시지 6: 게임 ===
msg6 = """🎮 게임팀 상세 보고 | 2026-04-26

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: AdMob 광고, 인앱 구매

📋 현재 진행상황
- HexDrop 1.3 비공개 테스트 게시 (4/10)
- 테트리스 AI 대결 게임 완성
- AdMob auth setup 완료

⚠️ 문제점
- 비공개 테스트 4/10부터 16일 경과 — 정식 출시 클릭 미실행
- 테스터 피드백 0건 (실유저 부재)
- AAB 업로드는 Play 콘솔 수동 (사용자 작업)

🔧 개선 가능성
- 정식 출시 클릭 1번 → 다운로드 채널 즉시 OPEN, AdMob 매출 발생 가능
- 신규 캐주얼 게임 1개 추가 개발 (게임팀 9시 실행 시 리서치+빌드 자동)

🎯 앞으로 진행 방향
- 이번 주: HexDrop 1.3 정식 출시 클릭
- 다음 주: 신규 캐주얼 게임 1개 비공개 출시
- 이번 달: AdMob 첫 매출, MAU 500"""

# === 메시지 7: 세무 ===
msg7 = """💼 세무팀 상세 보고 | 2026-04-26

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: 종소세 계산기 광고, CODEF 프록시 서비스

📋 현재 진행상황
- 종소세 계산기 완성, Vercel 배포 (tax-n-benefit-api.vercel.app)
- CODEF 프로덕션 승인 (4/22, .secrets 저장)
- service_no 000007456002, authorities PUBLIC 포함
- index.html 등 src/assets 최근 수정

⚠️ 문제점
- Vercel env CODEF_CLIENT_ID/SECRET/PUBLIC_KEY 미설정 → CODEF API 미연동
- /v1/kr/public/nt/proof-issue/tax-cert-all 엔드포인트 미구현
- 사용자 트래픽 0 (런칭 마케팅 부재)
- support.js Claude Agent SDK 분류 TODO

🔧 개선 가능성
- env 추가 + 엔드포인트 1개 구현 → 증명서 발급 자동화 (회당 100원 단가 가능)
- 종소세 마감 시즌(5월) 직전 트래픽 폭증 — 마케팅 1주일 집중

🎯 앞으로 진행 방향
- 이번 주: env 추가, CODEF 엔드포인트 연동, 첫 호출 테스트
- 다음 주: 종소세 5월 시즌 마케팅 (블로그/SEO/광고)
- 이번 달: 첫 1,000 트래픽, 첫 매출"""

# === 메시지 8: 여행지도 ===
msg8 = """🗺️ 여행지도팀 (KORLENS) 상세 보고 | 2026-04-26

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: 광고, 제휴, 공모전 상금/지원금

📋 현재 진행상황
- 2026 관광데이터 공모전 출품 완료 (4/18)
- Vercel 배포, AI 큐레이터 챗봇 가동
- Supabase + Google OAuth 연동중
- 카카오 OAuth Client ID 수정 대기 (KOE205)
- POI 일일 로그 수집중

⚠️ 문제점
- 카카오 OAuth KOE205 미해결 → 한국 사용자 로그인 차단
- 외국인 모드 UI 영문화 v2 미완료
- 공모전 결과 5월 예정 (대기)

🔧 개선 가능성
- 카카오 Client ID 수정 1회 → 로그인 OPEN, MAU 5배 가능
- 외국인 영문 UI 완성 → 일본/동남아 사용자 유입

🎯 앞으로 진행 방향
- 이번 주: 카카오 KOE205 해결, 영문 UI v2 50%
- 다음 주: 공모전 예비심사 결과 대비 (5월), 영문 UI 완성
- 이번 달: 예비심사 통과 시 개발지원금 + 컨설팅 수령"""

# === 메시지 9: 지원부서 ===
msg9 = """⚖️ 법무정책부: privacy.html ✅ / terms.html ✅ / GADP 겸업 보험팀 결정 대기 / 메모리 규칙 "법적 리스크 회피 최우선" 적용중
📊 데이터분석부: GA4 (G-90Y8GPVX1F) 설치완료 / 일일 트래픽 자동 보고 미구현 / Vercel Analytics API 연동 TODO (intelligence/sales_collector.py) / 첫 데이터 집계 시점 미정"""

# === 메시지 10: 수집부 ===
msg10 = """🔍 수집부 보고 | 2026-04-26

😤 사람들이 불편해하는 것 TOP 10
1. 종소세 신고 직접 하기 어려움 — Reddit r/korea — Claude로 단계별 자동화 가이드 + CODEF 연동 — 1주
2. 꿈 의미 검색 시 "no result" — 천명당 사용자 — 꿈사전 +120건 자동 추가 — 3일
3. KDP 표지 거절 사유 불명확 — KDP 커뮤니티 — 거절방지 체크리스트 자동 적용 — 1일
4. 보험 설계사 추천 신뢰성 부족 — 네이버 카페 — 보험다보여 GADP 결정 후 콘텐츠 전환 — 2주
5. 인스타 자동 포스팅 OAuth 막힘 — Postiz GitHub — multi_poster.py 직접 호스팅 CDN 우회 (메모리 적용) — 즉시
6. 한국 외국인 관광 정보 영문 부족 — KORLENS 분석 — 영문 UI v2 완성 — 1주
7. 일일 자영업 수익 집계 자동화 — 사용자 본인 — 부서별 unified_revenue.py 가동 (이미 구축) — 즉시
8. AAB 업로드 자동화 불가 — 메모리 기록 — Play 콘솔 수동 (변경 불가) — 사용자 작업
9. KORLENS 카카오 로그인 KOE205 — 사용자 본인 — Client ID 수정 1회 — 1일
10. AI 쇼츠 자막 후보정 시간 소모 — Edge TTS / Naver CLOVA Voice 무료 한도 활용 검토 (대체 후보 D:\KunStudio_IP\ 보고서 참조)

💰 수익 창출 좋은 모델 TOP 10
1. 종소세 5월 시즌 SaaS — 시장 800만 자영업자 — 진입장벽 중 — 월 200~500만 — CODEF 승인 + 5월 직전
2. KDP 영어 도서 (AI 활용) — 글로벌 — 진입장벽 하 — 월 50~200만 — 이미 10권 출판 중
3. Gumroad B2B 프롬프트팩 — 시장 글로벌 — 진입장벽 하 — 월 100~300만 — 3종 출시 임박
4. AI 쇼츠 광고 (3채널 자동) — YT 글로벌 — 진입장벽 하 — 월 30~100만 — schtasks 등록만 남음
5. 천명당 사주 인앱 SKU 6종 — 시장 한국 — 진입장벽 중 — 월 50~150만 — AAB 업로드 1회
6. KORLENS 외국인 광고/제휴 — 시장 K-tourism — 진입장벽 중 — 월 30~100만 — 영문 UI 후
7. 보험 설계사 콘텐츠 SaaS (GADP 회피형) — 시장 30만 설계사 — 진입장벽 하 — 월 50~200만 — 추천 모델로 전환
8. HexDrop AdMob — 시장 글로벌 — 진입장벽 하 — 월 10~50만 — 정식 출시 클릭만
9. 쿠팡 파트너스 SNS 자동 — 시장 한국 — 진입장벽 하 — 월 30~80만 — 누적 15만 달성 후
10. AI 쇼츠 콘텐츠 도매 (대행) — 시장 1인기업 — 진입장벽 중 — 월 50~150만 — 무료 TTS 스택(Edge/CLOVA) 기반 패키지화"""

# Send all
msgs = [msg1, msg2, msg3, msg4, msg5, msg6, msg7, msg8, msg9, msg10]
results = []
for i, m in enumerate(msgs, 1):
    r = send_tg(m)
    ok = 'ok' in r and r.get('ok')
    results.append((i, ok, r.get('error', '')))
    print(f"msg{i}: {'OK' if ok else 'FAIL'} {r.get('error','')}")
    time.sleep(1)

print("\n=== 발송 완료 ===")
print(f"성공: {sum(1 for _,ok,_ in results if ok)}/{len(results)}")
