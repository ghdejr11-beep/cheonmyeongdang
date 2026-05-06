# -*- coding: utf-8 -*-
import sys, urllib.request, urllib.parse, json
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOKEN = '8650272218:AAHIYmOVfqzMzr-hcOqWsfW6mftByoEd_SA'
CHAT = '8556067663'

msg = """🚨 K-스타트업 AI 리그 2026 (5억, 미신청, D-15)
━━━━━━━━━━━━━━━━━━━
검증 완료
• 주관: 중기부 + 창업진흥원
• 모집: 4/22~5/20 (D-15)
• 대상: AI 분야 업력 3년 미만
• KunStudio: 4/1 개업 → 적격 ✅
• 상금: 왕중왕전 5억원
• 본선 130팀 → 최종 20팀

📋 신청 흔적: 0건 (메일/메모리 모두)
🎯 적합도: HIGH
• 천명당 사주 AI + KORLENS AI + 세금N혜택
• 비수도권(경주) + 라이브 매출

📅 권장 액션
• 오늘: k-startup.go.kr 가입 + siren24 실명인증
• 5/8까지: 경북도약 HWP 베이스로 리라이트
• 5/15까지: 제출

🔗 www.k-startup.go.kr

━━━━━━━━━━━━━━━━━━━
✅ 5/5 마무리

PR #38/#39/#40: 머지 완료 (확인됨)

PR #41 (Tarot+Calendar+Recipes): 1클릭 필요
→ github.com/ghdejr11-beep/cheonmyeongdang/compare/main...feat/phase-a-round3-tarot-calendar-recipes?expand=1
→ "Create pull request" → "Merge"

LinkedIn 프로필 사진:
⚠️ ToS: 개인 프로필 = 본인 얼굴 필수
로고 업로드 X (자동 삭제 + affiliate 거절 risk)
→ 사용자가 셀카 직접 업로드 (3분)

생성한 KunStudio 로고 활용처:
• Beehiiv 로고
• Hashnode publication 아바타
• Discord 서버 아이콘
• X 브랜드 계정

📍 C:\\Users\\hdh02\\Desktop\\kunstudio_logo_512.png
"""

data = urllib.parse.urlencode({'chat_id': CHAT, 'text': msg}).encode('utf-8')
req = urllib.request.Request(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=data)
with urllib.request.urlopen(req, timeout=30) as r:
    result = json.loads(r.read())
print('telegram:', result.get('ok'))
