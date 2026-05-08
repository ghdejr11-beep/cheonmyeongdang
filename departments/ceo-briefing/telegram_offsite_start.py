"""사장님 외출 시작 시 텔레그램 push (자동 작업 시작 알림)."""
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

msg = """🌙 <b>사장님 외출 — 자동 작업 시작</b>

도착하실 때까지 다음 자동 처리합니다:

<b>1. KDP cover PDF→PNG 변환</b> (50개)
└ Vela 업로드용 이미지 미리 준비

<b>2. Pinterest FLASH507 promo 핀 12개 생성</b>
└ 4lang × 3핀 자동 발행

<b>3. Etsy CSV 이미지 컬럼 재매핑</b>
└ Vela 업로드 시 즉시 활성화 가능

<b>4. AppSumo 제출 준비</b>
└ 5/6 audit (25분→20분 단축) 사전 자동 처리

<b>5. Gumroad / PayPal 매출 모니터</b>
└ 신규 거래 발생 시 즉시 텔레그램 push
└ FLASH507 14:0 시 매출 발생 가능

<b>완료/실패 시 자동 보고</b> 보내드릴게요. 안전히 다녀오세요 🚗
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
