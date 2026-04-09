"""
🛠️ 개발부 (Dev Team)

매일 06:00 KST 자동 실행 + 핵심 코드 변경 시 push 트리거.

역할:
  1. 핵심 Python 파일 전체에 py_compile (구문 검사)
  2. 변경된 코드 진단 (어제 commit 분석)
  3. Claude 에게 1순위 작업 추천 받기
     - 카카오톡 사주봇 (현재 활발히 개발 중)
     - 멘토봇·lyrics_watcher·auto_watcher 안정화
  4. 결과를 텔레그램으로 보고

비-파괴적 (read-only): 코드 자동 수정·푸시는 안 함. 인사이트만.
실제 코드 작성은 Claude Code 가 직접 함.
"""

import os
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from scripts.lib.telegram_notify import notify_safe


KST = timezone(timedelta(hours=9))


def now_kst_str() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")


# ============================================================
# 핵심 Python 파일 정의 (10억 목표 직결 = 우선순위 P1)
# ============================================================
P1_FILES = [
    # 카카오톡 사주봇 = 100일 10억 1순위
    "ebook_system/projects/saju_ai_saas/server.py",
    "ebook_system/projects/saju_ai_saas/saju_calc.py",
    "ebook_system/projects/saju_ai_saas/kakao_endpoints.py",
    # AI 음악 수익화 파이프라인
    "lyrics_watcher.py",
    "youtube_uploader.py",
    "playlist_maker.py",
    "auto_watcher.py",
]

P2_FILES = [
    # 전자책·멘토봇 (보조 매출원)
    "ebook_system/mentor_bot/server.py",
    "ebook_system/generate_book.py",
    "ebook_system/make_pdf.py",
]

# AI 부서 자체
INFRA_FILES = [
    "scripts/lib/telegram_notify.py",
    "scripts/teams/analytics_team.py",
    "scripts/teams/dev_team.py",
]


def syntax_check(file_path: str) -> tuple[bool, str]:
    """py_compile 로 구문 검사. (성공, 메시지) 반환."""
    full = SCRIPT_DIR / file_path
    if not full.exists():
        return False, "MISSING"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(full)],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=15,
        )
        if result.returncode == 0:
            return True, "OK"
        return False, (result.stderr or "")[-200:]
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:100]}"


def line_count(file_path: str) -> int:
    full = SCRIPT_DIR / file_path
    if not full.exists():
        return 0
    try:
        return sum(1 for _ in full.open(encoding="utf-8"))
    except Exception:
        return 0


def yesterday_commits() -> list[str]:
    """최근 24시간 commit 메시지 1줄 요약."""
    try:
        result = subprocess.run(
            ["git", "log", "--since=24 hours ago",
             "--pretty=format:%h|%s|%an", "-30"],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            cwd=str(SCRIPT_DIR), timeout=10,
        )
        if result.returncode != 0:
            return []
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        return lines[:30]
    except Exception:
        return []


def changed_files_yesterday() -> list[str]:
    """최근 24시간에 변경된 파일 목록."""
    try:
        result = subprocess.run(
            ["git", "log", "--since=24 hours ago", "--name-only",
             "--pretty=format:", "-30"],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            cwd=str(SCRIPT_DIR), timeout=10,
        )
        if result.returncode != 0:
            return []
        files = set()
        for line in result.stdout.split("\n"):
            line = line.strip()
            if line:
                files.add(line)
        return sorted(files)[:20]
    except Exception:
        return []


def claude_dev_insight(p1_status: list, p2_status: list, commits: list[str],
                      changed: list[str]) -> str:
    """Claude Haiku 4.5 에게 개발부 인사이트 요청.
    실패 시 fallback.
    """
    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        return "(Claude API 키 없음 — 인사이트 생략)"
    try:
        import anthropic
    except ImportError:
        return "(anthropic 패키지 미설치)"

    p1_text = "\n".join(
        f"  {'✅' if ok else '❌'} {path} ({lines}줄): {msg}"
        for ok, path, lines, msg in p1_status
    )
    p2_text = "\n".join(
        f"  {'✅' if ok else '❌'} {path} ({lines}줄)"
        for ok, path, lines, msg in p2_status
    )
    commits_text = "\n".join(f"  • {c}" for c in commits[:10]) or "  (없음)"
    changed_text = "\n".join(f"  • {f}" for f in changed[:15]) or "  (없음)"

    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""너는 덕구네 AI 사업단의 개발부 책임자다.
오늘 06:00 일일 코드 검토 결과를 사용자에게 보고하려 한다.

