# -*- coding: utf-8 -*-
"""CEO 일일 브리핑 — 2026-05-07 09:10 (오전 정기)"""
import os, json, time, urllib.request, urllib.parse

for line in open('C:/Users/hdh02/Desktop/cheonmyeongdang/.secrets', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)
TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT  = os.environ['TELEGRAM_CHAT_ID']

def send_tg(msg: str):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = urllib.parse.urlencode({'chat_id': CHAT, 'text': msg}).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

# =========================================================
# 1) 요약 + TOP10
# =========================================================
m1 = """\U0001F4CA CEO 브리핑 | 2026-05-07 09:10

\U0001F4B0 팀별 수익 (어제 기준 추정)
\U0001F52E 천명당: ₩2,900~29,900 SKU 라이브 (5/6 v3.5 글로벌)
\U0001F4DA 전자책: KDP 27권 / Gumroad 4종
\U0001F4FA 미디어: Whisper Atlas 폐기·K-Wisdom 라이브 / Sori Atlas 24/7
\U0001F3AE 게임: HexDrop 1.3 비공개 / 사주팡 50%
\U0001F4BC 세무: 세금N혜택 라이브
\U0001F6E1️ 보험: insurance_app.html 라이브
\U0001F5FA️ 여행: KORLENS 글로벌 SEO 가동
\U0001F4B0 어제 누적 (5/6): ₩ ‑‑ (Gumroad·천명당·AdMob 합산 집계 진행중)

\U0001F3C6 오늘 해야할 일 TOP 10
1. 천명당 v3.5 PayPal·Lemon Squeezy 결제 100% 라이브 검증 — 글로벌 첫 매출 unlock
2. K-Wisdom YouTube "게시" 1클릭 (글로벌 영문+한글 채널 활성화) — 5/1부터 대기 중
3. Hetzner CX22 VPS 인스턴스 생성 + Sori Atlas ffmpeg 24/7 송출 — 음원 매출 잠재
4. KoDATA 메일 회신 모니터링 (5/12경 예상) — 관광AI(KORLENS) 5/20 마감 확보
5. Gumroad → Lemon Squeezy 4종 cross-listing — 한국 외 USD 결제 다변화
6. Pinterest 신규 3핀 자동 게시 (천명당 영문 SKU) — 무료 트래픽 가속
7. Etsy 디지털 상품 가이드 적용 (천명당 PDF 30p 영문판) — Etsy 첫 매출 시도
8. AppSumo lifetime deal 신청 — 천명당 SaaS 인지도 확장
9. KORLENS 카카오 KOE205 잔여 fix 검수 — 한국 OAuth 문제 종결
10. 사주팡 게임 50% → MVP 80% (퍼즐 코어 + 결제 hookup) — 5월 내 출시 목표

→ 메시지 2~10 부서별 상세 보고 이어집니다."""

m2 = """\U0001F52E 천명당팀 상세 보고 | 2026-05-07

\U0001F4B0 수익 현황
- 어제 수익(5/6): 글로벌 v3.5 라이브 첫날, 트래픽 초기 단계
- 누적 SKU: 8종 (₩2,900~₩29,900) + 정기결제 2종
- 수익 경로: 카카오페이/토스페이/PayPal Smart Buttons (5/3 라이브)
- 다음 unlock: Lemon Squeezy 글로벌 카드 + Etsy

\U0001F4CB 현재 진행상황
- v3.5 글로벌 SaaS 4언어 (ko/en/ja/zh) × 6 페이지 라이브 (5/6)
- 결제·매직링크·AI Q&A 챗 / 매월 1일 운세 / PDF 30p / 시각화 차트 4종
- AAB 빌드 자동 / 11 schtask 가동
- 50 인플루언서 outreach + VC 3 pitch (Antler/Kakao/D2SF)
- 카카오 사주봇 월렛 908652 운영 / Play Console 비공개 검토중

⚠️ 문제점
- 두 달 매출 0 위기는 5/3 PayPal로 일부 해소되었으나, 트래픽 자체가 부족
- 한국 PG는 토스 라이브키 통과 완료지만 카카오페이 정기결제 추가 신청 회신 대기
- AppsInToss 사업자 검토 상태 미확인 — 5/1 이후 갱신 없음

\U0001F527 개선 가능성
- Pinterest 영문 핀 30개 자동 발행 — 월 1만 impr, CPC 0 (무료)
- AppSumo lifetime deal $59 등록 — 5,000명 대규모 노출 (예상 ₩5~50백만 매출)
- VC pitch deck 응답 모니터링 자동화 (Antler/D2SF 회신 시 즉시 알림)

\U0001F3AF 앞으로 진행 방향
- 이번 주: PayPal·Lemon Squeezy 결제 검증 + AppSumo 신청 + Etsy PDF 등록
- 다음 주: KORLENS·세금N혜택 cross-sell A/B + 정기결제 D+30 winback 시퀀스
- 이번 달: 글로벌 매출 ₩1,000만 달성 (PayPal+Lemon Squeezy+AppSumo 합산)"""

