# -*- coding: utf-8 -*-
"""4/25 21:10 CEO 브리핑 발송 (10개 메시지)"""
import os, json, urllib.request, urllib.parse, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 환경 변수 로드
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
        return {'ok': False, 'error': str(e)}

DATE = '2026-04-25'
NOW = '2026-04-25 21:10'

# ==== 메시지 1: 요약 + TOP 10 ====
msg1 = f"""📊 CEO 브리핑 | {NOW}

💰 팀별 수익
🔮 천명당: ₩0
📚 전자책: $0 (Gumroad 0건/KDP 심사중)
📺 미디어: ₩0 (44신규/1커밋, YT 파이프라인 가동)
🎮 게임: ₩0 (HexDrop 1.3 비공개테스트)
💼 세무: ₩0 (leads 수집중)
🛡️ 보험: ₩0 (API 심사 대기)
🗺️ 여행: ₩0 (POI 수집 가동)
💰 총: ₩0

🏆 오늘 해야할 일 TOP 10
1. HexDrop 1.3 정식출시 클릭 — 비공개테스트→공개 1클릭, 즉시 다운로드 유입
2. 천명당 AAB 빌드+SKU 6개 등록 — 인앱결제 매출 즉시 활성
3. KDP 3권(fishing-log/caregiver-daily/추가) 게시 — 심사 빠를수록 수익↑
4. Gumroad B2B 프롬프트팩 3종 — 한국어 시장 빠른 매출
5. TikTok 4/29 연결 D-4 — Upload-Post 워밍업 마무리
6. 카카오 사주봇 월렛 908652 검증 — 결제 흐름 끊겼는지 확인
7. 쿠팡 파트너스 누적 15만원 — 미디어부 SNS에 단축링크 자동 삽입
8. 보험 API 심사 서류 제출 — 서비스소개서 완성, 다음 단계
9. 세무 leads_2026-04-24 LinkedIn DM 5건 — 콜드 아웃리치
10. 앱인토스 .ait 콘솔 등록 — 사업자검토 통과 시 즉시 게시

(상세 부서별 보고 이어집니다 1/10 → 10/10)
"""
print('1/10', send_tg(msg1))
time.sleep(1.5)

# ==== 메시지 2: 천명당 ====
msg2 = f"""🔮 천명당팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: 카카오페이/토스페이/Google Play 광고

📋 현재 진행상황
- Play Console: 1.1 비공개 테스트 출시 완료 (4/11), 검토중
- 카카오 사주봇: 실행중 (월렛 908652)
- 토스 인앱결제: 허가 완료, SKU 등록 대기
- 앱인토스 .ait: 빌드 완료, 콘솔 등록 대기 (사업자 검토중)
- 꿈해몽 DB: 239 → 350+ 확장 필요 (치아/시험/전남친 미커버)

⚠️ 문제점
- AAB 정식 빌드 + SKU 6종 등록 사용자 직접 필요
- 꿈 검색 자연어/유사도 알고리즘 데이터 부족
- 수익 흐름 무 (광고/결제 모두 미가동)

🔧 개선 가능성
- 꿈 데이터 350+ 확장 → 자연어 검색 정확도 70%+ → DAU 2배
- 인앱결제 SKU 6종 (오늘의운세 ₩990, 사주풀이 ₩4,900 등) → ARPPU ₩3,000 가능
- 바이오리듬 좌우분할 UI 완성 → 체류시간 1.5x

🎯 진행 방향
- 이번 주: AAB 빌드 + SKU 등록 + 정식 출시
- 다음 주: 꿈 DB 350+ 확장 + 자연어 검색 v2
- 이번 달: DAU 1,000명, 결제 30건/월 목표
"""
print('2/10', send_tg(msg2))
time.sleep(1.5)

