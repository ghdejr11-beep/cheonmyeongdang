"""5/7 Gmail OAuth 토큰 재발급.

기존 token.json + token_send.json refresh_token 이 Google 에 의해 revoke 됨
(OAuth 앱 'Testing' 상태에서 7일 후 자동 만료, 5/6 만료 추정).

사용자 액션 1번: 브라우저 OAuth 동의 화면에서 '허용' 클릭
→ 두 토큰 (read+modify, send) 모두 1회 OAuth 로 갱신.

실행:
  python departments/secretary/reauth_2026_05_07.py
"""
import os
import sys
import json

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from google_auth_oauthlib.flow import InstalledAppFlow

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CRED = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_READ = os.path.join(SCRIPT_DIR, 'token.json')
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token_send.json')

# 통합 scope: read+modify+send 모두 한 번에
COMBINED_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
]


def save_token(creds, path, scopes):
    out = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': scopes,
        'expiry': creds.expiry.isoformat() + 'Z' if creds.expiry else None,
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'[OK] saved: {path}')


def main():
    print('=== Gmail OAuth 재인증 ===')
    print('브라우저가 열립니다. 구글 계정 ghdejr11@gmail.com 로 로그인 후 "허용" 클릭하세요.\n')
    flow = InstalledAppFlow.from_client_secrets_file(CRED, COMBINED_SCOPES)
    creds = flow.run_local_server(port=0)

    # 같은 토큰을 두 파일에 저장 (scope 분리해서 기존 코드 호환)
    save_token(creds, TOKEN_READ,
               ['https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify'])
    save_token(creds, TOKEN_SEND,
               ['https://www.googleapis.com/auth/gmail.send'])
    print('\n=== 완료 ===')
    print('이제 다음을 실행하세요:')
    print('  python departments/secretary/scan_inbox_2026_05_07.py')


if __name__ == '__main__':
    main()
