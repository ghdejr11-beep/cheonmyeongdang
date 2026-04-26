#!/usr/bin/env python3
"""
자동 보안 수정 — 안전한 것만 스스로 고침 (보고 없이)

수정 가능한 것:
  1. .env 파일이 git staged면 자동 unstage + .gitignore 추가
  2. npm audit fix (--force 없이 breaking-free만)
  3. .gitignore에 .env 없으면 자동 추가

위험한 것은 자동 수정 하지 않음:
  - 소스코드 내 시크릿 삭제 (사람 판단 필요)
  - git history 재작성
  - 의존성 major 업그레이드

Usage:
  python auto_fix.py              # 전체 프로젝트 자동 수정
  python auto_fix.py --dry-run    # 수정 안 하고 뭘 할지만 출력
"""
import os
import sys
import subprocess
import requests
from datetime import datetime
from pathlib import Path

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
DEPT_DIR = os.path.join(ROOT, 'departments/security')
LOG_FILE = os.path.join(DEPT_DIR, 'logs/auto_fix.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

env = {}
secrets_path = os.path.join(ROOT, '.secrets')
if os.path.exists(secrets_path):
    for line in open(secrets_path, encoding='utf-8'):
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v
TG_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = env.get('TELEGRAM_CHAT_ID', '')

HOME = os.path.expanduser('~')
PROJECTS = [
    {'name': 'korlens', 'path': f'{HOME}/Desktop/korlens', 'type': 'node'},
    {'name': 'tax', 'path': f'{HOME}/Desktop/cheonmyeongdang/departments/tax/server', 'type': 'node'},
    {'name': 'hexdrop', 'path': f'{HOME}/Desktop/hexdrop', 'type': 'generic'},
]


def log(msg):
    line = f'[{datetime.now().isoformat(timespec="seconds")}] {msg}'
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def send_telegram(text):
    if not TG_TOKEN or not TG_CHAT:
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML'},
            timeout=10,
        )
    except Exception:
        pass


def fix_gitignore(project_path: str, dry_run: bool) -> list:
    """.gitignore에 .env* 패턴 없으면 추가"""
    gi = Path(project_path) / '.gitignore'
    actions = []
    if not gi.exists():
        if not dry_run:
            gi.write_text('# Secrets\n.env*\n.vercel\n', encoding='utf-8')
        actions.append('.gitignore 생성 (env/vercel 패턴 추가)')
        return actions
    content = gi.read_text(encoding='utf-8', errors='ignore')
    if '.env' not in content:
        if not dry_run:
            with open(gi, 'a', encoding='utf-8') as f:
                f.write('\n# Added by security auto_fix\n.env*\n')
        actions.append('.gitignore에 .env* 추가')
    return actions


def fix_env_tracked(project_path: str, dry_run: bool) -> list:
    """git에 .env 파일이 tracked면 언스테이징"""
    actions = []
    if not (Path(project_path) / '.git').exists():
        return actions
    try:
        r = subprocess.run(
            ['git', '-C', project_path, 'ls-files', '.env*'],
            capture_output=True, text=True, timeout=10,
        )
        files = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        for f in files:
            if dry_run:
                actions.append(f'git에서 언스테이징 예정: {f}')
            else:
                subprocess.run(
                    ['git', '-C', project_path, 'rm', '--cached', f],
                    capture_output=True, timeout=10,
                )
                actions.append(f'git에서 언스테이징: {f}')
    except Exception as e:
        actions.append(f'[ERROR] env tracked 체크 실패: {e}')
    return actions


def fix_npm_audit(project_path: str, dry_run: bool) -> list:
    """npm audit fix (breaking change 없이)"""
    pkg = Path(project_path) / 'package.json'
    actions = []
    if not pkg.exists():
        return actions
    try:
        if dry_run:
            r = subprocess.run(
                ['npm', 'audit', '--json', '--prefix', project_path],
                capture_output=True, text=True, timeout=60, shell=True,
            )
            import json as jlib
            data = jlib.loads(r.stdout or '{}')
            vuln = data.get('metadata', {}).get('vulnerabilities', {})
            total = sum(vuln.values()) if vuln else 0
            if total > 0:
                actions.append(f'npm audit fix 예정: 취약점 {total}개')
        else:
            subprocess.run(
                ['npm', 'audit', 'fix', '--prefix', project_path],
                capture_output=True, text=True, timeout=120, shell=True,
            )
            actions.append('npm audit fix 실행 완료')
    except Exception as e:
        actions.append(f'[ERROR] npm audit fix 실패: {str(e)[:100]}')
    return actions


def run(dry_run: bool = False):
    total_fixed = 0
    lines = [f'🔧 보안 자동 수정 시작 (dry_run={dry_run})']
    for p in PROJECTS:
        if not os.path.exists(p['path']):
            continue
        log(f"[{p['name']}] {p['path']}")
        actions = []
        actions.extend(fix_gitignore(p['path'], dry_run))
        actions.extend(fix_env_tracked(p['path'], dry_run))
        if p['type'] == 'node':
            actions.extend(fix_npm_audit(p['path'], dry_run))
        for a in actions:
            log(f"  · {a}")
        if actions:
            lines.append(f"[{p['name']}] {len(actions)}건")
            for a in actions[:5]:
                lines.append(f"  · {a}")
            total_fixed += len(actions)

    if total_fixed > 0 and not dry_run:
        send_telegram('🔧 <b>자동 보안 수정 완료</b>\n' + '\n'.join(lines[1:]))

    log(f'총 수정 {total_fixed}건')
    return total_fixed


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    run(dry_run=dry)
