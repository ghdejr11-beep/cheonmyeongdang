#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
morning_post_twitter.py
@deokgune_ai 매일 10:00 1 draft 자동 발행 (5일 순환).

동작:
  1) departments/media/global_marketing_2026_05_06/twitter_jp_drafts.json 로드
  2) 아직 발행 안 한 가장 낮은 id 1건 발행 (thread = 다중 reply / single = 1tweet)
  3) 발행 후 logs/twitter_posted_<id>.json 기록
  4) 5 drafts 모두 소진 시: telegram 알림 + 새 drafts 자동 생성 시도
     (Anthropic API 키 있으면 — K-pop 멤버 실명 X 정책 강제)

사용법:
  python scripts/morning_post_twitter.py --dry-run        # 다음 발행 예정 미리보기
  python scripts/morning_post_twitter.py                  # 실 발행
  python scripts/morning_post_twitter.py --reset          # 발행 이력 초기화 (디버그)

schtask 등록:
  schtasks /Create /SC DAILY /ST 10:00 ^
    /TN "KunStudio_Twitter_Daily" ^
    /TR "python C:\\Users\\hdh02\\Desktop\\cheonmyeongdang\\scripts\\morning_post_twitter.py" /F
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# UTF-8 stdout (Windows)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SECRETS = ROOT / ".secrets"

DRAFTS_FILE = (
    ROOT / "departments" / "media" / "global_marketing_2026_05_06"
    / "twitter_jp_drafts.json"
)
LOGS_DIR = ROOT / "logs"
STATE_FILE = LOGS_DIR / "twitter_post_state.json"


