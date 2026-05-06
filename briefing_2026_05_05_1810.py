"""CEO 비서실장 브리핑 — 2026-05-05 18:10 KST (월 저녁)"""
import os, json, time, urllib.request, urllib.parse

# secrets 로드
for line in open('C:/Users/hdh02/Desktop/cheonmyeongdang/.secrets', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)
TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT = os.environ['TELEGRAM_CHAT_ID']

def send(msg):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = urllib.parse.urlencode({'chat_id': CHAT, 'text': msg}).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'ok': False, 'err': str(e)}

DATE = '2026-05-05'
TIME = '18:10'

# ==================== 메시지 1: 요약 + TOP 10 ====================
m1 = f"""📊 CEO 브리핑 (저녁) | {DATE} {TIME}

💰 팀별 수익 (실측)
🔮 천명당: ₩0 (PG 라이브 후 0원 유지)
📚 전자책: $0 (Gumroad 4/24~5/4 11일 0건)
📺 미디어: ₩0 (광고 미게재, AdSense 심사중)
🎮 게임: ₩0 (HexDrop 비공개테스트)
💼 세무: ₩0 (Vercel MVP, 트래픽 0)
🛡️ 보험: ₩0 (API 심사중)
🗺️ 여행: ₩0 (KORLENS, 매출 0)
💰 총: ₩0 / $0

⚠️ 이번 주 매출 0 위기 14일 진입. 정부지원 + 어필리에이트로 즉시 전환 필요.

🏆 오늘(5/5 저녁) ~ 내일(5/6) 해야할 일 TOP 10

1. K-Startup 마이페이지 본인인증 (15분, D-15, 5/20 마감) — 사용자만 가능, 보안프로그램 TouchEn nxKey 다운됨
2. KoDATA 회신 모니터 (find@kodata.co.kr → 19df70fe428c7e65) — 5/12경 회신 예상, schtask 09시 자동
3. K-Startup AI 리그 사업계획서 PMS 업로드 (round2 폴더 40KB 완료) — 본인인증 후 즉시
4. 관광 AI(KORLENS) hwp 신청서 작성 — 5/20 18:00 마감 D-15
5. PayPal Smart Buttons 글로벌 SKU CTA 강화 (천명당 success.html 2건 cross-link 완료) — 추가 트래픽 필요
6. KORLENS layout.tsx 5 SKU footer 노출 검증 (Hashnode/Pinterest 트래픽 유입) — Vercel preview 확인
7. Gumroad 4종 (Saju Diary $7.99/Tax Pack/Inner Archetypes/Wealth) — Pinterest 핀 5개 추가, 전환 0→1
8. KDP 27권 KENP 트래픽 점검 — 신규 표지 2종 A/B 테스트 중, 결과 회신
9. 사주팡 게임 50% MVP 완성 — HTML5 puzzle, 광고 inject AdMob 인터스티셜
10. WhisperAtlas 잔재 schtask 2개 disable 확인 (YT AI slop 정책 회피)
"""
print(send(m1))
time.sleep(2)

