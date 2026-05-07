"""Verify all sent mail and drafts in last 24h+ for empty/bad content."""
import os
import json
import base64
import sys
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

io_encoding = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build('gmail', 'v1', credentials=creds)

def decode_part(data):
    try:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
    except Exception:
        return ''

def get_message_body(payload):
    """Recursively extract plain text body."""
    body_text = ''
    if 'parts' in payload:
        for part in payload['parts']:
            mt = part.get('mimeType', '')
            if mt == 'text/plain' and part.get('body', {}).get('data'):
                body_text += decode_part(part['body']['data'])
            elif mt.startswith('multipart'):
                body_text += get_message_body(part)
            elif mt == 'text/html' and not body_text and part.get('body', {}).get('data'):
                body_text += decode_part(part['body']['data'])
    elif payload.get('body', {}).get('data'):
        body_text = decode_part(payload['body']['data'])
    return body_text

def count_attachments(payload):
    count = 0
    parts = payload.get('parts', [])
    for p in parts:
        if p.get('filename'):
            count += 1
        if 'parts' in p:
            count += count_attachments(p)
    return count

def check_bad(subject, body, attachments, headers):
    flags = []
    body_stripped = body.strip()
    body_len = len(body_stripped)
    if body_len < 200:
        flags.append(f'SHORT_BODY({body_len}c)')
    bad_tokens = ['Lorem ipsum', 'TODO', '{{', 'TBD', '[placeholder]', '[PLACEHOLDER]', 'XXXX', 'FILL_ME']
    for tok in bad_tokens:
        if tok in body:
            flags.append(f'PLACEHOLDER:{tok}')
    if not subject or not subject.strip():
        flags.append('EMPTY_SUBJECT')
    return flags

def main():
    svc = get_service()

    # Sent in last 36h to be safe
    after_dt = datetime.now() - timedelta(hours=40)
    after_str = after_dt.strftime('%Y/%m/%d')
    query = f'from:me after:{after_str}'
    print(f'\n=== TASK 1: SENT MAIL — query: {query} ===\n')

    sent_results = svc.users().messages().list(userId='me', q=query, maxResults=100).execute()
    sent_msgs = sent_results.get('messages', [])
    print(f'Total sent: {len(sent_msgs)}')

    bad_sent = []
    ok_sent = []

    for m in sent_msgs:
        msg = svc.users().messages().get(userId='me', id=m['id'], format='full').execute()
        headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
        subject = headers.get('Subject', '')
        to = headers.get('To', '')
        date = headers.get('Date', '')
        body = get_message_body(msg['payload'])
        attachments = count_attachments(msg['payload'])
        flags = check_bad(subject, body, attachments, headers)
        rec = {
            'id': m['id'],
            'subject': subject,
            'to': to,
            'date': date,
            'body_len': len(body.strip()),
            'attachments': attachments,
            'flags': flags,
            'body_preview': body.strip()[:300]
        }
        if flags:
            bad_sent.append(rec)
        else:
            ok_sent.append(rec)

    print(f'\n--- BAD SENT ({len(bad_sent)}) ---')
    for r in bad_sent:
        print(f"  {r['date'][:25]} | TO: {r['to'][:50]} | SUBJ: {r['subject'][:60]}")
        print(f"    flags: {r['flags']} | body_len={r['body_len']} | attach={r['attachments']}")
        print(f"    preview: {r['body_preview'][:200]!r}")
        print()

    print(f'\n--- OK SENT ({len(ok_sent)}) ---')
    for r in ok_sent[:30]:
        print(f"  {r['date'][:25]} | TO: {r['to'][:50]} | SUBJ: {r['subject'][:60]} | body={r['body_len']}c")

    # Drafts
    print(f'\n\n=== TASK 2: DRAFTS ===\n')
    drafts = svc.users().drafts().list(userId='me', maxResults=100).execute()
    draft_list = drafts.get('drafts', [])
    print(f'Total drafts: {len(draft_list)}')
    bad_drafts = []
    ok_drafts = []
    for d in draft_list:
        full = svc.users().drafts().get(userId='me', id=d['id'], format='full').execute()
        msg = full.get('message', {})
        headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
        subject = headers.get('Subject', '')
        to = headers.get('To', '')
        body = get_message_body(msg.get('payload', {}))
        attachments = count_attachments(msg.get('payload', {}))
        flags = check_bad(subject, body, attachments, headers)
        rec = {
            'draftId': d['id'],
            'msgId': msg.get('id'),
            'subject': subject,
            'to': to,
            'body_len': len(body.strip()),
            'attachments': attachments,
            'flags': flags,
            'body_preview': body.strip()[:300]
        }
        if flags:
            bad_drafts.append(rec)
        else:
            ok_drafts.append(rec)

    print(f'\n--- BAD DRAFTS ({len(bad_drafts)}) ---')
    for r in bad_drafts:
        print(f"  draftId={r['draftId']} | TO: {r['to'][:50]} | SUBJ: {r['subject'][:60]}")
        print(f"    flags: {r['flags']} | body_len={r['body_len']} | attach={r['attachments']}")
        print(f"    preview: {r['body_preview'][:200]!r}")
        print()

    print(f'\n--- OK DRAFTS ({len(ok_drafts)}) ---')
    for r in ok_drafts[:30]:
        print(f"  draftId={r['draftId']} | TO: {r['to'][:50]} | SUBJ: {r['subject'][:60]} | body={r['body_len']}c")

    # Save report
    report = {
        'generated_at': datetime.now().isoformat(),
        'sent_total': len(sent_msgs),
        'sent_bad': bad_sent,
        'sent_ok_count': len(ok_sent),
        'drafts_total': len(draft_list),
        'drafts_bad': bad_drafts,
        'drafts_ok_count': len(ok_drafts),
    }
    out_path = os.path.join(os.path.dirname(__file__), 'logs', 'verify_sent_24h_2026_05_07.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f'\nReport saved: {out_path}')

if __name__ == '__main__':
    main()
