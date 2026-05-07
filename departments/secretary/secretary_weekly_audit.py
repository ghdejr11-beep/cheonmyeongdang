"""비서부 사후 감사 — 매주 월요일 09:00.

7일 인박스 IGNORED 메일 0건인지 확인.
0건 아니면 텔레그램 alert "비서부 잡지 못한 메일 X건"

검증 방법:
1) Gmail 7일 inbox 전수 가져오기
2) inbox_monitor_unified_state.json의 seen ID와 비교
3) seen이 아니지만 RED 분류 가능한 메일 → IGNORED
4) IGNORED 0건 = 정상, 아니면 alert
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
LOG_FILE = LOG_DIR / f"secretary_audit_{datetime.date.today().isoformat()}.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Reuse RED detection from inbox_monitor_unified
sys.path.insert(0, str(ROOT))
from inbox_monitor_unified import (
    is_red, load_secrets, get_access_token, search_messages, get_message_metadata, telegram_alert
)


def log(msg: str) -> None:
    line = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main() -> None:
    log("=== 비서부 주간 감사 시작 ===")
    env = load_secrets()
    token = get_access_token(env)
    if not token:
        log("[ABORT] no Gmail access token")
        telegram_alert(env, "❌ 비서부 주간 감사 — Gmail token 실패. monitor 자체가 안 돌고 있을 수 있음.")
        sys.exit(1)

    # state 로드
    seen_ids = set()
    if STATE_FILE.exists():
        try:
            seen_ids = set(json.loads(STATE_FILE.read_text(encoding="utf-8")).get("seen", []))
        except Exception:
            pass

    # 7일 inbox 전수 가져오기
    msgs = search_messages(token, "in:inbox newer_than:7d", max_results=200)
    log(f"  최근 7일 inbox: {len(msgs)}건")

    ignored_red = []
    for m in msgs[:200]:
        if m["id"] in seen_ids:
            continue
        em = get_message_metadata(token, m["id"])
        if not em:
            continue
        if is_red(em):
            ignored_red.append(em)

    if not ignored_red:
        log("✅ IGNORED RED 메일 0건 — 비서부 정상")
        # 정상도 알림 (잘 돌고 있다는 신호)
        telegram_alert(env, f"✅ <b>비서부 주간 감사</b> — 7일간 잡지 못한 RED 메일 0건. 정상 가동 중.")
    else:
        lines = ["🚨 <b>비서부 주간 감사 — IGNORED RED 메일 발견</b>", ""]
        for em in ignored_red[:15]:
            lines.append(f"• {em['from'][:60]}")
            lines.append(f"  ↳ {em['subject'][:80]}")
            lines.append(f"  ({em['date']})")
            lines.append("")
        if len(ignored_red) > 15:
            lines.append(f"...외 {len(ignored_red)-15}건")
        lines.append("")
        lines.append("inbox_monitor_unified.py state에 미등록. 즉시 확인 필요.")
        telegram_alert(env, "\n".join(lines))
        log(f"🚨 IGNORED RED 메일 {len(ignored_red)}건 발견")

    log("=== 감사 종료 ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        env = load_secrets()
        telegram_alert(env, f"❌ secretary_weekly_audit CRASH: {e}")
        log(f"[FATAL] {e}")
        sys.exit(1)
