"""
부서별 git 활동 + 파일 변경 집계
- "어제 대비 상황 변화" 자동 생성
- "잘한 점" 후보 추출 (큰 커밋, 새 파일 등)
- "문제점 / 해결" 은 TODO·FIXME 주석 + commit 메시지 분석
"""
import subprocess
import datetime
from pathlib import Path
from collections import defaultdict


BASE = Path(r"D:\cheonmyeongdang")
DEPARTMENTS = [
    "ceo-briefing", "cheonmyeongdang", "digital-products",
    "ebook", "game", "insurance-daboyeo", "intelligence",
    "korlens", "media", "secretary", "security", "tax", "travelmap",
]


def _git(args, cwd=None):
    cwd = cwd or str(BASE)
    try:
        r = subprocess.run(
            ["git"] + args, cwd=cwd,
            capture_output=True, text=True, encoding="utf-8", timeout=30
        )
        return r.stdout
    except Exception as e:
        return ""


def _since(days_back=1):
    return (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d %H:%M")


def department_commits(dept_key, days_back=1):
    """특정 부서의 커밋 내역"""
    path = f"departments/{dept_key}/"
    log = _git([
        "log",
        f"--since={_since(days_back)}",
        "--pretty=format:%H|%ai|%s",
        "--", path,
    ])
    commits = []
    for line in log.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            commits.append({
                "hash": parts[0][:8],
                "date": parts[1],
                "msg": parts[2],
            })
    return commits


def department_changed_files(dept_key, days_back=1):
    """부서 폴더에서 변경된 파일 목록 (추가/수정/삭제)"""
    path = f"departments/{dept_key}/"
    log = _git([
        "log",
        f"--since={_since(days_back)}",
        "--name-status",
        "--pretty=format:",
        "--", path,
    ])
    adds, mods, dels = [], [], []
    for line in log.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            status, fname = parts
            short = fname.replace(f"departments/{dept_key}/", "")
            if status.startswith("A"):
                adds.append(short)
            elif status.startswith("M"):
                mods.append(short)
            elif status.startswith("D"):
                dels.append(short)
    return {"added": adds, "modified": mods, "deleted": dels}


def _recently_changed_files(dept_key, days_back=1):
    """git commit 없이도 mtime 기반으로 최근 변경 감지"""
    import time
    cutoff = time.time() - days_back * 86400
    path = BASE / "departments" / dept_key
    if not path.exists():
        return []
    changed = []
    IGNORE = ["__pycache__", "node_modules", ".git", "build", "dist", ".next"]
    for f in path.rglob("*"):
        if not f.is_file():
            continue
        if any(ig in str(f) for ig in IGNORE):
            continue
        try:
            if f.stat().st_mtime >= cutoff:
                changed.append({
                    "path": str(f.relative_to(BASE)),
                    "mtime": f.stat().st_mtime,
                    "size": f.stat().st_size,
                })
        except Exception:
            continue
    return sorted(changed, key=lambda x: x["mtime"], reverse=True)


def department_summary(dept_key, days_back=1):
    """부서별 요약 (변화/잘한점/문제점 후보)"""
    commits = department_commits(dept_key, days_back)
    files = department_changed_files(dept_key, days_back)
    # mtime-based (git 커밋 없을 때 폴백)
    mtime_changed = _recently_changed_files(dept_key, days_back)

    changes = []
    if commits:
        recent_msgs = [c["msg"] for c in commits[:3]]
        changes.append(f"커밋 {len(commits)}건: " + " / ".join(recent_msgs[:2]))
    if files["added"]:
        changes.append(f"신규 {len(files['added'])}개")
    if files["modified"]:
        changes.append(f"수정 {len(files['modified'])}개")
    if files["deleted"]:
        changes.append(f"삭제 {len(files['deleted'])}개")
    # 커밋 없이 편집만 있는 경우 — 건수만 알림, 파일명은 내부 로그에만
    if not commits and mtime_changed:
        changes.append(f"편집 작업 {len(mtime_changed)}건 (미반영)")

    # "잘한 점" 후보: 커밋 메시지에서 긍정 키워드
    positive = []
    POSITIVE_KEY = ["fix", "add", "implement", "complete", "launch", "deploy",
                    "success", "optimize", "improve", "resolve", "ship",
                    "완료", "추가", "구현", "배포", "수정", "개선", "해결"]
    for c in commits:
        if any(k in c["msg"].lower() for k in POSITIVE_KEY):
            positive.append(c["msg"])

    # "문제점" 후보: TODO/FIXME/BUG 주석 스캔
    # 주의: 코드 안 string literal("TODO:", f"...TODO: {x}") 은 가짜 TODO이므로 제외.
    # 진짜 TODO는 코드 줄 시작이 # / // / /* (주석)에서만 잡는다.
    import re as _re
    problems = []
    seen_texts = set()
    dept_path = BASE / "departments" / dept_key
    # 주석 prefix 정규식: 줄 앞쪽이 #, //, /*, *, ; 같은 주석 시작이어야 함
    COMMENT_PREFIX = _re.compile(r'^\s*(#+|//+|/\*+|\*+|;+|<!--)\s*(TODO|FIXME|BUG|HACK)[\s:]', _re.IGNORECASE)
    if dept_path.exists():
        for ext in ["*.py", "*.js", "*.ts", "*.html"]:
            for f in dept_path.rglob(ext):
                if "node_modules" in str(f) or "__pycache__" in str(f):
                    continue
                try:
                    for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                        m = COMMENT_PREFIX.match(line)
                        if not m:
                            continue
                        kw = m.group(2).upper()
                        # kw 뒤의 실제 텍스트만 추출
                        body = line[m.end():].strip()
                        if not body or body in seen_texts:
                            continue
                        # placeholder 만 있는 경우 (예: '{text}\n컨텍스트: ...') 스킵
                        if body.startswith("{") and body.endswith("}"):
                            continue
                        seen_texts.add(body)
                        problems.append({
                            "file": str(f.relative_to(BASE)),
                            "kw": kw,
                            "text": body[:120],
                        })
                        if len(problems) >= 5:
                            break
                    if len(problems) >= 5:
                        break
                except Exception:
                    continue
                if len(problems) >= 5:
                    break
            if len(problems) >= 5:
                break

    return {
        "dept": dept_key,
        "commits_count": len(commits),
        "files_changed_count": len(files["added"]) + len(files["modified"]) + len(files["deleted"]),
        "mtime_changed_count": len(mtime_changed),
        "changes_summary": " / ".join(changes) if changes else "변화 없음",
        "positive_highlights": positive[:3],
        "active_problems": problems[:3],
        "files": files,
        "recent_files_mtime": [x["path"] for x in mtime_changed[:5]],
    }


def all_departments_summary(days_back=1):
    """전 부서 요약"""
    return {d: department_summary(d, days_back) for d in DEPARTMENTS}


if __name__ == "__main__":
    import sys, json
    sys.stdout.reconfigure(encoding="utf-8")
    result = all_departments_summary(days_back=1)
    for dept, summ in result.items():
        print(f"━━━ {dept} ━━━")
        print(f"  커밋: {summ['commits_count']}, 파일: {summ['files_changed_count']}")
        print(f"  변화: {summ['changes_summary']}")
        if summ['positive_highlights']:
            print(f"  ✅ 잘한점: {summ['positive_highlights'][0][:80]}")
        if summ['active_problems']:
            p = summ['active_problems'][0]
            print(f"  ⚠ {p['kw']}: {p['text'][:60]}")
        print()