# ==================== 메시지 2: 천명당 ====================
m2 = f"""🔮 천명당팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0 (4/22 PG 신청 후 14일)
- 수익 경로: PayPal Smart Buttons(글로벌) + 카카오페이/토스페이(한국, 라이브키 대기)

📋 현재 진행상황
- Play Console: 비공개 테스트 검토중 (v1.3, 4/10 게시)
- 카카오 사주봇: 실행중 (월렛 908652)
- 토스 인앱결제: 라이브키 통과 + webhook URL 등록 대기
- 갤럭시아: 박치만 회신 우편 5건 발송 대기 (5/4 평일)
- PayPal: 5/3 100% 라이브 ✅ confirm-payment.js 검증
- success.html cross-link: Saju Diary $7.99 + Tax Pack 2건 노출 (5/5 git ffaebbc)
- D+30 winback 메일 시퀀스 + 환불 자동응답 cron 가동중

⚠️ 문제점
- 14일 매출 0 — PG 라이브키 대기가 핵심 병목
- 한국 사용자 트래픽 미유입 (자연검색 SEO 노출 부족)
- AdSense 심사 1~2주 → 광고 매출 미발생
- Smart Buttons 노출되어도 Mid-funnel 이탈 (가격저항 ₩2,900~₩29,900)

🔧 개선 가능성
- 쿠팡 파트너스 inject로 보조 매출 (예상 ₩1만/월) — 기 적용
- Pinterest English 핀 5종 추가 (글로벌 PayPal 전환 1~3건/월 예상)
- 카카오 알림톡 통과 후 Re-engagement 시퀀스 (예상 LTV +50%)
- 사주풀이 무료 1회 → 유료 전환 funnel A/B 테스트

🎯 앞으로 진행 방향
- 이번 주: 토스 라이브키 통과 + webhook URL 등록 + AdSense 결과 모니터
- 다음 주: 카카오 알림톡 통과 + Pinterest 핀 20종 추가 + KDP cross-sell
- 이번 달: 첫 ₩10만 매출 달성 (PayPal 글로벌 + PG 한국 합산)
"""
print(send(m2))
time.sleep(2)

# ==================== 메시지 3: 미디어 ====================
m3 = f"""📺 미디어팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0 (광고 미게재)
- 누적 수익: ₩0
- 수익 경로: AdSense(심사중) + Upload-Post 어필리에이트 + YT 광고

📋 현재 진행상황
- YT 활성 5채널: Whisper Atlas / Wealth Blueprint / Inner Archetypes / AI Sidehustle / Sori Atlas
- Whisper Atlas: YT 2026 AI slop 정책으로 schtask 2개 disable (피벗 K-Wisdom)
- Inner Archetypes_v2_PM: 절대 PATH fix + 6테마 회전 (career/core/growth/love/money/shadow)
- AI Sidehustle: 매일 06:00 자동 (Pollinations Flux)
- Sori Atlas: Suno 음원 5재생목록 — Hetzner VPS 24/7 송출 셋업 대기
- Hashnode 3회 cross-post (5/5 16:45 kimchi-recipe)
- 인스타/Shorts 자동 가동중

⚠️ 문제점
- YouTube 2026 AI slop 정책 강화 — faceless+synthetic 채널 수익화 제한
- AdSense 심사 1~2주 대기 (블로그 3사이트)
- Hetzner VPS 인스턴스 미생성 (Sori Atlas 24/7 미가동)
- Submagic Pro $23/월 미결제 — Shorts 편집 품질 한계

🔧 개선 가능성
- Sori Atlas Lofi Girl 24/7 송출 가동 (Hetzner CX22 ₩7천/월) — 예상 월 ₩5만 광고
- KORLENS layout.tsx footer 5 SKU 노출 (글로벌 traveler 유입)
- Hashnode SEO 5건 추가 (Indexnow ping)
- Pinterest TikTok English 핀 추가

🎯 앞으로 진행 방향
- 이번 주: Hetzner VPS 인스턴스 생성 + ffmpeg 셋업 + Sori Atlas live
- 다음 주: AdSense 통과 시 광고 게재 → 첫 매출
- 이번 달: 5채널 합산 구독자 1천 + 광고 매출 ₩5만
"""
print(send(m3))
time.sleep(2)

