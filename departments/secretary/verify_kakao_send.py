"""5/7 09:00 schtask로 발송됐다는 카카오 벤처스 cold email 발송 여부 검증."""
import os
import sys
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_READ = os.path.join(SCRIPT_DIR, 'token.json')

creds = Credentials.from_authorized_user_file(TOKEN_READ)
svc = build('gmail', 'v1', credentials=creds)

# 5/7 발송됐다는 모든 메일 검색
queries = [
    'in:sent newer_than:1d',
    'in:sent subject:"천명당" newer_than:2d',
    'in:sent kakao newer_than:7d',
    'in:sent ventures newer_than:7d',
    'in:sent vc newer_than:2d',
    'in:sent newer_than:2d to:kakao',
]

for q in queries:
    print(f'\n=== {q} ===')
    try:
        res = svc.users().messages().list(userId='me', q=q, maxResults=20).execute()
        msgs = res.get('messages', [])
        print(f'  → {len(msgs)} hit(s)')
        for m in msgs[:10]:
            full = svc.users().messages().get(userId='me', id=m['id'], format='metadata').execute()
            headers = {h['name'].lower(): h['value'] for h in full['payload'].get('headers', [])}
            print(f"    {headers.get('date','')[:25]} | TO:{headers.get('to','')[:50]} | {headers.get('subject','')[:60]}")
    except Exception as e:
        print(f'  ERROR: {e}')
