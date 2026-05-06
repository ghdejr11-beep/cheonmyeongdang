#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_post_x_jp.py
Twitter/X 일본어 5 draft 자동 발행 스크립트 (manual confirm 필요).

⚠️ 주의:
- Twitter 정책상 대량 자동 발행은 spam 판정 RISK 높음.
- 1일 1건씩, 5일에 걸쳐 발행 권장.
- 사용자 confirm 후 실행 (--yes 플래그 필요).

사용법:
    python auto_post_x_jp.py --list                  # draft 목록 보기
    python auto_post_x_jp.py --tweet 1 --dry-run     # draft #1 미리보기
    python auto_post_x_jp.py --tweet 1 --yes         # draft #1 발행 (확인 필요)
    python auto_post_x_jp.py --all --yes --schedule  # 5일 스케줄 (1일 1건)

권장: 사용자가 Twitter 웹에서 직접 1클릭 발행.
"""
from __future__ import annotations
import argparse
import io
import json
import sys
import time
from pathlib import Path

# Force UTF-8 stdout (Windows cp949 fix)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SECRETS = ROOT / ".secrets"
DRAFTS = HERE / "twitter_jp_drafts.json"

def load_secrets():
    creds = {}
    if not SECRETS.exists():
        return creds
    with open(SECRETS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            creds[k.strip()] = v.strip().strip('"').strip("'")
    return creds

def load_drafts():
    if not DRAFTS.exists():
        print(f"[FAIL] {DRAFTS} not found")
        sys.exit(1)
    with open(DRAFTS, "r", encoding="utf-8") as f:
        return json.load(f)

def cmd_list(data):
    print(f"=== Twitter/X 일본어 Drafts (account: {data['account']}) ===\n")
    for t in data["tweets"]:
        n = len(t["tweets"])
        print(f"  [{t['id']}] {t['type']:10s} ({n} tweet{'s' if n>1 else ''}) — {t['title']}")
        print(f"        publish_recommend: {t['publish_date_recommend']}")
    print(f"\nTotal: {len(data['tweets'])} drafts")

def cmd_dry_run(data, tweet_id):
    target = next((t for t in data["tweets"] if t["id"] == tweet_id), None)
    if not target:
        print(f"[FAIL] Draft #{tweet_id} not found")
        sys.exit(1)
    print(f"=== Draft #{tweet_id}: {target['title']} ({target['type']}) ===\n")
    for i, tweet in enumerate(target["tweets"], 1):
        print(f"--- Tweet {i}/{len(target['tweets'])} ---")
        print(tweet)
        print(f"[length: {len(tweet)} chars]\n")

def cmd_post(data, tweet_id, confirmed=False):
    if not confirmed:
        print("[ABORT] --yes flag required to actually post")
        sys.exit(1)
    creds = load_secrets()
    required = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"]
    if any(not creds.get(k) for k in required):
        print("[FAIL] X credentials missing in .secrets")
        sys.exit(1)
    try:
        import tweepy  # type: ignore
    except ImportError:
        print("[FAIL] tweepy required: pip install tweepy")
        sys.exit(1)

    target = next((t for t in data["tweets"] if t["id"] == tweet_id), None)
    if not target:
        print(f"[FAIL] Draft #{tweet_id} not found")
        sys.exit(1)

    client = tweepy.Client(
        consumer_key=creds["X_API_KEY"],
        consumer_secret=creds["X_API_SECRET"],
        access_token=creds["X_ACCESS_TOKEN"],
        access_token_secret=creds["X_ACCESS_SECRET"],
    )

    print(f"[POST] Draft #{tweet_id}: {target['title']}")
    last_id = None
    for i, tweet in enumerate(target["tweets"], 1):
        try:
            kwargs = {"text": tweet}
            if last_id and target["type"] == "thread":
                kwargs["in_reply_to_tweet_id"] = last_id
            resp = client.create_tweet(**kwargs)
            tid = resp.data["id"]
            last_id = tid
            print(f"  [OK {i}/{len(target['tweets'])}] tweet_id={tid}")
            time.sleep(2)  # rate limit
        except Exception as e:
            print(f"  [FAIL {i}/{len(target['tweets'])}] {e}")
            return False
    print(f"[DONE] Draft #{tweet_id} posted successfully")
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true", help="List all drafts")
    p.add_argument("--tweet", type=int, help="Tweet draft ID (1-5)")
    p.add_argument("--dry-run", action="store_true", help="Preview only")
    p.add_argument("--yes", action="store_true", help="Confirm post")
    p.add_argument("--all", action="store_true", help="Post all drafts (5-day schedule)")
    p.add_argument("--schedule", action="store_true", help="Sleep 24h between drafts")
    args = p.parse_args()

    data = load_drafts()

    if args.list or (not args.tweet and not args.all):
        cmd_list(data)
        return 0

    if args.tweet:
        if args.dry_run:
            cmd_dry_run(data, args.tweet)
            return 0
        cmd_post(data, args.tweet, confirmed=args.yes)
        return 0

    if args.all:
        if not args.yes:
            print("[ABORT] --yes flag required")
            return 1
        for t in data["tweets"]:
            cmd_post(data, t["id"], confirmed=True)
            if args.schedule and t["id"] < len(data["tweets"]):
                print(f"[SLEEP] 24h until next draft...")
                time.sleep(86400)
        return 0

    return 0

if __name__ == "__main__":
    sys.exit(main())
