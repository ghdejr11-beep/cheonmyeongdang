"""B2B Saju Engine cold-email sender — placeholder, awaiting user approval.

Workflow:
1. User fills `{COMPANY_NAME}`, `{RECIPIENT_NAME}`, `{RECIPIENT_EMAIL}` in
   `cold_emails_2026_05_05.json` (Apollo / LinkedIn lead sourcing — see
   `lead_sourcing_guide.md`).
2. User runs:
       python send_b2b_emails.py --confirm --batch 1
   ...sends batch 1 (10 emails). Repeat for batches 2..5 across 5 days.
3. Without `--confirm`, the script does a DRY RUN — it prints what would be
   sent and stops. NEVER sends without explicit `--confirm`.

Reuses the Gmail send pattern from departments/secretary/send_kodata_2026_05_05.py
"""
import os
import sys
import json
import time
import base64
import argparse
import datetime as dt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Stdout UTF-8 (Windows safety)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(ROOT, 'cold_emails_2026_05_05.json')
SENT_LOG = os.path.join(ROOT, 'sent_log.json')

# Reuse secretary token (gmail.modify scope, send-capable)
TOKEN_PATH = os.path.normpath(os.path.join(
    ROOT, '..', 'secretary', 'token.json'
))

FROM_NAME = 'Deokhun Hong (KunStudio)'
FROM_EMAIL = 'ghdejr11@gmail.com'
BATCH_SIZE = 10  # emails per day
SLEEP_BETWEEN_SENDS = 6  # seconds — 10 emails / 60s = under Gmail per-minute soft cap


def load_emails():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def is_filled(email_record):
    """True if all 3 placeholders have been replaced with real values."""
    body = email_record['body']
    subject = email_record['subject']
    recipient = email_record.get('recipient_email_placeholder', '')
    company = email_record.get('company_placeholder', '')
    if '{COMPANY_NAME}' in body or '{COMPANY_NAME}' in subject:
        return False
    if '{RECIPIENT_NAME}' in body:
        return False
    if recipient == '{RECIPIENT_EMAIL}' or '@' not in recipient:
        return False
    if company == '{COMPANY_NAME}' or not company.strip():
        return False
    return True


def build_mime(record):
    msg = MIMEMultipart()
    msg['From'] = '{} <{}>'.format(FROM_NAME, FROM_EMAIL)
    msg['To'] = record['recipient_email_placeholder']
    msg['Subject'] = record['subject']
    msg.attach(MIMEText(record['body'], 'plain', 'utf-8'))
    return msg


def load_gmail_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    if not os.path.isfile(TOKEN_PATH):
        raise SystemExit('[ABORT] Gmail token not found: {}'.format(TOKEN_PATH))
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


def append_log(entry):
    log = []
    if os.path.isfile(SENT_LOG):
        try:
            with open(SENT_LOG, 'r', encoding='utf-8') as f:
                log = json.load(f)
        except Exception:
            log = []
    log.append(entry)
    with open(SENT_LOG, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--confirm', action='store_true',
                        help='ACTUALLY send emails. Without this flag, dry-run only.')
    parser.add_argument('--batch', type=int, default=1,
                        help='Batch number 1..5 (10 emails per batch).')
    args = parser.parse_args()

    data = load_emails()
    emails = data['emails']

    # Sort by priority then idx so high-priority first
    priority_order = {'높음': 0, '중간': 1, '낮음': 2}
    emails_sorted = sorted(emails, key=lambda e: (priority_order.get(e['priority'], 9), e['idx']))

    start = (args.batch - 1) * BATCH_SIZE
    end = start + BATCH_SIZE
    batch = emails_sorted[start:end]

    if not batch:
        print('[INFO] Batch {} is empty — nothing to do.'.format(args.batch))
        return

    print('=== B2B Saju Engine cold-email sender ===')
    print('  Batch        : {} of 5'.format(args.batch))
    print('  Emails in this batch: {}'.format(len(batch)))
    print('  Mode         : {}'.format('LIVE SEND' if args.confirm else 'DRY RUN'))
    print('')

    not_filled = [r for r in batch if not is_filled(r)]
    if not_filled:
        print('[ABORT] {} of {} emails still have unfilled placeholders.'.format(len(not_filled), len(batch)))
        print('  Fill {COMPANY_NAME}, {RECIPIENT_NAME}, {RECIPIENT_EMAIL} in the JSON before sending.')
        for r in not_filled[:3]:
            print('  - idx={} sector={} title={}'.format(r['idx'], r['sector'], r['recipient_title']))
        if not args.confirm:
            print('')
            print('[DRY-RUN] Continuing to show what WOULD be sent if filled.')
        else:
            sys.exit(2)

    if not args.confirm:
        print('[DRY-RUN] No emails will be sent. Add --confirm to send.')
        for r in batch:
            print('  -> idx={} sector={} priority={} subject="{}"'.format(
                r['idx'], r['sector'], r['priority'], r['subject'][:60]))
        return

    service = load_gmail_service()
    sent_count = 0
    for r in batch:
        if not is_filled(r):
            print('  [SKIP] idx={} (placeholders unfilled)'.format(r['idx']))
            continue
        msg = build_mime(r)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        try:
            res = service.users().messages().send(
                userId='me', body={'raw': raw}
            ).execute()
            mid = res.get('id')
            print('  [SENT] idx={} to={} subject="{}" message_id={}'.format(
                r['idx'], r['recipient_email_placeholder'], r['subject'][:50], mid))
            append_log({
                'sent_at': dt.datetime.now().isoformat(),
                'idx': r['idx'],
                'sector': r['sector'],
                'recipient': r['recipient_email_placeholder'],
                'subject': r['subject'],
                'message_id': mid,
            })
            sent_count += 1
            time.sleep(SLEEP_BETWEEN_SENDS)
        except Exception as exc:
            print('  [ERROR] idx={} -> {}'.format(r['idx'], exc))

    print('')
    print('=== Done. Sent {} of {} in batch {} ==='.format(sent_count, len(batch), args.batch))


if __name__ == '__main__':
    main()
