"""B2B D+3 / D+7 follow-up sender — auto-detects sent_log.json entries needing follow-up.

Logic:
- For each entry in sent_log.json, calculate days since sent_at.
- If 3 <= days < 7 and no D+3 follow-up sent yet  → send "D+3 bump" (short, 2 lines).
- If days >= 7 and no D+7 follow-up sent yet  → send "D+7 break-up" (final email, polite close).
- Tracks follow-up state in followup_log.json (separate from sent_log.json).
- Skips entries that already received a reply (placeholder: replies_log.json — manual flag).
- Defaults to DRY-RUN. Add --confirm to actually send.

Schedule: Windows Task Scheduler — daily at 11:30 (after primary daily 11:00 batch).
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

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
SENT_LOG = os.path.join(ROOT, 'sent_log.json')
FOLLOWUP_LOG = os.path.join(ROOT, 'followup_log.json')
REPLIES_LOG = os.path.join(ROOT, 'replies_log.json')  # manual flag: {"<msg_id>": "replied"}
TOKEN_PATH = os.path.normpath(os.path.join(ROOT, '..', 'secretary', 'token.json'))

FROM_NAME = 'Deokhun Hong (KunStudio)'
FROM_EMAIL = 'ghdejr11@gmail.com'
SLEEP_BETWEEN_SENDS = 6
DAILY_CAP = 10  # safety: max follow-ups per day


D3_BODY = """Hi,

Quick bump on my note from a few days back — wanted to make sure it didn't get buried.

The 1-day API integration claim still stands: Saju Engine returns a full 4-pillar reading in under 3 seconds, and we'd give you a 90-day free pilot to test on a small audience segment.

Worth a 15-min call this week or next?

Best,
Deokhun Hong
KunStudio · https://cheonmyeongdang.vercel.app
ghdejr11@gmail.com
"""

D7_BODY = """Hi,

Closing the loop on Saju Engine — I won't keep nudging.

If Korean cultural personalization isn't a priority right now, totally fair. If it becomes one later this year (we're already seeing K-pop / K-travel / K-beauty teams test the angle), the API will still be live at:
https://cheonmyeongdang.vercel.app

90-day pilots are open — just reply to this thread anytime.

All the best,
Deokhun Hong
KunStudio
"""


def load_json(path, default):
    if not os.path.isfile(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def parse_dt(s):
    return dt.datetime.fromisoformat(s)


def gmail_service():
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


def build_mime(to, subject, body, in_reply_to=None):
    msg = MIMEMultipart()
    msg['From'] = '{} <{}>'.format(FROM_NAME, FROM_EMAIL)
    msg['To'] = to
    msg['Subject'] = subject
    if in_reply_to:
        # Reference the original send to keep thread context where possible
        msg['In-Reply-To'] = '<{}@mail.gmail.com>'.format(in_reply_to)
        msg['References'] = '<{}@mail.gmail.com>'.format(in_reply_to)
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    return msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--confirm', action='store_true',
                        help='ACTUALLY send. Without this flag, dry-run only.')
    args = parser.parse_args()

    sent = load_json(SENT_LOG, [])
    followups = load_json(FOLLOWUP_LOG, {})  # { sent_msg_id: {"d3_at":..., "d7_at":...} }
    replies = load_json(REPLIES_LOG, {})

    today = dt.date.today()
    now = dt.datetime.now()
    queue = []  # list of (kind, original entry)

    for entry in sent:
        mid = entry.get('message_id')
        if not mid:
            continue
        if mid in replies:
            continue  # got a reply — don't follow up
        sent_at = parse_dt(entry['sent_at'])
        days = (now - sent_at).days
        state = followups.get(mid, {})

        if 3 <= days < 7 and not state.get('d3_at'):
            queue.append(('D3', entry))
        elif days >= 7 and not state.get('d7_at'):
            queue.append(('D7', entry))

    print('=== B2B follow-up sender ===')
    print('  Today                   : {}'.format(today.isoformat()))
    print('  Eligible follow-ups     : {}'.format(len(queue)))
    print('  Daily cap               : {}'.format(DAILY_CAP))
    print('  Mode                    : {}'.format('LIVE SEND' if args.confirm else 'DRY RUN'))
    print('')

    if not queue:
        print('[INFO] No follow-ups due. Done.')
        return

    queue = queue[:DAILY_CAP]

    if not args.confirm:
        for kind, entry in queue:
            print('  [DRY] {} -> idx={} to={} subject="{}"'.format(
                kind, entry['idx'], entry['recipient'], entry['subject'][:60]))
        print('')
        print('[DRY-RUN] Add --confirm to actually send.')
        return

    service = gmail_service()
    sent_now = 0
    for kind, entry in queue:
        body = D3_BODY if kind == 'D3' else D7_BODY
        # subject: prefix Re: to original
        orig_subject = entry['subject']
        new_subject = orig_subject if orig_subject.lower().startswith('re:') else 'Re: ' + orig_subject
        msg = build_mime(entry['recipient'], new_subject, body, in_reply_to=entry['message_id'])
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        try:
            res = service.users().messages().send(userId='me', body={'raw': raw}).execute()
            new_mid = res.get('id')
            print('  [SENT] {} idx={} to={} new_msg_id={}'.format(
                kind, entry['idx'], entry['recipient'], new_mid))
            mid = entry['message_id']
            state = followups.get(mid, {})
            ts = dt.datetime.now().isoformat()
            if kind == 'D3':
                state['d3_at'] = ts
                state['d3_msg_id'] = new_mid
            else:
                state['d7_at'] = ts
                state['d7_msg_id'] = new_mid
            followups[mid] = state
            save_json(FOLLOWUP_LOG, followups)
            sent_now += 1
            time.sleep(SLEEP_BETWEEN_SENDS)
        except Exception as exc:
            print('  [ERROR] {} idx={} -> {}'.format(kind, entry['idx'], exc))

    print('')
    print('=== Done. Sent {} follow-ups ==='.format(sent_now))


if __name__ == '__main__':
    main()
