"""KoDATA D+7 follow-up (5/14 09:00) — 결과 안 왔으면 follow-up 메일 draft."""
import os, sys, json, urllib.request, urllib.parse, base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent
CHEON = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
TOKEN = ROOT / "token.json"

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def load_secrets():
    env = {}
    p = CHEON / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_service():
    with open(TOKEN, 'r', encoding='utf-8') as f:
        d = json.load(f)
    creds = Credentials(
        token=d.get('token'), refresh_token=d.get('refresh_token'),
        token_uri=d.get('token_uri'), client_id=d.get('client_id'),
        client_secret=d.get('client_secret'), scopes=d.get('scopes'),
    )
    return build('gmail', 'v1', credentials=creds)


def telegram(env, text):
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat = env.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        return False
    body = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=body, method="POST")
    try:
        urllib.request.urlopen(req, timeout=15).read()
        return True
    except Exception:
        return False


def main():
    env = load_secrets()
    svc = load_service()

    res = svc.users().messages().list(
        userId='me',
        q='(from:kodata.co.kr OR from:85343@ OR from:xn--2n1bp39a0wfq1b) newer_than:9d',
        maxResults=20,
    ).execute()
    msgs = res.get('messages', [])
    print(f'[D+7] KoDATA 수신: {len(msgs)}건')

    if msgs:
        text = """🎯 KoDATA D+7 (5/14) — 응답 확인됨

5/7 정정 발송 후 1주일. KoDATA 회신 {n}건.

✅ 액션:
1) 처리 완료 여부 확인
2) 완료라면 → 즉시 투어라즈 가입 + 관광 AI 신청 (5/20 마감 D-6)
3) 추가 보완 요구라면 → 즉시 답신 → 5/15까지 보완 마감""".format(n=len(msgs))
        telegram(env, text)
        return

    # 회신 없음 — follow-up draft 작성
    body_text = """안녕하세요, 한국평가데이터 담당자님.

5/7 16:34 발송한 쿤스튜디오 기업정보 등록의뢰서 정정본 (85343@xn--2n1bp39a0wfq1b.co.kr 수신)에 대한 처리 진행 상황을 문의드립니다.

처리 기간(1주일) 경과로 5/14 기준 회신을 받지 못한 상황입니다.

추가 보완 필요사항 있으시면 즉시 회신 또는 02-3279-6500 통화 부탁드립니다.

5/20 한국관광공사 관광 AI 신청 마감을 앞두고 KoDATA 등록이 선결조건이라 시급합니다.

감사합니다.

쿤스튜디오 대표 홍덕훈
사업자등록번호: 552-59-00848
이메일: ghdejr11@gmail.com
전화: 070-8018-7832
"""

    msg = MIMEMultipart()
    msg['To'] = '85343@xn--2n1bp39a0wfq1b.co.kr'
    msg['Cc'] = 'find@kodata.co.kr'
    msg['From'] = '"쿤스튜디오 홍덕훈" <ghdejr11@gmail.com>'
    msg['Subject'] = '[처리 상태 문의] 기업정보등록-한국관광공사-쿤스튜디오 (5/7 정정 발송 D+7)'
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    draft = svc.users().drafts().create(
        userId='me', body={'message': {'raw': raw}}
    ).execute()
    draft_id = draft.get('id')
    print(f'[DRAFT] {draft_id}')

    text = f"""🚨 KoDATA D+7 (5/14) — 1주일 회신 없음

처리 기간 만료, follow-up draft 자동 작성:
Draft ID: {draft_id}

✅ 즉시 액션:
1) 02-3279-6500 통화 (담당 직통, 우선)
2) Gmail 임시보관함 → draft SEND
3) 통과 안 되면 5/20 관광 AI 신청 위험

📅 D-6 (5/20): 관광 AI(KORLENS) 신청 마감"""
    telegram(env, text)


if __name__ == '__main__':
    main()
