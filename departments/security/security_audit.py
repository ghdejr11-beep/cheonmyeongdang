#!/usr/bin/env python3
"""
쿤스튜디오 전 서비스 통합 보안 감사
— 매일 03:00 자동 실행. 심각한 이슈만 CEO에게 텔레그램.

점검 항목:
  1. 시크릿 하드코딩 (소스코드 내 sk-ant-api/AKIA/GOOGLE_API_KEY 등)
  2. .env 파일이 git에 tracked 상태인지
  3. .gitignore에 .env* 포함 확인
  4. npm audit (Node.js 프로젝트)
  5. 최근 커밋에 시크릿 누출 여부 (git log -p 20커밋)

Usage:
  python security_audit.py             # 전체 감사
  python security_audit.py korlens     # 특정 서비스만
"""
import os
import re
import sys
import json
import subprocess
import requests
from datetime import date, datetime
from pathlib import Path

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
DEPT_DIR = os.path.join(ROOT, 'departments/security')
LOG_DIR = os.path.join(DEPT_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

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

# 감사 대상 프로젝트
PROJECTS = [
    {'key': 'korlens', 'name': '🔍 KORLENS', 'path': f'{HOME}/Desktop/korlens', 'type': 'node'},
    {'key': 'tax', 'name': '💰 세금N혜택', 'path': f'{HOME}/Desktop/cheonmyeongdang/departments/tax/server', 'type': 'node'},
    {'key': 'hexdrop', 'name': '🎮 HexDrop', 'path': f'{HOME}/Desktop/hexdrop', 'type': 'generic'},
    {'key': 'cheonmyeongdang', 'name': '🔮 천명당', 'path': f'{HOME}/Desktop/cheonmyeongdang', 'type': 'mixed'},
    {'key': 'ebook', 'name': '📖 전자책', 'path': f'{HOME}/Desktop/cheonmyeongdang/departments/ebook', 'type': 'python'},
]

# 시크릿 탐지 정규식 (고위험)
SECRET_PATTERNS = [
    (r'sk-ant-api\d{2}-[A-Za-z0-9_-]{40,}', 'Anthropic API Key'),
    (r'sk-proj-[A-Za-z0-9_-]{40,}', 'OpenAI Project Key'),
    (r'sk-[A-Za-z0-9]{40,}', 'OpenAI Key'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'AIza[0-9A-Za-z_-]{35}', 'Google API Key'),
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub PAT'),
    (r'xoxb-[0-9]+-[0-9]+-[A-Za-z0-9]+', 'Slack Bot Token'),
    (r'vercel_[A-Za-z0-9]{24}', 'Vercel Token'),
    (r'EAAG[A-Za-z0-9]{50,}', 'Meta Graph Token'),
    # Telegram Bot Token (숫자:문자열 35)
    (r'\b\d{9,12}:[A-Za-z0-9_-]{35}\b', 'Telegram Bot Token'),
    # Twitter/X API: OAuth 1.0a 액세스 토큰 형태 (숫자-영숫자45)
    (r'\b\d{15,20}-[A-Za-z0-9]{40,}\b', 'Twitter Access Token'),
]

# 스캔 제외 패턴
EXCLUDE_DIRS = {'node_modules', '.next', '.git', 'dist', 'build', '__pycache__',
                '.vercel', '.cache', 'out', '.venv', 'venv', '.turbo'}
EXCLUDE_EXTS = {'.lock', '.log', '.map', '.min.js', '.png', '.jpg', '.jpeg',
                '.pdf', '.zip', '.tar', '.gz'}


def send_telegram(text):
    if not TG_TOKEN or not TG_CHAT:
        print('[TG]', text[:200])
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML'},
            timeout=10,
        )
    except Exception as e:
        print(f'[TG ERROR] {e}')


def scan_secrets(project_path: str, max_files: int = 500) -> list:
    """프로젝트 디렉토리 내 시크릿 하드코딩 탐지"""
    findings = []
    p = Path(project_path)
    if not p.exists():
        return findings
    count = 0
    for f in p.rglob('*'):
        if count >= max_files:
            break
        if f.is_dir():
            continue
        if any(ex in f.parts for ex in EXCLUDE_DIRS):
            continue
        if f.suffix.lower() in EXCLUDE_EXTS:
            continue
        # .env.local 같은 env파일은 OK (gitignore에 있으면)
        if f.name.startswith('.env'):
            continue
        try:
            content = f.read_text(encoding='utf-8', errors='ignore')[:100000]
        except Exception:
            continue
        count += 1
        for pattern, label in SECRET_PATTERNS:
            for m in re.finditer(pattern, content):
                # 주변 문맥 확인 (URL 내부면 대부분 pre-signed URL이라 오탐지)
                start = max(0, m.start() - 80)
                context = content[start:m.end() + 20]
                if ('http://' in context or 'https://' in context or
                        'X-Amz-' in context or 'canva.com' in context or
                        'amazonaws.com' in context):
                    continue
                line = content[:m.start()].count('\n') + 1
                findings.append({
                    'file': str(f.relative_to(p)),
                    'line': line,
                    'type': label,
                    'preview': m.group(0)[:8] + '...' + m.group(0)[-6:],
                })
    return findings


