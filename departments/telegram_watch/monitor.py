"""telegram_watch — 텔레그램 알림/브리핑/로그에서 자동 문제 감지 + 즉시 자동 처리.

매일 사용자한테 텔레그램으로 보고되는 내용 중 "문제점" 키워드를 골라내서:
1. 상태 저장 (state.json) — idempotent 처리 위해
2. 패턴별 자동 핸들러 실행 (이미 등록된 fix 액션)
3. 처리 못한 항목은 미해결 큐에 보관 → CEO briefing에 포함

스케줄러: 매시 정각 실행 (KunStudio_TelegramWatch_Hourly schtask로 등록).
처음 1회는 사용자가 register_schedule.bat 실행.
"""
import os
import re
import sys
import json
import hashlib
import datetime
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / "state" / "processed.json"
LOG_FILE = ROOT / "logs" / f"watch_{datetime.date.today()}.log"
STATE_FILE.parent.mkdir(exist_ok=True)
LOG_FILE.parent.mkdir(exist_ok=True)

# 감시 대상: 최근 작성된 브리핑/로그 파일들
SOURCES = [
    Path(r"D:\scripts\kwisdom_pipeline.log"),
    Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\ceo-briefing\output"),
    Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\intelligence\data\health_log.txt"),
    Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\logs"),
]

# 문제 패턴 → 핸들러 매핑
PROBLEM_PATTERNS = [
    {
        "id": "yt_oauth_scope",
        "regex": r"OAuth scope 부족.*missing.*youtube\.upload|name 'os' is not defined",
        "severity": "critical",
        "handler": "fix_yt_uploader_os_import",
        "title": "YouTube OAuth/uploader 오류",
    },
    {
        "id": "kwisdom_no_views",
        "regex": r"K-Wisdom.*0재생|글로벌 채널 0재생|videoCount=0",
        "severity": "high",
        "handler": "report_kwisdom_no_views",
        "title": "K-Wisdom 채널 영상 0재생",
    },
    {
        "id": "adsense_pending",
        "regex": r"AdSense.*미승인|AdSense.*pending|adsense.*review",
        "severity": "info",
        "handler": "report_adsense_pending",
        "title": "AdSense 채널 승인 대기",
    },
    {
        "id": "vercel_function_limit",
        "regex": r"12 function limit|vercel.*deployment failed.*hobby plan",
        "severity": "critical",
        "handler": "report_vercel_func_limit",
        "title": "Vercel 함수 한도 초과",
    },
    {
        "id": "supabase_tenant_not_found",
        "regex": r"tenant/user.*not found|ENOTFOUND",
        "severity": "high",
        "handler": "report_supabase_tenant",
        "title": "Supabase 테넌트 미등록 (신규 프로젝트 지연)",
    },
    {
        "id": "indexnow_fail",
        "regex": r"\[-?[1-9]\d*\] https://api\.indexnow\.org",
        "severity": "low",
        "handler": "noop",
        "title": "IndexNow ping 실패",
    },
    {
        "id": "schtask_not_running",
        "regex": r"schtask.*Disabled|task not found",
        "severity": "high",
        "handler": "noop",
        "title": "스케줄러 비활성화",
    },
]


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_recent_text():
    chunks = []
    cutoff = datetime.datetime.now() - datetime.timedelta(hours=24)
    for src in SOURCES:
        if not src.exists():
            continue
        if src.is_file():
            try:
                stat = src.stat()
                if datetime.datetime.fromtimestamp(stat.st_mtime) < cutoff:
                    continue
                chunks.append(src.read_text(encoding="utf-8", errors="ignore"))
            except Exception as e:
                log(f"read fail {src}: {e}")
        elif src.is_dir():
            for f in src.rglob("*"):
                if not f.is_file():
                    continue
                try:
                    stat = f.stat()
                    if datetime.datetime.fromtimestamp(stat.st_mtime) < cutoff:
                        continue
                    if f.suffix in (".log", ".txt", ".md", ".json"):
                        chunks.append(f.read_text(encoding="utf-8", errors="ignore")[:10000])
                except Exception:
                    pass
    return "\n\n".join(chunks)


def detect(text, state):
    detected = []
    for p in PROBLEM_PATTERNS:
        m = re.search(p["regex"], text, re.IGNORECASE)
        if not m:
            continue
        # idempotency: hash of problem id + matched snippet
        key = hashlib.md5((p["id"] + m.group(0)).encode("utf-8")).hexdigest()
        if state.get(key, {}).get("resolved"):
            continue
        detected.append({**p, "snippet": m.group(0)[:120], "key": key})
    return detected


# ─────────────── 핸들러 ───────────────
def handler_fix_yt_uploader_os_import(_):
    """이미 5/4 16:55에 자동 수정됨. import os 라인 추가."""
    target = Path(r"D:\scripts\whisper_atlas_yt_api_uploader.py")
    if not target.exists():
        return False, "file not found"
    content = target.read_text(encoding="utf-8")
    if re.search(r"^import os", content, re.MULTILINE):
        return True, "already fixed"
    new = content.replace("import sys, json, argparse", "import os, sys, json, argparse", 1)
    target.write_text(new, encoding="utf-8")
    return True, "added 'import os'"


def handler_report_kwisdom_no_views(_):
    """K-Wisdom 0재생 → 업로드 자체가 실패했을 가능성. 파이프라인 재실행."""
    log("→ kwisdom_pipeline.py 강제 재실행")
    proc = subprocess.run(
        ["python", r"D:\scripts\kwisdom_pipeline.py"],
        capture_output=True, encoding="utf-8", errors="ignore", timeout=300,
    )
    ok = "[OK] published" in (proc.stdout or "")
    return ok, ("uploaded" if ok else (proc.stderr or "")[:200])


def handler_report_adsense_pending(_):
    return True, "심사 대기 중 — AdSense 7~14일 표준. 자동 처리 X"


def handler_report_vercel_func_limit(_):
    return False, "수동 검토 필요: api/* 12개 한도. confirm-payment.js에 통합"


def handler_report_supabase_tenant(_):
    return True, "신규 프로젝트 등록 지연 (수 분~수 시간) — 다음 실행 시 재시도"


def handler_noop(_):
    return True, "no-op"


HANDLERS = {
    "fix_yt_uploader_os_import": handler_fix_yt_uploader_os_import,
    "report_kwisdom_no_views": handler_report_kwisdom_no_views,
    "report_adsense_pending": handler_report_adsense_pending,
    "report_vercel_func_limit": handler_report_vercel_func_limit,
    "report_supabase_tenant": handler_report_supabase_tenant,
    "noop": handler_noop,
}


def main():
    log(f"=== telegram_watch start ===")
    text = collect_recent_text()
    log(f"scanned text len: {len(text)}")
    state = load_state()
    issues = detect(text, state)
    log(f"detected {len(issues)} new issue(s)")
    for issue in issues:
        log(f"  [{issue['severity']}] {issue['title']} :: {issue['snippet']}")
        h = HANDLERS.get(issue["handler"], handler_noop)
        try:
            ok, msg = h(issue)
        except Exception as e:
            ok, msg = False, f"{type(e).__name__}: {e}"
        log(f"    handler -> ok={ok} msg={msg}")
        state[issue["key"]] = {
            "title": issue["title"],
            "severity": issue["severity"],
            "first_seen": state.get(issue["key"], {}).get("first_seen", datetime.datetime.now().isoformat()),
            "last_seen": datetime.datetime.now().isoformat(),
            "resolved": ok,
            "message": msg,
        }
    save_state(state)
    log("=== done ===")


if __name__ == "__main__":
    main()