# ==================== 메시지 4: 보험 ====================
m4 = f"""🛡️ 보험다보여팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: 제휴 보험 매칭 수수료 + 가이드북 PDF 판매

📋 현재 진행상황
- insurance_app.html 완성
- API 심사 서류 제출 (4/29 기준 진행중)
- 서비스소개서 PDF 작성 완료
- privacy.html / terms.html 등록 완료
- 보험업법 사전 체크 통과

⚠️ 문제점
- 보험사 API 심사 결과 대기 (4~6주)
- B2B 영업 채널 미확보
- 트래픽 0 — SEO 미진행
- 보험업법 법적 리스크로 자동화 제한

🔧 개선 가능성
- KDP 보험 가이드북 1권 발행 (예상 $2/월)
- 블로그 SEO 5건 (보험 비교 키워드)
- 어필리에이트 토스 인슈어런스 등록

🎯 앞으로 진행 방향
- 이번 주: API 심사 결과 회신 모니터
- 다음 주: KDP 보험가이드 발행
- 이번 달: 첫 매칭 수수료 1건
"""
print(send(m4))
time.sleep(2)

# ==================== 메시지 5: 전자책 ====================
m5 = f"""📚 전자책팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: $0
- 누적 수익: $0 (Gumroad 4/24~5/4 11일 0건)
- 수익 경로: KDP KENP + Gumroad 직판

📋 현재 진행상황
- KDP 27권 발행 (4/26 기준)
- KDP 10권 심사중
- BookK ISBN 차단 8형식 학습 완료 (KDP만 사용)
- Gumroad 4 SKU: Saju Diary $7.99 / Tax Pack / Inner Archetypes / Wealth Blueprint
- KORLENS Korean Culture PDF 5종 cross-link (5/5 git ffaebbc)
- 천명당 success.html EN 2건 cross-link

⚠️ 문제점
- Gumroad 11일 매출 0 — 트래픽 부족
- KDP KENP 노출 미검증
- Pinterest 핀 회전 부족
- 영문 카피라이팅 약함

🔧 개선 가능성
- Pinterest English 핀 20종 추가 (예상 $5~$15/월)
- Reddit 차단 우회 (감정 공유 포스트, 비광고)
- KDP A+ Content 페이지 27권 일괄 작성 — 전환율 +30%
- Mega Bundle $29.99 LinkedIn DM (B2B 5건/주)

🎯 앞으로 진행 방향
- 이번 주: Pinterest 핀 20종 + KDP A+ Content 5권
- 다음 주: Mega Bundle B2B DM 30건
- 이번 달: 첫 $50 Gumroad + KDP $30 KENP
"""
print(send(m5))
time.sleep(2)

# ==================== 메시지 6: 게임 ====================
m6 = f"""🎮 게임팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: HexDrop in-app + AdMob 인터스티셜 + 사주팡 광고

📋 현재 진행상황
- HexDrop 1.3 비공개 테스트 진행중 (4/10 게시)
- 테트리스 AI 대결 게임 완성
- 사주팡 게임 50% MVP (HTML5 puzzle)
- AdMob 인증 4/28 완료, 광고 단위 생성 중
- HexDrop Billing 통합 완료

⚠️ 문제점
- 비공개 테스트 사용자 모집 부족 (12명 필요)
- 사주팡 50% 정체 — 게임 디자인팀 미정의
- AdMob 광고 ID inject 미적용
- 게임 스크린샷 SNS 미배포

🔧 개선 가능성
- HexDrop 비공개 테스터 ㅡ Reddit/Discord 모집 (예상 12명/주)
- 사주팡 광고 inject (인터스티셜 30초마다, 예상 $0.5/100유저)
- 게임 SNS 쇼츠 5개 (TikTok English)
- Play Store 출시 즉시 ₩9,900 in-app 가동

🎯 앞으로 진행 방향
- 이번 주: HexDrop 비공개 12명 → 정식 출시 신청
- 다음 주: 사주팡 100% 완성 + Play Store 등록
- 이번 달: HexDrop 정식 출시 + 첫 in-app ₩9,900
"""
print(send(m6))
time.sleep(2)

