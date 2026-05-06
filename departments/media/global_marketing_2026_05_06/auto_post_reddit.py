#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_post_reddit.py
Reddit r/AskAstrologers Draft 1 자동 발행 시도.

⚠️ Reddit API key (.secrets에 REDDIT_*) 없으면 skip.
⚠️ 1건만 자동 발행 (다른 4건은 사용자 수동).

사용법:
    python auto_post_reddit.py --dry-run    # 미리보기
    python auto_post_reddit.py --yes        # 발행
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SECRETS = ROOT / ".secrets"

DRAFT_TITLE = "Korean Saju vs Western Astrology — anyone here familiar with both?"
DRAFT_SUBREDDIT = "AskAstrologers"
DRAFT_BODY = """I've been studying Western astrology for ~5 years (Sun/Moon/Rising basics + houses + transits).

Recently a Korean friend introduced me to "Saju" (사주) — the Korean version of the Chinese Four Pillars system.

Some things that struck me as different from Western astrology:

**1. Time-based, not space-based**
Saju uses the exact moment of birth (year/month/day/hour) → 8 characters representing 4 pillars of heaven/earth.
Western: location-based houses + planet positions.

**2. Five-Element framework instead of 12 signs**
Saju: Wood, Fire, Earth, Metal, Water — looks at WHICH element you have too much/too little of.
Western: Aries-Pisces archetypes + planetary aspects.

**3. "Ten Gods" interpretive layer**
Saju has 10 dynamic relations (Friend, Rival, Output, Wealth, Officer, Resource etc.) that map to life domains.
Closer to natal chart "houses" but more relational.

**4. Decade-cycles ("Daewoon")**
Each 10 years gets its own pillar that interacts with your natal chart — kinda like a transit but personalized.

Has anyone here practiced both? I'm finding Saju gives more concrete career/relationship advice while Western gives better psychological/spiritual depth.

(I've been using a free Korean site for the calculations — happy to share if anyone wants to compare against their own chart. Mods, please remove the link if not allowed: https://www.cheonmyeongdang.com/en/)
"""

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

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes", action="store_true")
    args = p.parse_args()

    if args.dry_run:
        print(f"=== DRY RUN ===")
        print(f"Subreddit: r/{DRAFT_SUBREDDIT}")
        print(f"Title: {DRAFT_TITLE}\n")
        print(f"Body:\n{DRAFT_BODY}")
        return 0

    if not args.yes:
        print("[ABORT] --yes required")
        return 1

    creds = load_secrets()
    required = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD"]
    missing = [k for k in required if not creds.get(k)]
    if missing:
        print(f"[SKIP] Reddit credentials missing in .secrets: {missing}")
        print(f"[SKIP] Auto-post not possible. Use the markdown drafts to post manually.")
        return 0

    try:
        import praw  # type: ignore
    except ImportError:
        print("[FAIL] praw required: pip install praw")
        return 1

    try:
        reddit = praw.Reddit(
            client_id=creds["REDDIT_CLIENT_ID"],
            client_secret=creds["REDDIT_CLIENT_SECRET"],
            username=creds["REDDIT_USERNAME"],
            password=creds["REDDIT_PASSWORD"],
            user_agent="cheonmyeongdang-marketing-bot/1.0 by " + creds["REDDIT_USERNAME"],
        )
        sub = reddit.subreddit(DRAFT_SUBREDDIT)
        post = sub.submit(title=DRAFT_TITLE, selftext=DRAFT_BODY)
        print(f"[OK] Posted: {post.url}")
        return 0
    except Exception as e:
        print(f"[FAIL] {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
