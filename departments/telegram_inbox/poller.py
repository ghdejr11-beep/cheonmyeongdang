"""Telegram inbox poller — 사용자 텔레그램 답변을 읽어 inbox.jsonl에 누적.

Telegram Bot API의 getUpdates를 사용 (long-polling 아님, short polling).
schtask로 5분마다 실행 → 사용자가 폰에서 보낸 메시지를 저장 → 다음 Claude
세션 시작 시 제가 inbox.jsonl을 읽고 명령처럼 처리.

용도:
- 폰에서 "PostEverywhere MCP 설치해" 보내면 → inbox에 저장 → 다음 세션 자동 처리
- 폰에서 "오늘 매출 알려줘" 보내면 → inbox 처리 + 자동 답변

Run: python departments/telegram_inbox/poller.py
schtask: KunStudio_Telegram_Poll_5min (매 5분)
"""
import os, sys, json, urllib.request, urllib.parse, urllib.error, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG = LOG_DIR / f"poll_{datetime.date.today()}.log"

INBOX = DATA / "telegram_inbox.jsonl"
STATE = DATA / "poll_state.json"  # last_update_id


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_secrets():
    env = {}
    p = CHEON / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"last_update_id": 0}


def save_state(s):
    STATE.write_text(json.dumps(s, indent=2), encoding="utf-8")


def telegram_get_updates(token, offset=0, timeout=2):
    """Short polling — short timeout to avoid 409 conflicts with parallel calls."""
    url = f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout={timeout}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout + 3) as r:
        return json.loads(r.read())


def telegram_send(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def main():
    secrets = load_secrets()
    token = secrets.get("TELEGRAM_BOT_TOKEN")
    chat_id = secrets.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log("[ERR] TELEGRAM_BOT_TOKEN/CHAT_ID missing")
        return

    state = load_state()
    last = state["last_update_id"]
    try:
        resp = telegram_get_updates(token, offset=last + 1 if last else 0)
    except Exception as e:
        log(f"[ERR] getUpdates: {e}")
        return

    if not resp.get("ok"):
        log(f"[ERR] {resp}")
        return

    updates = resp.get("result", [])
    if not updates:
        log("[ok] no new messages")
        return

    saved = 0
    for u in updates:
        uid = u.get("update_id", 0)
        if uid <= last:
            continue
        msg = u.get("message") or u.get("edited_message")
        if not msg:
            continue
        text = msg.get("text", "")
        chat = msg.get("chat", {})
        from_ = msg.get("from", {})
        ts = msg.get("date", 0)

        # Filter: only authorized chat_id (security)
        if str(chat.get("id")) != str(chat_id):
            log(f"[skip] unauthorized chat_id: {chat.get('id')}")
            last = uid
            continue

        record = {
            "update_id": uid,
            "text": text,
            "from_username": from_.get("username") or from_.get("first_name", "user"),
            "datetime": datetime.datetime.fromtimestamp(ts).isoformat(),
            "processed": False,
        }
        with INBOX.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        saved += 1
        last = uid
        log(f"[saved] {text[:80]}")

        # Auto-acknowledge so user knows Claude received it
        try:
            telegram_send(token, chat_id, f"✅ 받았어요: \"{text[:60]}{'...' if len(text)>60 else ''}\"\n다음 Claude 세션에서 처리할게요.")
        except Exception as e:
            log(f"[ack-fail] {e}")

    state["last_update_id"] = last
    save_state(state)
    log(f"[done] +{saved} new messages → {INBOX}")


if __name__ == "__main__":
    main()
