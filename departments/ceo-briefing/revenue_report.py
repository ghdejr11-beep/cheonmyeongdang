#!/usr/bin/env python3
"""
부서별 수익 현황 일일 리포트 — 텔레그램 자동 발송

지원 부서:
- 크티 (프롬프트팩 9종)
- 쿠팡 파트너스 (7개 채널 ID)
- 세금N혜택 (사전예약 수)
- 천명당 Play Store (유료 구매)
- KDP 전자책 (해외 판매)
- 보험다보여 (설계사 구독)

각 부서는 자체 API/파일로 수익 데이터 제공.
CRON: 매일 아침 9시 발송 (schtasks.exe로 등록)
"""
import requests
import json
import os
import sys
from datetime import datetime, date

# .secrets 로드
SECRETS = os.path.expanduser('~/Desktop/cheonmyeongdang/.secrets')
env = {}
if os.path.exists(SECRETS):
    for line in open(SECRETS, encoding='utf-8'):
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

TG_BOT_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT_ID = env.get('TELEGRAM_CHAT_ID', '')

# 부서별 수익 소스 정의
# 실제 데이터는 각 부서가 data/revenue.json에 매일 적재해야 함 (수동 또는 자동)

DEPARTMENTS = {
    "ebook": {
        "name": "📚 디지털상품부 (크티 9종)",
        "file": "departments/digital-products/prompts/revenue.json",
        "note": "크티 판매자센터에서 수동 업데이트",
    },
    "coupang": {
        "name": "🛒 쿠팡 파트너스 (7채널)",
        "file": "departments/media/src/coupang_revenue.json",
        "note": "쿠팡 파트너스 리포트 월말 확정",
    },
    "tax": {
        "name": "💰 세금N혜택",
        "file": "departments/tax/data/revenue.json",
        "note": "CODEF 승인 전: 사전예약 수만 집계",
    },
    "cheonmyeongdang": {
        "name": "🔮 천명당 (Play Store)",
        "file": "departments/cheonmyeongdang/data/revenue.json",
        "note": "토스페이먼츠 Webhook 연동 필요",
    },
    "insurance": {
        "name": "🛡️ 보험다보여",
        "file": "departments/insurance-daboyeo/data/revenue.json",
        "note": "설계사 구독 수 (월 29,000원/명)",
    },
    "kdp": {
        "name": "📖 KDP 전자책",
        "file": "departments/digital-products/kdp/revenue.json",
        "note": "Amazon KDP 리포트 월 2회 확정",
    },
}

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')


def load_revenue(dept_key):
    info = DEPARTMENTS[dept_key]
    path = os.path.join(ROOT, info['file'])
    if not os.path.exists(path):
        return {
            'today': 0, 'week': 0, 'month': 0, 'total': 0,
            'count_today': 0, 'count_month': 0,
            'status': 'not_set',
        }
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'today': 0, 'week': 0, 'month': 0, 'total': 0}


def format_won(n):
    if n == 0:
        return '0원'
    return f'{int(n):,}원'


def build_report():
    today = date.today()
    lines = [
        f'<b>📊 {today.strftime("%Y-%m-%d")} 부서별 수익 리포트</b>',
        '',
    ]

    grand_today = 0
    grand_month = 0

    for key, info in DEPARTMENTS.items():
        rev = load_revenue(key)
        lines.append(f'<b>{info["name"]}</b>')
        if rev.get('status') == 'not_set':
            lines.append(f'  <i>연동 대기 — {info["note"]}</i>')
        elif rev.get('status') == 'error':
            lines.append(f'  ⚠️ 에러: {rev.get("error")}')
        else:
            today_val = rev.get('today', 0)
            month_val = rev.get('month', 0)
            count_today = rev.get('count_today', 0)
            count_month = rev.get('count_month', 0)
            lines.append(f'  오늘: {format_won(today_val)} ({count_today}건)')
            lines.append(f'  이달: {format_won(month_val)} ({count_month}건)')
            grand_today += today_val
            grand_month += month_val
        lines.append('')

    lines.append('━━━━━━━━━━━━━━━━━━━━')
    lines.append(f'<b>🏢 쿤스튜디오 전체</b>')
    lines.append(f'  오늘: {format_won(grand_today)}')
    lines.append(f'  이달: {format_won(grand_month)}')
    lines.append('')

    # 100일 10억 진행률
    TARGET = 1_000_000_000
    start = date(2026, 4, 16)
    elapsed = (today - start).days + 1
    remaining = 100 - elapsed
    progress_pct = (grand_month / TARGET * 100) if TARGET else 0

    lines.append('━━━━━━━━━━━━━━━━━━━━')
    lines.append(f'<b>🎯 100일 10억 프로젝트</b>')
    lines.append(f'  D+{elapsed} / D-{remaining}')
    lines.append(f'  이달 목표 대비: {progress_pct:.2f}%')

    return '\n'.join(lines)


def send(text):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print('[ERROR] TELEGRAM_BOT_TOKEN/CHAT_ID 미설정')
        return False
    r = requests.post(
        f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage',
        data={'chat_id': TG_CHAT_ID, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': True},
    )
    return r.ok


def main():
    report = build_report()
    if '--dry' in sys.argv:
        print(report)
        return
    if send(report):
        print('[OK] 리포트 텔레그램 발송')
    else:
        print('[FAIL] 발송 실패')


if __name__ == '__main__':
    main()
