"""KoDATA 회신 메일 찾기 + 첨부 다운로드 (2026-05-07).

Gmail API로 from:kodata.co.kr OR find@kodata.co.kr OR subject:기업정보등록 검색
- newer_than:7d
- 본문 + 첨부 list 출력
- 첨부 있으면 round2_2026_05/ 로 다운로드
"""
import os
import sys
import json
import base64
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(SCRIPT_DIR, 'token.json')
ROUND2_DIR = r'D:\cheonmyeongdang\departments\tax\applications\round2_2026_05'


def load_service():
    with open(TOKEN_PATH, 'r', encoding='utf-8') as f:
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


def walk_parts(payload, attachments, body_parts):
    mt = payload.get('mimeType', '')
    filename = payload.get('filename', '')
    body = payload.get('body', {})
    if filename:
        attachments.append({
            'filename': filename,
            'attachmentId': body.get('attachmentId'),
            'size': body.get('size', 0),
            'mimeType': mt,
        })
    elif mt.startswith('text/'):
        data = body.get('data')
        if data:
            try:
                txt = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                body_parts.append((mt, txt))
            except Exception:
                pass
    for sub in payload.get('parts', []) or []:
        walk_parts(sub, attachments, body_parts)


def main():
    svc = load_service()
    q = '(from:kodata.co.kr OR from:find@kodata.co.kr OR subject:기업정보등록) newer_than:7d'
    print(f'[Q] {q}')
    res = svc.users().messages().list(userId='me', q=q, maxResults=20).execute()
    msgs = res.get('messages', [])
    print(f'[FOUND] {len(msgs)} message(s)')

    if not msgs:
        print('[NONE] no kodata replies in last 7 days')
        return

    for m in msgs:
        full = svc.users().messages().get(userId='me', id=m['id'], format='full').execute()
        headers = {h['name']: h['value'] for h in full['payload']['headers']}
        labels = full.get('labelIds', [])
        attachments = []
        body_parts = []
        walk_parts(full['payload'], attachments, body_parts)
        print('=' * 80)
        print(f'  message_id : {m["id"]}')
        print(f'  threadId   : {full.get("threadId")}')
        print(f'  Date       : {headers.get("Date")}')
        print(f'  From       : {headers.get("From")}')
        print(f'  To         : {headers.get("To")}')
        print(f'  Subject    : {headers.get("Subject")}')
        print(f'  Labels     : {labels}')
        print(f'  Attachments: {len(attachments)}')
        for a in attachments:
            print(f'    - {a["filename"]} ({a["size"]:,} B, {a["mimeType"]})')

        # 본문 출력 (text/plain 우선)
        plain = next((t for mt, t in body_parts if mt == 'text/plain'), None)
        if not plain and body_parts:
            plain = body_parts[0][1]
        if plain:
            preview = plain[:1500]
            print('--- BODY (preview) ---')
            print(preview)
            print('--- /BODY ---')

        # 회신 메일이면 (from kodata or find@kodata) → 첨부 다운로드
        from_addr = (headers.get('From') or '').lower()
        if 'kodata' in from_addr and attachments:
            print('  [DOWNLOAD] kodata reply with attachments')
            for a in attachments:
                if not a['attachmentId']:
                    continue
                att = svc.users().messages().attachments().get(
                    userId='me', messageId=m['id'], id=a['attachmentId']
                ).execute()
                data = base64.urlsafe_b64decode(att['data'])
                # 안전 파일명
                safe_name = a['filename'].replace('/', '_').replace('\\', '_')
                out_path = os.path.join(ROUND2_DIR, f'(KoDATA회신_{m["id"][:8]}){safe_name}')
                with open(out_path, 'wb') as f:
                    f.write(data)
                print(f'    [SAVED] {out_path} ({len(data):,} B)')


if __name__ == '__main__':
    main()
