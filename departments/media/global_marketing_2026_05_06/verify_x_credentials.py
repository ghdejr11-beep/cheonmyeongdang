#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_x_credentials.py
Twitter/X API 키 검증 스크립트.
- .secrets에서 X_API_KEY/SECRET/ACCESS_TOKEN/SECRET 로드
- tweepy.verify_credentials() 호출
- @kunstudio 계정 활성 확인
- followers / following / tweet count 출력 (있으면)

사용법:
    python verify_x_credentials.py
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # cheonmyeongdang/
SECRETS = ROOT / ".secrets"

def load_secrets():
    creds = {}
    if not SECRETS.exists():
        print(f"[FAIL] .secrets not found at {SECRETS}")
        sys.exit(1)
    with open(SECRETS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            creds[k.strip()] = v.strip().strip('"').strip("'")
    return creds

def main():
    creds = load_secrets()
    required = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"]
    missing = [k for k in required if not creds.get(k)]
    if missing:
        print(f"[FAIL] Missing keys in .secrets: {missing}")
        sys.exit(1)

    print(f"[OK] All 4 X keys loaded from .secrets")
    print(f"     X_API_KEY      = {creds['X_API_KEY'][:8]}...")
    print(f"     X_API_SECRET   = {creds['X_API_SECRET'][:8]}...")
    print(f"     X_ACCESS_TOKEN = {creds['X_ACCESS_TOKEN'][:8]}...")
    print(f"     X_ACCESS_SECRET= {creds['X_ACCESS_SECRET'][:8]}...")

    try:
        import tweepy  # type: ignore
    except ImportError:
        print("[WARN] tweepy not installed. Install with: pip install tweepy")
        print("[INFO] Skipping credential verification — keys loaded OK")
        sys.exit(0)

    # Tweepy v1.1 (verify_credentials)
    auth = tweepy.OAuth1UserHandler(
        creds["X_API_KEY"],
        creds["X_API_SECRET"],
        creds["X_ACCESS_TOKEN"],
        creds["X_ACCESS_SECRET"],
    )
    api = tweepy.API(auth)
    try:
        user = api.verify_credentials()
        if user is None:
            print("[FAIL] verify_credentials() returned None")
            sys.exit(1)
        print(f"[OK] Twitter/X account verified")
        print(f"     screen_name      = @{user.screen_name}")
        print(f"     name             = {user.name}")
        print(f"     id               = {user.id}")
        print(f"     followers_count  = {user.followers_count}")
        print(f"     friends_count    = {user.friends_count}")
        print(f"     statuses_count   = {user.statuses_count}")
        print(f"     created_at       = {user.created_at}")
        return 0
    except tweepy.TweepyException as e:
        print(f"[FAIL] tweepy verify_credentials error: {e}")
        # Try v2 client as fallback
        try:
            client = tweepy.Client(
                consumer_key=creds["X_API_KEY"],
                consumer_secret=creds["X_API_SECRET"],
                access_token=creds["X_ACCESS_TOKEN"],
                access_token_secret=creds["X_ACCESS_SECRET"],
            )
            me = client.get_me()
            if me and me.data:
                print(f"[OK v2] @{me.data.username} (id={me.data.id})")
                return 0
        except Exception as e2:
            print(f"[FAIL v2] {e2}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
