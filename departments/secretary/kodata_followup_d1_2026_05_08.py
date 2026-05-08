"""KoDATA D+1 follow-up (5/8 09:00) — 접수 확인 안 왔으면 02-3279-6500 통화 알림.

체크 로직:
1) Gmail 받은편지함에서 from:kodata.co.kr OR from:85343@ 5/7 이후 수신 검색
2) 접수 확인 메일 없으면 → Telegram alert: "전화 02-3279-6500 통화 필요"
3) 접수 확인 메일 있으면 → log only
"""
import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent
CHEON = Path(r"D:\cheonmyeongdang")
TOKEN = ROOT / "token.json"


def load_secrets():
    env = {}
    p = CHEON / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def get_token():
    with TOKEN.open('r', encoding='utf-8') as f:
        tok = json.load(f)
    body = urllib.parse.urlencode({
        "client_id": tok["client_id"], "client_secret": tok["client_secret"],
        "refresh_token": tok["refresh_token"], "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=body, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read()).get("access_token")


def search_messages(token, q):
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?{urllib.parse.urlencode({'q': q, 'maxResults': 20})}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read()).get("messages", [])


def telegram(env, text):
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat = env.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        return False
    body = urllib.parse.urlencode({"chat_id": chat, "text": text, "disable_web_page_preview": "true"}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=body, method="POST")
    try:
        urllib.request.urlopen(req, timeout=15).read()
        return True
    except Exception as e:
        print(f"[telegram fail] {e}")
        return False


def main():
    env = load_secrets()
    tok = get_token()
    if not tok:
        print('[ABORT] no Gmail token')
        return

    # KoDATA에서 5/7 이후 수신 메일
    q = '(from:kodata.co.kr OR from:85343@ OR from:xn--2n1bp39a0wfq1b) newer_than:2d'
    msgs = search_messages(tok, q)
    print(f'[D+1] KoDATA 수신: {len(msgs)}건')

    if msgs:
        print('  → 접수 확인 또는 보완 요청 메일 있음, 통화 불필요')
        # inbox_monitor_unified에서 이미 RED push 했으므로 추가 알림 X
        return

    # 회신 없음 → 통화 알림
    text = """⏰ KoDATA D+1 (5/8 09:00) — 회신 없음

5/7 16:34 정정 메일 발송 후 24시간 경과, 아직 회신 없음.

✅ 즉시 액션:
1) 02-3279-6500 통화 (KoDATA 담당 직통)
2) "쿤스튜디오 5/7 16:34 정정 메일 (3 첨부) 접수 확인" 문의
3) 처리 진행상태 + 추가 보완 필요 여부 확인

📋 참고:
- 5/5 1차 발송: find@kodata.co.kr (첨부 부족)
- 5/7 16:34 발송: 85343@codate.co.kr (도메인 오타 — 반송)
- 5/7 (재발송 draft): 85343@xn--2n1bp39a0wfq1b.co.kr (정정)
"""
    ok = telegram(env, text)
    print(f'[ALERT] telegram={ok}')


if __name__ == '__main__':
    main()