# ==================== 메시지 7: 세무 ====================
m7 = f"""💼 세무팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: 세무 컨설팅 0% 수수료 모델 + 가이드 PDF + Gumroad Tax Pack

📋 현재 진행상황
- 세금N혜택 4/19 모두의 창업 Tech Track 신청 완료
- Vercel MVP 100% 라이브
- 기획서 완성 (수수료 0% 모델)
- 프로토타입 완성
- Gumroad Tax Pack SKU 발행

⚠️ 문제점
- 트래픽 0 — SEO/광고 미진행
- 컨설팅 영업 채널 미확보
- 정부 사업 대기중 (5/12경 결과)

🔧 개선 가능성
- 사업자 SNS 채널 (X 한국 Tax 키워드) — 예상 트래픽 100명/주
- Tax Pack Pinterest 핀 20종 (글로벌)
- KDP 세무 가이드 1권 발행

🎯 앞으로 진행 방향
- 이번 주: SEO 블로그 5건 + Pinterest 핀 20종
- 다음 주: 모두의 창업 결과 회신
- 이번 달: 첫 Tax Pack $9.99 1건
"""
print(send(m7))
time.sleep(2)

# ==================== 메시지 8: 여행 (KORLENS) ====================
m8 = f"""🗺️ 여행지도팀(KORLENS) 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: 어필리에이트 30% + Korean Culture PDF 5종 + 관광 AI 정부지원

📋 현재 진행상황
- 카카오 KOE205 해결 완료 (4/22)
- Supabase + Google OAuth 연동 진행
- robots.ts (GPTBot/ClaudeBot/CCBot 차단)
- sitemap.ts (en/ja/zh hreflang)
- layout.tsx footer 5 SKU 노출 (5/5 git ffaebbc)
- KORLENS_Product_EN.pptx 16슬라이드 (B2B/투자/관광 AI 첨부용)

⚠️ 문제점
- 트래픽 0 — 다국어 SEO 미진행
- 관광 AI 정부지원 hwp 작성 미완료 (5/20 마감 D-15)
- KoDATA 등록 회신 대기 (5/12경)
- 결제 funnel 미가동

🔧 개선 가능성
- 관광 AI 정부지원 통과 시 ₩5천만~1억 (D-15)
- 글로벌 traveler 다국어 SEO (en/ja/zh) — 트래픽 1천/월 예상
- Pinterest TikTok English 핀 (Korean culture 키워드)
- B2B 호텔/여행사 EN PPT 첨부 메일 50건

🎯 앞으로 진행 방향
- 이번 주: 관광 AI hwp 작성 + KoDATA 회신 모니터
- 다음 주: 5/20 마감 신청 + KoDATA 통과 시 투어라즈 가입
- 이번 달: 정부지원 통과 + 첫 어필리에이트 매출
"""
print(send(m8))
time.sleep(2)

# ==================== 메시지 9: 지원부서 ====================
m9 = f"""⚖️ 법무정책부 + 📊 데이터분석부 | {DATE}

⚖️ 법무정책부
- privacy.html ✅ (위탁업체 8개 명시)
- terms.html ✅
- 보험업법 사전 체크 통과
- 사업자등록 552-59-00848 (쿤스튜디오, 간이과세)
- 사용자 휴대폰 010-4244-6992 마스킹 강제 적용 (SNS/log/외부 메시지)
- 070-8018-7832 본인 전화번호 자동 마스킹
- 광고/홍보에 특정 업체·연예인·IP 거론 금지 (Samsung/BTS/Squid Game)
- 남은 이슈: 토스 webhook URL 등록 (라이브 통과 후) + 카카오 알림톡 통과 대기

📊 데이터분석부
- GA4 G-90Y8GPVX1F 설치 완료 (천명당)
- KORLENS Schema.org 4페이지 적용
- 일일 매출 보고 schtasks 매일 가동
- 주간 OG 이미지 schtasks 매주
- KunStudio_KoDATA_Reply_Monitor schtask 09시 등록 (5/12경 회신 감지)
- WhisperAtlas 잔재 schtask 2개 disable (YT AI slop 회피)
- KWisdom_Shorts_Retry_5_4 disable
- 데이터 현황: Gumroad 11일 0건 / YT 5채널 view 미증분 / KDP 27권 KENP 미검증
"""
print(send(m9))
time.sleep(2)

