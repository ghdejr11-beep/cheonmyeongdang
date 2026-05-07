"""5/7 OAuth reauth — Chrome MCP 자동 처리용 (webbrowser 자동 열기 OFF, URL을 stdout으로 출력)."""
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
    print(f'[OK] saved: {path}', flush=True)


def main():
    print('=== Gmail OAuth 재인증 (Chrome MCP 모드) ===', flush=True)
    flow = InstalledAppFlow.from_client_secrets_file(CRED, COMBINED_SCOPES)
    # open_browser=False → URL만 출력, 시스템 브라우저 안 열림
    creds = flow.run_local_server(port=0, open_browser=False)
    save_token(creds, TOKEN_READ,
               ['https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify'])
    save_token(creds, TOKEN_SEND,
               ['https://www.googleapis.com/auth/gmail.send'])
    print('[DONE] 두 토큰 모두 저장 완료. 영구 (프로덕션 모드).', flush=True)


if __name__ == '__main__':
    main()
