"""[DEPRECATED 5/7] KoDATA 단일 키워드 모니터.

⚠️ 5/6 RCA: 이 스크립트는 print만 있고 텔레그램 alert 코드가 없어서
KoDATA 5/6 09:24 회신을 사용자에게 알리지 못했음.
→ inbox_monitor_unified.py로 통합 (5분 주기 + telegram push 강제).

이 파일은 호환성으로 남아있으나, schtask는 KunStudio_Inbox_Monitor_Unified로
교체됨. 신규 키워드 추가는 inbox_monitor_unified.py의 RED_FROM_DOMAINS/
RED_SUBJECT_KEYWORDS에 추가할 것.
"""
import os, json, sys, datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_READ = os.path.join(SCRIPT_DIR, 'token.json')
STATE_FILE = os.path.join(SCRIPT_DIR, 'kodata_monitor_state.json')

def load_service():
    with open(TOKEN_READ, 'r', encoding='utf-8') as f:
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

def main():
    svc = load_service()
    res = svc.users().messages().list(
        userId='me',
        q='from:kodata.co.kr OR from:find@kodata.co.kr OR subject:기업정보등록',
        maxResults=10,
    ).execute()
    msgs = res.get('messages', [])
    if not msgs:
        print('[NONE] no kodata replies yet')
        return

    seen = set()
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            seen = set(json.load(f).get('seen', []))

    new = [m['id'] for m in msgs if m['id'] not in seen]
    if new:
        for mid in new:
            full = svc.users().messages().get(
                userId='me', id=mid, format='metadata',
                metadataHeaders=['From','Subject','Date'],
            ).execute()
            headers = {h['name']: h['value'] for h in full['payload']['headers']}
            print(f'[NEW] {headers.get("Date")} | {headers.get("From")} | {headers.get("Subject")}')

    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'seen': list(seen | set(m['id'] for m in msgs)),
                   'last_check': datetime.datetime.now().isoformat()}, f)

if __name__ == '__main__':
    main()
