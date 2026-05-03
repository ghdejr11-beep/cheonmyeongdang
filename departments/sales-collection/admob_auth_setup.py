#!/usr/bin/env python3
"""
AdMob OAuth 1회 셋업 - 사용자 직접 실행 필수.

흐름:
1) Google Cloud Console (https://console.cloud.google.com)
   → API & Services → Credentials → "OAuth client ID" → Desktop app
   → JSON 다운로드 → 본 스크립트와 같은 폴더에 client_secret.json 저장
2) AdMob API 활성화: Library → AdMob API → Enable
3) 본 스크립트 실행:
       python admob_auth_setup.py
   브라우저가 열리면 ghdejr11@gmail.com 으로 로그인 + 권한 승인
4) 자동으로 token.json 저장됨 (.secrets 에 명시된 경로)
5) .secrets 에 다음 키 추가:
       ADMOB_PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX
       ADMOB_OAUTH_TOKEN_PATH=C:/Users/hdh02/Desktop/cheonmyeongdang/.secrets_admob_token.json
"""
import os
import sys
import json
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
DEFAULT_CLIENT_SECRET = BASE / "client_secret.json"
DEFAULT_TOKEN_OUT = Path(
    r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets_admob_token.json"
)
SECRETS_PATH = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets")
ADMOB_API_SCOPES = [
    "https://www.googleapis.com/auth/admob.readonly",
    # monetization scope: 광고 단위 자동 생성/수정/삭제용 (2026-05-01 추가)
    "https://www.googleapis.com/auth/admob.monetization",
    # report scope: networkReport / mediationReport 호출용
    "https://www.googleapis.com/auth/admob.report",
]


def _load_env():
    env = {}
    if SECRETS_PATH.exists():
        for line in SECRETS_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def main():
    env = _load_env()
    token_out_str = env.get("ADMOB_OAUTH_TOKEN_PATH")
    token_out = Path(token_out_str) if token_out_str else DEFAULT_TOKEN_OUT

    if not DEFAULT_CLIENT_SECRET.exists():
        print("[ERROR] client_secret.json 없음.")
        print(f"  → Google Cloud Console에서 OAuth Desktop client 생성 후")
        print(f"     이 경로에 저장: {DEFAULT_CLIENT_SECRET}")
        print()
        print("절차:")
        print("  1) https://console.cloud.google.com")
        print("  2) 프로젝트 선택 (또는 신규 생성)")
        print("  3) APIs & Services → Library → AdMob API → Enable")
        print("  4) APIs & Services → Credentials → Create Credentials")
        print("     → OAuth client ID → Application type: Desktop app")
        print("  5) JSON 다운로드 → client_secret.json 으로 저장")
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("[ERROR] google-auth-oauthlib 미설치.")
        print("  pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(DEFAULT_CLIENT_SECRET), ADMOB_API_SCOPES
    )
    # 로컬 서버 모드 (브라우저 자동 오픈, 콜백 자동 캡처)
    creds = flow.run_local_server(port=0, prompt="consent")

    token_out.parent.mkdir(parents=True, exist_ok=True)
    token_out.write_text(creds.to_json(), encoding="utf-8")
    print(f"[OK] 토큰 저장 완료: {token_out}")
    print()
    print("[다음 단계] .secrets 에 아래 키가 모두 있는지 확인:")
    print(f"  ADMOB_PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX  (AdMob 콘솔 → 계정 → 게시자 ID)")
    print(f"  ADMOB_OAUTH_TOKEN_PATH={token_out.as_posix()}")
    print()
    print("[테스트] python admob_collector.py")


if __name__ == "__main__":
    main()
