"""
📊 분석부 (Analytics Team)

매일 23:00 KST 자동 실행 (GitHub Actions cron).
역할:
  1. 환경 자가 진단 (API 키, 토큰, 의존성)
  2. 어제 작업 결과 요약 (git log 기준 — 1차 버전)
  3. Claude 에게 짧은 인사이트 요청
  4. 텔레그램으로 일일 리포트 발송

추후 확장 (TODO):
  - YouTube Data API 로 어제 영상 조회수 수집
  - Gumroad API 로 매출 가져오기
  - 사주 SaaS Render 헬스체크
  - Google Calendar 에서 [분석부] 이벤트 우선 처리
  - 100일 10억 진행률 계산

실행:
  python scripts/teams/analytics_team.py
환경변수:
  ANTHROPIC_API_KEY    - Claude API
  TELEGRAM_BOT_TOKEN   - 봇 토큰
  TELEGRAM_CHAT_ID     - 알림 받을 chat id
"""

import os
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

# scripts/ 가 PYTHONPATH 에 없을 때 대비
SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from scripts.lib.telegram_notify import notify_safe, TelegramNotifyError


KST = timezone(timedelta(hours=9))


def now_kst_str() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")


def env_check() -> dict:
    """필수 환경 자가 진단."""
    return {
        "ANTHROPIC_API_KEY": bool((os.environ.get("ANTHROPIC_API_KEY") or "").strip()),
        "TELEGRAM_BOT_TOKEN": bool((os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()),
        "TELEGRAM_CHAT_ID": bool((os.environ.get("TELEGRAM_CHAT_ID") or "").strip()),
        "python_version": sys.version.split()[0],
        "cwd": os.getcwd(),
    }


def yesterday_git_summary() -> str:
    """어제 commit 들을 가져와서 한 줄씩 요약."""
    try:
        result = subprocess.run(
            ["git", "log", "--since=24 hours ago", "--pretty=format:%h %s", "-20"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(SCRIPT_DIR), timeout=10,
        )
        if result.returncode != 0:
            return "(git log 실패)"
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        if not lines:
            return "(어제 commit 없음)"
        return "\n".join(f"  • {line}" for line in lines[:10])
    except Exception as e:
        return f"(git 조회 에러: {e})"


def claude_insight(env: dict, git_summary: str) -> str:
    """Claude 에게 짧은 인사이트 요청.
    실패하면 fallback 메시지 반환.
    """
    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        return "(Claude API 키 없음 — 인사이트 생략)"

    try:
        import anthropic
    except ImportError:
        return "(anthropic 패키지 미설치 — pip install anthropic 필요)"

    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""너는 덕구네 AI 사업단의 분석부 책임자다.
오늘 새벽 분석부 첫 가동 테스트야. 다음 정보를 보고 **3문장** 으로 짧게 인사이트를 줘:

[환경 체크]
- ANTHROPIC_API_KEY: {'OK' if env['ANTHROPIC_API_KEY'] else 'MISSING'}
- TELEGRAM_BOT_TOKEN: {'OK' if env['TELEGRAM_BOT_TOKEN'] else 'MISSING'}
- TELEGRAM_CHAT_ID: {'OK' if env['TELEGRAM_CHAT_ID'] else 'MISSING'}
- Python: {env['python_version']}

[어제 commit 요약]
{git_summary}

[배경]
사용자는 100일 안에 10억 매출 달성이 목표. 사주 AI SaaS, AI 음악 YouTube,
전자책, 멘토봇 등 다각화된 프로젝트 운영 중.

요구사항:
1. 환경 자가 진단 결과 1문장 (정상/문제)
2. 어제 작업 인사이트 1문장 (방향성)
3. 내일 우선순위 추천 1문장
한국어, 친근한 톤, 이모지 OK."""

        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in msg.content if hasattr(b, "text"))
    except Exception as e:
        return f"(Claude 호출 실패: {type(e).__name__}: {str(e)[:120]})"


def build_report() -> str:
    env = env_check()
    git = yesterday_git_summary()
    insight = claude_insight(env, git)

    env_lines = []
    for key in ["ANTHROPIC_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]:
        mark = "✅" if env[key] else "❌"
        env_lines.append(f"  {mark} {key}")

    report = f"""🤖 [분석부] 일일 리포트
🕒 {now_kst_str()}

━━━━━━━━━━━━━━━━━━━
📋 환경 자가 진단
{chr(10).join(env_lines)}
  Python {env['python_version']}

━━━━━━━━━━━━━━━━━━━
📝 최근 24시간 commit
{git}

━━━━━━━━━━━━━━━━━━━
💡 분석부 인사이트
{insight}

━━━━━━━━━━━━━━━━━━━
🎯 100일 10억 진행률
(다음 버전에서 YouTube/Gumroad/사주 SaaS 데이터 자동 수집 예정)

다음 자동 실행: 매일 23:00 KST"""

    return report


def main() -> int:
    print(f"[분석부] 시작 {now_kst_str()}")

    try:
        report = build_report()
    except Exception as e:
        report = f"🚨 [분석부] 리포트 생성 실패\n{type(e).__name__}: {str(e)[:300]}"
        print(report)

    print("=" * 60)
    print(report)
    print("=" * 60)

    sent = notify_safe(report)
    if sent:
        print("✅ 텔레그램 발송 성공")
        return 0
    else:
        print("❌ 텔레그램 발송 실패 (위 로그 참고)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
