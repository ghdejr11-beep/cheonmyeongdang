#!/usr/bin/env python3
"""
천명당 영수증 이메일 발송용 — Gmail OAuth 재인증 (gmail.send scope 추가)

사용법:
  python authorize_gmail_send.py

동작:
  1) credentials.json (secretary 부서 OAuth Client) 로드
  2) gmail.modify + gmail.send scope 로 OAuth 흐름 시작 → 브라우저 열림
  3) ghdejr11@gmail.com 으로 로그인 + 권한 동의
  4) token_send.json 으로 저장 (기존 token.json 은 건드리지 않음)
  5) refresh_token / client_id / client_secret 출력 → Vercel 환경변수에 그대로 입력
"""
import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token_send.json')

# gmail.send 만 있으면 충분 (영수증 발송 전용)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def main():
    if not os.path.exists(CREDENTIALS_FILE):
        print(f'[ERR] credentials.json 없음: {CREDENTIALS_FILE}', file=sys.stderr)
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0, prompt='consent', access_type='offline')

    data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes or []),
        'expiry': creds.expiry.isoformat() + 'Z' if creds.expiry else None,
    }
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print()
    print('=' * 60)
    print('  ✅ Gmail send 권한 발급 완료')
    print('=' * 60)
    print(f'저장 위치: {TOKEN_FILE}')
    print()
    print('▼ Vercel 환경변수에 추가할 값 (cheonmyeongdang.com 프로젝트)')
    print('-' * 60)
    print(f'GMAIL_FROM={data["client_id"].split("-")[0] and "ghdejr11@gmail.com"}')
    print(f'GMAIL_OAUTH_CLIENT_ID={data["client_id"]}')
    print(f'GMAIL_OAUTH_CLIENT_SECRET={data["client_secret"]}')
    print(f'GMAIL_OAUTH_REFRESH_TOKEN={data["refresh_token"]}')
    print('-' * 60)
    print()
    print('▼ Vercel CLI 로 추가 (권장):')
    print('  cd C:\\Users\\hdh02\\Desktop\\cheonmyeongdang')
    print(f'  vercel env add GMAIL_FROM production       # ghdejr11@gmail.com')
    print(f'  vercel env add GMAIL_OAUTH_CLIENT_ID production')
    print(f'  vercel env add GMAIL_OAUTH_CLIENT_SECRET production')
    print(f'  vercel env add GMAIL_OAUTH_REFRESH_TOKEN production')
    print(f'  vercel --prod --yes')
    print()


if __name__ == '__main__':
    main()
