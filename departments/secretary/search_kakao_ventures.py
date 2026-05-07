"""카카오 벤처스 답장 검색 + 분류 + draft 작성 (5/7).

5/7 09:00 schtask로 자동 발송된 cold email에 대한 응답 fetch.
"""
import os
import sys
import json
import base64
import datetime
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_READ = os.path.join(SCRIPT_DIR, 'token.json')
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token_send.json')
LOG_DIR = os.path.join(SCRIPT_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

FROM_EMAIL = 'ghdejr11@gmail.com'

# Gmail search queries (broad → narrow)
QUERIES = [
    'from:kakao.vc newer_than:2d',
    'from:@kakao.vc newer_than:2d',
    '"kakao ventures" newer_than:2d',
    '"카카오벤처스" newer_than:2d',
    '"카카오 벤처스" newer_than:2d',
    'from:hello@kakao.vc',
    'subject:"천명당" newer_than:2d',
    'subject:Re:"천명당" newer_than:7d',
]


def get_service(token_path, scopes_hint=''):
    creds = Credentials.from_authorized_user_file(token_path)
    return build('gmail', 'v1', credentials=creds)


def fetch_message_full(svc, msg_id):
    msg = svc.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = {h['name'].lower(): h['value'] for h in msg['payload'].get('headers', [])}
    body_text = ''
    def extract(payload):
        nonlocal body_text
        if payload.get('body', {}).get('data'):
            try:
                data = base64.urlsafe_b64decode(payload['body']['data'] + '==')
                body_text += data.decode('utf-8', errors='replace')
            except Exception:
                pass
        for p in payload.get('parts', []) or []:
            extract(p)
    extract(msg['payload'])
    return {
        'id': msg_id,
        'threadId': msg.get('threadId'),
        'from': headers.get('from', ''),
        'to': headers.get('to', ''),
        'subject': headers.get('subject', ''),
        'date': headers.get('date', ''),
        'snippet': msg.get('snippet', ''),
        'body': body_text,
        'labels': msg.get('labelIds', []),
    }


def main():
    print('=== Kakao Ventures 답장 검색 시작 ===\n')
    svc_read = get_service(TOKEN_READ)
    svc_send = get_service(TOKEN_SEND)

    seen_ids = set()
    matches = []

    for q in QUERIES:
        print(f'  query: {q}')
        try:
            res = svc_read.users().messages().list(userId='me', q=q, maxResults=20).execute()
            msgs = res.get('messages', [])
            print(f'    → {len(msgs)} hit(s)')
            for m in msgs:
                if m['id'] in seen_ids:
                    continue
                seen_ids.add(m['id'])
                full = fetch_message_full(svc_read, m['id'])
                # in:inbox 필터
                if 'INBOX' not in full['labels']:
                    print(f"      skip (not in inbox): {full['subject'][:50]}")
                    continue
                matches.append(full)
        except Exception as e:
            print(f'    ERROR: {e}')

    print(f'\n총 hit: {len(matches)}건\n')

    if not matches:
        # 더 광범위 검색 (지난 7일)
        print('--- 더 광범위 검색 (newer_than:7d) ---')
        for q in [
            'from:kakao.vc newer_than:7d',
            '"kakao ventures" newer_than:7d',
            '"카카오벤처스" newer_than:7d',
            '"카카오 벤처스" newer_than:7d',
        ]:
            print(f'  query: {q}')
            try:
                res = svc_read.users().messages().list(userId='me', q=q, maxResults=10).execute()
                msgs = res.get('messages', [])
                print(f'    → {len(msgs)} hit(s)')
                for m in msgs:
                    if m['id'] in seen_ids:
                        continue
                    seen_ids.add(m['id'])
                    full = fetch_message_full(svc_read, m['id'])
                    matches.append(full)
            except Exception as e:
                print(f'    ERROR: {e}')

    # 보낸편지함 확인 (5/7 발송됐다는 schtask 검증)
    print('\n--- 보낸편지함 확인 (5/7 발송 cold email) ---')
    try:
        sent = svc_read.users().messages().list(
            userId='me',
            q='to:kakao.vc OR to:hello@kakao.vc newer_than:2d',
            maxResults=10,
        ).execute()
        sent_msgs = sent.get('messages', [])
        print(f'  보낸 메일: {len(sent_msgs)}건')
        for m in sent_msgs:
            full = fetch_message_full(svc_read, m['id'])
            print(f"    SENT → {full['to'][:60]} | {full['subject'][:60]}")
    except Exception as e:
        print(f'  ERROR: {e}')

    # 결과 저장
    out = {
        'scanned_at': datetime.datetime.now().isoformat(),
        'matches': [
            {
                'from': m['from'],
                'subject': m['subject'],
                'date': m['date'],
                'snippet': m['snippet'][:200],
                'body_head': m['body'][:500],
                'id': m['id'],
                'threadId': m['threadId'],
            }
            for m in matches
        ],
    }
    out_path = os.path.join(LOG_DIR, 'kakao_ventures_search_2026_05_07.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\n저장: {out_path}')

    # 매치된 메일 상세 출력
    print('\n=== 매치된 메일 상세 ===')
    for i, m in enumerate(matches, 1):
        print(f'\n[{i}] from: {m["from"]}')
        print(f'    subject: {m["subject"]}')
        print(f'    date: {m["date"]}')
        print(f'    snippet: {m["snippet"][:200]}')
        print(f'    body_head: {m["body"][:400]}')

    return matches, svc_send


if __name__ == '__main__':
    matches, svc_send = main()
    sys.exit(0 if matches else 1)
