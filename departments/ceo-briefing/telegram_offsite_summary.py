"""사장님 도착 시 외출 시간 종합 보고 텔레그램 push."""
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

msg = """🌅 <b>사장님 도착 — 외출 시간 종합 보고</b>
━━━━━━━━━━━━━━

<b>💸 매출 현황 (5/8 11시 기준)</b>
• Gumroad: 5/7 이후 <b>0건</b> (FLASH507 promo 활성)
• PayPal: Vercel cron 09시 자동 fetch (신규 거래 시 즉시 알림)
• 토스: 라이브키 미발급

━━━ <b>✅ 자동 작업 결과 (오늘 새벽~오전)</b> ━━━

<b>1. KDP cover 31개 PNG 변환 완료</b>
└ Vela 업로드 시 drag-drop 즉시 매칭 가능
└ 위치: departments/etsy/cover_kdp_png/

<b>2. Schtask 자동 가동 (모두 정상)</b>
✅ Pinterest_4Lang_Daily 09:30 R=0
✅ B2B_Outreach_Daily 09:30 R=0 (cold mail 5건/일)
✅ BlueskyFeed_Hourly 10:10 R=0
✅ Twitter_Daily 10:00 R=0
✅ Inbox_Monitor_V2 11:00 R=0

<b>3. SEO/SNS 콘텐츠 5/8</b>
✅ Quora draft 자동 생성 (saju 정확도, blog 링크 포함)
✅ SEO blog factory JSON fallback 작동 검증

<b>4. 새벽 OAuth 검증 완료</b>
✅ YT 4채널 OAuth (Sori Atlas / K-Wisdom / Wealth Blueprint / sori_atlas slot)
✅ AI Sidehustle 06시 영상 업로드 정상

❌ InnerArchetypes 06시 Upload-Post API 실패 (R=1) — 진단 필요

━━━ <b>⚠ 사장님 액션 대기</b> ━━━

<b>🔴 Payoneer / Etsy 가입</b> (어제 외출로 중단)
└ Payoneer 주소 입력 단계에서 막힘
└ KDP PNG 31개 + Etsy CSV 모두 준비 완료
└ 가입만 끝나면 1시간 내 40 listings 라이브

<b>🟡 인플루언서 IG/TikTok DM</b>
└ drafts 50개 [departments/influencer_outreach/drafts_global_2026_05_06](파일)

<b>🟢 AppSumo 제출</b>
└ 5/6 audit (25→20분 단축 적용 후) 사장님 form 입력만

━━━ <b>📊 진행 중 모니터</b> ━━━

🔄 Vercel paypal-monitor cron (매일 09시 자동)
🔄 5채널 SNS push (Telegram·Bluesky·X·Threads·Pinterest)
🔄 FLASH507 promo (24h 진행 중, 7상품 × 20개 max)
🔄 B2B cold mail 5건/일 자동 발송 중

━━━━━━━━━━━━━━
<b>핵심:</b> 인프라 정상 / 매출 첫 발생 대기 중. 어제 6 SNS 채널에 promo push했고 Pinterest/B2B 오늘 추가 발행. 24h 안에 첫 매출 가능성 있음.
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
