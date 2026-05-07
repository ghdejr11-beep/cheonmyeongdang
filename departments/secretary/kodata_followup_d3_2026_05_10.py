"""KoDATA D+3 follow-up (5/10 09:00) — 처리 진행 상태 문의 알림."""
import os, sys, json, urllib.request, urllib.parse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent
CHEON = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
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
    body = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=body, method="POST")
    try:
        urllib.request.urlopen(req, timeout=15).read()
        return True
    except Exception:
        return False


def main():
    env = load_secrets()
    tok = get_token()
    if not tok:
        return
    q = '(from:kodata.co.kr OR from:85343@ OR from:xn--2n1bp39a0wfq1b) newer_than:5d'
    msgs = search_messages(tok, q)
    print(f'[D+3] KoDATA 수신: {len(msgs)}건')
    if msgs:
        # 처리 완료 메일이 있다면 inbox_monitor가 이미 push
        # 단순 접수 확인이라면 D+7까지 결과 대기
        text = """📊 KoDATA D+3 (5/10) — 진행 상태 점검

5/7 정정 메일 발송 후 3일 경과. KoDATA에서 회신 ({n}건) 확인됨.

✅ 액션:
1) 회신 내용 확인 (Gmail KoDATA 검색)
2) 추가 보완 필요시 즉시 답신
3) 접수 완료 상태면 D+7 결과 대기""".format(n=len(msgs))
    else:
        text = """⏰ KoDATA D+3 (5/10) — 회신 없음 (3일째)

처리 기간 1주일 중 절반 경과, 회신 없음.

✅ 즉시 액션:
1) 02-3279-6500 통화 → 진행 상태 문의
2) "5/7 16:34 정정 발송 (85343@xn--2n1bp39a0wfq1b.co.kr) 접수됐는지" 확인
3) 추가 누락 요구사항 있는지 확인

📅 D-10 (5/20): 관광 AI(KORLENS) 신청 마감
"""
    telegram(env, text)


if __name__ == '__main__':
    main()
