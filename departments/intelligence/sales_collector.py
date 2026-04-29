#!/usr/bin/env python3
"""
통합 판매 수집 에이전트 (v1 스켈레톤)
— 모든 서비스 일일 매출·사용자 수를 한 곳에 모아 텔레그램 리포트

현재 상태:
  - 🎮 HexDrop: Play Console API (미구현, 수동 입력 대체)
  - 📖 KDP: KDP Reports (미구현, 수동 입력 대체)
  - 🔮 천명당: Firebase Analytics (미구현)
  - 💰 세금N혜택: 자체 DB (아직 런칭 전)
  - 🔍 KORLENS: Vercel Analytics (API 구현 가능)
  - 🎨 크티/Etsy: 각 플랫폼 API (미구현)

v1: 수동 매출 입력 JSON(manual_sales.json) + Vercel 트래픽만 자동
v2: 각 플랫폼 API 연동

Usage:
  python sales_collector.py          # 일일 리포트 생성 + 텔레그램
  python sales_collector.py --input  # manual 수동 입력 프롬프트
"""
import os
import sys
import json
import requests
from datetime import date, datetime

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
DATA_DIR = os.path.join(ROOT, 'departments/intelligence/data')
MANUAL_FILE = os.path.join(DATA_DIR, 'manual_sales.json')
REPORT_DIR = os.path.join(DATA_DIR, 'sales_reports')
os.makedirs(REPORT_DIR, exist_ok=True)

env = {}
secrets_path = os.path.join(ROOT, '.secrets')
if os.path.exists(secrets_path):
    for line in open(secrets_path, encoding='utf-8'):
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v
TG_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = env.get('TELEGRAM_CHAT_ID', '')
VERCEL_TOKEN = env.get('VERCEL_TOKEN', '')

SERVICES = [
    {'key': 'hexdrop', 'name': '🎮 HexDrop', 'platform': 'Play Store'},
    {'key': 'ebook', 'name': '📖 전자책 (KDP)', 'platform': 'Amazon KDP'},
    {'key': 'cheonmyeongdang', 'name': '🔮 천명당 사주', 'platform': 'Android'},
    {'key': 'taxnbenefit', 'name': '💰 세금N혜택', 'platform': 'Vercel'},
    {'key': 'korlens', 'name': '🔍 KORLENS', 'platform': 'Vercel'},
    {'key': 'prompts', 'name': '🎨 크티 프롬프트', 'platform': '크티'},
    {'key': 'etsy', 'name': '🎨 Etsy', 'platform': 'Etsy'},
]


def send_telegram(text):
    if not TG_TOKEN or not TG_CHAT:
        print(text)
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML'},
            timeout=10,
        )
    except Exception as e:
        print(f'[TG ERROR] {e}')


def load_manual():
    """수동으로 입력한 어제 판매 데이터"""
    if os.path.exists(MANUAL_FILE):
        with open(MANUAL_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_manual(data):
    with open(MANUAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def prompt_input():
    """대화형으로 어제 판매 입력"""
    print('=== 어제 판매 데이터 수동 입력 ===')
    print('(건너뛰려면 빈 Enter)')
    today = date.today().isoformat()
    data = load_manual()
    data[today] = data.get(today, {})
    for svc in SERVICES:
        prev = data[today].get(svc['key'], {})
        r = input(f"{svc['name']} [{svc['platform']}] 매출(원, 건수): ").strip()
        if not r:
            continue
        parts = r.replace(',', ' ').split()
        try:
            revenue = int(parts[0]) if parts else 0
            count = int(parts[1]) if len(parts) > 1 else None
            data[today][svc['key']] = {'revenue': revenue, 'count': count}
        except ValueError:
            print('  입력 형식 오류, 건너뜀')
    save_manual(data)
    print(f'저장 완료: {MANUAL_FILE}')


def fetch_vercel_analytics(project_id: str):
    """Vercel 트래픽/배포 — ceo-briefing/integrations/vercel_analytics 위임.

    ⚠️ Vercel Web Analytics PV/UV 는 공식 REST API 미지원 (2026-04 기준).
    배포 통계만 자동, PV/UV 는 Drain JSON 또는 GA4 fallback.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, 'departments/ceo-briefing'))
        from integrations import vercel_analytics  # type: ignore
        snap = vercel_analytics.fetch_vercel_daily(project_ids=[project_id])
        return snap.get("projects", {}).get(project_id)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:160]}"}


def build_report(for_date: str = None):
    for_date = for_date or date.today().isoformat()
    manual = load_manual().get(for_date, {})

    lines = [f'💰 <b>일일 매출·트래픽 리포트 · {for_date}</b>', '']
    total = 0
    has_data = False

    for svc in SERVICES:
        entry = manual.get(svc['key'])
        if entry:
            rev = entry.get('revenue', 0)
            count = entry.get('count')
            total += rev
            has_data = True
            cstr = f' · {count}건' if count is not None else ''
            lines.append(f"{svc['name']}: {rev:,}원{cstr}")
        else:
            lines.append(f"{svc['name']}: <i>데이터 없음</i>")

    lines.append('')
    lines.append(f'💎 <b>합계: {total:,}원</b>')
    if not has_data:
        lines.append('')
        lines.append('⚠️ 수동 입력 필요: <code>python sales_collector.py --input</code>')

    return '\n'.join(lines)


def run():
    report = build_report()
    # 리포트 저장
    today = date.today().isoformat()
    with open(os.path.join(REPORT_DIR, f'{today}.txt'), 'w', encoding='utf-8') as f:
        f.write(report)
    send_telegram(report)
    return report


if __name__ == '__main__':
    if '--input' in sys.argv:
        prompt_input()
    else:
        r = run()
        print(r)
