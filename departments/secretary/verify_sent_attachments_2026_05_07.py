"""Verify all sent mail attachments from 2026-05-03 to 2026-05-07.

Detects:
- Empty/blank form templates (filename starts with (양식)/[양식]/template/sample)
- HWP < 30KB
- DOCX with placeholders ([회사명], {{...}}, _____)
- PDF with empty form fields
- Suspiciously small attachments
"""
import os
import json
import base64
import sys
import re
import zipfile
import io
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(SCRIPT_DIR, 'token.json')
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
]

OUT_DIR = os.path.join(SCRIPT_DIR, 'logs')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, 'verify_sent_attachments_2026_05_07.json')

PLACEHOLDER_PATTERNS = [
    r'\{\{[^}]+\}\}',         # {{name}}
    r'\[회사명\]',
    r'\[기업명\]',
    r'\[대표자\]',
    r'\[성명\]',
    r'\[이름\]',
    r'\[주소\]',
    r'\[연락처\]',
    r'\[이메일\]',
    r'_{5,}',                  # _____
    r'\[\s*\]',                # [ ] (empty box)
    r'XXXX',
    r'placeholder',
    r'PLACEHOLDER',
    r'TBD',
    r'TODO',
    r'예시\s*:',
    r'\(예시\)',
]

# Filename hints that suggest blank template
TEMPLATE_NAME_HINTS = ['(양식)', '[양식]', '(서식)', '[서식]', '_template', 'template_', 'sample', 'blank', '예시', '(예시)']


def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build('gmail', 'v1', credentials=creds)


def decode_part(data):
    try:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
    except Exception:
        return ''


def get_message_body(payload):
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


def collect_attachments(svc, msg_id, payload, results):
    """Recursively collect attachment metadata + download bodies."""
    if 'parts' in payload:
        for p in payload['parts']:
            collect_attachments(svc, msg_id, p, results)
    fname = payload.get('filename')
    if fname and payload.get('body', {}).get('attachmentId'):
        att_id = payload['body']['attachmentId']
        size = payload['body'].get('size', 0)
        results.append({
            'filename': fname,
            'mime': payload.get('mimeType', ''),
            'size': size,
            'attachmentId': att_id,
        })
    elif fname and payload.get('body', {}).get('data'):
        # inline
        results.append({
            'filename': fname,
            'mime': payload.get('mimeType', ''),
            'size': payload['body'].get('size', 0),
            'attachmentId': None,
            'inline_data': payload['body']['data'],
        })


def fetch_attachment_bytes(svc, msg_id, att):
    if att.get('attachmentId'):
        a = svc.users().messages().attachments().get(
            userId='me', messageId=msg_id, id=att['attachmentId']
        ).execute()
        data = a.get('data', '')
        return base64.urlsafe_b64decode(data)
    if att.get('inline_data'):
        return base64.urlsafe_b64decode(att['inline_data'])
    return b''


def analyze_docx(content_bytes):
    """Return list of placeholder hits from a .docx file."""
    hits = []
    try:
        zf = zipfile.ZipFile(io.BytesIO(content_bytes))
        names = zf.namelist()
        text_blob = ''
        for n in names:
            if n.startswith('word/') and n.endswith('.xml'):
                try:
                    text_blob += zf.read(n).decode('utf-8', errors='ignore')
                except Exception:
                    pass
        # strip XML tags for text-only scan
        text_only = re.sub(r'<[^>]+>', '', text_blob)
        for pat in PLACEHOLDER_PATTERNS:
            ms = re.findall(pat, text_only)
            if ms:
                hits.append(f'{pat}:{len(ms)}x')
        text_len = len(text_only.strip())
        return hits, text_len
    except Exception as e:
        return [f'DOCX_PARSE_ERR:{e}'], 0


def analyze_hwp(content_bytes, fname):
    """HWP can't be parsed easily; use heuristics."""
    flags = []
    size = len(content_bytes)
    # hwp 5.0 = compound binary; hwpx = zip
    is_hwpx = content_bytes[:4] == b'PK\x03\x04'
    if is_hwpx:
        try:
            zf = zipfile.ZipFile(io.BytesIO(content_bytes))
            text_blob = ''
            for n in zf.namelist():
                if n.endswith('.xml') or n.endswith('.txt'):
                    try:
                        text_blob += zf.read(n).decode('utf-8', errors='ignore')
                    except Exception:
                        pass
            text_only = re.sub(r'<[^>]+>', '', text_blob)
            for pat in PLACEHOLDER_PATTERNS:
                ms = re.findall(pat, text_only)
                if ms:
                    flags.append(f'{pat}:{len(ms)}x')
        except Exception as e:
            flags.append(f'HWPX_PARSE_ERR:{e}')
    else:
        # binary HWP; just size + filename hint
        flags.append('HWP_BINARY_NO_PARSE')
    return flags, size


