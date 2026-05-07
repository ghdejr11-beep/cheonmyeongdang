"""인플루언서/B2B cold email 응답 모니터 (v2 — 응답 패턴 분류 강화).

매시간 schtask 가동 → outreach_log.json + b2b_sales/sent_log.json에서 보낸 메시지 list 추출 →
Gmail INBOX에서 해당 발신자로부터 신규 응답 검색 → 응답 발견 시 Telegram 알림.

v2 추가 (2026-05-07):
- 응답 텍스트를 4 패턴으로 자동 분류: interested / declined / partnership_ask / question
- 분류 결과를 Telegram 메시지에 표시 (어떤 답장 템플릿을 쓸지 한눈에 보임)
- reply_classifications.json 으로 통계 누적
- 자동 응답 템플릿은 auto_reply_templates_v2.md 참조 (수동 review 후 발송)

발송된 이메일:
- influencer_outreach/outreach_log.json (인플루언서 PR/Collab address)
- b2b_sales/sent_log.json (B2B 회사)
- secretary 직접 발송 메일 (KoDATA, KakaoPay 등)
"""
import os, sys, json, base64, re, urllib.request, urllib.parse, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
OUTREACH_LOG = CHEON / "departments" / "influencer_outreach" / "outreach_log.json"
B2B_LOG = CHEON / "departments" / "b2b_sales" / "sent_log.json"
SEEN_FILE = ROOT / "data" / "reply_monitor_seen.json"
CLASSIFY_FILE = ROOT / "data" / "reply_classifications.json"
LOG = ROOT / "logs" / f"reply_monitor_{datetime.date.today()}.log"
LOG.parent.mkdir(parents=True, exist_ok=True)
SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────
# v2: Reply pattern classifier
# ─────────────────────────────────────────────────────────
# Order matters: applied in this priority sequence.
# 1) declined  → never gets re-classified as interested
# 2) partnership_ask → paid/rate keywords beat generic positive
# 3) question  → only if has '?' or info-seeking phrase AND no commitment word
# 4) interested → fallback positive
# 5) unknown   → flag for human review

CLASSIFIER_PATTERNS = [
    (
        "declined",
        [
            r"\bnot a fit\b", r"\bnot the right fit\b", r"\bpass\b",
            r"\bdecline\b", r"\bnot interested\b", r"\bnot at this time\b",
            r"\bunfortunately\b", r"\bcurrently full\b", r"\bbooked\b",
            r"\bappreciate but\b", r"\bnot for me\b", r"\bunsubscribe\b",
            r"\bplease remove\b", r"\bremove me\b", r"\bopt out\b",
            r"\bno thank(?:s| you)\b", r"\bno thanks\b",
        ],
    ),
    (
        "partnership_ask",
        [
            r"\brate card\b", r"\bmedia kit\b", r"\brates?\b", r"\bpricing\b",
            r"\bbudget\b", r"\bpaid partnership\b", r"\bflat fee\b",
            r"\busage rights\b", r"\bwhitelisting\b", r"\bexclusive\b",
            r"\bmonthly retainer\b", r"\blong[- ]term\b", r"\bnegotiate\b",
            r"\bagency\b", r"\bmanager\b", r"\brepresentation\b",
            r"\$\s?\d{2,}", r"\bquote\b", r"\binvoice\b", r"\bcompensation\b",
        ],
    ),
    (
        "interested",
        [
            r"\binterested\b", r"\bi'?d love to\b", r"\blet'?s do it\b",
            r"\bsounds great\b", r"\bcount me in\b", r"\bhappy to (?:collaborate|partner|work)\b",
            r"\blet'?s chat\b", r"\bdm me\b", r"\bsend me details\b",
            r"\bexcited\b", r"\blooks fun\b", r"\bi'?m in\b", r"\blove this\b",
            r"\bhappy to\b", r"\bsign me up\b", r"\bgame\b",
        ],
    ),
    (
        "question",
        [
            r"\bquestion\b", r"\bclarify\b", r"\bmore info\b", r"\btell me more\b",
            r"\bhow does it work\b", r"\bwhat is\b", r"\bexplain\b",
            r"\bdetails\b", r"\bwho are you\b", r"\bwhat'?s the catch\b",
            r"\bis this real\b", r"\blegit\b", r"\bcan you\b", r"\bcould you\b",
        ],
    ),
]


