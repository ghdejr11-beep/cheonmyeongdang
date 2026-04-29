#!/usr/bin/env python3
"""
천명당 일일 운세 발송 러너 (schtasks 진입점).

매일 08:00 실행:
  1) daily_fortune_send.run_daily_send 를 daily_fortune_generator.generate_fortune 와 연결
  2) 만료 회원 자동 비활성화
  3) 로그 → logs/daily_fortune_YYYY-MM-DD.json
  4) 관리자에게 텔레그램 요약

발송 우선순위 (daily_fortune_send.send_daily_fortune):
  카카오 알림톡 → 카카오 친구톡 → 텔레그램
"""
import os, sys, json, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DEPT = Path(__file__).parent
LOG_DIR = DEPT / "logs"
LOG_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(DEPT))
from daily_fortune_generator import generate_fortune, format_message
from daily_fortune_send import run_daily_send, post_telegram, load_env, SUBSCRIBERS_PATH


def fortune_for(subscriber):
    """run_daily_send 가 호출 — (text, score) 반환"""
    today = datetime.date.today()
    f = generate_fortune(subscriber, today=today)
    text = format_message(f, name=subscriber.get("name", ""))
    # 점수: lucky_number 평균을 1~100으로 매핑 (단순 휴리스틱)
    nums = f.get("lucky_number") or []
    score = max(50, min(99, int(sum(nums[:3]) * 1.3) % 50 + 50)) if nums else 75
    return text, score


def expire_inactive(today):
    """paid_until 만료 회원 active=False 처리"""
    if not os.path.exists(SUBSCRIBERS_PATH):
        return 0
    with open(SUBSCRIBERS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    n = 0
    for sub in data.get("subscribers", []):
        pu = sub.get("paid_until", "")
        if pu and pu < today.isoformat() and sub.get("active", True):
            sub["active"] = False
            sub["expired_at"] = today.isoformat()
            n += 1
    if n:
        with open(SUBSCRIBERS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return n


def main():
    today = datetime.date.today()
    print(f"📅 {today.isoformat()} 천명당 일일 운세 발송")

    expired = expire_inactive(today)
    if expired:
        print(f"⏳ 만료 비활성화: {expired}명")

    result = run_daily_send(fortune_generator=fortune_for, dry_run=False)

    # 로그
    log_file = LOG_DIR / f"daily_fortune_{today.isoformat()}.json"
    log_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📂 로그: {log_file}")
    print(f"   성공 {result.get('sent', 0)} · 스킵 {result.get('skipped', 0)} · 실패 {result.get('failed', 0)}")

    # 관리자 요약
    env = load_env()
    admin_chat = env.get("TELEGRAM_CHAT_ID", "").strip()
    if admin_chat:
        msg = (
            f"🪷 천명당 일일 운세 {today.isoformat()}\n"
            f"성공 {result.get('sent', 0)} · 스킵 {result.get('skipped', 0)} · 실패 {result.get('failed', 0)}"
            + (f"\n만료 자동비활성: {expired}명" if expired else "")
        )
        post_telegram(admin_chat, msg, env=env)

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