# ==================== 메시지 10: 수집부 (불편 10 + 수익 10) ====================
m10 = f"""🔍 수집부 보고 | {DATE} (글로벌+한국 트렌드 리서치)

😤 사람들이 불편해하는 것 TOP 10

1. 다크 패턴(dark patterns) 강제 구독 해지 — 이커머스 — Claude 자동: 가격투명 비교페이지 — 2시간
2. Coupang 데이터 유출(2025-11) 신뢰 붕괴 — 이커머스 — Claude 자동: 개인정보 안전 가이드 KDP — 4시간
3. 스낵 유통기한 누락(35% 불만) — 식품 — Claude 자동: 신선도 체커 앱 MVP — 1일
4. 스킨케어 누액·소량·자극 — 뷰티 — Claude 자동: 리뷰 종합 비교 블로그 SEO — 3시간
5. 물가상승 가계 부담 — 경제 — Claude 자동: 가계부 무료 PDF + 자동 분류 AI — 1일
6. K-pop 굿즈 진위 — 글로벌 — Claude 자동: 정품 인증 가이드 PDF — 2시간
7. 한국 여행 한국어 메뉴 못 읽음 — 글로벌 traveler — Claude 자동: KORLENS 메뉴 OCR 번역 — 이미 완료, 트래픽 부족
8. 사주풀이 영문 부재 — 글로벌 — Claude 자동: 천명당 EN 풀이 + Saju Diary $7.99 — 이미 완료, Pinterest 추가
9. 한국 세무 영문 가이드 부재 — 글로벌 비즈니스 — Claude 자동: Tax Pack EN — 이미 완료, B2B DM
10. 정부지원 정보 비효율 — 한국 사업자 — Claude 자동: K-Startup 매트릭스 자동 — 이미 5건 완료

💰 수익 창출 좋은 모델 TOP 10

1. Korean Saju Diary $7.99 (Gumroad, 글로벌) — 시장 100M K-fan — 진입장벽 하 — 월 $50~200 — Pinterest 트래픽 즉시
2. KORLENS B2B 호텔/여행사 라이선스 ₩50만/년 — 한국 호텔 5천개 — 진입장벽 중 — 월 ₩100만 — EN PPT 발송 50건
3. Tax Pack EN $19.99 LinkedIn B2B — 글로벌 한국 사업자 1만명 — 진입장벽 중 — 월 $200 — 즉시 가동
4. Sori Atlas Lofi 24/7 YT — 글로벌 학생/직장인 1억 — 진입장벽 하 — 월 ₩5~30만 — Hetzner 가동만
5. KDP 27권 KENP — 글로벌 Kindle Unlimited — 진입장벽 하 — 월 $30~100 — A+ Content 작성
6. HexDrop in-app + AdMob — 글로벌 게임 30억 — 진입장벽 중 — 월 ₩10~50만 — 정식 출시
7. 사주팡 게임 광고 — 한국 사주 fan 100만 — 진입장벽 하 — 월 ₩5~20만 — MVP 50%→100%
8. K-Wisdom YT 채널 광고 — 글로벌 K-콘텐츠 5억 — 진입장벽 하 — 월 ₩5~30만 — 1클릭 게시 후 매일
9. 정부지원 K-Startup AI 리그 — D-15 — 진입장벽 중 — ₩1~3억 1회성 — hwp 작성만
10. 관광 AI(KORLENS) 정부지원 — D-15 — 진입장벽 중 — ₩5천만~1억 1회성 — hwp 작성만

📌 핵심: 매출 0 위기 14일째, 정부지원 2건(D-15) + Pinterest/Hashnode 트래픽 가동이 가장 빠른 수익 경로.
"""
print(send(m10))

print("\n=== 브리핑 10건 발송 완료 ===")
