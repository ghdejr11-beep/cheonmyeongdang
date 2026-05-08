#!/usr/bin/env python3
"""
고객센터 자동 처리 에이전트
— 텔레그램 /support 메시지 수집 → Claude에게 판단 요청 → 자동 처리

처리 흐름:
  1. auto_fix     → Claude Agent가 코드 PR 생성 + git push
  2. bug_report   → Claude Agent가 로그 분석 + 수정
  3. needs_approval → CEO에게 "수정할까요?" 물어봄
  4. reject       → 자동 거부 답변
  5. general      → FAQ DB 검색 후 자동 답변

Claude Agent SDK가 실제 수정까지 실행. 이 파일은 큐 관리.
"""
import os
import json
import time
import requests
import subprocess
from datetime import datetime

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
QUEUE_FILE = os.path.join(ROOT, 'departments/ceo-briefing/support_queue.json')

env = {}
for line in open(os.path.join(ROOT, '.secrets'), encoding='utf-8'):
    if '=' in line:
        k, v = line.strip().split('=', 1)
        env[k] = v

TG_TOKEN = env['TELEGRAM_BOT_TOKEN']
TG_CHAT = env['TELEGRAM_CHAT_ID']


def send_telegram(text):
    requests.post(
        f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
        data={'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML'}
    )


def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []


def save_queue(queue):
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def enqueue(ticket):
    """웹폼/API에서 고객 요청 받으면 큐에 추가"""
    queue = load_queue()
    ticket['id'] = f'T{int(time.time())}'
    ticket['created_at'] = datetime.now().isoformat()
    ticket['status'] = 'pending'
    queue.append(ticket)
    save_queue(queue)
    return ticket['id']


def process_ticket(ticket):
    """각 분류별 처리 로직"""
    tid = ticket['id']
    clf = ticket.get('classification', 'general')

    if clf == 'reject':
        # 자동 거부
        send_telegram(f'🚫 티켓 {tid} 자동 거부 (스팸/부적절)')
        ticket['status'] = 'rejected'
        ticket['resolution'] = '자동 거부'
        return

    if clf == 'auto_fix':
        # Claude Agent가 실제 수정 PR 생성 (claude CLI subprocess 호출)
        send_telegram(
            f'🔧 티켓 {tid} 자동수정 시작\n'
            f'제목: {ticket["title"]}\n'
            f'Claude Agent가 분석·수정 PR을 만들 예정'
        )
        try:
            import subprocess, shutil
            claude_bin = shutil.which('claude') or 'claude'
            prompt = (
                f"고객 티켓 #{tid}: {ticket['title']}\n"
                f"내용: {ticket.get('content','')[:1000]}\n\n"
                f"이 티켓을 분석해서 실제 코드/문서 수정이 필요하면 적절한 변경을 만들고 "
                f"새 브랜치(autofix/ticket-{tid})에 커밋한 뒤 PR을 생성하세요. "
                f"수정이 필요 없으면 분석 결과만 보고하세요."
            )
            # 비동기 spawn — 응답 안 기다림 (긴 작업)
            subprocess.Popen(
                [claude_bin, '-p', prompt],
                cwd=r'D:\cheonmyeongdang',
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0),
            )
            ticket['status'] = 'auto_fix_running'
            ticket['claude_invoked_at'] = datetime.datetime.now().isoformat()
        except Exception as e:
            send_telegram(f'⚠️ 티켓 {tid} claude CLI 호출 실패: {str(e)[:200]}')
            ticket['status'] = 'auto_fix_failed'
        return

    if clf == 'needs_approval':
        # CEO에게 인터랙티브 질문
        send_telegram(
            f'🤔 <b>CEO 판단 필요</b> (티켓 {tid})\n\n'
            f'{ticket["title"]}\n\n'
            f'{ticket["content"][:300]}\n\n'
            f'답변: /approve {tid} (승인) / /reject {tid} (거부)'
        )
        ticket['status'] = 'awaiting_ceo'
        return

    if clf == 'bug_report':
        send_telegram(
            f'🐞 티켓 {tid} 버그 분석 시작\n'
            f'{ticket["title"]}'
        )
        ticket['status'] = 'bug_investigating'
        return

    # general
    send_telegram(f'💬 티켓 {tid}: {ticket["title"][:50]}')
    ticket['status'] = 'pending_manual'


def process_pending():
    queue = load_queue()
    changed = False
    for t in queue:
        if t.get('status') == 'pending':
            process_ticket(t)
            changed = True
    if changed:
        save_queue(queue)


def list_tickets():
    queue = load_queue()
    print(f'총 티켓: {len(queue)}건')
    for t in queue:
        print(f'  [{t["id"]}] {t.get("status", "?")} - {t.get("title", "")[:50]}')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_tickets()
    elif len(sys.argv) > 1 and sys.argv[1] == 'process':
        process_pending()
    else:
        print('Usage: python support_agent.py [list|process]')
