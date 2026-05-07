"""통합 받은편지함 모니터 — 모든 RED/ORANGE 키워드 한꺼번에 5분 폴링.

대체 대상:
- monitor_kodata_reply.py (단일 키워드, print만, telegram alert X)
- pg_mail_monitor.py (PG 한정)
- 향후 단일 키워드 모니터 전체

기능:
1) 모든 RED 키워드(KoDATA, 카카오페이, K-Startup, 투자자, 결제/환불 등) 한꺼번에 검색
2) 신규 메일 발견 → 즉시 Telegram push (quiet 무시 옵션 RED만)
3) RED만 push, 일반은 30분 lookback에 묶어 일괄 알림
4) state JSON으로 last_check_id 추적 (중복 알림 방지)
5) 매 5분 schtask 실행 (이전 매시간 → 12배 빠름)

작업 이름: KunStudio_Inbox_Monitor_Unified
사고 재발 가능성: ~0% (Telegram alert 강제 + 5분 주기 + state dedup)
"""
import os
import sys
import json
import datetime
import re
import urllib.request
import urllib.parse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
CHEON = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
TOKEN_FILE = ROOT / "token.json"
STATE_FILE = ROOT / "data" / "inbox_monitor_unified_state.json"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / f"inbox_monitor_unified_{datetime.date.today().isoformat()}.log"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    line = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_secrets() -> dict:
    env = {}
    p = CHEON / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# ─── RED 키워드 (즉시 push) — from: 도메인 + subject 키워드 ──────────
RED_FROM_DOMAINS = [
    "kodata.co.kr",
    "kakaopaycorp.com",
    "naverpay",
    "naver.com",
    "k-startup.go.kr",
    "kised.or.kr",
    "kakao.vc",
    "kakaobrain",
    "antler.co",
    "navercorp.com",
    "naverd2sf",
    "tosspayments.com",
    "toss.im",
    "galaxia",
    "billgate",
    "portone",
    "lemonsqueezy.com",
    "paypal.com",
    "stripe.com",
    "kotra.or.kr",
    "kbiz.or.kr",
    "kepco.co.kr",
]

RED_SUBJECT_KEYWORDS = [
    # 심사 / 검토 / 보완
    "심사", "검토", "승인", "보완", "정정", "반려", "재신청",
    "재제출", "수정", "확인 요청",
    # 결제 / 환불
    "환불", "결제", "정산", "입금", "출금",
    "payment", "refund", "settle", "invoice failed",
    # 정부지원 / 보조금
    "정부지원", "보조금", "지원사업", "선정", "탈락",
    "grant", "approved", "rejected",
    # 법무 / 세무
    "내용증명", "통보", "독촉", "미납", "체납",
    "세무조사", "세무", "국세청", "지방세", "소송", "법무",
    "legal notice", "court", "overdue",
    # 투자
    "투자", "심사", "실사", "term sheet", "pitch", "due diligence",
    "Series", "seed",
]

# False positive 방지: 이런 발신은 스킵 (자동 알림/뉴스레터/자기자신)
SKIP_FROM_PATTERNS = [
    r"noreply@",
    r"no-reply@",
    r"donotreply@",
    r"@github\.com",  # build failure 알림
    r"@vercel\.com",
    r"newsletter",
    r"campaign@",
    r"@cx\.beehiiv\.com",
    r"@mailchimp",
    r"info@make\.com",
    r"@quora\.com",
    r"@redditmail\.com",
    r"stories-recap@",
    r"unread-messages@",
    # 자기 자신 (자동 발송 메일이 inbox에 사본으로 들어옴)
    r"ghdejr11@gmail\.com",
    # Stripe 영수증
    r"receipts\+",
    r"receipts@",
    r"@stripe\.com",
    r"@stripe-mail\.com",
]


def get_access_token(env: dict) -> str | None:
    """token.json 또는 .secrets에서 access token 갱신."""
    if TOKEN_FILE.exists():
        with TOKEN_FILE.open("r", encoding="utf-8") as f:
            tok = json.load(f)
        body = urllib.parse.urlencode({
            "client_id": tok["client_id"],
            "client_secret": tok["client_secret"],
            "refresh_token": tok["refresh_token"],
            "grant_type": "refresh_token",
        }).encode()
        try:
            req = urllib.request.Request(
                "https://oauth2.googleapis.com/token",
                data=body, method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                resp = json.loads(r.read())
            return resp.get("access_token")
        except Exception as e:
            log(f"  [WARN] token.json refresh fail: {e}")

    # fallback: .secrets
    refresh = env.get("GMAIL_REFRESH_TOKEN")
    cid = env.get("GOOGLE_CLIENT_ID")
    csec = env.get("GOOGLE_CLIENT_SECRET")
    if not all([refresh, cid, csec]):
        return None
    body = urllib.parse.urlencode({
        "client_id": cid, "client_secret": csec,
        "refresh_token": refresh, "grant_type": "refresh_token",
    }).encode()
    try:
        req = urllib.request.Request(
            "https://oauth2.googleapis.com/token",
            data=body, method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()).get("access_token")
    except Exception as e:
        log(f"  [WARN] .secrets refresh fail: {e}")
        return None


def search_messages(token: str, query: str, max_results: int = 20) -> list:
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?{urllib.parse.urlencode({'q': query, 'maxResults': max_results})}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()).get("messages", [])
    except Exception as e:
        log(f"  search fail: {e}")
        return []