# ==== 메시지 3: 미디어 ====
msg3 = f"""📺 미디어팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0 (Adsense 미연동)
- 누적 수익: ₩0
- 수익 경로: YouTube Adsense / 쿠팡 파트너스 / KDP 프로모

📋 현재 진행상황
- YouTube 3채널 파이프라인 dry-run 통과 (Whisper Atlas/Wealth Blueprint/Inner Archetypes)
- AI Side Hustle 자동화 (Pollinations Flux, 매일 06:00) — 첫 영상 성공 4/23
- 44개 신규 파일 / 1 커밋: feat: YouTube BGM 채널 + AI Side Hustle 고도화
- 쿠팡 rotator 가동중 (단축링크 교체 TODO)
- Postiz 셀프호스트 가동 (Railway $5/월)
- TikTok 워밍업 D-4 (4/29 Upload-Post 연결)
- Bluesky/Discord/텔레그램 멀티채널 가동

⚠️ 문제점
- Adsense 수익화 전 4,000h 시청시간 미달
- coupang_rotator.py TODO: 파트너스 단축링크 교체 미완
- TikTok 본인인증 사용자 직접 필요
- 일본 시장(라인) 미진입

🔧 개선 가능성
- AI Side Hustle 일일 자동 → 30일 만에 50개 쇼츠 → 시청시간 충당
- 쿠팡 단축링크 교체 → 미디어부 SNS 모든 포스트에 자동 삽입 → 누적 15만원 빠른 도달
- Sleep Gyeongju 채널 + Wealth Blueprint 동시 가동 → ASMR/금융 듀얼 트래픽

🎯 진행 방향
- 이번 주: TikTok 4/29 연결, 쿠팡 단축링크 자동화
- 다음 주: 라인 일본 출시 자동 게시 추가
- 이번 달: 4,000h 시청시간 달성, Adsense 활성
"""
print('3/10', send_tg(msg3))
time.sleep(1.5)

# ==== 메시지 4: 보험 ====
msg4 = f"""🛡️ 보험다보여팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: B2B 데이터 라이선스 / 보험 비교 수수료

📋 현재 진행상황
- insurance_app.html 완성
- API 심사 서류 준비 완료
- 서비스소개서 작성 완료
- 변화 없음 (4/24 이후 정체)

⚠️ 문제점
- 보험업법 광고 표시 의무 사전 점검 필요 (FTC/공정위)
- API 심사 서류 제출 미진행
- 명리감수자 제거된 후속 콘텐츠 점검 필요

🔧 개선 가능성
- 보험 비교 페이지 → KORLENS/관광지도와 크로스 연결 → 이용자 풀 공유
- 데이터 라이선스 B2B 1건 = 월 100만원+ (1건이라도 큰 임팩트)

🎯 진행 방향
- 이번 주: API 심사 서류 제출 (사용자 직접)
- 다음 주: 광고 표시 의무 코드 자동 삽입
- 이번 달: B2B 리드 5건 발굴
"""
print('4/10', send_tg(msg4))
time.sleep(1.5)

# ==== 메시지 5: 전자책 ====
msg5 = f"""📚 전자책팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: $0 (Gumroad 0건)
- 누적 수익: $0
- 수익 경로: KDP 인세 / Gumroad / B2B 프롬프트팩

📋 현재 진행상황
- KDP 10권 심사중
- 신규 작업: fishing-log-book / caregiver-daily-log (6건 편집, PDF/리스팅 진행)
- AI Side Hustle 재등록 BLOCKED → 새 제목 일요일 후 재등록 대기
- 표지 일괄 수정 4/19 완료 (Deokgu Studio 통일)

⚠️ 문제점
- 표지 템플릿 텍스트 잔존 시 즉시 거절 (사전 검수 필수)
- spine 0.5인치 여백 누락 위험
- Gumroad 매출 0 (한국어 프롬프트팩 미게시)

🔧 개선 가능성
- KDP 3권 추가 게시 → 30일 후 인세 발생 시작
- Gumroad 한국어 B2B 프롬프트팩 3종 즉시 게시 → 단가 ₩39,000 × 5건 = ₩195,000/주
- 일러스트 표지 → 텍스트 표지 변환 자동화

🎯 진행 방향
- 이번 주: fishing-log + caregiver-daily 게시, KDP 3권 추가
- 다음 주: Gumroad B2B 프롬프트팩 3종 출시
- 이번 달: KDP 누적 20권, Gumroad 월 $200 달성
"""
print('5/10', send_tg(msg5))
time.sleep(1.5)

