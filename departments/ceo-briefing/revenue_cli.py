#!/usr/bin/env python3
"""
수익 기록 CLI — 어느 부서든 판매 생기면 한 줄 명령으로 기록

사용법:
  python revenue_cli.py ebook 9900 "블로그 프롬프트" --channel 크티
  python revenue_cli.py tax 15000 "환급 신청 수수료" --count 1
  python revenue_cli.py coupang 2500 "제휴 수수료" --channel telegram01
  python revenue_cli.py cheonmyeongdang 29900 "프리미엄 사주" --customer 홍*
  python revenue_cli.py insurance 29000 "설계사 월구독"
  python revenue_cli.py kdp 3500 "AI Side Hustle" --channel Amazon

목록:
  python revenue_cli.py --list
  python revenue_cli.py --show ebook
"""
import sys
import json
import os
import argparse
from datetime import datetime, date
from zoneinfo import ZoneInfo

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
KST = ZoneInfo('Asia/Seoul')

DEPT_PATHS = {
    "ebook":            "departments/digital-products/prompts/revenue.json",
    "kdp":              "departments/digital-products/kdp/revenue.json",
    "coupang":          "departments/media/src/coupang_revenue.json",
    "tax":              "departments/tax/data/revenue.json",
    "cheonmyeongdang":  "departments/cheonmyeongdang/data/revenue.json",
    "insurance":        "departments/insurance-daboyeo/data/revenue.json",
}


def load(dept):
    p = os.path.join(ROOT, DEPT_PATHS[dept])
    if not os.path.exists(p):
        return _empty()
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def save(dept, data):
    p = os.path.join(ROOT, DEPT_PATHS[dept])
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _empty():
    return {'today': 0, 'week': 0, 'month': 0, 'total': 0,
            'count_today': 0, 'count_month': 0,
            'last_updated': None, 'events': []}


def add_revenue(dept, amount, product, channel=None, customer=None, count=1, note=None):
    if dept not in DEPT_PATHS:
        print(f'[ERROR] 알 수 없는 부서: {dept}')
        print(f'  사용 가능: {list(DEPT_PATHS.keys())}')
        sys.exit(1)

    data = load(dept)
    now = datetime.now(KST)

    # 이벤트 추가
    event = {
        'at': now.isoformat(),
        'amount': amount,
        'product': product,
    }
    if channel: event['channel'] = channel
    if customer: event['customer'] = customer
    if note: event['note'] = note
    data['events'].append(event)

    # 집계 업데이트
    today_str = now.date().isoformat()
    last = data.get('last_updated')
    if last:
        last_date = last[:10]
        if last_date != today_str:
            # 다른 날이면 today 리셋
            data['today'] = 0
            data['count_today'] = 0
        # 월 리셋 확인
        if last[:7] != today_str[:7]:
            data['month'] = 0
            data['count_month'] = 0

    data['today'] = data.get('today', 0) + amount
    data['month'] = data.get('month', 0) + amount
    data['total'] = data.get('total', 0) + amount
    data['count_today'] = data.get('count_today', 0) + count
    data['count_month'] = data.get('count_month', 0) + count
    data['last_updated'] = now.isoformat()

    save(dept, data)
    print(f'[OK] {dept}: +{amount:,}원 기록')
    print(f'     오늘 합계: {data["today"]:,}원 ({data["count_today"]}건)')
    print(f'     이달 합계: {data["month"]:,}원 ({data["count_month"]}건)')


def show(dept):
    data = load(dept)
    print(f'[{dept}]')
    print(f'  오늘: {data.get("today", 0):,}원 ({data.get("count_today", 0)}건)')
    print(f'  이달: {data.get("month", 0):,}원 ({data.get("count_month", 0)}건)')
    print(f'  누적: {data.get("total", 0):,}원')
    print(f'  마지막 업데이트: {data.get("last_updated", "없음")}')
    print(f'  이벤트: {len(data.get("events", []))}건')


def list_all():
    total_today = 0
    total_month = 0
    print(f'{"부서":<20} {"오늘":>12} {"이달":>14} {"누적":>16}')
    print('─' * 66)
    for dept in DEPT_PATHS:
        data = load(dept)
        t = data.get('today', 0)
        m = data.get('month', 0)
        tot = data.get('total', 0)
        total_today += t
        total_month += m
        print(f'{dept:<20} {t:>11,}원 {m:>13,}원 {tot:>15,}원')
    print('─' * 66)
    print(f'{"합계":<20} {total_today:>11,}원 {total_month:>13,}원')


def main():
    parser = argparse.ArgumentParser(description='쿤스튜디오 부서별 수익 기록 CLI')
    parser.add_argument('dept', nargs='?', help='부서 (ebook/kdp/coupang/tax/cheonmyeongdang/insurance)')
    parser.add_argument('amount', nargs='?', type=int, help='금액 (원)')
    parser.add_argument('product', nargs='?', help='상품명')
    parser.add_argument('--channel', help='판매 채널')
    parser.add_argument('--customer', help='고객 (익명 해시 권장)')
    parser.add_argument('--count', type=int, default=1, help='건수 (기본 1)')
    parser.add_argument('--note', help='메모')
    parser.add_argument('--list', action='store_true', help='전체 부서 요약')
    parser.add_argument('--show', help='특정 부서 상세')

    args = parser.parse_args()

    if args.list:
        list_all()
        return
    if args.show:
        show(args.show)
        return

    if not all([args.dept, args.amount, args.product]):
        parser.print_help()
        sys.exit(1)

    add_revenue(args.dept, args.amount, args.product,
                channel=args.channel, customer=args.customer,
                count=args.count, note=args.note)


if __name__ == '__main__':
    main()