def classify_reply(text: str) -> str:
    """Classify a reply snippet/body into one of:
    declined | partnership_ask | interested | question | unknown.
    """
    if not text:
        return "unknown"
    t = text.lower()

    matched = []
    for label, patterns in CLASSIFIER_PATTERNS:
        for pat in patterns:
            if re.search(pat, t, flags=re.IGNORECASE):
                matched.append(label)
                break

    if not matched:
        # Question fallback: only a '?' but no other signal → still question
        if "?" in t:
            return "question"
        return "unknown"

    # Priority order from CLASSIFIER_PATTERNS list (declined > partnership_ask > interested > question)
    for label, _ in CLASSIFIER_PATTERNS:
        if label in matched:
            return label
    return "unknown"


CLASSIFY_EMOJI = {
    "interested": "🟢",
    "partnership_ask": "💰",
    "question": "❓",
    "declined": "🚫",
    "unknown": "⚪",
}

CLASSIFY_HINT = {
    "interested": "→ template #1 (next steps + affiliate link)",
    "partnership_ask": "→ template #3 (rate options A/B + ask media kit)",
    "question": "→ template #4 (5 FAQ answered)",
    "declined": "→ template #2 (graceful close + add to do_not_contact)",
    "unknown": "→ HUMAN REVIEW (no template auto-match)",
}


def load_classifications():
    if CLASSIFY_FILE.exists():
        try:
            return json.loads(CLASSIFY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"counts": {}, "history": []}
    return {"counts": {}, "history": []}


def save_classifications(data):
    CLASSIFY_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


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
                snippet = full.get("snippet", "")[:400]
                # v2: classify reply pattern from snippet + subject
                classify_text = f"{h.get('Subject', '')} {snippet}"
                pattern = classify_reply(classify_text)
                new_replies.append({
                    "msg_id": mid,
                    "from": h.get("From", ""),
                    "subject": h.get("Subject", ""),
                    "date": h.get("Date", ""),
                    "snippet": snippet,
                    "matched_recipient": rcpt,
                    "pattern": pattern,
                })
                seen.add(mid)
        except Exception as e:
            log(f"  search fail for {rcpt}: {e}")

    if new_replies:
        log(f"NEW REPLIES: {len(new_replies)}")
        # v2: aggregate by pattern
        by_pattern = {}
        for r in new_replies:
            p = r.get("pattern", "unknown")
            by_pattern.setdefault(p, []).append(r)
            log(f"  [{CLASSIFY_EMOJI.get(p,'?')} {p}] from={r['from'][:50]} subj={r['subject'][:50]}")

        # Persist classification stats
        cl = load_classifications()
        for p, items in by_pattern.items():
            cl["counts"][p] = cl["counts"].get(p, 0) + len(items)
            for r in items:
                cl["history"].append({
                    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                    "from": r["from"][:80],
                    "subject": r["subject"][:120],
                    "pattern": p,
                    "msg_id": r["msg_id"],
                })
        # Cap history at last 500 entries to avoid runaway file growth
        cl["history"] = cl["history"][-500:]
        save_classifications(cl)

        # Telegram alert with pattern grouping
        summary_bits = [f"{CLASSIFY_EMOJI[p]} {p}: {len(items)}" for p, items in by_pattern.items()]
        msg_lines = [
            f"📬 새 응답 {len(new_replies)}건 (인플라/B2B)",
            "  " + "  ·  ".join(summary_bits),
            "",
        ]
        # Show in priority order: partnership_ask → interested → question → declined → unknown
        priority = ["partnership_ask", "interested", "question", "declined", "unknown"]
        shown = 0
        for p in priority:
            for r in by_pattern.get(p, []):
                if shown >= 10:
                    break
                msg_lines.append(f"{CLASSIFY_EMOJI[p]} <b>[{p}]</b>")
                msg_lines.append(f"  From: {r['from'][:60]}")
                msg_lines.append(f"  Subj: {r['subject'][:60]}")
                msg_lines.append(f"  ↳ {r['snippet'][:140]}")
                msg_lines.append(f"  📝 {CLASSIFY_HINT[p]}")
                msg_lines.append("")
                shown += 1
        if len(new_replies) > 10:
            msg_lines.append(f"...외 {len(new_replies)-10}건 (logs/reply_monitor 참조)")
        telegram_alert("\n".join(msg_lines), env)
    else:
        log("no new replies")

    save_seen(seen)


if __name__ == "__main__":
    main()