# ==== 메시지 6: 게임 ====
msg6 = f"""🎮 게임팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: Google Play / 광고 / IAP

📋 현재 진행상황
- HexDrop 1.3 비공개 테스트 게시 완료 (4/10)
- 테트리스 AI 대결 게임 완성
- 변화 없음 (4/22 이후 신규 작업 0)

⚠️ 문제점
- HexDrop 1.3 정식 출시 1클릭 미진행 → 다운로드 유입 정체
- 테트리스 AI 게임 게시 미진행
- 캐주얼 게임 트렌드 리서치 9시 자동 실행 외 자체 점검 부재

🔧 개선 가능성
- HexDrop 1.3 정식 출시 → 즉시 다운로드 유입 + 광고 수익 발생
- 테트리스 AI 게임 별도 게시 → HexDrop 사용자 풀 활용
- 캐주얼 게임 추가 1종 → 멀티 게임 포트폴리오 효과

🎯 진행 방향
- 이번 주: HexDrop 1.3 정식 출시 (사용자 1클릭)
- 다음 주: 테트리스 AI 게시
- 이번 달: 신규 게임 1종 출시
"""
print('6/10', send_tg(msg6))
time.sleep(1.5)

# ==== 메시지 7: 세무 ====
msg7 = f"""💼 세무팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: 수수료 0% 모델 (B2B SaaS / 광고)

📋 현재 진행상황
- 기획서 완성 (수수료 0% 모델)
- 프로토타입 완성
- leads_2026-04-24.md 수집 완료
- support.js TODO: Claude Agent SDK 분류 재판정 + auto_fix PR 자동 생성

⚠️ 문제점
- CODEF 정식 신청 대기중
- B2B SaaS 시장 진입 전 경쟁사 분석 미흡
- 수수료 0% 모델 → 수익원 명확화 필요 (광고? 부가서비스?)

🔧 개선 가능성
- leads → 콜드 DM 5건/일 → 1주일 후 첫 미팅
- 광고 모델 → 세무사·회계사 광고 ₩50,000/월 × 20개 = ₩1,000,000
- Claude Agent SDK 분류 자동화 → 운영비 절감

🎯 진행 방향
- 이번 주: leads LinkedIn DM 5건/일, support.js TODO 처리
- 다음 주: CODEF 신청 결과 추적
- 이번 달: B2B 첫 계약 1건
"""
print('7/10', send_tg(msg7))
time.sleep(1.5)

# ==== 메시지 8: 여행지도 ====
msg8 = f"""🗺️ 여행지도팀 상세 보고 | {DATE}

💰 수익 현황
- 어제 수익: ₩0
- 누적 수익: ₩0
- 수익 경로: KORLENS 광고 / 관광 협업

📋 현재 진행상황
- POI 수집 4/25 작업중
- KORLENS 4/25 로그 수집중
- KORLENS 현지인 픽 구축: Supabase + Google OAuth 연동중
- 카카오 KOE205 해결 완료 (사용자 Client ID 수정)

⚠️ 문제점
- KORLENS 사용자 트래픽 0
- 관광 마케팅 채널 미연결
- POI 데이터 양이 경쟁사 대비 적음

🔧 개선 가능성
- KORLENS + 천명당 크로스링크 → 천명당 사용자 → KORLENS 유입
- 경주 타겟 → "경주도약" 사업계획서 통과 시 정부 지원 광고비 확보
- POI 1,000+ 확장 → 검색 노출 ↑

🎯 진행 방향
- 이번 주: Supabase 연동 마무리, POI 500+ 추가
- 다음 주: 천명당 ↔ KORLENS 크로스링크
- 이번 달: KORLENS DAU 100명
"""
print('8/10', send_tg(msg8))
time.sleep(1.5)