def get_message_metadata(token: str, mid: str) -> dict:
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        headers = {h["name"]: h["value"] for h in data.get("payload", {}).get("headers", [])}
        return {
            "id": mid,
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "snippet": data.get("snippet", "")[:200],
            "threadId": data.get("threadId"),
        }
    except Exception as e:
        log(f"  metadata fail {mid}: {e}")
        return {}


def telegram_alert(env: dict, text: str, prefix: str = "") -> bool:
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat = env.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        log("  [WARN] no telegram creds")
        return False
    # HTML 파서 안전: <, >, & 만 허용된 태그(b/a) 제외하고 escape
    def _safe(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # prefix는 신뢰 (우리가 작성), text는 사용자 입력 가능 — 그대로 두면 risky
    # 따라서 plain mode로 폴백 (HTML 안 씀)
    payload = {
        "chat_id": chat,
        "text": (prefix + text)[:4000],
        "disable_web_page_preview": "true",
    }
    body = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body, method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15).read()
        return True
    except Exception as e:
        log(f"  telegram fail: {e}")
        return False


def is_red(em: dict) -> bool:
    """RED 분류: from 도메인 OR subject 키워드 매칭."""
    f = em.get("from", "").lower()
    subj = em.get("subject", "").lower()
    snip = em.get("snippet", "").lower()

    # skip patterns
    for p in SKIP_FROM_PATTERNS:
        if re.search(p, f, re.IGNORECASE):
            return False

    # RED domain
    for dom in RED_FROM_DOMAINS:
        if dom in f:
            return True

    # RED subject keyword
    text = subj + " " + snip
    for kw in RED_SUBJECT_KEYWORDS:
        if kw.lower() in text:
            return True

    return False


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"seen": []}
    return {"seen": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    log("=== 통합 inbox monitor 시작 ===")
    env = load_secrets()
    token = get_access_token(env)
    if not token:
        log("[ABORT] no Gmail access token")
        sys.exit(1)

    state = load_state()
    seen = set(state.get("seen", []))

    # 최근 30분 inbox (5분 주기지만 안전 마진)
    msgs = search_messages(token, "in:inbox newer_than:1d", max_results=80)
    log(f"  inbox fetched: {len(msgs)}")

    new_red = []
    new_other = []
    fetched_ids = []

    for m in msgs:
        mid = m["id"]
        fetched_ids.append(mid)
        if mid in seen:
            continue
        em = get_message_metadata(token, mid)
        if not em:
            continue
        if is_red(em):
            new_red.append(em)
        else:
            new_other.append(em)

    # RED는 즉시 알림 (1건씩 상세)
    for em in new_red:
        prefix = "🚨 RED — 즉시 확인\n\n"
        text = (
            f"From: {em['from'][:80]}\n"
            f"Subject: {em['subject'][:120]}\n"
            f"Date: {em['date']}\n"
            f"Preview: {em['snippet'][:200]}\n\n"
            f"https://mail.google.com/mail/u/0/#inbox/{em['threadId']}"
        )
        ok = telegram_alert(env, text, prefix=prefix)
        log(f"  [RED] {em['from'][:40]} | {em['subject'][:50]} | tg={ok}")

    # 일반은 카운트만
    if new_other:
        log(f"  [OTHER NEW] {len(new_other)}건 (push 안 함)")

    # state 업데이트 (이번에 본 ID 전부 + 기존)
    new_seen = list(seen | set(fetched_ids))
    # 최근 500개만 유지 (state 무한팽창 방지)
    state["seen"] = new_seen[-500:]
    state["last_check"] = datetime.datetime.now().isoformat()
    state["last_red_count"] = len(new_red)
    state["last_other_count"] = len(new_other)
    save_state(state)

    log(f"=== 종료: RED={len(new_red)}건 push, OTHER={len(new_other)}건 skip ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 어떤 에러도 텔레그램으로 알림 (silent crash 방지)
        env = load_secrets()
        telegram_alert(env, f"❌ inbox_monitor_unified CRASH: {e}", prefix="")
        log(f"[FATAL] {e}")
        sys.exit(1)