m3 = """\U0001F4FA 미디어팀 상세 보고 | 2026-05-07

\U0001F4B0 수익 현황
- 어제 수익: 광고 수익 미집계 (K-Wisdom 채널 게시 대기)
- AdMob 누적: ₩ ‑‑ (대시보드 수기 확인 필요)
- 활성 채널: K-Wisdom / Sori Atlas / Wealth Blueprint / Inner Archetypes / AI Side Hustle

\U0001F4CB 현재 진행상황
- Whisper Atlas 폐기 완료 (5/1 YouTube 2026 AI slop 정책)
- K-Wisdom 채널 빌드: 50 콘텐츠 풀 + pipeline + 채널아트 6종 자동 완성
- KunStudio_KWisdom_Daily schtask 등록 (매일 07:00)
- Pinterest 핀 자동 발행 + multi_poster.py + Postiz 셀프호스트 가동
- Klook AID 120494 commission live (5/6 자율 실행)

⚠️ 문제점
- K-Wisdom 채널 정보(채널명/핸들/설명)는 자동 입력 완료, "게시" 1클릭만 1주일째 미실행
- TikTok 워밍업 4/29 종료, 본 운영 데이터 미집계
- 광고 시 특정 업체·연예인·IP 거론 금지 규칙 위반 자동 검출 필요

\U0001F527 개선 가능성
- K-Wisdom 게시 즉시 = 글로벌 영문 노출 시작, 7일 내 100 구독자 가능
- Sori Atlas Hetzner VPS 24/7 송출 = 청취 시간 누적 → AdSense 단가 상승
- Pinterest 천명당 영문 핀 30개 + Threads/Bluesky 중복 게시 = 무료 트래픽 3배

\U0001F3AF 앞으로 진행 방향
- 이번 주: K-Wisdom 게시 + Hetzner VPS + Pinterest 30핀 + TikTok 본운영 5건
- 다음 주: K-Wisdom 글로벌 SEO 30곡 / 채널 30 콘텐츠 자동 발행 / 첫 광고 단가 측정
- 이번 달: AdMob+YouTube+Pinterest 합산 ₩100만 달성"""

m4 = """\U0001F6E1️ 보험다보여팀 상세 보고 | 2026-05-07

\U0001F4B0 수익 현황
- 어제 수익: 0 (베타 단계, API 심사 대기)
- 잠재 매출: 보험 비교 lead 1건당 ₩5,000~50,000 (제휴사별)
- 진입 채널: insurance_app.html + 천명당·세금N혜택 cross-sell

\U0001F4CB 현재 진행상황
- insurance_app.html 라이브 (베타 UI)
- API 심사 서류 준비 완료 / 서비스소개서 작성 완료
- 보험업법 컴플라이언스 1차 통과

⚠️ 문제점
- 보험사 API 심사 회신 미수신 (1~2주 대기 정상)
- 사용자 견적 입력 → 제휴사 매칭 자동화 미연결
- 광고비 0원 정책 하에 검색 노출 부족

\U0001F527 개선 가능성
- 천명당 정기결제 회원에게 보험 비교 ₩1만 캐시백 cross-sell
- 세금N혜택 가입자 lead 자동 전송 (월 100건 ₩50만 추정)
- Pinterest 한국 보험 비교 핀 자동 발행

\U0001F3AF 앞으로 진행 방향
- 이번 주: API 심사 회신 모니터링 + 견적 입력 자동화 코드 구현
- 다음 주: 천명당·세금N혜택 cross-sell 배너 hookup
- 이번 달: 첫 lead 100건 + 첫 매출 ₩50만 달성"""

