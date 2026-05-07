#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
morning_post_twitter.py
@deokgune_ai 매일 10:00 1 draft 자동 발행 (30 drafts × 30일 cycle).

동작:
  1) departments/media/global_marketing_2026_05_06/twitter_drafts_v2_30.json 로드
  2) logs/twitter_state.json 의 last_posted_index 다음 draft 발행
  3) 발행 후 state 업데이트, 30개 모두 소진 시 처음으로 cycle
  4) 403 duplicate content 발생 시 다음 index 자동 retry (최대 3회)

draft 형식 (v2_30):
  - type=thread: hook → body[0..N-1] → 마지막 reply 에 cta+hashtags
  - type=single: hook 단일 트윗, hashtags 마지막 줄에 추가

사용법:
  python scripts/morning_post_twitter.py --dry-run        # 다음 발행 예정 미리보기
  python scripts/morning_post_twitter.py                  # 실 발행
  python scripts/morning_post_twitter.py --reset          # state 초기화 (디버그)
  python scripts/morning_post_twitter.py --index N        # 특정 index 강제 (디버그)

schtask:
  KunStudio_Twitter_Daily — 매일 10:00 자동 실행
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
    / "twitter_drafts_v2_30.json"
)
LOGS_DIR = ROOT / "logs"
STATE_FILE = LOGS_DIR / "twitter_state.json"

MAX_DUPLICATE_RETRIES = 3
TWEET_MAX_LEN = 280


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
    # 첫 실행: -1 → 다음 index 0 부터
    return {
        "last_posted_index": -1,
        "cycle_count": 0,
        "history": [],
        "skipped_duplicates": [],
    }


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


def build_tweets(draft: dict) -> list[str]:
    """draft → 발행할 트윗 list 생성 (hook + body + cta+hashtags)."""
    tweets: list[str] = []
    hook = (draft.get("hook") or "").strip()
    body = draft.get("body") or []
    cta = (draft.get("cta") or "").strip()
    tags = draft.get("hashtags") or []
    tag_line = " ".join(tags) if tags else ""

    if draft.get("type") == "single" or not body:
        # 단일 트윗: hook + (hashtags 가능 시 줄바꿈으로)
        text = hook
        if tag_line and (len(text) + 2 + len(tag_line)) <= TWEET_MAX_LEN:
            text = f"{text}\n\n{tag_line}"
        tweets.append(text[:TWEET_MAX_LEN])
        return tweets

    # thread
    tweets.append(hook[:TWEET_MAX_LEN])
    for b in body:
        tweets.append(b[:TWEET_MAX_LEN])
    # 마지막 reply: cta + hashtags
    closer_parts: list[str] = []
    if cta:
        closer_parts.append(cta)
    if tag_line:
        closer_parts.append(tag_line)
    if closer_parts:
        closer = "\n\n".join(closer_parts)
        tweets.append(closer[:TWEET_MAX_LEN])
    return tweets


def get_draft_at(data: dict, index: int) -> dict:
    drafts = data.get("drafts") or data.get("tweets") or []
    return drafts[index]


def total_drafts(data: dict) -> int:
    drafts = data.get("drafts") or data.get("tweets") or []
    return len(drafts)


def is_duplicate_error(err: str) -> bool:
    e = (err or "").lower()
    return "duplicate content" in e or "duplicate" in e and "403" in e


def post_draft(
    draft: dict,
    dry_run: bool = False,
) -> tuple[bool, list[str], str]:
    """Returns (ok, posted_tweet_ids, error_msg)."""
    tweets = build_tweets(draft)
    if dry_run:
        print(f"\n[DRY-RUN] Draft #{draft['id']}: {draft.get('title','')} "
              f"({draft.get('type','?')}, lang={draft.get('language','?')})")
        for i, tw in enumerate(tweets, 1):
            print(f"\n--- Tweet {i}/{len(tweets)} ({len(tw)} chars) ---")
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

    print(f"[POST] Draft #{draft['id']}: {draft.get('title','')}")
    last_id = None
    posted_ids: list[str] = []
    is_thread = draft.get("type") != "single" and len(tweets) > 1
    for i, tw in enumerate(tweets, 1):
        try:
            kwargs: dict = {"text": tw}
            if last_id and is_thread:
                kwargs["in_reply_to_tweet_id"] = last_id
            resp = client.create_tweet(**kwargs)
            tid = str(resp.data["id"])
            posted_ids.append(tid)
            last_id = tid
            print(f"  [OK {i}/{len(tweets)}] tweet_id={tid}")
            time.sleep(2)  # rate limit
        except Exception as e:
            err = f"tweet {i}/{len(tweets)}: {type(e).__name__}: {e}"
            print(f"  [FAIL] {err}")
            return False, posted_ids, err
    return True, posted_ids, ""