[배경]
- 사용자 100일 안에 10억 매출 목표
- 1순위 프로젝트: 카카오톡 사주봇 (사주 SaaS 확장)
- 2순위: AI 음악 YouTube 자동 업로드 파이프라인 (lyrics_watcher 등)
- 3순위: 전자책 멘토봇

[P1 핵심 파일 구문 검사]
{p1_text}

[P2 보조 파일]
{p2_text}

[최근 24시간 commit]
{commits_text}

[변경된 파일]
{changed_text}

요구사항:
1. 어제 진행된 작업 1줄 요약 (의미 있는 흐름 짚기)
2. 코드 위험 신호 감지 (구문 에러, 미완성 함수 등) 1~2줄
3. **오늘 우선순위 작업 3개** (구체적, 사용자가 바로 실행 가능한 형태)
   - 가장 높은 ROI 부터
   - 카카오톡 사주봇 진행 단계 우선 고려
4. 한국어, 친근, 전체 600자 이내, 이모지 OK

리포트 본문만 출력 (제목·서론 생략)."""

        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in msg.content if hasattr(b, "text"))
    except Exception as e:
        return f"(Claude 호출 실패: {type(e).__name__}: {str(e)[:120]})"


def build_report() -> tuple[str, int]:
    """리포트 텍스트 + 실패 파일 수 반환."""
    # P1 검사
    p1_status = []
    for f in P1_FILES:
        ok, msg = syntax_check(f)
        p1_status.append((ok, f, line_count(f), msg))

    # P2 검사
    p2_status = []
    for f in P2_FILES:
        ok, msg = syntax_check(f)
        p2_status.append((ok, f, line_count(f), msg))

    # Infra 검사
    infra_status = []
    for f in INFRA_FILES:
        ok, msg = syntax_check(f)
        infra_status.append((ok, f, line_count(f), msg))

    fail_count = sum(1 for ok, *_ in p1_status if not ok)
    fail_count += sum(1 for ok, *_ in p2_status if not ok)
    fail_count += sum(1 for ok, *_ in infra_status if not ok)

    commits = yesterday_commits()
    changed = changed_files_yesterday()

    insight = claude_dev_insight(p1_status, p2_status, commits, changed)

    # P1 라인 짧게
    p1_lines = []
    for ok, path, lines, msg in p1_status:
        mark = "✅" if ok else "❌"
        name = path.rsplit("/", 1)[-1]
        if ok:
            p1_lines.append(f"  {mark} {name} ({lines}줄)")
        else:
            p1_lines.append(f"  {mark} {name}: {msg[:80]}")

    p2_lines = []
    for ok, path, lines, _ in p2_status:
        mark = "✅" if ok else "❌"
        name = path.rsplit("/", 1)[-1]
        p2_lines.append(f"  {mark} {name} ({lines}줄)")

    infra_lines = []
    for ok, path, lines, _ in infra_status:
        mark = "✅" if ok else "❌"
        name = path.rsplit("/", 1)[-1]
        infra_lines.append(f"  {mark} {name}")

    commits_brief = (
        "\n".join(f"  • {c.split('|')[1] if '|' in c else c}" for c in commits[:5])
        or "  (어제 commit 없음)"
    )

    report = f"""🛠️ [개발부] 일일 코드 검토
🕒 {now_kst_str()}

━━━━━━━━━━━━━━━━━━━
🎯 P1 (10억 직결 코드)
{chr(10).join(p1_lines)}

━━━━━━━━━━━━━━━━━━━
📦 P2 (보조)
{chr(10).join(p2_lines)}

━━━━━━━━━━━━━━━━━━━
🤖 AI 부서 인프라
{chr(10).join(infra_lines)}

━━━━━━━━━━━━━━━━━━━
📝 최근 24h commit (top 5)
{commits_brief}

━━━━━━━━━━━━━━━━━━━
💡 개발부 인사이트
{insight}

━━━━━━━━━━━━━━━━━━━
다음 자동 실행: 매일 06:00 KST"""

    return report, fail_count


def main() -> int:
    print(f"[개발부] 시작 {now_kst_str()}")

    try:
        report, fail_count = build_report()
    except Exception as e:
        report = f"🚨 [개발부] 리포트 생성 실패\n{type(e).__name__}: {str(e)[:300]}"
        fail_count = 99
        print(report)

    print("=" * 60)
    print(report)
    print("=" * 60)

    sent = notify_safe(report)
    if sent:
        print("✅ 텔레그램 발송 성공")
    else:
        print("❌ 텔레그램 발송 실패")
        return 1

    # 구문 에러 있으면 워크플로우 빨간 X 로 알림
    if fail_count > 0:
        print(f"⚠️ 구문 에러 {fail_count}개 발견 → 워크플로우 fail 처리")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