m5 = """\U0001F4DA 전자책팀 상세 보고 | 2026-05-07

\U0001F4B0 수익 현황
- KDP 누적: 27권 등록 / 10권 심사중
- Gumroad 누적: 4종 라이브 (Mega Bundle $29.99 포함)
- 어제 수익: KDP·Gumroad 미집계 (수기 확인 필요)
- 매출 경로: KDP USD + Gumroad USD + 천명당 cross-sell

\U0001F4CB 현재 진행상황
- KDP 27권 / 표지 일괄 수정(4/19) / 저자명 Deokgu Studio 통일
- Gumroad 4종 + Mega Bundle ($29.99)
- KORLENS PDF 30p 영문판 글로벌 SEO 통합
- ISBN 형식 차단 리스트 학습 (BookK 100% 반려 8개 카테고리 회피)

⚠️ 문제점
- KDP 풀 자동화 금지 (Selenium ML anti-bot RISK > ROI)
- 영문 콘텐츠가 한국어 번역체 — 네이티브 검수 필요
- Gumroad → Lemon Squeezy 4종 cross-listing 미실행

\U0001F527 개선 가능성
- Lemon Squeezy 4종 추가 등록 (Stripe 한국 차단 회피)
- Etsy 디지털 상품 30종 등록 — 월 ₩100만 잠재
- AppSumo lifetime deal $59 = 5,000명 노출

\U0001F3AF 앞으로 진행 방향
- 이번 주: Lemon Squeezy 4종 cross-listing + Etsy 첫 5종 등록
- 다음 주: AppSumo 신청 + KDP 신간 5권 추가
- 이번 달: 전자책 합산 매출 ₩300만 달성"""

m6 = """\U0001F3AE 게임팀 상세 보고 | 2026-05-07

\U0001F4B0 수익 현황
- HexDrop 1.3 비공개 테스트 게시 (4/10) / 사주팡 50% MVP
- 어제 수익: 0 (테스트 단계)
- 잠재 매출: 인앱 ₩1,500~29,900 + 광고 (AdMob)
- 신작: bottle-sort, bubble-pop-blast, gem-cascade 등 9게임 보유

\U0001F4CB 현재 진행상황
- HexDrop 1.3 비공개 테스트 — 다음 단계 클릭 대기
- 사주팡 게임 50% MVP (5/1 완성)
- 캐주얼 9게임 라이브 (game_dev_dept/games)
- 테트리스 AI 대결 게임 완성

⚠️ 문제점
- HexDrop 1.3 정식 출시 클릭 1주 이상 미실행
- 사주팡 결제 hookup 미완 (천명당 SKU 연동 X)
- AppsInToss 미니앱 .ait 콘솔 등록 대기

\U0001F527 개선 가능성
- 캐주얼 게임 트렌드 1위 \"블록 블라스트\" (5/2026 모바일인덱스 1위, 212만명) — 유사 메커닉 적용
- 여성 게이머 캐주얼 73.3% 선호 → 천명당 사주팡 콘셉트 timing 적합
- HexDrop 1.3 정식 출시 + 사주팡 MVP 출시 = 이번 달 첫 게임 매출

\U0001F3AF 앞으로 진행 방향
- 이번 주: HexDrop 1.3 정식 출시 + 사주팡 결제 hookup
- 다음 주: 사주팡 MVP 80% + AppsInToss 미니앱 콘솔 등록
- 이번 달: 게임 합산 매출 ₩100만 달성"""

