# -*- coding: utf-8 -*-
import sys, urllib.request, urllib.parse, json
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOKEN = '8650272218:AAHIYmOVfqzMzr-hcOqWsfW6mftByoEd_SA'
CHAT = '8556067663'

msg = """🚀 5월~7월 신청 가능 공모전 TOP 5 (전수 검색 완료)
━━━━━━━━━━━━━━━━━━━

📊 KunStudio 적격 13건 발견. ROI 순:

1️⃣ K-스타트업 AI 리그 2026 ⭐⭐⭐
   마감: 5/20 (D-15)
   상금: 왕중왕전 5억
   매칭: 천명당+세금N혜택+KORLENS 3 AI 라인업
   🔗 k-startup.go.kr

2️⃣ 관광기업 데이터·AI 활용 지원 ⭐⭐⭐
   마감: 5/20 (D-15)
   지원: AI솔루션 100만 + 캠페인비 최대 1천만
   매칭: KORLENS 100%
   🔗 touraz.kr/announcementList

3️⃣ 모두의 창업 로컬트랙 ⭐⭐⭐
   마감: 5/15 (D-10)
   상금: 활동 200만 + 사업화 3천만 + 우승 1억
   매칭: 비수도권 90% 선발 = 경주 SS급
   🔗 modoostartup.kr

4️⃣ K-Global 해외진출 (GDIN) ⭐⭐
   마감: 상시 (~9/30, 매월 평가)
   지원: 컨설팅+해외전시+IR+테크매칭
   매칭: 글로벌 매출 라이브 = 검증 자료
   🔗 k-global.kr

5️⃣ 콘텐츠 스타트업 지원 (콘진원) ⭐⭐
   마감: 2026 모집중 (확인 필요)
   지원: 최대 1.8억
   매칭: 게임 8종 + ebooks 27+
   🔗 콘진원 검색

❌ 부적격 (자동 제외)
• 청년기업가대회 (41세 → 청년X)
• 로컬기업 (제주 한정)
• 인디크래프트/GMEP (마감)
• 스포츠 공모 (분야X)

━━━━━━━━━━━━━━━━━━━
💡 4/24 경북도약 사업계획서 docx 3건 70% 재활용 가능
   (지난번 작성한 사업계획서_초안/로컬KORLENS/혁신세금N혜택)
   AI 리그/관광 AI/모두의창업 모두 30% 리라이트만

📷 LinkedIn 사진 알림
사진 받으려 했는데 기존 봇이 offset 이미 advance 시켜
서버 큐에서 사라짐 ㅠ
👉 사진 다시 한 번 보내주세요!
   봇 업데이트해서 이번엔 자동 저장 → 즉시 LinkedIn 업로드

━━━━━━━━━━━━━━━━━━━
🤔 사용자 결정 필요

A) 사업계획서 5개 자동 작성 시작? (오늘 기존 docx 베이스 70% 재활용)
B) 1순위 K-스타트업만 먼저? (안전)
C) k-startup.go.kr 가입 + siren24 실명인증부터? (사용자만 가능)

→ 답변 주시면 즉시 시작
"""

data = urllib.parse.urlencode({'chat_id': CHAT, 'text': msg}).encode('utf-8')
req = urllib.request.Request(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=data)
with urllib.request.urlopen(req, timeout=30) as r:
    print('telegram:', json.loads(r.read()).get('ok'))
