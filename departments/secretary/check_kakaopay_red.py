"""5/7 RED 우선 — 카카오페이 심사 보완 메일 본문 확인."""
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

# RED 메일 본문 fetch
queries = {
    'kakaopay': 'from:jella.tto@kakaopaycorp.com newer_than:2d',
    'naverpay': 'from:naverpayadmin_noreply@navercorp.com newer_than:2d',
    'kakao_any': 'kakao newer_than:1d',
    'vc_any': 'ventures OR vc.com newer_than:2d',
    'investor_any': 'subject:천명당 OR subject:사주 newer_than:2d -from:ghdejr11',
}

for label, q in queries.items():
    print(f'\n========== {label}: {q} ==========')
    res = svc.users().messages().list(userId='me', q=q, maxResults=5).execute()
    msgs = res.get('messages', [])
    print(f'hits: {len(msgs)}')
    for m in msgs:
        full = svc.users().messages().get(userId='me', id=m['id'], format='full').execute()
        headers = {h['name'].lower(): h['value'] for h in full['payload'].get('headers', [])}
        body_buf = []
        def extract(p):
            if p.get('body', {}).get('data'):
                try:
                    body_buf.append(base64.urlsafe_b64decode(p['body']['data'] + '==').decode('utf-8', errors='replace'))
                except Exception:
                    pass
            for sub in p.get('parts', []) or []:
                extract(sub)
        extract(full['payload'])
        body = ''.join(body_buf)
        print(f"\n  FROM: {headers.get('from','')}")
        print(f"  TO:   {headers.get('to','')}")
        print(f"  SUBJ: {headers.get('subject','')}")
        print(f"  DATE: {headers.get('date','')}")
        print(f"  ID:   {m['id']} / Thread: {full.get('threadId')}")
        print(f"  LABELS: {full.get('labelIds',[])}")
        print(f"  --- BODY (first 2000 chars) ---")
        # Strip HTML rough
        import re
        text = re.sub(r'<[^>]+>', ' ', body)
        text = re.sub(r'\s+', ' ', text).strip()
        print(f"  {text[:2000]}")
