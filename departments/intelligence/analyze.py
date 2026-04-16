#!/usr/bin/env python3
"""
경쟁사 수익 기회 + 불만 분석 엔진
— 매주 실행하여 Claude Agent에게 분석 프롬프트 전달

작동 방식:
1. 이번 주 수집된 경쟁사 스냅샷 모음 (data/*_snapshot_*.json)
2. Claude Agent CLI (claude -p) 또는 Anthropic API 호출
3. 응답을 `insights_YYYY-WW.md`로 저장 + 텔레그램 발송

Manual 실행:
  python analyze.py           # 최근 7일 스냅샷 분석
  python analyze.py --daily   # 오늘 것만
"""
import os
import json
import glob
from datetime import datetime, date, timedelta
import requests

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
DATA_DIR = os.path.join(ROOT, 'departments/intelligence/data')
OUTPUT_DIR = os.path.join(ROOT, 'departments/intelligence/insights')
os.makedirs(OUTPUT_DIR, exist_ok=True)

env = {}
for line in open(os.path.join(ROOT, '.secrets'), encoding='utf-8'):
    if '=' in line:
        k, v = line.strip().split('=', 1)
        env[k] = v

TG_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = env.get('TELEGRAM_CHAT_ID', '')


def collect_snapshots(days=7):
    """최근 N일 스냅샷 전부 모음"""
    cutoff = date.today() - timedelta(days=days)
    snapshots = []
    for path in glob.glob(os.path.join(DATA_DIR, '*_snapshot_*.json')):
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            snap_date = datetime.fromisoformat(data['date']).date()
            if snap_date >= cutoff:
                snapshots.append(data)
        except Exception:
            continue
    return snapshots


def build_prompt(snapshots):
    """Claude에게 분석 요청할 프롬프트"""
    lines = ["다음은 쿤스튜디오의 5개 서비스에 대한 경쟁사 HTML 스크래핑 스냅샷이다.", ""]
    for s in snapshots:
        lines.append(f"\n## {s['dept']} ({s.get('label', '')})")
        lines.append(f"수집일: {s['date']}")
        for t in s['targets']:
            if not t['fetched']:
                continue
            lines.append(f"\n### {t['name']} ({t['url']})")
            for txt in t['texts'][:20]:
                lines.append(f"- {txt}")
    lines.append('''
---

위 데이터를 기반으로 "수익 기회 10개 + 고객 불만 10개"를 도출하라.

각 항목에:
1. 어느 경쟁사에서 발견
2. 내용 한 줄
3. 우리에게 주는 시사점
4. 실행 난이도 (쉬움/중간/어려움)

추가로 플레이스토어/앱스토어/커뮤니티에서 해당 경쟁사 **리뷰**를 웹 검색해서 실제 불만 데이터 수집.

마지막에 "지금 당장 실행 가능한 TOP 3" 요약.

마크다운 출력, 500~1000단어.
''')
    return '\n'.join(lines)


def send_tg(text):
    if not TG_TOKEN:
        return
    # 4000자 단위로 잘라서 발송
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for c in chunks:
        requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'text': c, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        )


def save_and_notify(content):
    today = date.today()
    week = today.strftime('%Y-W%W')
    out = os.path.join(OUTPUT_DIR, f'insights_{week}.md')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(f'# 경쟁사 분석 리포트 — {today.isoformat()}\n\n')
        f.write(content)
    print(f'[OK] 저장: {out}')

    # 텔레그램 발송
    tg_text = f'<b>🧠 경쟁사 분석 리포트 ({today})</b>\n\n{content[:3500]}...\n\n<i>전문은 insights/{week}.md</i>'
    send_tg(tg_text)


def main():
    snapshots = collect_snapshots(days=7)
    if not snapshots:
        print('[ERROR] 최근 7일 스냅샷 없음. watch.py 먼저 실행.')
        return

    prompt = build_prompt(snapshots)
    prompt_file = os.path.join(OUTPUT_DIR, f'prompt_{date.today().isoformat()}.txt')
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt)
    print(f'[OK] 분석 프롬프트 생성: {prompt_file}')
    print(f'[NEXT] Claude Code 수동 실행:')
    print(f'  claude -p "$(cat {prompt_file})" > {OUTPUT_DIR}/latest_result.md')
    print(f'  또는 Anthropic API 연동 후 자동화')


if __name__ == '__main__':
    main()
