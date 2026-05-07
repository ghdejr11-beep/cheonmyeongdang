"""KoDATA 발송 메일 검증 (2026-05-07).

5/7 16:30경 사용자가 SEND 클릭한 KoDATA 정정 메일 검증:
- from:me to:코데이터 OR to:kodata.co.kr after:2026/05/07
- 첨부 list 검증 (의뢰서 hwp + 사업자등록증 + 주민등록등본 = 3개 기대)
- bounce/error 없는지

thread: 19df70fe428c7e65 (사용자 안내)
수신: 85343@xn--2n1bp39a0wfq1b.co.kr (= 85343@코데이터.co.kr)
"""
import os
import sys
import json
import base64

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# token.json 우선 (read/modify scope), token_send는 send 전용이라 list 불가
TOKEN_PATHS = [
    os.path.join(SCRIPT_DIR, 'token.json'),
    os.path.join(SCRIPT_DIR, 'token_send.json'),
]


def load_service():
    for tp in TOKEN_PATHS:
        if os.path.exists(tp):
            with open(tp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            creds = Credentials(
                token=data.get('token'),
                refresh_token=data.get('refresh_token'),
                token_uri=data.get('token_uri'),
                client_id=data.get('client_id'),
                client_secret=data.get('client_secret'),
                scopes=data.get('scopes'),
            )
            print(f'[TOKEN] {tp}')
            return build('gmail', 'v1', credentials=creds)
    raise SystemExit('[FATAL] no token file found')


def walk_attachments(payload, attachments):
    filename = payload.get('filename', '')
    body = payload.get('body', {})
    if filename:
        attachments.append({
            'filename': filename,
            'size': body.get('size', 0),
            'mimeType': payload.get('mimeType', ''),
        })
    for sub in payload.get('parts', []) or []:
        walk_attachments(sub, attachments)


def main():
    svc = load_service()

    # 1) 보낸 편지함 검색 (5/7 이후)
    queries = [
        # KoDATA 도메인 이메일
        'in:sent (to:kodata.co.kr OR to:85343 OR to:xn--2n1bp39a0wfq1b) after:2026/05/07',
        # thread 직접 조회
        'rfc822msgid:* in:sent newer_than:1d',
    ]
    found_total = 0
    target_ids = []
    for q in queries[:1]:
        print(f'\n[QUERY] {q}')
        res = svc.users().messages().list(userId='me', q=q, maxResults=20).execute()
        msgs = res.get('messages', [])
        print(f'[FOUND] {len(msgs)}건')
        found_total += len(msgs)
        for m in msgs:
            target_ids.append(m['id'])

    # thread 직접 조회 (thread id 19df70fe428c7e65)
    thread_id = '19df70fe428c7e65'
    print(f'\n[THREAD] {thread_id}')
    try:
        thr = svc.users().threads().get(userId='me', id=thread_id, format='full').execute()
        thr_msgs = thr.get('messages', [])
        print(f'  thread messages: {len(thr_msgs)}')
        for tm in thr_msgs:
            target_ids.append(tm['id'])
    except Exception as e:
        print(f'  [WARN] thread fetch fail: {e}')

    # dedup
    target_ids = list(dict.fromkeys(target_ids))
    print(f'\n[ANALYZE] 분석 대상 message: {len(target_ids)}건')

    sent_to_kodata = []
    for mid in target_ids:
        full = svc.users().messages().get(userId='me', id=mid, format='full').execute()
        headers = {h['name']: h['value'] for h in full['payload']['headers']}
        labels = full.get('labelIds', [])
        from_h = (headers.get('From') or '').lower()
        to_h = (headers.get('To') or '').lower()
        subject = headers.get('Subject') or ''
        date = headers.get('Date') or ''

        is_sent = 'SENT' in labels
        is_kodata = ('kodata' in to_h or '85343' in to_h or 'xn--2n1bp39a0wfq1b' in to_h
                     or 'kodata' in from_h)
        if not (is_sent and is_kodata):
            continue

        attachments = []
        walk_attachments(full['payload'], attachments)
        sent_to_kodata.append({
            'id': mid,
            'date': date,
            'from': from_h,
            'to': to_h,
            'subject': subject,
            'attachments': attachments,
            'thread_id': full.get('threadId'),
        })

    print(f'\n[KoDATA 발송 메일] {len(sent_to_kodata)}건')
    print('=' * 80)
    for em in sent_to_kodata:
        print(f'  message_id   : {em["id"]}')
        print(f'  thread_id    : {em["thread_id"]}')
        print(f'  Date         : {em["date"]}')
        print(f'  From         : {em["from"]}')
        print(f'  To           : {em["to"]}')
        print(f'  Subject      : {em["subject"]}')
        print(f'  Attachments  : {len(em["attachments"])}')
        for a in em['attachments']:
            print(f'    - {a["filename"]} ({a["size"]:,} B, {a["mimeType"]})')
        print('-' * 80)

    # 2) bounce 검색 (mailer-daemon)
    print('\n[BOUNCE CHECK]')
    bounce_q = 'from:mailer-daemon OR from:postmaster OR subject:"Delivery Status" OR subject:"undeliverable" newer_than:1d'
    res = svc.users().messages().list(userId='me', q=bounce_q, maxResults=10).execute()
    bounces = res.get('messages', [])
    if bounces:
        print(f'  [WARN] {len(bounces)}건 bounce 의심')
        for b in bounces:
            full = svc.users().messages().get(userId='me', id=b['id'], format='metadata',
                                              metadataHeaders=['From', 'Subject', 'Date']).execute()
            headers = {h['name']: h['value'] for h in full['payload']['headers']}
            print(f'    - {headers.get("Date")} | {headers.get("From")} | {headers.get("Subject")}')
    else:
        print('  [OK] bounce 없음')

    # 결과 JSON
    out = {
        'verified_at': '2026-05-07',
        'sent_count': len(sent_to_kodata),
        'sent_messages': sent_to_kodata,
        'bounces': len(bounces),
    }
    state_file = os.path.join(SCRIPT_DIR, 'kodata_send_verify.json')
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\n[STATE] {state_file}')


if __name__ == '__main__':
    main()
