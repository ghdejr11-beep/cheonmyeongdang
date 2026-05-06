#!/usr/bin/env python3
"""
텔레그램 봇 — 어디서든 수익 기록

명령어:
  /revenue ebook 9900 블로그프롬프트
  /revenue tax 15000 환급수수료
  /revenue coupang 2500 제휴
  /status  (오늘/이달 전체 부서 요약)
  /report  (리포트 즉시 발송)

백그라운드로 실행:
  python -X utf8 telegram_bot.py &
"""
import os
import sys
import json
import time
import requests
import subprocess

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
SECRETS = os.path.join(ROOT, '.secrets')

env = {}
for line in open(SECRETS, encoding='utf-8'):
    if '=' in line:
        k, v = line.strip().split('=', 1)
        env[k] = v

TOKEN = env['TELEGRAM_BOT_TOKEN']
ALLOWED_CHAT = int(env['TELEGRAM_CHAT_ID'])
BASE = f'https://api.telegram.org/bot{TOKEN}'

OFFSET_FILE = os.path.join(ROOT, 'departments/ceo-briefing/bot_offset.txt')


def get_offset():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE) as f:
            return int(f.read().strip() or 0)
    return 0


def set_offset(o):
    with open(OFFSET_FILE, 'w') as f:
        f.write(str(o))


def send(chat_id, text):
    requests.post(f'{BASE}/sendMessage', data={
        'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'
    })


PHOTO_DIR = os.path.join(ROOT, 'departments/telegram_inbox/photos')


def save_photo(msg):
    """Download photo from Telegram → /telegram_inbox/photos/."""
    os.makedirs(PHOTO_DIR, exist_ok=True)
    photos = msg.get('photo', [])
    if not photos:
        return None
    # highest resolution = largest file_size
    photos = sorted(photos, key=lambda p: p.get('file_size', 0), reverse=True)
    file_id = photos[0]['file_id']
    info = requests.get(f'{BASE}/getFile', params={'file_id': file_id}).json()
    if not info.get('ok'):
        return None
    file_path = info['result']['file_path']
    ext = file_path.rsplit('.', 1)[-1] if '.' in file_path else 'jpg'
    msg_id = msg.get('message_id', 'unknown')
    out = os.path.join(PHOTO_DIR, f'photo_{msg_id}.{ext}')
    img = requests.get(f'https://api.telegram.org/file/{TOKEN.split(":")[0] and "bot"+TOKEN}/{file_path}').content
    with open(out, 'wb') as f:
        f.write(img)
    # also save as latest.jpg
    latest = os.path.join(PHOTO_DIR, f'latest.{ext}')
    with open(latest, 'wb') as f:
        f.write(img)
    return out


def handle(msg):
    chat_id = msg['chat']['id']
    if chat_id != ALLOWED_CHAT:
        return

    # Handle photos first (no text)
    if msg.get('photo'):
        try:
            saved = save_photo(msg)
            if saved:
                send(chat_id, f'📷 사진 받았어요!\n저장: <code>{saved}</code>\n다음 Claude 세션에서 사용 가능.')
                return
        except Exception as e:
            send(chat_id, f'⚠️ 사진 저장 실패: {e}')
            return

    text = msg.get('text', '').strip()
    if not text.startswith('/'):
        return

    parts = text.split()
    cmd = parts[0].lower()

    if cmd == '/revenue':
        if len(parts) < 4:
            send(chat_id, '<b>사용법:</b>\n<code>/revenue [부서] [금액] [상품명]</code>\n\n부서: ebook, kdp, coupang, tax, cheonmyeongdang, insurance')
            return
        dept = parts[1]
        try:
            amount = int(parts[2])
        except ValueError:
            send(chat_id, '금액은 숫자로 입력해주세요.')
            return
        product = ' '.join(parts[3:])

        cli = os.path.join(ROOT, 'departments/ceo-briefing/revenue_cli.py')
        result = subprocess.run(
            [sys.executable, '-X', 'utf8', cli, dept, str(amount), product],
            capture_output=True, text=True, encoding='utf-8'
        )
        send(chat_id, f'<pre>{result.stdout or result.stderr}</pre>')

    elif cmd == '/status' or cmd == '/list':
        cli = os.path.join(ROOT, 'departments/ceo-briefing/revenue_cli.py')
        result = subprocess.run(
            [sys.executable, '-X', 'utf8', cli, '--list'],
            capture_output=True, text=True, encoding='utf-8'
        )
        send(chat_id, f'<pre>{result.stdout}</pre>')

    elif cmd == '/report':
        rpt = os.path.join(ROOT, 'departments/ceo-briefing/revenue_report.py')
        subprocess.run([sys.executable, '-X', 'utf8', rpt])

    elif cmd == '/help' or cmd == '/start':
        send(chat_id,
            '<b>🏢 쿤스튜디오 수익 봇</b>\n\n'
            '<b>/revenue</b> [부서] [금액] [상품]\n'
            '  ex: <code>/revenue ebook 9900 블로그</code>\n\n'
            '<b>/status</b> — 전체 부서 요약\n'
            '<b>/report</b> — 상세 리포트 즉시 발송\n\n'
            '부서: ebook · kdp · coupang · tax · cheonmyeongdang · insurance'
        )


def run():
    offset = get_offset()
    print(f'Bot started. offset={offset}')
    while True:
        try:
            r = requests.get(f'{BASE}/getUpdates', params={
                'offset': offset + 1, 'timeout': 30
            }, timeout=40)
            data = r.json()
            for update in data.get('result', []):
                offset = max(offset, update['update_id'])
                set_offset(offset)
                if 'message' in update:
                    handle(update['message'])
        except Exception as e:
            print(f'ERROR: {e}')
            time.sleep(3)


if __name__ == '__main__':
    run()