# ==== 메시지 9: 지원부서 ====
msg9 = f"""⚖️ 법무정책부 + 📊 데이터분석부 | {DATE}

⚖️ 법무정책부
- privacy.html ✅
- terms.html ✅
- 보험업법 광고 표시 의무 사전 점검 (다음 주 보험API 제출 전 필수)
- TikTok·Upload-Post 워밍업 광고 게시 기록 → FTC/공정위 표시 의무
- 자동 포스트에 본인·고객(박솔이 등) 개인정보 삽입 금지 (브랜드명만)

📊 데이터분석부
- GA4 (G-90Y8GPVX1F) 설치 완료
- intelligence/sales_collector.py TODO: 실제 Vercel Analytics API 연동 필요
- Gumroad/pytrends/Product Hunt 자동 수집 가동
- Reddit·X 검색 스킵 상태 (대안 채널 필요 시 검토)
- 부서mtime 자동 추적: 미디어 압도(44신규), 그 외 6개 부서 변화 0
"""
print('9/10', send_tg(msg9))
time.sleep(1.5)

# ==== 메시지 10: 수집부 ====
msg10 = f"""🔍 수집부 보고 | {DATE}

😤 사람들이 불편해하는 것 TOP 10
1. Z세대 외로움 73% — 트렌드코리아2026 — 천명당 사주봇/감정 챗봇 솔루션 — 즉시 가능 (2주)
2. 1인가구 식사·청소·돌봄 부담 — 서울복지실 — caregiver-daily-log + AI 자동화 — 1주
3. 세무·연말정산 어려움 — 직장인 인터뷰 다수 — 세무팀 SaaS — 진행중 1개월
4. 보험 비교 어려움 — 한국웰스리포트 — 보험다보여 API — 심사 대기 2주
5. AI 도구 너무 많아 선택 곤란 — 부업 검색 트래픽 — Gumroad 큐레이션 팩 — 1주
6. 꿈 해몽 검색해도 정확한 답 없음 — 천명당 로그 — 꿈DB 350+ 확장 — 1주
7. 게임 광고 너무 길고 강제 — 모바일게임 리뷰 — HexDrop 광고 최소화 출시 — 즉시
8. 한국 여행 정보 외국인 접근 어려움 — KORLENS 가설 — 다국어 POI — 2주
9. 캐주얼 일러스트 표지 KDP 거절 — 메모리 기록 — 표지 자동 검수 스크립트 — 3일
10. 콘텐츠 자동 게시 후 광고 표시 누락 위험 — FTC 가이드 — 미디어부 자동 #광고 태그 — 1일

💰 수익 창출 좋은 모델 TOP 10
1. AI 자동화 사이드허슬 강의/팩 — 시장 ₩1,000억+ — 진입 하 — 월 ₩300만 — 트렌드 정점
2. 한국어 GPT 프롬프트팩 B2B — ₩100억+ — 하 — 월 ₩200만 — 경쟁 적음
3. KDP 일지/플래너 (낚시·돌봄) — $5억+ — 중 — 월 $300 — 진입 빠름
4. AI 쇼츠 자동화 채널 운영대행 — ₩500억+ — 중 — 월 ₩500만 — 4,000h 후 폭발
5. 외로움 타겟 운세·감정 챗봇 — ₩300억+ — 중 — 월 ₩300만 — Z세대 73%
6. 1인가구 돌봄 일정·체크리스트 SaaS — ₩200억+ — 중 — 월 ₩200만 — 정부지원
7. 캐주얼 모바일게임 광고 모델 — ₩2조+ — 상 — 월 ₩100만 — HexDrop 발판
8. 세무사 광고 매칭 플랫폼 — ₩500억+ — 중 — 월 ₩100만 — 수수료 0%
9. 다국어 한국 여행 큐레이션 — ₩1,000억+ — 중 — 월 ₩200만 — KORLENS
10. 보험 데이터 B2B 라이선스 — ₩300억+ — 상 — 월 ₩100만 — 1건 임팩트 큼

(브리핑 종료 10/10)
"""
print('10/10', send_tg(msg10))
print('완료')