def analyze_pdf(content_bytes):
    """Quick PDF heuristic — small + filename hint."""
    flags = []
    size = len(content_bytes)
    # detect blank fields by looking for AcroForm + /V () empty strings
    try:
        text = content_bytes.decode('latin-1', errors='ignore')
        if '/AcroForm' in text:
            empty_fields = re.findall(r'/V\s*\(\s*\)', text)
            if empty_fields:
                flags.append(f'PDF_EMPTY_FORM_FIELDS:{len(empty_fields)}')
    except Exception:
        pass
    return flags, size


def analyze_attachment(att, content):
    """Return verdict, reasons for one attachment."""
    reasons = []
    fname = att['filename']
    fname_lower = fname.lower()
    size = len(content)

    # filename template hint
    for hint in TEMPLATE_NAME_HINTS:
        if hint.lower() in fname_lower:
            reasons.append(f'FNAME_TEMPLATE_HINT:{hint}')
            break

    if fname_lower.endswith('.hwp') or fname_lower.endswith('.hwpx'):
        if size < 30 * 1024:
            reasons.append(f'HWP_TOO_SMALL:{size}b')
        hits, _ = analyze_hwp(content, fname)
        for h in hits:
            reasons.append(f'HWP_PLACEHOLDER:{h}')
    elif fname_lower.endswith('.docx'):
        hits, text_len = analyze_docx(content)
        if text_len < 200:
            reasons.append(f'DOCX_SHORT_TEXT:{text_len}c')
        for h in hits:
            reasons.append(f'DOCX_PLACEHOLDER:{h}')
    elif fname_lower.endswith('.pdf'):
        hits, _ = analyze_pdf(content)
        for h in hits:
            reasons.append(h)
        if size < 5 * 1024:
            reasons.append(f'PDF_TOO_SMALL:{size}b')

    return reasons


def main():
    svc = get_service()
    query = 'from:me after:2026/05/03 before:2026/05/08'
    print(f'\n=== Query: {query} ===\n')
    msgs = []
    page_token = None
    while True:
        res = svc.users().messages().list(
            userId='me', q=query, maxResults=100, pageToken=page_token
        ).execute()
        msgs.extend(res.get('messages', []))
        page_token = res.get('nextPageToken')
        if not page_token:
            break
    print(f'Total sent: {len(msgs)}')

    bad = []
    ok = []
    no_attach = []
    for i, m in enumerate(msgs):
        try:
            msg = svc.users().messages().get(userId='me', id=m['id'], format='full').execute()
        except Exception as e:
            print(f'  [ERR] msg {m["id"]}: {e}')
            continue
        headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
        subject = headers.get('Subject', '')
        to = headers.get('To', '')
        date = headers.get('Date', '')
        body = get_message_body(msg['payload'])
        atts = []
        collect_attachments(svc, m['id'], msg['payload'], atts)
        rec = {
            'id': m['id'],
            'date': date,
            'to': to,
            'subject': subject,
            'body_len': len(body.strip()),
            'attachments': [],
        }
        any_bad = False
        for att in atts:
            try:
                content = fetch_attachment_bytes(svc, m['id'], att)
            except Exception as e:
                rec['attachments'].append({'filename': att['filename'], 'error': str(e)})
                any_bad = True
                continue
            reasons = analyze_attachment(att, content)
            att_rec = {
                'filename': att['filename'],
                'mime': att['mime'],
                'size': len(content),
                'reasons': reasons,
            }
            rec['attachments'].append(att_rec)
            if reasons:
                any_bad = True
        if not atts:
            no_attach.append(rec)
        elif any_bad:
            bad.append(rec)
        else:
            ok.append(rec)
        if (i + 1) % 10 == 0:
            print(f'  Processed {i+1}/{len(msgs)}')

    print(f'\n=== BAD (attachment issues): {len(bad)} ===\n')
    for r in bad:
        print(f"  {r['date'][:25]} | TO: {r['to'][:50]}")
        print(f"    SUBJ: {r['subject'][:80]}")
        for a in r['attachments']:
            if a.get('reasons') or a.get('error'):
                print(f"    [BAD] {a['filename']} ({a.get('size', '?')}b) -> {a.get('reasons') or a.get('error')}")
            else:
                print(f"    [OK]  {a['filename']} ({a.get('size', '?')}b)")
        print()

    print(f'\n=== OK (with attachments): {len(ok)} ===\n')
    for r in ok[:30]:
        att_str = ', '.join(f"{a['filename']}({a['size']}b)" for a in r['attachments'])
        print(f"  {r['date'][:25]} | TO: {r['to'][:40]} | {r['subject'][:50]} | {att_str[:100]}")

    print(f'\n=== NO ATTACHMENT: {len(no_attach)} (just listing count) ===')

    report = {
        'generated_at': datetime.now().isoformat(),
        'query': query,
        'total_sent': len(msgs),
        'bad': bad,
        'ok_count': len(ok),
        'no_attach_count': len(no_attach),
        'ok_samples': ok[:30],
    }
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f'\nReport saved: {OUT_PATH}')


if __name__ == '__main__':
    main()
