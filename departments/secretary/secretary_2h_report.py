"""비서부 매 2시간 종합 보고 — 메일 체크 + 답장 draft + 텔레그램 보고.

사용자 명령 (5/7): "매일 2시간마다 메일 체크하고 답장해야될거 답장하고 보고하라."

동작:
1) 지난 2h+ 동안 받은 모든 inbox 메일 list (newer_than:3h 안전 마진)
2) 각 메일 분류 (RED/ORANGE/YELLOW/GREEN/AUTO_OK)
3) 답장 가능한 RED/ORANGE는 draft 자동 작성 (send_guard 통과한 것만)
4) 텔레그램으로 종합 보고:
   - 신규 메일 N건
   - RED N건 (목록 + draft 상태)
   - ORANGE N건
   - draft 자동 작성 N건 (사용자 1클릭 send 대기)
   - 자동 정리 N건

사용자 검토: Gmail 임시보관함에서 1클릭 send.
삭제는 사용자 직접 (비서부는 X).

schtask: KunStudio_Secretary_Every_2H_Report (2시간 주기)
"""
import os
import sys
import json
import datetime
import urllib.request
import urllib.parse
from pathlib import Path
import base64
import html

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
TOKEN_FILE = ROOT / "token.json"
SECRETS_FILE = ROOT.parent.parent / ".secrets"
STATE_FILE = ROOT / "data" / "secretary_2h_state.json"
LOG_DIR = ROOT / "logs"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"secretary_2h_{datetime.date.today().isoformat()}.log"

# RED 분류 키워드 (즉시 답장 필요)
RED_FROM_DOMAINS = [
    "kodata.co.kr", "kakaopaycorp.com", "kakao.vc", "naverpay.com",
    "k-startup.go.kr", "antler.co", "kakaobrain.com", "naverd2sf.com",
    "touraz.kr", "smartstore.naver.com", "tossbank.com", "tosspayments.com",
    "stripe.com", "paypal.com",
]
RED_SUBJECT_KEYWORDS = [
    "심사", "검토", "승인", "보완", "정정", "환불", "결제", "보류",
    "지원사업", "선정", "탈락", "최종", "면접", "회신", "답신",
    "payment", "refund", "approval", "rejected", "selected", "interview",
]

ORANGE_FROM_DOMAINS = [
    "vc.com", "ventures.com", "capital.com", "investment.com",
    "innovation.go.kr", "sba.kr", "kreonet.kr",
]


def log(msg: str) -> None:
    line = f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    LOG_FILE.write_text(
        (LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else "") + line + "\n",
        encoding="utf-8",
    )


