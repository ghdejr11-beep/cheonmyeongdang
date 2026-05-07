"""Bounce 메일 상세 확인 (2026-05-07)."""
import os, sys, json, base64
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.path.join(SCRIPT_DIR, 'token.json')

def load_service():
    with open(TOKEN, 'r', encoding='utf-8') as f:
        data = json.load(f)
    creds = Credentials(
        token=data.get('token'),
        refresh_token=data.get('refresh_token'),
        token_uri=data.get('token_uri'),
        client_id=data.get('client_id'),
        client_secret=data.get('client_secret'),
        scopes=data.get('scopes'),
    )
    return build('gmail', 'v1', credentials=creds)


def walk_text(payload, parts):
    mt = payload.get('mimeType', '')
    body = payload.get('body', {})
    if mt.startswith('text/'):
        d = body.get('data')
        if d:
            try:
                txt = base64.urlsafe_b64decode(d).decode('utf-8', errors='replace')
                parts.append((mt, txt))
            except Exception:
                pass
    for sub in payload.get('parts', []) or []:
        walk_text(sub, parts)


def main():
    svc = load_service()
    res = svc.users().messages().list(
        userId='me',
        q='from:mailer-daemon newer_than:2d',
        maxResults=10,
    ).execute()
    msgs = res.get('messages', [])
    print(f'[BOUNCES] {len(msgs)}건')
    for m in msgs:
        full = svc.users().messages().get(userId='me', id=m['id'], format='full').execute()
        headers = {h['name']: h['value'] for h in full['payload']['headers']}
        print('=' * 80)
        print(f'  Date: {headers.get("Date")}')
        print(f'  Subject: {headers.get("Subject")}')
        parts = []
        walk_text(full['payload'], parts)
        plain = next((t for mt, t in parts if mt == 'text/plain'), None)
        if not plain and parts:
            plain = parts[0][1]
        if plain:
            print('--- BODY ---')
            print(plain[:2000])

if __name__ == '__main__':
    main()