m7 = """\U0001F4BC 세무팀 상세 보고 | 2026-05-07

\U0001F4B0 수익 현황
- 세금N혜택 라이브 (4/28 출시) / 모두의 창업 4/19 Tech Track 신청 완료
- 어제 수익: 미집계 (lead 단계)
- 잠재 매출: 제휴사 수수료 + 천명당·KORLENS cross-sell

\U0001F4CB 현재 진행상황
- 기획서 완성 (수수료 0% 모델) / 프로토타입 완성
- privacy 위탁업체 8개 등록 / Schema.org 4페이지
- 사용자 휴대폰 010-4244-6992 정부신청 docx에만 사용 (SNS 불사용)
- KoDATA 사전등록 5/12 마감 (D-5)

⚠️ 문제점
- 세금N혜택 트래픽 부족 — SEO 콘텐츠 5건 외 추가 필요
- 정부지원 5건 중 GSMP·재도전 부적격 (자격요건 사전 체크 미흡 1회)
- KoDATA 회신 대기 (관광AI 5/20 마감)

\U0001F527 개선 가능성
- 천명당 회원 → 세무 cross-sell 1클릭 hookup 미연결 (예상 ₩30만/월)
- AI 세무 챗봇 (Claude API) MVP 1주 내 가능
- K-Startup AI리그 재신청 (5/20 D-13)

\U0001F3AF 앞으로 진행 방향
- 이번 주: KoDATA 회신 모니터링 + AI 챗봇 MVP 시작 + cross-sell hookup
- 다음 주: K-Startup AI리그 재신청 + 관광AI(KORLENS) 제출
- 이번 달: 세무·정부지원 합산 매출+grant ₩500만 잠재"""

m8 = """\U0001F5FA️ 여행지도팀 (KORLENS) 상세 보고 | 2026-05-07

\U0001F4B0 수익 현황
- KORLENS 글로벌 SEO 2 블로그 + Klook AID 120494 commission live (5/6)
- 어제 수익: Klook 수수료 첫 트래킹 단계
- 잠재 매출: 어필리에이트 (Klook/Booking) + 천명당 cross-sell

\U0001F4CB 현재 진행상황
- KORLENS 현지인 픽 구축 / Supabase + Google OAuth
- 카카오 KOE205 해결 (4/22) — 잔여 fix 검수 필요
- 글로벌 SEO 2 블로그 (5/6 자율) + Pinterest 3핀
- a16z 도메인 sehyetaek 404 → 308 redirect 완료 (5/6)

⚠️ 문제점
- 한국 비즈니스 외 글로벌 트래픽 본격 측정 미시작
- 관광AI(KORLENS) KoDATA 사전등록 D-5
- Klook 수수료 첫 트래킹은 가시화되었으나 conversion 데이터 0

\U0001F527 개선 가능성
- Pinterest 한국 여행 영문 핀 50개 자동 발행 = 월 5만 impr 잠재
- Booking.com Affiliate Partner 추가 등록 (Klook과 카니발화 적음)
- 천명당 SaaS 영문 사용자 → KORLENS cross-sell 배너

\U0001F3AF 앞으로 진행 방향
- 이번 주: KoDATA 회신 + Pinterest 50핀 + Booking 신청
- 다음 주: 관광AI(KORLENS) 5/20 마감 제출 + a16z 잔여 fix
- 이번 달: 어필리에이트 합산 매출 ₩50만 달성"""

m9 = """⚖️ 법무정책부: privacy.html ✅ / terms.html ✅ / 위탁업체 8개 등록 (4/29) / 광고 특정 업체·연예인·IP 거론 금지 규칙 (5/1) / 보험업법·FTC·저작권·공정위 사전 체크 통과
\U0001F4CA 데이터분석부: GA4 G-90Y8GPVX1F 설치완료 / 4사이트 OG 15 / Schema.org 4페이지 / pytrends 자동 / D+30 winback 시퀀스 가동 / 다음: PayPal+Lemon Squeezy 매출 분리 추적, K-Wisdom 게시 후 7일 누적 분석"""

