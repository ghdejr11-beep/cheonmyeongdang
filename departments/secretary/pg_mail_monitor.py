#!/usr/bin/env python3
"""
PG 메일 모니터링 — [REDACTED](갤럭시아), 한국결제네트웍스, 카카오페이, 빌게이트
매시간 Gmail 새 메일 확인 후 텔레그램 알림
"""
import os, sys, json, requests, base64
from email.utils import parseaddr
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
SECRETS = {}
for line in open(os.path.join(ROOT, '.secrets'), encoding='utf-8'):
    if '=' in line and not line.strip().startswith('#'):
        k, v = line.split('=', 1)
        SECRETS[k.strip()] = v.strip()

GMAIL_REFRESH = SECRETS.get('GMAIL_REFRESH_TOKEN', '')
GMAIL_CLIENT_ID = SECRETS.get('GOOGLE_CLIENT_ID', '')
GMAIL_CLIENT_SECRET = SECRETS.get('GOOGLE_CLIENT_SECRET', '')
TG_TOKEN = SECRETS.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = SECRETS.get('TELEGRAM_CHAT_ID', '')

PG_KEYWORDS = [
    '갤럭시아', '[REDACTED]', '빌게이트', 'BillGate', 'galaxia',
    '한국결제네트웍스', 'KCN', '카카오페이 가맹점', '카카오페이 심사',
    '포트원', 'PortOne', 'pgs@portone', '입점심사', 'CID 발급',
    'TossPayments', '토스페이먼츠 검토', '토스페이먼츠 라이브'
]

STATE_FILE = os.path.join(os.path.dirname(__file__), 'pg_mail_state.json')

def get_access_token():
    if not GMAIL_REFRESH: return None
    r = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': GMAIL_CLIENT_ID,
        'client_secret': GMAIL_CLIENT_SECRET,
        'refresh_token': GMAIL_REFRESH,
        'grant_type': 'refresh_token',
    }, timeout=10)
    return r.json().get('access_token') if r.ok else None

def list_recent_pg_mails():
    token = get_access_token()
    if not token: return []
    state = {}
    if os.path.exists(STATE_FILE):
        state = json.load(open(STATE_FILE, encoding='utf-8'))
    last_seen = state.get('last_seen_msg_id', '')

    query = ' OR '.join(['from:' + k if '@' in k else 'subject:' + k for k in PG_KEYWORDS])
    r = requests.get(
        'https://gmail.googleapis.com/gmail/v1/users/me/messages',
        headers={'Authorization': f'Bearer {token}'},
        params={'q': query + ' newer_than:1d', 'maxResults': 10},
        timeout=15,
    )
    if not r.ok: return []
    msgs = r.json().get('messages', [])
    new = []
    for m in msgs:
        if m['id'] == last_seen: break
        new.append(m['id'])
    if msgs:
        state['last_seen_msg_id'] = msgs[0]['id']
        json.dump(state, open(STATE_FILE, 'w', encoding='utf-8'), ensure_ascii=False)
    return new[::-1], token

def get_subject(token, msg_id):
    r = requests.get(
        f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}',
        headers={'Authorization': f'Bearer {token}'},
        params={'format': 'metadata', 'metadataHeaders': 'Subject,From'},
        timeout=10,
    )
    if not r.ok: return None, None
    headers = {h['name']: h['value'] for h in r.json().get('payload', {}).get('headers', [])}
    return headers.get('Subject', '(no subject)'), headers.get('From', '(no sender)')

def send_telegram(text):
    if not TG_TOKEN or not TG_CHAT: return
    requests.post(
        f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
        json={'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML'},
        timeout=15,
    )

def main():
    result = list_recent_pg_mails()
    if not result: return
    new_ids, token = result
    if not new_ids: return
    msg_lines = []
    for mid in new_ids[:5]:
        subject, sender = get_subject(token, mid)
        if subject: msg_lines.append(f'• <b>{subject[:60]}</b>\n  ↳ {sender[:60]}')
    if msg_lines:
        text = '🔔 <b>PG 신규 메일</b> ' + str(len(new_ids)) + '건\n\n' + '\n\n'.join(msg_lines)
        send_telegram(text)
        print(text)

if __name__ == '__main__':
    main()