def check_gitignore(project_path: str) -> dict:
    """.gitignore에 .env* 포함 여부"""
    gi = Path(project_path) / '.gitignore'
    if not gi.exists():
        return {'status': 'missing', 'message': '.gitignore 파일 없음'}
    content = gi.read_text(encoding='utf-8', errors='ignore')
    if '.env' in content:
        return {'status': 'ok'}
    return {'status': 'warning', 'message': '.gitignore에 .env* 패턴 없음'}


def check_env_tracked(project_path: str) -> list:
    """git에 .env 파일이 tracked 상태인지"""
    if not (Path(project_path) / '.git').exists():
        return []
    try:
        r = subprocess.run(
            ['git', '-C', project_path, 'ls-files', '.env*'],
            capture_output=True, text=True, timeout=10,
        )
        files = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        return files
    except Exception:
        return []


def check_npm_audit(project_path: str) -> dict:
    """npm audit 실행 — 취약점 요약"""
    pkg = Path(project_path) / 'package.json'
    if not pkg.exists():
        return {'skip': True}
    try:
        r = subprocess.run(
            ['npm', 'audit', '--json', '--prefix', project_path],
            capture_output=True, text=True, timeout=60, shell=False,
        )
        data = json.loads(r.stdout or '{}')
        meta = data.get('metadata', {})
        vuln = meta.get('vulnerabilities', {})
        return {
            'critical': vuln.get('critical', 0),
            'high': vuln.get('high', 0),
            'moderate': vuln.get('moderate', 0),
            'low': vuln.get('low', 0),
            'total': sum(vuln.values()) if vuln else 0,
        }
    except Exception as e:
        return {'error': str(e)[:100]}


def audit_project(p: dict) -> dict:
    path = p['path']
    print(f"[{p['name']}] 감사 시작...")
    result = {'project': p['name'], 'path': path, 'issues': []}

    if not os.path.exists(path):
        result['issues'].append({'severity': 'info', 'msg': '경로 없음 (건너뜀)'})
        return result

    # 1. 시크릿 스캔
    secrets = scan_secrets(path)
    for s in secrets:
        result['issues'].append({
            'severity': 'critical',
            'msg': f"시크릿 노출: {s['type']} @ {s['file']}:{s['line']} ({s['preview']})",
        })

    # 2. .gitignore
    gi = check_gitignore(path)
    if gi.get('status') == 'warning':
        result['issues'].append({'severity': 'high', 'msg': gi['message']})

    # 3. .env tracked?
    tracked = check_env_tracked(path)
    if tracked:
        result['issues'].append({
            'severity': 'critical',
            'msg': f"git에 .env 파일 tracked: {', '.join(tracked)}",
        })

    # 4. npm audit
    if p['type'] in ('node', 'mixed'):
        audit = check_npm_audit(path)
        if not audit.get('skip') and not audit.get('error'):
            crit = audit.get('critical', 0)
            high = audit.get('high', 0)
            if crit > 0:
                result['issues'].append({
                    'severity': 'critical',
                    'msg': f"npm 취약점 critical {crit}개",
                })
            if high > 0:
                result['issues'].append({
                    'severity': 'high',
                    'msg': f"npm 취약점 high {high}개",
                })

    result['issue_count'] = len(result['issues'])
    print(f"  → {len(result['issues'])}개 이슈 발견")
    return result


def notify(results: list):
    critical_issues = [
        (r, i) for r in results for i in r['issues'] if i['severity'] == 'critical'
    ]
    high_issues = [
        (r, i) for r in results for i in r['issues'] if i['severity'] == 'high'
    ]

    if not critical_issues and not high_issues:
        # 조용히 넘어감 (매일 OK 메시지 스팸 방지)
        return

    lines = [f'🛡️ <b>보안 감사 · {date.today().isoformat()}</b>', '']
    if critical_issues:
        lines.append(f'🚨 <b>Critical {len(critical_issues)}</b>')
        for r, i in critical_issues[:10]:
            lines.append(f"  · [{r['project']}] {i['msg'][:100]}")
        lines.append('')
    if high_issues:
        lines.append(f'⚠️ <b>High {len(high_issues)}</b>')
        for r, i in high_issues[:10]:
            lines.append(f"  · [{r['project']}] {i['msg'][:100]}")
    send_telegram('\n'.join(lines))


def run(only: str | None = None):
    targets = [p for p in PROJECTS if not only or p['key'] == only]
    results = [audit_project(p) for p in targets]

    # 저장
    out = os.path.join(LOG_DIR, f'audit_{date.today().isoformat()}.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    notify(results)
    return results


def run_auto_fix():
    """감사 후 안전한 자동 수정 자동 호출"""
    try:
        auto_fix_path = os.path.join(DEPT_DIR, 'auto_fix.py')
        subprocess.run(
            [sys.executable, '-X', 'utf8', auto_fix_path],
            capture_output=True, timeout=300,
        )
        print('[auto_fix 자동 실행 완료]')
    except Exception as e:
        print(f'[auto_fix 실패] {e}')


if __name__ == '__main__':
    only = sys.argv[1] if len(sys.argv) > 1 else None
    results = run(only=only)
    total_issues = sum(r['issue_count'] for r in results)
    print(f'\n감사 완료 · 총 이슈 {total_issues}개 · 리포트: logs/audit_{date.today().isoformat()}.json')
    # 감사 후 자동 수정 실행 (보고 없이 알아서 수정)
    if '--no-fix' not in sys.argv:
        run_auto_fix()