def load_secrets() -> dict[str, str]:
    out: dict[str, str] = {}
    if not SECRETS.exists():
        return out
    with open(SECRETS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def telegram_alert(msg: str) -> None:
    creds = load_secrets()
    token = creds.get("TELEGRAM_BOT_TOKEN")
    chat = creds.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return
    try:
        data = urllib.parse.urlencode(
            {"chat_id": chat, "text": msg, "disable_web_page_preview": "true"}
        ).encode()
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        req = urllib.request.Request(url, data=data, method="POST")
        urllib.request.urlopen(req, timeout=10).read()
    except Exception:
        pass


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posted_ids": [], "history": []}


def save_state(state: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_drafts() -> dict:
    if not DRAFTS_FILE.exists():
        raise FileNotFoundError(f"drafts not found: {DRAFTS_FILE}")
    return json.loads(DRAFTS_FILE.read_text(encoding="utf-8"))


def pick_next_draft(data: dict, state: dict) -> dict | None:
    posted = set(state.get("posted_ids", []))
    candidates = [t for t in data["tweets"] if t["id"] not in posted]
    if not candidates:
        return None
    return min(candidates, key=lambda t: t["id"])


def post_draft(target: dict, dry_run: bool = False) -> tuple[bool, list[str], str]:
    """Returns (ok, posted_tweet_ids, error_msg)."""
    if dry_run:
        print(f"\n[DRY-RUN] Draft #{target['id']}: {target['title']} "
              f"({target['type']})")
        for i, tw in enumerate(target["tweets"], 1):
            print(f"\n--- Tweet {i}/{len(target['tweets'])} ({len(tw)} chars) ---")
            print(tw)
        return True, [], ""

    creds = load_secrets()
    required = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"]
    missing = [k for k in required if not creds.get(k)]
    if missing:
        return False, [], f"X credentials missing: {missing}"

    try:
        import tweepy  # type: ignore
    except ImportError:
        return False, [], "tweepy not installed (pip install tweepy)"

    client = tweepy.Client(
        consumer_key=creds["X_API_KEY"],
        consumer_secret=creds["X_API_SECRET"],
        access_token=creds["X_ACCESS_TOKEN"],
        access_token_secret=creds["X_ACCESS_SECRET"],
    )

    print(f"[POST] Draft #{target['id']}: {target['title']}")
    last_id = None
    posted_ids: list[str] = []
    for i, tw in enumerate(target["tweets"], 1):
        try:
            kwargs: dict = {"text": tw}
            if last_id and target["type"] == "thread":
                kwargs["in_reply_to_tweet_id"] = last_id
            resp = client.create_tweet(**kwargs)
            tid = str(resp.data["id"])
            posted_ids.append(tid)
            last_id = tid
            print(f"  [OK {i}/{len(target['tweets'])}] tweet_id={tid}")
            time.sleep(2)  # rate limit
        except Exception as e:
            err = f"tweet {i}/{len(target['tweets'])}: {type(e).__name__}: {e}"
            print(f"  [FAIL] {err}")
            return False, posted_ids, err
    return True, posted_ids, ""


def write_post_log(target: dict, posted_ids: list[str], ok: bool, error: str) -> Path:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"twitter_posted_{target['id']}_{ts}.json"
    log_path.write_text(
        json.dumps({
            "ok": ok,
            "draft_id": target["id"],
            "title": target["title"],
            "type": target["type"],
            "tweet_count": len(target["tweets"]),
            "posted_tweet_ids": posted_ids,
            "error": error,
            "posted_at": datetime.now().isoformat(),
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return log_path


def try_generate_new_drafts() -> bool:
    """5 drafts 소진 후 Claude API 로 새 drafts 생성 (best-effort)."""
    creds = load_secrets()
    api_key = creds.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return False
    # 정책: K-pop 멤버 실명 / Samsung / Squid Game 등 거론 X
    policy = (
        "정책 제약: 특정 K-pop 멤버 실명, Samsung, BTS, Squid Game 등 "
        "특정 업체·연예인·IP 거론 절대 금지. 일반화('한국 대기업', "
        "'top K-pop group') 표현 사용. 천명당 본인 제품은 OK."
    )
    prompt = f"""@deokgune_ai 일본어 트위터용 5 drafts 새로 생성 (twitter_jp_drafts.json 동일 schema).
- 타겟: 일본 K-wave/한국 점성술 관심층
- 톤: 친근, 정보성, CTA: https://www.cheonmyeongdang.com/ja/
- 각 트윗 280자 이하 (일본어 카운팅 주의)
- thread / single / single_set 혼합
- {policy}

JSON 형식으로만 응답하세요. 마크다운 fence X."""
    try:
        body = json.dumps({
            "model": "claude-haiku-4-5",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read())
        text = resp.get("content", [{}])[0].get("text", "")
        # JSON 추출
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < 0:
            return False
        new_data = json.loads(text[start:end + 1])
        if "tweets" not in new_data:
            return False
        # id 충돌 방지: 기존 id + 100
        for i, t in enumerate(new_data["tweets"], 1):
            t["id"] = 100 + i
        # 백업 후 덮어쓰기
        backup = DRAFTS_FILE.with_suffix(".json.bak")
        backup.write_bytes(DRAFTS_FILE.read_bytes())
        # 기존 drafts 와 합치기 (history 보존용 X — 단순 교체)
        existing = json.loads(DRAFTS_FILE.read_text(encoding="utf-8"))
        existing["tweets"] = new_data["tweets"]
        existing["regenerated_at"] = datetime.now().isoformat()
        DRAFTS_FILE.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    except Exception as e:
        print(f"  [WARN] new drafts gen failed: {e}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="다음 발행 예정 draft 미리보기 (실 발행 X)")
    ap.add_argument("--reset", action="store_true",
                    help="발행 이력 초기화 (디버그용)")
    args = ap.parse_args()

    print("=" * 60)
    print(f"Twitter daily post — {datetime.now().isoformat()}")
    print("=" * 60)

    if args.reset:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        print("[RESET] state cleared")
        return 0

    state = load_state()
    try:
        data = load_drafts()
    except FileNotFoundError as e:
        print(f"[FAIL] {e}")
        telegram_alert(f"[Twitter] drafts 파일 없음: {DRAFTS_FILE.name}")
        return 1

    target = pick_next_draft(data, state)
    if target is None:
        print(f"[INFO] 모든 drafts 발행 완료 (posted={state['posted_ids']})")
        if args.dry_run:
            return 0
        # 새 drafts 생성 시도
        if try_generate_new_drafts():
            print("[REGEN] 새 drafts 생성 완료 — state 초기화")
            state = {"posted_ids": [], "history": state.get("history", [])}
            save_state(state)
            data = load_drafts()
            target = pick_next_draft(data, state)
            telegram_alert(
                "[Twitter] 5 drafts 소진 → 새 drafts 자동 생성 완료. "
                "재발행 시작."
            )
        else:
            telegram_alert(
                "[Twitter] 모든 drafts 발행 완료. 새 drafts 수동 생성 필요. "
                f"파일: {DRAFTS_FILE.name}"
            )
            return 0

    if target is None:
        print("[INFO] 발행 가능한 draft 없음")
        return 0

    # 발행
    ok, posted_ids, err = post_draft(target, dry_run=args.dry_run)

    if args.dry_run:
        return 0

    log_path = write_post_log(target, posted_ids, ok, err)
    print(f"  [LOG] {log_path}")

    if ok:
        state.setdefault("posted_ids", []).append(target["id"])
        state.setdefault("history", []).append({
            "draft_id": target["id"],
            "title": target["title"],
            "posted_at": datetime.now().isoformat(),
            "tweet_ids": posted_ids,
        })
        save_state(state)
        telegram_alert(
            f"[Twitter] Draft #{target['id']} 발행 완료\n"
            f"제목: {target['title']}\n"
            f"트윗 수: {len(posted_ids)}\n"
            f"첫 tweet_id: {posted_ids[0] if posted_ids else 'N/A'}"
        )
        return 0
    else:
        telegram_alert(
            f"[Twitter 발행 실패] Draft #{target['id']}\n"
            f"제목: {target['title']}\n"
            f"오류: {err}\n"
            f"부분 발행 ID: {posted_ids}"
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
