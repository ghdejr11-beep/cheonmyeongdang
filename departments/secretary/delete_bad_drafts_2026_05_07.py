"""5/7 12:30 — 나쁜 draft 14건 자동 삭제.

사용자가 드라프트함에서 부적절한 자동답장 14건 발견하여 분노함.
- Stripe receipt에 "메일 잘 받았습니다" 답장 draft
- Anthropic invoice에 "검토 후 회신드리겠습니다" 답장 draft
- Instagram 스토리 알림에 답장 draft
- Quora cheating-spouse 스레드에 답장 draft
- dev.to confirm에 답장 draft

이런 자동알림에는 절대 답장 X. 즉시 삭제.
유일하게 보존: 카카오페이 jella.tto draftId=r8645647452764228186 (1187자, 정상).
"""
import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.path.join(ROOT, 'token_send.json')

# 보존할 draft (whitelist) — 나머지 BAD draft 모두 삭제
KEEP = {
    'r8645647452764228186',  # 카카오페이 jella.tto - 1187c, OK
}

# 명시적 삭제 대상 (verify 결과 BAD list)
DELETE_TARGETS = [
    'r-7446819322472583900',  # dev.to
    'r7476371072331734030',   # Heepsy
    'r-5150041059270796968',  # Anthropic invoice
    'r2649519323506236410',   # 천명당 인플루언서 (자기자신)
    'r-4764689228306189944',  # 천명당 인플루언서 (자기자신)
    'r5505720716256720483',   # make.com 광고
    'r1282757389445820013',   # beehiiv preeya
    'r-7993338832859089755',  # beehiiv tyler
    'r-5685903690681475598',  # 천명당 인플루언서 (자기자신)
    'r-768581985823041633',   # Instagram stories
    'r4068091373715801312',   # Instagram messages
    'r8483216545633287271',   # Stripe receipt
    'r1830880269538833446',   # CODEF demo expiry
    'r3599848457117557306',   # Quora cheating spouse
    'r-3979572612311305921',  # iverson9914@naver.com 빈제목 (진료기록 첨부)
]

def main():
    creds = Credentials.from_authorized_user_file(TOKEN)
    svc = build('gmail', 'v1', credentials=creds)

    deleted = []
    failed = []
    for did in DELETE_TARGETS:
        if did in KEEP:
            continue
        try:
            svc.users().drafts().delete(userId='me', id=did).execute()
            deleted.append(did)
            print(f'  [DELETED] {did}')
        except Exception as e:
            failed.append({'id': did, 'err': str(e)[:200]})
            print(f'  [FAIL] {did} -- {e}')

    print(f'\n총 삭제: {len(deleted)}, 실패: {len(failed)}')

    log_path = os.path.join(ROOT, 'logs', 'bad_drafts_deleted_2026_05_07.json')
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump({'deleted': deleted, 'failed': failed, 'kept': list(KEEP)},
                  f, ensure_ascii=False, indent=2)
    print(f'log: {log_path}')

if __name__ == '__main__':
    main()
