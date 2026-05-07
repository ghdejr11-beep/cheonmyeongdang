"""Kakao Ventures D+10 second touch (예정 발송: 2026-05-17 09:00).

마지막 정중 push. 응답 없으면 6개월 후 재컨택 schedule로 close out.
"""
import os
import json
import sys
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token_send.json')

FROM_EMAIL = 'ghdejr11@gmail.com'
FROM_NAME = 'Hong Deokhoon (KunStudio)'
TO_EMAIL = 'hello@kakao.vc'
ORIGINAL_THREAD_ID = '19e006f9ff81e2ab'

SUBJECT = 'Re: [Seed 제안] 천명당 - 2주차 close out (AppSumo 출시 직후 데이터 공유)'

BODY = """안녕하세요, 카카오벤처스 팀.

세 번째이자 마지막 메일입니다 (이후 6개월 후 진척 후 재컨택).

【지난 2주 진척 (5/7 → 5/17)】
- AppSumo LTD 5/20 출시: 스토어 페이지 라이브, 첫 48시간 매출 데이터 수집 예정
- K-Startup AI리그 5/20 마감: 사업계획서 제출 완료
- Day 50 (5/21) 시점에 첫 paid customer 데이터 공유 가능

【한 줄 회신 부탁】
- "관심 있음 → 미팅" / "지금은 fit 아님" / "스킵" 셋 중 하나만 알려주시면
  다른 VC 우선순위 조정에 큰 도움이 됩니다.

만약 fit이 아니어도 솔직히 말씀해주시면 6개월 후 재컨택 시 그 피드백 반영하겠습니다.

라이브: https://cheonmyeongdang.vercel.app
1-pager 재첨부 필요하시면 회신 부탁드립니다.

감사합니다.
홍덕훈 / 쿤스튜디오 대표
"""


def load_service():
    with open(TOKEN_SEND, 'r', encoding='utf-8') as f:
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


def has_reply(svc):
    try:
        thread = svc.users().threads().get(userId='me', id=ORIGINAL_THREAD_ID).execute()
        messages = thread.get('messages', [])
        for m in messages:
            headers = {h['name'].lower(): h['value'] for h in m['payload'].get('headers', [])}
            from_h = headers.get('from', '').lower()
            if 'kakao.vc' in from_h:
                return True
        return False
    except Exception as e:
        print(f'  [WARN] thread check 실패: {e}')
        return False


def main(dry_run=False):
    print('=== Kakao Ventures D+10 close out ===')
    svc = load_service()

    if has_reply(svc):
        print('  [SKIP] 이미 카카오벤처스 측 회신 있음.')
        return None

    msg = MIMEText(BODY, 'plain', 'utf-8')
    msg['From'] = f'{FROM_NAME} <{FROM_EMAIL}>'
    msg['To'] = TO_EMAIL
    msg['Subject'] = SUBJECT

    if dry_run:
        print('  [DRY RUN] 발송 스킵, draft 검토용')
        print(BODY)
        return None

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    res = svc.users().messages().send(
        userId='me',
        body={'raw': raw, 'threadId': ORIGINAL_THREAD_ID}
    ).execute()
    print(f'  [SENT] message_id={res.get("id")}')
    return res.get('id')


if __name__ == '__main__':
    dry = '--dry' in sys.argv
    main(dry_run=dry)
