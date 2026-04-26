#!/usr/bin/env python3
"""
KORLENS 고객센터 자동 처리 에이전트
— 텔레그램 /korlens_support 메시지 수집 → 분류 → 자동 답변 또는 CEO 확인 큐

처리 흐름:
  1. faq         → FAQ DB 검색 후 자동 답변
  2. bug_report  → 버그 리포트 큐에 등록 + CEO 알림
  3. feature_req → 기능 요청 큐에 등록
  4. data_issue  → TourAPI 데이터 이슈 (cache 무효화 요청 등)
  5. general     → 일반 문의, 수동 처리 큐

ceo-briefing/support_agent.py 패턴을 KORLENS 전용으로 복제.
"""
import os
import json
import time
import requests
from datetime import datetime

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
QUEUE_FILE = os.path.join(ROOT, 'departments/korlens/support_queue.json')

env = {}
secrets_path = os.path.join(ROOT, '.secrets')
if os.path.exists(secrets_path):
    for line in open(secrets_path, encoding='utf-8'):
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

TG_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = env.get('TELEGRAM_CHAT_ID', '')

# KORLENS FAQ - 자주 묻는 질문 자동 응답
FAQ = {
    '무료': '네, KORLENS는 완전 무료입니다. 로그인 없이 사용 가능합니다.',
    '영어': '상세 페이지에서 🇬🇧 View in English 버튼을 눌러 주세요. 한국관광공사 영문 데이터가 실시간으로 표시됩니다.',
    'english': 'Click the "🇬🇧 View in English" button on any place detail page. KORLENS uses official Korean Tourism Organization English data.',
    '지역': '현재 17개 광역시도 전체를 지원합니다. 각 지역마다 외국인·커플·가족·솔로 4가지 관점으로 장소를 재해석해 보여드려요.',
    '혼잡도': '각 장소마다 한산/보통/붐빔 3단계 혼잡도 필터를 제공합니다. 유형별로 기본값이 자동 적용돼요 (솔로→한산 우선).',
    '무장애': '장소 상세 페이지에 열린관광 API 기반 무장애 편의시설(휠체어·유모차·수유실 등) 태그가 표시됩니다.',
    '챗봇': 'AI 큐레이터는 "내일 서울 커플 4시간" 같은 자연어 질의에 실제 TourAPI 장소로 답해드립니다. 상단 🤖 AI 큐레이터 버튼을 눌러보세요.',
    '배포': 'https://korlens.vercel.app — Vercel icn1 (서울) 리전 배포.',
}


def send_telegram(text):
    if not TG_TOKEN or not TG_CHAT:
        print('[WARN] Telegram credentials missing, printing instead:')
        print(text)
        return
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
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def classify(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ['버그', '오류', 'error', '안 됨', '안돼', '크래시', '깨짐']):
        return 'bug_report'
    if any(w in msg for w in ['기능', '추가해', '있었으면', 'feature', '제안']):
        return 'feature_req'
    if any(w in msg for w in ['데이터', '틀린', '이상한', '없어진', '업데이트']):
        return 'data_issue'
    if any(kw in msg for kw in FAQ.keys()):
        return 'faq'
    return 'general'


def answer_faq(message: str) -> str | None:
    msg = message.lower()
    for kw, answer in FAQ.items():
        if kw in msg:
            return f'[KORLENS] {answer}'
    return None


def enqueue(ticket: dict):
    """웹폼/API에서 고객 요청 받으면 큐에 추가"""
    queue = load_queue()
    ticket['id'] = f'KLT{int(time.time())}'
    ticket['created_at'] = datetime.now().isoformat()
    ticket['category'] = classify(ticket.get('message', ''))
    ticket['status'] = 'pending'

    # FAQ는 즉시 자동 응답
    if ticket['category'] == 'faq':
        auto = answer_faq(ticket['message'])
        if auto:
            ticket['auto_response'] = auto
            ticket['status'] = 'auto_resolved'

    queue.append(ticket)
    save_queue(queue)
    return ticket


def notify_ceo(ticket: dict):
    """bug/feature/data_issue는 CEO에게 즉시 알림"""
    emoji = {
        'bug_report': '🐛',
        'feature_req': '💡',
        'data_issue': '📊',
        'general': '💬',
    }.get(ticket['category'], '📨')
    text = (
        f"{emoji} <b>KORLENS {ticket['category']}</b>\n"
        f"ID: {ticket['id']}\n"
        f"메시지: {ticket.get('message', '')[:300]}"
    )
    send_telegram(text)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # 테스트 티켓
        t = enqueue({'message': '영어로 보고 싶어요', 'user': 'test'})
        print('티켓 생성:', t)
    elif len(sys.argv) > 1 and sys.argv[1] == 'list':
        queue = load_queue()
        print(f'총 {len(queue)}개 티켓')
        for t in queue[-10:]:
            print(f"  [{t['category']}] {t['id']}: {t.get('message', '')[:60]}")
    else:
        print('Usage: support_agent.py [test|list]')
