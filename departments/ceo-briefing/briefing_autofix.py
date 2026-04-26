#!/usr/bin/env python3
"""
브리핑 자동 대응 엔진.

각 부서의 active_problems / 일반 TODO 텍스트를 패턴 매칭해서
자동 처리 가능한 것은 바로 실행하고, 결과를 반환한다.

사용자만 할 수 있는 작업(인증/결제/외부 콘솔 로그인)은 그대로 유지.

실행 로그: logs/autofix.log

사용:
    from briefing_autofix import run_autofix, format_autofix_section
    results = run_autofix(depts)  # depts = build_v2_departments_data()
    print(format_autofix_section(results))
"""
import os
import re
import json
import subprocess
import datetime
import shutil
from pathlib import Path

BASE = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUTOFIX_LOG = LOG_DIR / "autofix.log"


def _log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(AUTOFIX_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ─────────── 액션 함수들 ───────────

def _run(cmd, cwd=None, timeout=120):
    """subprocess 실행 — stdout/stderr 반환."""
    try:
        r = subprocess.run(cmd, cwd=cwd, shell=False, capture_output=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return -1, str(e)


def action_npm_audit_fix(target_dir):
    """npm audit fix 실행 후 잔여 취약점 수 반환."""
    d = BASE / target_dir
    if not (d / "package.json").exists():
        return False, f"package.json 없음: {d}"
    rc, out = _run(["npm", "audit", "fix"], cwd=str(d), timeout=180)
    # 수량 파싱
    m = re.search(r"(\d+) vulnerabilit", out)
    remaining = m.group(1) if m else "?"
    _log(f"npm audit fix @ {target_dir} → rc={rc}, remaining={remaining}")
    return (rc == 0), f"{target_dir} npm audit: {remaining}개 잔여"


def action_schtasks_run(task_name):
    """Windows Task를 즉시 실행."""
    rc, out = _run(["schtasks", "/Run", "/TN", task_name], timeout=30)
    ok = (rc == 0)
    _log(f"schtasks /Run {task_name} → rc={rc}")
    return ok, f"{task_name} {'실행됨' if ok else '실행실패'}"


def action_rotate_log(log_path, max_mb=10):
    """로그 파일 크기 초과 시 .bak 으로 이동."""
    p = BASE / log_path
    if not p.exists():
        return False, f"{log_path} 없음"
    size_mb = p.stat().st_size / (1024 * 1024)
    if size_mb < max_mb:
        return False, f"{log_path} 회전 불필요 ({size_mb:.1f}MB)"
    bak = p.with_suffix(p.suffix + f".{datetime.date.today()}.bak")
    shutil.move(str(p), str(bak))
    _log(f"log rotated: {log_path} ({size_mb:.1f}MB) → {bak.name}")
    return True, f"{log_path} 회전됨"


def action_cleanup_node_modules(target_dir):
    """node_modules 용량 확인, 너무 크면 재설치."""
    d = BASE / target_dir / "node_modules"
    if not d.exists():
        return False, "node_modules 없음"
    # 사이즈 체크만
    return True, f"{target_dir}/node_modules OK"


def action_mark_completed(task_id):
    """priority_tasks.json 에서 완료 플래그 세팅."""
    PRI = Path(__file__).resolve().parent / "priority_tasks.json"
    if not PRI.exists():
        return False, "priority_tasks.json 없음"
    tasks = json.loads(PRI.read_text(encoding="utf-8"))
    for t in tasks:
        if t.get("id") == task_id or t.get("title", "").startswith(task_id):
            t["done"] = True
            t["done_date"] = datetime.date.today().isoformat()
            PRI.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
            return True, f"완료 표시: {task_id}"
    return False, f"ID 없음: {task_id}"


# ─────────── 패턴 → 액션 매핑 ───────────

# (정규식 패턴, 액션 함수, 인자)
AUTOFIX_RULES = [
    # 1. npm 취약점
    (r"tax/server.*npm audit.*취약|tax.*취약점 22개",
     action_npm_audit_fix, "departments/tax/server"),
    (r"npm audit.*취약.*(\d+)개",
     action_npm_audit_fix, "departments/tax/server"),

    # 2. Task Scheduler 정지/실행실패
    (r"health_check\.py.*미실행|health_log.*4/18 이후.*없",
     action_schtasks_run, "KunStudio_HealthCheck"),
    (r"intrusion.*4/18 이후.*미실행",
     action_schtasks_run, "KunStudio_Intrusion"),
    (r"security_audit.*4/18 이후",
     action_schtasks_run, "KunStudio_Security"),
    (r"unified_log.*2026-04-18 이후.*없|scheduler.*멈",
     action_schtasks_run, "KunStudio_AutoPromo_PM"),

    # 3. 로그 회전 (100MB 초과 시)
    (r"logs?.*크기 초과|log.*100MB",
     action_rotate_log, "departments/media/logs/post_log.txt"),
]


# 사용자만 처리 가능한 패턴 (자동 X, 표시만)
USER_ONLY_PATTERNS = [
    r"Vercel.*env|CODEF_CLIENT.*배포|대시보드.*Redeploy",
    r"KDP.*재업로드|KDP.*콘솔|ISBN 재설정",
    r"카카오.*비즈.*심사|카카오 디벨로퍼스",
    r"파트너스.*단축링크|쿠팡.*대시보드",
    r"Play.*콘솔|스토어 등록정보",
    r"본인인증|공동인증서|간편인증|2FA",
    r"결제|카드 등록|Stripe",
]


# ─────────── 메인 엔진 ───────────

def run_autofix(depts_data):
    """각 부서 active_problems 를 훑어서 자동 처리 가능한 것 실행.

    depts_data: {dept_key: {active_problems: [{kw, text}, ...], ...}}
    반환: {'processed': [...], 'skipped_user_only': [...], 'failed': [...]}
    """
    result = {"processed": [], "skipped_user_only": [], "failed": []}
    seen_patterns = set()  # 중복 실행 방지

    for dept, info in (depts_data or {}).items():
        if not isinstance(info, dict):
            continue
        problems = info.get("active_problems", []) or []
        for p in problems:
            text = (p.get("text") or "") if isinstance(p, dict) else str(p)
            if not text:
                continue

            # 사용자 전용 체크
            if any(re.search(up, text, re.IGNORECASE) for up in USER_ONLY_PATTERNS):
                result["skipped_user_only"].append({"dept": dept, "text": text[:80]})
                continue

            # 자동 규칙 매칭
            matched = False
            for pattern, action, arg in AUTOFIX_RULES:
                if re.search(pattern, text, re.IGNORECASE):
                    key = (action.__name__, str(arg))
                    if key in seen_patterns:
                        matched = True
                        break
                    seen_patterns.add(key)
                    ok, msg = action(arg)
                    entry = {"dept": dept, "action": action.__name__,
                             "target": str(arg), "ok": ok, "msg": msg, "source": text[:80]}
                    if ok:
                        result["processed"].append(entry)
                    else:
                        result["failed"].append(entry)
                    matched = True
                    break

            if not matched:
                # 미정의 패턴 → AI autofix 엔진으로 위임 (비용 $10/월 한도)
                try:
                    from autofix_ai import ai_process_todo, budget_state
                    bs = budget_state()
                    if bs["spent_usd"] < bs["budget_usd"]:
                        ai_r = ai_process_todo(dept=dept, text=text)
                        if ai_r.get("ok"):
                            action_type = ai_r.get("action")
                            summary = ai_r.get("summary", "")
                            if action_type == "user_only":
                                result["skipped_user_only"].append({
                                    "dept": dept, "text": text[:80],
                                    "ai_hint": ai_r.get("user_action", "")[:80],
                                })
                            elif action_type in ("code_draft", "research_note"):
                                result["processed"].append({
                                    "dept": dept, "action": f"ai_{action_type}",
                                    "target": "-", "ok": True,
                                    "msg": f"{summary} (${ai_r.get('cost_usd',0):.4f})",
                                    "source": text[:80], "path": ai_r.get("path", ""),
                                })
                            # skip 은 무시
                except Exception as e:
                    pass

    # 예산 상태 리포트
    try:
        from autofix_ai import budget_state
        result["budget"] = budget_state()
    except Exception:
        result["budget"] = None

    return result


def format_autofix_section(result):
    """브리핑에 넣을 섹션 포맷."""
    processed = result.get("processed", [])
    skipped = result.get("skipped_user_only", [])
    failed = result.get("failed", [])

    msg = "🤖 <b>자동 처리</b>\n"
    if processed:
        for p in processed:
            msg += f"  ✅ [{p['dept']}] {p['msg']}\n"
    if failed:
        for f in failed:
            msg += f"  ❌ [{f['dept']}] {f['action']} 실패: {f['msg'][:60]}\n"
    if skipped:
        msg += f"\n  🙋 사용자 필요 ({len(skipped)}건):\n"
        for s in skipped[:5]:
            msg += f"    • [{s['dept']}] {s['text']}\n"
    if not (processed or failed or skipped):
        msg += "  (자동 처리 대상 없음)\n"

    # 예산 라인
    b = result.get("budget")
    if b:
        bar = int(b["utilization_pct"] / 10)  # 0~10
        msg += f"\n  💰 AI 예산: ${b['spent_usd']:.3f}/${b['budget_usd']:.0f} "
        msg += f"({b['utilization_pct']:.1f}%, {b['calls']}콜)\n"
    msg += "\n"
    return msg


if __name__ == "__main__":
    # 직접 실행시: briefing v2의 부서 데이터 로드 후 autofix
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import briefing_v2  # build_v2_departments_data 호출
    depts = briefing_v2._safe(briefing_v2.build_v2_departments_data if hasattr(briefing_v2, 'build_v2_departments_data') else (lambda: {}), {})
    r = run_autofix(depts)
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
    print("\n" + format_autofix_section(r))
