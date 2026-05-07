"""Kakao Ventures D+5 follow-up (예정 발송: 2026-05-12 09:00).

원 메일 thread에 reply (In-Reply-To). 응답 없으면 정중 push.
실행 시 응답 여부를 자동 체크하고 응답 있으면 skip.
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
ORIGINAL_THREAD_ID = '19e006f9ff81e2ab'  # 5/7 발송 thread

SUBJECT = 'Re: [Seed 제안] 천명당 - 1주차 업데이트 (AppSumo D-8, K-Startup grant 진행)'

BODY = """안녕하세요, 카카오벤처스 팀.

지난 5/7 발송 메일에 대한 1주차 업데이트입니다.

【지난 주 진척】
- AppSumo LTD 5/20 출시 D-8 (스토어 페이지 검토 진행)
- K-Startup AI리그 5/20 마감 - 사업계획서 finalize 단계
- Pinterest 4언어 53핀 큐 → 발행 시작, 첫 organic impression 데이터 수집 중
- Etsy 40 SKU 라이브, Gumroad 18 SKU 검수 통과

【30분 미팅 요청】
지난 메일에서 5/12~5/16 중 시간 알려주시면 라이브 데모 + 콘솔 보여드린다고 했습니다.
이번 주 늦은 시간이라도 조정 가능합니다 (저녁/주말 OK).

만약 검토하지 않으실 거면 한 줄 회신만 부탁드립니다 (다른 VC 컨택 우선순위 조정 위함).

라이브: https://cheonmyeongdang.vercel.app

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
    """원 thread에 카벤 측 회신이 있으면 True."""
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
    print('=== Kakao Ventures D+5 follow-up ===')
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
