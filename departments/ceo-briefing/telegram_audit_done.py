"""5/8 시스템 점검 완료 — 자동 보수 + 사용자 액션 종합 보고."""
import os, json, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / ".secrets"
env = {}
if SECRETS.exists():
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or env.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID") or env.get("TELEGRAM_CHAT_ID", "")

msg = """🔧 <b>시스템 점검 + 자동 보수 완료 (5/8 11:30)</b>
━━━━━━━━━━━━━━

<b>📊 매출 현황</b>
• Gumroad 전체 누적: <b>0건</b>
• 5/7 + 5/8 새벽: 0건
• FLASH507 promo 14h 경과 (전환 0)
• 인프라 100% / 트래픽 부족

━━━ <b>✅ 자동 보수 처리 (5건)</b> ━━━

1. WhisperAtlas dead schtask 2개 삭제
2. ceo-briefing/output 22개 7일+ 산출물 archive
3. __pycache__ 16개 정리
4. <b>ebook 20권 표지+interior 재생성</b> (KDP 표준 8.5x11/6x9 적용)
5. SEO/Korlens/CmdViral 실패 schtask 원인 진단

━━━ <b>🔍 schtask 14건 실패 진단</b> ━━━

<b>자동 정상화 예정:</b>
• Longform_Mon_Thu (5/11 자동 fix, OAuth 재인증 후)
• CmdViral_12 R=2 (직접 실행 OK, msg 1487)
• OG_Weekly_Monitor R=2 (KORLENS OG 23/38 404 보고, 정상 동작)
• InnerArchetypes (Upload-Post API 일시적)

<b>사용자 액션 필수:</b>
• Korlens / KorlensPOI — TOUR_API_KEY 발급 (한국관광공사)
• YT_SleepGyeongju — music.mp3 다운 (Pixabay)

<b>버그 (low priority):</b>
• SEO_BlogFactory_0600 — Claude API 응답 JSON escape 문제. 어제 fallback 파서로 못 잡는 케이스. 매출 영향 X (long-term SEO)

━━━ <b>⚠ 사장님 액션 우선순위</b> ━━━

🔴 <b>1순위 — AppSumo submit (20분, ROI ₩6,500만~3.1억)</b>
└ 5/6 audit 사전 자동 처리 완료, 제출만

🔴 <b>2순위 — Etsy 가입 + Vela 업로드 (25분)</b>
└ KDP PNG 31개 + Vela CSV 모두 준비 완료
└ Payoneer 가입 먼저 필요 (어제 주소 단계 막힘)

🟡 <b>3순위 — KDP 20권 재업로드 (권당 5분)</b>
└ 방금 자동 fix 완료. KDP 콘솔에 재업로드만
└ +$40~100/월 잠재

🟡 <b>4순위 — 인플루언서 IG/TikTok DM 50건</b>
└ drafts 50개 [departments/influencer_outreach/drafts_global_2026_05_06](파일)
└ 1 collab = ₩300K

🟢 <b>5순위 — TOUR_API_KEY 발급</b>
└ Korlens 14일 마비 중

━━━━━━━━━━━━━━

<b>핵심 인사이트:</b> 자동화 인프라 더 이상 매출 가속 X. 매출 첫 발생 = <b>사장님 직접 액션 (DM/제출/업로드)</b> 필수. 1순위 AppSumo만 끝내도 ROI 가장 큼.

다음 자동 점검은 매일 09시 Vercel cron.
"""

url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
data = urllib.parse.urlencode({
    "chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": "true",
}).encode("utf-8")
try:
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15) as r:
        body = json.loads(r.read().decode("utf-8"))
        print(f"[OK] msg_id={body.get('result',{}).get('message_id')} length={len(msg)}")
except Exception as e:
    print(f"[ERR] {e}")
