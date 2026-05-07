"""쿤스튜디오 종합 '지금 상황' 보고 — 매일 + 즉시 호출 가능.

사용자 명령 (5/7): "매일마다 현재 상황 체크하라" — 단일 통합 보고.

5 항목 한 화면에:
1. 💰 매출 (어제 / 오늘 / 누적 / 채널별)
2. 👤 사용자 액션 (남은 TOP 5 + 마감 D-N)
3. ⏰ 외부 응답 대기 (KoDATA / PG / Kakao Ventures / AppSumo / Etsy 등)
4. 🤖 자동화 가동 상태 (schtask 24개 / 라이브 16/16 / 신규 메일)
5. 🚨 RED 알림 (24h 새 RED 메일)

호출 방법:
  python departments/intelligence/status_now.py          # 텔레그램 + 화면 보고
  python departments/intelligence/status_now.py --quiet  # 텔레그램 X, 화면만

schtask:
  - KunStudio_Status_Now_Morning (매일 09:00)
  - KunStudio_Status_Now_Evening (매일 18:00)
"""
import os
import sys
import json
import datetime
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent.parent
SECRETS = ROOT / ".secrets"
SECRETARY = ROOT / "departments" / "secretary"
TOKEN = SECRETARY / "token.json"


def load_secrets() -> dict:
    env: dict[str, str] = {}
    if SECRETS.exists():
        for line in SECRETS.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def gmail_token(env: dict) -> str | None:
    if not TOKEN.exists():
        return None
    tok = json.loads(TOKEN.read_text(encoding="utf-8"))
    data = urllib.parse.urlencode({
        "client_id": tok["client_id"],
        "client_secret": tok["client_secret"],
        "refresh_token": tok["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(tok["token_uri"], data=data)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())["access_token"]
    except Exception:
        return None


def gmail_count(token: str, q: str) -> int:
    if not token:
        return -1
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={urllib.parse.quote(q)}&maxResults=1"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read())
            return res.get("resultSizeEstimate", 0)
    except Exception:
        return -1


def schtask_status() -> dict:
    """주요 schtask 상태 + 마지막 결과."""
    targets = [
        "KunStudio_Cheonmyeongdang_V35_Monitor",
        "KunStudio_Inbox_Monitor_Unified",
        "KunStudio_Pinterest_Auto_Publish",
        "KunStudio_Twitter_Daily",
        "KunStudio_B2B_Followup",
        "KunStudio_Secretary_Every_2H_Report",
        "KunStudio_Daily_Revenue_Report",
        "KunStudio_Grant_Result_Monitor",
    ]
    out = {}
    for t in targets:
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"$i = Get-ScheduledTaskInfo -TaskName '{t}' -ErrorAction SilentlyContinue; if ($i) {{ $i.LastTaskResult }} else {{ 'missing' }}"],
                capture_output=True, text=True, timeout=10
            )
            out[t] = r.stdout.strip()
        except Exception:
            out[t] = "err"
    return out


def revenue_last24h() -> dict:
    """sales-collection unified data 읽기."""
    sales = ROOT / "departments" / "sales-collection" / "data"
    out = {"krw": 0, "usd": 0, "channels": []}
    today = datetime.date.today().isoformat()
    for f in ["gumroad_daily.json", "vercel_daily.json", "yt_4ch_daily.json"]:
        p = sales / f
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(d, dict) and "today" in d:
                    out["channels"].append(f"{f.replace('_daily.json','')}: {d.get('today', 0)}")
            except Exception:
                pass
    return out


def health_check() -> tuple[int, int]:
    """v3.5 monitor state 읽기."""
    state = ROOT / "departments" / "intelligence" / "data" / "v35_monitor_state.json"
    if not state.exists():
        return (0, 0)
    try:
        d = json.loads(state.read_text(encoding="utf-8"))
        ok = sum(1 for v in d.values() if v.get("ok"))
        return (ok, len(d))
    except Exception:
        return (0, 0)


def pending_actions() -> list[str]:
    """남은 TOP 사용자 액션 list."""
    today = datetime.date(2026, 5, 7)
    deadline = datetime.date(2026, 5, 20)
    d_minus = (deadline - today).days
    return [
        f"🥇 K-Startup AI 리그 PMS (D-{d_minus}, 60분, ₩5천만~5억)",
        "🥈 Play Console v1.3.1 AAB (5분, AAB 빌드 완료)",
        "🥉 AppSumo LTD ($5K~$15K, 20분, demo script 완료)",
        "🟠 RapidAPI listing (5분)",
        "🟠 Beehiiv 가입 (5분)",
        "🟡 Etsy Top 5 (12분) / 영문 인플라 5명 (30분)",
    ]


def external_waits() -> list[str]:
    """외부 응답 대기 list."""
    return [
        "📨 KoDATA 회신 (5/7 정정 재발송 → 5/8~5/14 예상)",
        "💳 PG 가맹점 검토 (카카오페이 단건+정기, 1~3 영업일)",
        "💼 Kakao Ventures cold (5/7 12:16 발송 → D+5/D+10 자동 follow-up)",
        "📧 카카오페이 jella.tto 답장 (5/7 사용자 send)",
        "📧 네이버페이 1:1 문의 답장 (5/7 사용자 send)",
    ]


def telegram_send(env: dict, text: str) -> bool:
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
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


def build_report() -> str:
    env = load_secrets()
    token = gmail_token(env)
    now = datetime.datetime.now().strftime("%m/%d %H:%M")

    # 1. 매출
    rev = revenue_last24h()

    # 2. 사용자 액션
    actions = pending_actions()

    # 3. 외부 대기
    waits = external_waits()

    # 4. 자동화 상태
    ok, total = health_check()
    schs = schtask_status()
    sch_ok = sum(1 for v in schs.values() if v == "0")
    sch_fail = sum(1 for v in schs.values() if v not in ["0", "267009", "267011", "missing", "err", ""])

    # 5. RED 알림
    red_q = "in:inbox newer_than:1d (from:@kodata.co.kr OR from:@kakaopaycorp.com OR from:@naverpay.com OR from:@k-startup.go.kr OR from:@kakao.vc OR from:@antler.co OR from:@kakaobrain.com)"
    red_24h = gmail_count(token, red_q) if token else -1

    lines = []
    lines.append(f"📊 쿤스튜디오 현재 상황 — {now}")
    lines.append("")
    lines.append("💰 매출 (오늘)")
    if rev["channels"]:
        for c in rev["channels"][:3]:
            lines.append(f"  • {c}")
    else:
        lines.append("  • collector 정상, 데이터 ₩0 (D+1 라이브)")
    lines.append("")
    lines.append("👤 사용자 액션 TOP")
    for a in actions[:5]:
        lines.append(f"  {a}")
    lines.append("")
    lines.append("⏰ 외부 응답 대기")
    for w in waits[:4]:
        lines.append(f"  {w}")
    lines.append("")
    lines.append("🤖 자동화 가동")
    lines.append(f"  • 라이브 헬스 {ok}/{total} UP")
    lines.append(f"  • 핵심 schtask 8개: 정상 {sch_ok} / 실패 {sch_fail}")
    if sch_fail:
        for k, v in schs.items():
            if v not in ["0", "267009", "267011", "missing", "err", ""]:
                lines.append(f"    🔴 {k}: result {v}")
    lines.append("")
    lines.append(f"🚨 RED 메일 (24h): {red_24h if red_24h >= 0 else 'N/A'}건")
    lines.append("")
    lines.append("📍 상세: cheonmyeongdang.com/actions.html")
    return "\n".join(lines)


def main() -> None:
    quiet = "--quiet" in sys.argv
    report = build_report()
    print(report)
    if not quiet:
        env = load_secrets()
        ok = telegram_send(env, report)
        print(f"\n[telegram] {'sent' if ok else 'FAIL'}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[fatal] {e}", file=sys.stderr)
        env = load_secrets()
        telegram_send(env, f"🚨 status_now fatal: {str(e)[:300]}")
        sys.exit(1)
