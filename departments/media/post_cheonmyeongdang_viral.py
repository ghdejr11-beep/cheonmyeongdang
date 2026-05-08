#!/usr/bin/env python3
"""천명당 viral promo — 6 schtasks (06/09/12/15/18/21) 호출.

기존 스크립트가 누락되어 6개 schtask가 매일 6번 result=2로 실패 중이었다.
이 스크립트는 Telegram 1채널만 사용하여 시간대별로 다른 카피를 회전 발송.
"""
import os
import sys
import io
import json
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

if not TG_TOKEN or not TG_CHAT:
    print("[SKIP] TELEGRAM creds missing in env or .secrets")
    sys.exit(0)

LANDING = "https://cheonmyeongdang.com"

VARIANTS = [
    "🌅 <b>오늘의 운세, 1초만에</b>\n생년월일·태어난 시간만 입력 → AI 사주 풀이.\n무료 체험 → " + LANDING,
    "🍀 <b>이번 주 행운의 색·숫자·방향</b>\n천명당 AI 사주가 매일 자동으로 알려줍니다.\n구독 → " + LANDING,
    "🔮 <b>월별 운세 PDF 30p 무료</b>\n매월 1일 메일 자동 발송 (한/영/일/중).\n받기 → " + LANDING,
    "💌 <b>매직링크 1클릭 로그인</b>\n비번 없이 시작 — 글로벌 결제 PayPal 라이브.\n시작 → " + LANDING,
    "📊 <b>커리어·재물·연애 차트 4종</b>\n시각화 카드 자동 생성, SNS 공유 OK.\n체험 → " + LANDING,
    "🌙 <b>밤 9시 — 내일의 한 줄</b>\n천명당 AI Q&A 챗으로 5초 안에 답.\n바로 → " + LANDING,
]

hour = datetime.now().hour
idx = ([0, 1, 2, 3, 4, 5][hour // 4]) % len(VARIANTS) if hour < 24 else 0
text = VARIANTS[idx]

url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
data = urllib.parse.urlencode({
    "chat_id": TG_CHAT,
    "text": text,
    "parse_mode": "HTML",
    "disable_web_page_preview": "false",
}).encode("utf-8")

try:
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15) as r:
        body = json.loads(r.read().decode("utf-8"))
        ok = body.get("ok", False)
        print(f"[{'OK' if ok else 'FAIL'}] viral idx={idx} hour={hour} message_id={body.get('result',{}).get('message_id')}")
        sys.exit(0 if ok else 1)
except Exception as e:
    print(f"[ERR] {type(e).__name__}: {e}")
    sys.exit(1)