def write_post_log(
    draft: dict,
    posted_ids: list[str],
    ok: bool,
    error: str,
    index_used: int,
) -> Path:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"twitter_posted_{draft['id']}_{ts}.json"
    log_path.write_text(
        json.dumps({
            "ok": ok,
            "draft_id": draft["id"],
            "draft_index": index_used,
            "title": draft.get("title", ""),
            "type": draft.get("type", ""),
            "language": draft.get("language", ""),
            "posted_tweet_ids": posted_ids,
            "error": error,
            "posted_at": datetime.now().isoformat(),
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return log_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="다음 발행 예정 draft 미리보기 (실 발행 X)")
    ap.add_argument("--reset", action="store_true",
                    help="state 초기화 (디버그용)")
    ap.add_argument("--index", type=int, default=None,
                    help="특정 draft index 강제 (0-based, 디버그용)")
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

    total = total_drafts(data)
    if total == 0:
        print("[FAIL] drafts 비어있음")
        return 1

    last = state.get("last_posted_index", -1)
    if args.index is not None:
        start = args.index % total
    else:
        start = (last + 1) % total

    # duplicate 발생 시 자동 next index retry
    attempted: list[int] = []
    final_ok = False
    final_posted_ids: list[str] = []
    final_err = ""
    final_index = -1
    final_draft: dict = {}

    for retry in range(MAX_DUPLICATE_RETRIES):
        idx = (start + retry) % total
        draft = get_draft_at(data, idx)
        attempted.append(idx)
        print(f"\n[ATTEMPT {retry+1}/{MAX_DUPLICATE_RETRIES}] index={idx} "
              f"(draft id={draft['id']}, total={total})")
        ok, posted_ids, err = post_draft(draft, dry_run=args.dry_run)

        if args.dry_run:
            return 0

        log_path = write_post_log(draft, posted_ids, ok, err, idx)
        print(f"  [LOG] {log_path}")

        final_ok = ok
        final_posted_ids = posted_ids
        final_err = err
        final_index = idx
        final_draft = draft

        if ok:
            break
        if is_duplicate_error(err) and not posted_ids:
            # 깔끔한 duplicate (아무것도 못 보냄) → 다음 index 시도
            state.setdefault("skipped_duplicates", []).append({
                "index": idx,
                "draft_id": draft["id"],
                "at": datetime.now().isoformat(),
            })
            print(f"  [SKIP] duplicate → next index 재시도")
            continue
        # 다른 종류의 실패 또는 부분 발행 → 중단
        break

    # state 업데이트
    if final_ok:
        state["last_posted_index"] = final_index
        if final_index == total - 1:
            state["cycle_count"] = state.get("cycle_count", 0) + 1
            print(f"  [CYCLE] {state['cycle_count']}회 완료, 다음은 처음부터")
        state.setdefault("history", []).append({
            "index": final_index,
            "draft_id": final_draft["id"],
            "title": final_draft.get("title", ""),
            "language": final_draft.get("language", ""),
            "posted_at": datetime.now().isoformat(),
            "tweet_ids": final_posted_ids,
            "attempts": attempted,
        })
        save_state(state)
        telegram_alert(
            f"[Twitter] Draft #{final_draft['id']} (idx {final_index}) 발행 완료\n"
            f"제목: {final_draft.get('title','')}\n"
            f"언어: {final_draft.get('language','')}\n"
            f"트윗 수: {len(final_posted_ids)}\n"
            f"첫 tweet_id: {final_posted_ids[0] if final_posted_ids else 'N/A'}\n"
            f"시도 indices: {attempted}"
        )
        return 0
    else:
        # 실패해도 duplicate skip은 state 에 반영
        save_state(state)
        telegram_alert(
            f"[Twitter 발행 실패] Draft #{final_draft.get('id','?')} "
            f"(idx {final_index})\n"
            f"제목: {final_draft.get('title','')}\n"
            f"오류: {final_err}\n"
            f"부분 발행 ID: {final_posted_ids}\n"
            f"시도 indices: {attempted}"
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