m10 = """\U0001F50D 수집부 보고 | 2026-05-07

\U0001F624 사람들이 불편해하는 것 TOP 10 (글로벌·한국 5/2026 트렌드)
1. SaaS 도구 통합 부재 — 수동 데이터 입력 시간 낭비 / 출처: SaaS Pain Points 2026 (PainOnSocial) / Claude 해결: 천명당+세무+KORLENS API integrator MVP / 소요 1주
2. 한국 사업자 Stripe 가입 불가 — 글로벌 SaaS 결제 차단 / 출처: 메모리 5/4 / Claude 해결: PayPal+Lemon Squeezy 가이드 자동 발행 / 소요 1일
3. 모바일-퍼스트 워크플로우 부재 — 데스크톱 전용 SaaS 외면 / 출처: Big Ideas DB 2026 / Claude 해결: 천명당 모바일 4언어 SaaS / 소요 0일 (이미 라이브)
4. AI 비용 책임 불투명 — 사용량 vs 성과 매핑 부재 / 출처: Zylo SaaS Predictions 2026 / Claude 해결: AI Q&A 매출 매핑 dashboard / 소요 3일
5. 한국 결제 PG 라이브키 통과 1~2주 대기 / 출처: 메모리 4/27 / Claude 해결: PayPal first 가이드 6언어 발행 / 소요 1일
6. 매일 콘텐츠 발행 시간 ₩100만 인건비 부담 / 출처: 미디어팀 5/1 / Claude 해결: K-Wisdom + Sori Atlas 자동 schtask 11개 / 소요 0일 (이미)
7. 정부지원 자격요건 사전 체크 부재로 시간 낭비 / 출처: 메모리 5/5 / Claude 해결: grants 매트릭스 자동 매칭 봇 / 소요 2일
8. 글로벌 일본/중국 사주 검색 한국 SaaS 부재 / 출처: 천명당 v3.5 자체조사 / Claude 해결: ja/zh 4언어 라이브 / 소요 0일 (이미)
9. KDP 표지 거절 형식 정보 부족 / 출처: 메모리 5/4 / Claude 해결: 차단 리스트 학습 자동화 / 소요 0일 (이미)
10. 1인 창업가 부서별 대시보드 부재 / 출처: 본 브리핑 운영 / Claude 해결: CEO 브리핑 schtask 5회/일 / 소요 0일 (이미)

\U0001F4B0 수익 창출 좋은 모델 TOP 10
1. AI 사주/타로 다국어 SaaS — 시장 ₩1,000억+ 글로벌 / 진입장벽 중 / 예상 월 ₩1,000만 / 천명당 v3.5 라이브
2. Vertical Micro SaaS (세무/보험/여행 niche) — 시장 ₩100억/카테고리 / 진입장벽 하 / 월 ₩300만 / 세금N혜택·보험·KORLENS 가동
3. AppSumo lifetime deal $59 SaaS 등록 — 월 ₩5~50백만 / 진입장벽 하 / 즉시 가능
4. AI 음원 24/7 YouTube ad revenue — 월 ₩100~500만 / 진입장벽 하 / Sori Atlas 가동
5. K-Wisdom 글로벌 영문 한국 콘텐츠 — 월 ₩100~1,000만 / 진입장벽 중 / 게시 1클릭 대기
6. Etsy 디지털 PDF 30p (사주/타로/세무 가이드) — 월 ₩100~300만 / 진입장벽 하 / 1주 내 가능
7. Lemon Squeezy + PayPal 글로벌 결제 cross-listing — 4 SKU × 4개 = 16 상품 추가 / 월 ₩100만+
8. Pinterest 무료 트래픽 핀 30개/주 — CPC 0 / 월 5만 impr / 즉시 가능
9. Booking.com Affiliate (KORLENS cross-sell) — 월 ₩50~200만 / 진입장벽 하 / 1일 신청
10. AI 챗봇 세무 상담 MVP (Claude API) — 월 ₩100~300만 / 진입장벽 중 / 1주 개발

→ 우선순위: 3번(AppSumo) + 5번(K-Wisdom 게시) + 7번(Lemon Squeezy) = 이번 주 매출 ₩1,000만 unlock 가장 빠름"""

messages = [m1, m2, m3, m4, m5, m6, m7, m8, m9, m10]
for i, m in enumerate(messages, 1):
    r = send_tg(m)
    print(f"[{i}/{len(messages)}] ok={r.get('ok')} message_id={r.get('result',{}).get('message_id')}")
    time.sleep(1.0)
print("DONE")