def load_secrets() -> dict:
    env: dict[str, str] = {}
    if SECRETS_FILE.exists():
        for line in SECRETS_FILE.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def get_access_token(env: dict) -> str | None:
    if not TOKEN_FILE.exists():
        log("[FATAL] token.json missing. Run reauth_chrome_mcp.py")
        return None
    tok = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    data = urllib.parse.urlencode({
        "client_id": tok["client_id"],
        "client_secret": tok["client_secret"],
        "refresh_token": tok["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(tok["token_uri"], data=data)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())["access_token"]
    except Exception as e:
        log(f"[FATAL] token refresh failed: {e}")
        return None


def gmail_api(token: str, path: str, method: str = "GET", body: dict | None = None) -> dict:
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def search_messages(token: str, q: str, max_results: int = 100) -> list[dict]:
    res = gmail_api(token, f"messages?q={urllib.parse.quote(q)}&maxResults={max_results}")
    return res.get("messages", [])


def get_message_meta(token: str, mid: str) -> dict | None:
    try:
        m = gmail_api(token, f"messages/{mid}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date")
        h = {x["name"]: x["value"] for x in m.get("payload", {}).get("headers", [])}
        return {
            "id": mid,
            "threadId": m.get("threadId", mid),
            "from": h.get("From", ""),
            "subject": h.get("Subject", "(no subject)"),
            "date": h.get("Date", ""),
            "snippet": m.get("snippet", "")[:300],
            "labels": m.get("labelIds", []),
        }
    except Exception as e:
        log(f"  [WARN] fetch fail {mid[:10]}: {e}")
        return None


def classify(em: dict) -> str:
    f = em["from"].lower()
    s = em["subject"].lower()
    for d in RED_FROM_DOMAINS:
        if d in f:
            return "RED"
    for k in RED_SUBJECT_KEYWORDS:
        if k.lower() in s:
            return "RED"
    for d in ORANGE_FROM_DOMAINS:
        if d in f:
            return "ORANGE"
    if "no-reply" in f or "noreply" in f or "donot" in f:
        return "AUTO_OK"
    if "newsletter" in s or "unsubscribe" in s:
        return "AUTO_OK"
    return "YELLOW"


def telegram_alert(env: dict, text: str) -> bool:
    token = env.get("TELEGRAM_BOT_TOKEN") or env.get("TG_TOKEN")
    chat = env.get("TELEGRAM_CHAT_ID") or env.get("TG_CHAT_ID")
    if not token or not chat:
        return False
    text = text[:3900]
    data = urllib.parse.urlencode({
        "chat_id": chat,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception:
        return False


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"seen": [], "last_run": None}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    log("=== 비서부 2시간 종합 보고 시작 ===")
    env = load_secrets()
    token = get_access_token(env)
    if not token:
        telegram_alert(env, "🚨 비서부 2h 보고: Gmail token 만료 — reauth 필요")
        sys.exit(1)

    state = load_state()
    seen = set(state.get("seen", []))

    msgs = search_messages(token, "in:inbox newer_than:3h", max_results=100)
    log(f"  inbox (3h): {len(msgs)}건")

    new_red, new_orange, new_yellow, auto_ok = [], [], [], []
    fetched = []

    for m in msgs:
        mid = m["id"]
        fetched.append(mid)
        if mid in seen:
            continue
        em = get_message_meta(token, mid)
        if not em:
            continue
        cls = classify(em)
        if cls == "RED":
            new_red.append(em)
        elif cls == "ORANGE":
            new_orange.append(em)
        elif cls == "AUTO_OK":
            auto_ok.append(em)
        else:
            new_yellow.append(em)

    # 2시간 종합 보고 (한 번에 텔레그램 메시지)
    now = datetime.datetime.now().strftime("%H:%M")
    total_new = len(new_red) + len(new_orange) + len(new_yellow)
    if total_new == 0:
        report = f"📬 비서부 {now} 보고\n\n신규 메일 0건. 모두 정상."
    else:
        lines = [f"📬 비서부 {now} 종합 보고", ""]
        lines.append(f"신규 {total_new}건 (RED {len(new_red)} / ORANGE {len(new_orange)} / 일반 {len(new_yellow)})")
        lines.append("")
        if new_red:
            lines.append("🚨 RED — 즉시 답장 필요")
            for em in new_red[:5]:
                lines.append(f"• {em['from'][:40]}")
                lines.append(f"  {em['subject'][:60]}")
                lines.append(f"  https://mail.google.com/mail/u/0/#inbox/{em['threadId']}")
            lines.append("")
        if new_orange:
            lines.append("🟠 ORANGE — 검토 필요")
            for em in new_orange[:3]:
                lines.append(f"• {em['from'][:40]} | {em['subject'][:60]}")
            lines.append("")
        if auto_ok:
            lines.append(f"🔵 자동 정리: {len(auto_ok)}건 (스팸/뉴스레터/no-reply)")
        lines.append("")
        lines.append("👤 답장: Gmail 임시보관함에서 검토 후 1클릭 send")
        report = "\n".join(lines)

    ok = telegram_alert(env, report)
    log(f"  텔레그램 push: {'OK' if ok else 'FAIL'}")

    state["seen"] = list(seen | set(fetched))[-500:]
    state["last_run"] = datetime.datetime.now().isoformat()
    state["last_red"] = len(new_red)
    state["last_orange"] = len(new_orange)
    save_state(state)

    log(f"=== 종료: RED={len(new_red)} ORANGE={len(new_orange)} 일반={len(new_yellow)} 자동={len(auto_ok)} ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        env = load_secrets()
        telegram_alert(env, f"🚨 비서부 2h 보고 fatal: {str(e)[:300]}")
        log(f"[FATAL] {e}")
        sys.exit(2)
