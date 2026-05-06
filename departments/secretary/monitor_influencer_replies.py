"""인플루언서/B2B cold email 응답 모니터.

매시간 schtask 가동 → outreach_log.json + b2b_sales/sent_log.json에서 보낸 메시지 list 추출 →
Gmail INBOX에서 해당 발신자로부터 신규 응답 검색 → 응답 발견 시 Telegram 알림.

발송된 이메일:
- influencer_outreach/outreach_log.json (인플루언서 PR/Collab address)
- b2b_sales/sent_log.json (B2B 회사)
- secretary 직접 발송 메일 (KoDATA, KakaoPay 등)
"""
import os, sys, json, base64, urllib.request, urllib.parse, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
OUTREACH_LOG = CHEON / "departments" / "influencer_outreach" / "outreach_log.json"
B2B_LOG = CHEON / "departments" / "b2b_sales" / "sent_log.json"
SEEN_FILE = ROOT / "data" / "reply_monitor_seen.json"
LOG = ROOT / "logs" / f"reply_monitor_{datetime.date.today()}.log"
LOG.parent.mkdir(parents=True, exist_ok=True)
SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)


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
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_recipients():
    """Collect every recipient address we have outreach to."""
    recipients = set()
    if OUTREACH_LOG.exists():
        try:
            data = json.loads(OUTREACH_LOG.read_text(encoding="utf-8"))
            for s in data.get("sent", []):
                if s.get("recipient"):
                    recipients.add(s["recipient"].lower())
        except Exception as e:
            log(f"  outreach_log parse error: {e}")
    if B2B_LOG.exists():
        try:
            data = json.loads(B2B_LOG.read_text(encoding="utf-8"))
            entries = data if isinstance(data, list) else data.get("sent", [])
            for s in entries:
                if s.get("recipient"):
                    recipients.add(s["recipient"].lower())
        except Exception as e:
            log(f"  b2b_log parse error: {e}")
    return recipients


def load_seen():
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")).get("seen", []))
        except Exception:
            return set()
    return set()


def save_seen(seen):
    SEEN_FILE.write_text(
        json.dumps({"seen": sorted(seen), "updated": datetime.datetime.now().isoformat()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def telegram_alert(text, env):
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat = env.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        log("  no telegram creds, skipping alert")
        return False
    body = urllib.parse.urlencode({"chat_id": chat, "text": text[:4000]}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body,
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15).read()
        return True
    except Exception as e:
        log(f"  telegram fail: {e}")
        return False


def main():
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        log("[ABORT] google-api-python-client not installed")
        return

    creds = Credentials.from_authorized_user_file(str(ROOT / "token.json"))
    service = build("gmail", "v1", credentials=creds)

    recipients = load_recipients()
    if not recipients:
        log("no recipients to monitor")
        return
    log(f"monitoring {len(recipients)} recipients")

    seen = load_seen()
    env = load_secrets()
    new_replies = []

    # Search Gmail for messages from any tracked recipient (last 7 days, INBOX only)
    for rcpt in list(recipients)[:50]:  # cap for safety
        q = f"from:{rcpt} newer_than:7d"
        try:
            res = service.users().messages().list(userId="me", q=q, maxResults=10).execute()
            for m in res.get("messages", []):
                mid = m["id"]
                if mid in seen:
                    continue
                full = service.users().messages().get(
                    userId="me", id=mid, format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                ).execute()
                h = {x["name"]: x["value"] for x in full["payload"]["headers"]}
                snippet = full.get("snippet", "")[:200]
                new_replies.append({
                    "msg_id": mid,
                    "from": h.get("From", ""),
                    "subject": h.get("Subject", ""),
                    "date": h.get("Date", ""),
                    "snippet": snippet,
                    "matched_recipient": rcpt,
                })
                seen.add(mid)
        except Exception as e:
            log(f"  search fail for {rcpt}: {e}")

    if new_replies:
        log(f"NEW REPLIES: {len(new_replies)}")
        for r in new_replies:
            log(f"  from={r['from'][:60]} subj={r['subject'][:60]}")
        # Telegram alert
        msg_lines = [f"📬 새 응답 {len(new_replies)}건 (인플루언서/B2B outreach)"]
        for r in new_replies[:10]:
            msg_lines.append(f"")
            msg_lines.append(f"From: {r['from']}")
            msg_lines.append(f"Subject: {r['subject']}")
            msg_lines.append(f"  → {r['snippet'][:120]}")
        telegram_alert("\n".join(msg_lines), env)
    else:
        log("no new replies")

    save_seen(seen)


if __name__ == "__main__":
    main()
