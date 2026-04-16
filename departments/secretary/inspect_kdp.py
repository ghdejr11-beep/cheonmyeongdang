#!/usr/bin/env python3
"""KDP 메일 내용 확인 — 거절 키워드 파악용"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from secretary import authenticate, fetch_recent_emails, classify_email

service = authenticate()
emails = fetch_recent_emails(service, hours=168, max_results=100)  # 7일간

for email in emails:
    meta = classify_email(email)
    if meta['partner'] == 'KDP (Amazon)':
        print("=" * 60)
        print(f"제목: {email['subject']}")
        print(f"발신: {email['from']}")
        print(f"본문 미리보기:")
        print(email['body'][:800])
        print()
