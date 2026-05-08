"""FLASH507 50% off promo — Telegram만 (사장님 본인 채팅) 발송."""
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

msg = """🔥 <b>24시간 FLASH SALE 50% OFF</b> 🔥

쿤스튜디오 Gumroad 7개 상품 전체 반값
코드: <code>FLASH507</code>
한도: 각 상품 20개 (선착순)

<b>대상 상품 (7개)</b>
• Korean Saju Birth Chart Reading $7.99 → <b>$3.99</b>
• Korean Tax Smart Guide 2026 $7.99 → <b>$3.99</b>
• K-Wisdom Daily Planner 2026 $11.99 → <b>$5.99</b>
• Korean Wisdom Wall Art Bundle $9.99 → <b>$4.99</b>
• KunStudio Notion 5-Pack $22 → <b>$11</b>
• Korean Productivity Planner $6 → <b>$3</b>
• AI Side Hustle Tracker $5 → <b>$2.5</b>

🔗 https://ghdejr.gumroad.com/

━━━ <b>사장님 1탭 공유용</b> ━━━

🔥 24h FLASH SALE — 50% OFF on all 7 KunStudio digital products! Code: FLASH507 (limit 20 each)

✨ Korean Saju · Planner · Notion 5-Pack · Wall Art · Tax Guide · AI Side Hustle Tracker

👉 https://ghdejr.gumroad.com/

#KoreanCulture #DigitalProducts #Notion #Saju #Productivity #AIsidehustle

위 영문 메시지 복사해서 X / Threads / Bluesky / IG 스토리에 붙이시면 5채널 동시 push.
"""

url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
data = urllib.parse.urlencode({
    "chat_id": TG_CHAT,
    "text": msg,
    "parse_mode": "HTML",
    "disable_web_page_preview": "false",
}).encode("utf-8")
try:
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15) as r:
        body = json.loads(r.read().decode("utf-8"))
        print(f"[OK] msg_id={body.get('result',{}).get('message_id')} length={len(msg)}자")
except Exception as e:
    print(f"[ERR] {type(e).__name__}: {e}")
