"""24h FLASH 50% off promo — Telegram + Bluesky 직접 push (다른 채널은 schtask로 자동 발행)."""
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

# 한글 promo (텔레그램 → 사장님)
ko_msg = """🔥 <b>24시간 FLASH SALE 50% OFF</b> 🔥

쿤스튜디오 Gumroad 7개 상품 전체 반값
코드: <code>FLASH507</code>
한도: 각 상품 20개 (선착순)

<b>대상 상품</b>
• Korean Saju Birth Chart Reading $7.99 → <b>$3.99</b>
• Korean Tax Smart Guide 2026 $7.99 → <b>$3.99</b>
• K-Wisdom Daily Planner 2026 $11.99 → <b>$5.99</b>
• Korean Wisdom Wall Art Bundle $9.99 → <b>$4.99</b>
• KunStudio Notion 5-Pack $22 → <b>$11</b>
• Korean Productivity Planner $6 → <b>$3</b>
• AI Side Hustle Tracker $5 → <b>$2.5</b>

🔗 https://ghdejr.gumroad.com/

이 promo 메시지를 X/Threads/Bluesky/IG/카카오에 사장님이 1탭 공유하시면 매출 4-5채널 동시 푸시. 자동 schtask는 이미 trigger됨.
"""

# 영문 promo (Bluesky 등 글로벌 SNS 용)
en_msg = """🔥 24h FLASH SALE — 50% OFF on all 7 KunStudio digital products! Code: FLASH507 (limit 20 each)

✨ Korean Saju, Wisdom Planner, Notion 5-Pack, Productivity Planner, Wall Art, Tax Guide, AI Side Hustle Tracker

👉 https://ghdejr.gumroad.com/

#KoreanCulture #DigitalProduct #Notion #Saju #Productivity"""

# Telegram push
url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
data = urllib.parse.urlencode({
    "chat_id": TG_CHAT,
    "text": ko_msg,
    "parse_mode": "HTML",
    "disable_web_page_preview": "false",
}).encode("utf-8")
try:
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15) as r:
        body = json.loads(r.read().decode("utf-8"))
        print(f"[Telegram KO] message_id={body.get('result',{}).get('message_id')} ok={body.get('ok')}")
except Exception as e:
    print(f"[Telegram ERR] {e}")

# Bluesky push (kunstudio.bsky.social)
BSKY_HANDLE = env.get("BSKY_HANDLE", "")
BSKY_PASSWORD = env.get("BSKY_APP_PASSWORD") or env.get("BSKY_PASSWORD", "")
if BSKY_HANDLE and BSKY_PASSWORD:
    try:
        # 1) login
        auth_data = json.dumps({"identifier": BSKY_HANDLE, "password": BSKY_PASSWORD}).encode("utf-8")
        auth_req = urllib.request.Request(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            data=auth_data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(auth_req, timeout=15) as r:
            auth_body = json.loads(r.read().decode("utf-8"))
            jwt = auth_body.get("accessJwt")
            did = auth_body.get("did")
        # 2) post
        from datetime import datetime, timezone
        post_data = json.dumps({
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": en_msg,
                "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "langs": ["en"],
            }
        }).encode("utf-8")
        post_req = urllib.request.Request(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            data=post_data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {jwt}"},
        )
        with urllib.request.urlopen(post_req, timeout=15) as r:
            post_body = json.loads(r.read().decode("utf-8"))
            print(f"[Bluesky] uri={post_body.get('uri','')[:80]}")
    except Exception as e:
        print(f"[Bluesky ERR] {type(e).__name__}: {str(e)[:100]}")
else:
    print("[Bluesky] BSKY_HANDLE / BSKY_APP_PASSWORD missing — skipped")

print("Done.")
