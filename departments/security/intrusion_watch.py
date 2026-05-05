#!/usr/bin/env python3
"""
침입·해킹 탐지 에이전트
— 5분마다 Vercel 프로덕션 서비스 로그/메트릭 조회 → 이상 감지 → 긴급 알림

탐지 항목:
  1. 401/403 급증 (brute force 공격 의심)
  2. 429 Rate limit 급증 (DoS 의심)
  3. 5xx 급증 (서버 공격 or 장애)
  4. 동일 경로 비정상 요청 패턴
  5. 응답 시간 급증 (DDoS 징후)

현재 v1: Health check 로그 기반 간이 탐지
v2: Vercel Log API 연동 (VERCEL_TOKEN 필요)

Usage:
  python intrusion_watch.py          # 최근 5분 구간 분석
  python intrusion_watch.py --debug  # 상세 출력
"""
import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from collections import Counter

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
DEPT_DIR = os.path.join(ROOT, 'departments/security')
HEALTH_LOG = os.path.join(ROOT, 'departments/intelligence/data/health_log.txt')
STATE_FILE = os.path.join(DEPT_DIR, 'logs/intrusion_state.json')
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

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

# 모니터링 프로젝트
VERCEL_PROJECTS = [
    {'name': 'korlens', 'team': 'kunstudio'},
    {'name': 'tax-n-benefit-api', 'team': 'kunstudio'},
]

# 이상 감지 임계치 (5분 구간)
THRESHOLDS = {
    'response_time_ms': 3000,   # 평균 응답 3초 초과 (일반 페이지)
    'error_rate': 0.30,         # 30% 이상 에러
    'consecutive_fails': 3,     # 연속 3회 실패
    'min_sample_size': 5,       # 5개 미만 sample은 alert X (1/1 = 100% false positive 방지)
    'dns_failure_skip': True,   # DNS 해상도 실패는 5xx로 분류 X (로컬 DNS 캐시 이슈)
}

# 서비스별 임계값 오버라이드 — LLM/AI 호출 endpoint는 느린 게 정상
SLOW_OVERRIDES = {
    'AI': 12000,        # AI 챗봇 응답: Claude/GPT 호출 시 2~10초 정상
    '챗봇': 12000,
    'chat': 12000,
    'gpt': 12000,
    'claude': 12000,
    'chatbot': 12000,
}


def _slow_threshold_for(service_name: str) -> int:
    """서비스 이름에 LLM/AI 키워드가 들어가면 더 높은 임계값 사용."""
    s = (service_name or '').lower()
    for kw, override in SLOW_OVERRIDES.items():
        if kw.lower() in s:
            return override
    return THRESHOLDS['response_time_ms']


def send_telegram_urgent(text):
    if not TG_TOKEN or not TG_CHAT:
        print('[TG URGENT]', text)
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={
                'chat_id': TG_CHAT,
                'text': text,
                'parse_mode': 'HTML',
                'disable_notification': 'false',
            },
            timeout=10,
        )
    except Exception as e:
        print(f'[TG ERROR] {e}')


def parse_health_log(window_minutes: int = 5) -> dict:
    """최근 N분 health_log.txt 분석"""
    if not os.path.exists(HEALTH_LOG):
        return {}
    cutoff = datetime.now() - timedelta(minutes=window_minutes)
    by_service: dict = {}
    try:
        with open(HEALTH_LOG, encoding='utf-8') as f:
            for line in f:
                # [2026-04-18T13:48:02] 🔍 KORLENS: UP (200, 433ms)
                line = line.strip()
                if not line.startswith('['):
                    continue
                try:
                    ts_str = line[1:20]
                    ts = datetime.fromisoformat(ts_str)
                except Exception:
                    continue
                if ts < cutoff:
                    continue
                # 서비스명 추출
                rest = line[22:]
                parts = rest.split(':', 1)
                if len(parts) < 2:
                    continue
                svc_name = parts[0].strip()
                payload = parts[1]
                is_up = 'UP' in payload
                # (200, 433ms)
                import re
                m = re.search(r'\((\d+),\s*(\d+)ms\)', payload)
                status = int(m.group(1)) if m else 0
                elapsed = int(m.group(2)) if m else 0

                by_service.setdefault(svc_name, []).append({
                    'ts': ts_str,
                    'up': is_up,
                    'status': status,
                    'elapsed_ms': elapsed,
                })
    except Exception as e:
        print(f'[PARSE ERROR] {e}')
    return by_service


def detect_anomalies(by_service: dict) -> list:
    """이상 탐지"""
    alerts = []
    for svc, samples in by_service.items():
        if not samples:
            continue
        total = len(samples)
        fails = sum(1 for s in samples if not s['up'])
        error_rate = fails / total if total else 0
        avg_ms = sum(s['elapsed_ms'] for s in samples) / total if total else 0
        # 연속 실패
        consecutive = 0
        max_consec = 0
        for s in samples:
            if not s['up']:
                consecutive += 1
                max_consec = max(max_consec, consecutive)
            else:
                consecutive = 0

        # 5xx 발생
        server_errors = sum(1 for s in samples if s['status'] >= 500)

        # min_sample_size 미달이면 alert 차단 (1/1 = 100% false positive 방지)
        if total < THRESHOLDS.get('min_sample_size', 5):
            continue
        if error_rate >= THRESHOLDS['error_rate']:
            alerts.append({
                'service': svc,
                'severity': 'high',
                'type': 'error_rate',
                'msg': f"에러율 {error_rate*100:.0f}% ({fails}/{total})",
            })
        slow_threshold = _slow_threshold_for(svc)
        if avg_ms >= slow_threshold:
            alerts.append({
                'service': svc,
                'severity': 'medium',
                'type': 'slow',
                'msg': f"평균 응답 {int(avg_ms)}ms (임계값 {slow_threshold}ms 초과 — DDoS 의심)",
            })
        if max_consec >= THRESHOLDS['consecutive_fails']:
            alerts.append({
                'service': svc,
                'severity': 'critical',
                'type': 'outage',
                'msg': f"연속 {max_consec}회 실패",
            })
        if server_errors > 0:
            alerts.append({
                'service': svc,
                'severity': 'critical',
                'type': '5xx',
                'msg': f"5xx 서버 에러 {server_errors}회",
            })
    return alerts


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {'last_alerts': []}


def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ─── 자동 방어 모듈 ─────────────────────────────
def _service_to_vercel_project(svc: str) -> str | None:
    """서비스 이름 → Vercel 프로젝트 이름 매핑."""
    s = (svc or '').lower()
    if 'korlens' in s:
        return 'korlens'
    if 'tax' in s or '세금' in s:
        return 'tax-n-benefit-api'
    if 'cheon' in s or '천명' in s:
        return 'cheonmyeongdang'
    return None


def _vercel_redeploy(project_name: str, team_slug: str = 'kunstudio') -> tuple[bool, str]:
    """Vercel API로 production 재배포 트리거. 최신 배포의 git source를 새 배포로."""
    if not VERCEL_TOKEN:
        return False, 'no token'
    try:
        # 1. 최신 production 배포 조회
        list_url = f'https://api.vercel.com/v6/deployments?app={project_name}&limit=1&target=production&teamId={team_slug}'
        r = requests.get(list_url, headers={'Authorization': f'Bearer {VERCEL_TOKEN}'}, timeout=10)
        if r.status_code != 200:
            return False, f'list: {r.status_code}'
        depls = r.json().get('deployments', [])
        if not depls:
            return False, 'no prev deployment'
        prev = depls[0]
        prev_id = prev.get('uid')
        # 2. 같은 git commit으로 재배포 (rollback이 아니라 같은 코드 새 deploy)
        redeploy_url = f'https://api.vercel.com/v13/deployments?teamId={team_slug}'
        payload = {
            'name': project_name,
            'deploymentId': prev_id,
            'target': 'production',
        }
        r2 = requests.post(redeploy_url, headers={'Authorization': f'Bearer {VERCEL_TOKEN}', 'Content-Type': 'application/json'}, json=payload, timeout=15)
        if r2.status_code in (200, 201):
            new_id = r2.json().get('id', '?')
            return True, f'new deploy {new_id[:20]}'
        return False, f'redeploy: {r2.status_code} {r2.text[:200]}'
    except Exception as e:
        return False, f'exception: {str(e)[:100]}'


def auto_defend(alert: dict) -> str:
    """알림 type별 자동 방어 조치. 결과 메시지 반환."""
    svc = alert.get('service', '')
    atype = alert.get('type', '')
    severity = alert.get('severity', '')

    if atype == 'slow':
        # 응답 느림 — false positive 가능성. 자동 방어 X (캐시 강화는 코드 변경 필요)
        return '관찰만 (slow는 false positive 가능)'

    if atype == 'error_rate':
        # 에러율 30%+ → Vercel WAF rate limit 강화 권장 (수동), 자동 redeploy 시도 X
        return 'Vercel WAF rate limit 활성화 권장 (수동 5분)'

    if atype in ('outage', '5xx'):
        # 자동 재배포 시도
        proj = _service_to_vercel_project(svc)
        if not proj:
            return f'프로젝트 매핑 없음 ({svc})'
        ok, msg = _vercel_redeploy(proj)
        if ok:
            return f'✅ 자동 재배포 트리거 ({proj}: {msg})'
        return f'❌ 자동 재배포 실패 ({proj}: {msg})'

    return '액션 없음'


def run(debug=False):
    by_svc = parse_health_log(window_minutes=5)
    if debug:
        print(f'[DEBUG] 파싱: {len(by_svc)}개 서비스, 샘플: {sum(len(v) for v in by_svc.values())}개')

    alerts = detect_anomalies(by_svc)
    state = load_state()
    prev_keys = set(a['type'] + ':' + a['service'] for a in state.get('last_alerts', []))
    new_alerts = [a for a in alerts if (a['type'] + ':' + a['service']) not in prev_keys]

    if new_alerts:
        lines = ['🚨 <b>침입·이상 탐지 ALERT</b>', '']
        # 자동 방어 액션 실행 + 보고
        defense_lines = []
        for a in new_alerts:
            icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡'}.get(a['severity'], '⚪')
            lines.append(f"{icon} [{a['service']}] {a['msg']}")
            # 자동 방어 — critical/high 만 자동 액션, medium은 관찰만
            if a['severity'] in ('critical', 'high'):
                action_result = auto_defend(a)
                defense_lines.append(f"🛡️ [{a['service']}] {action_result}")
        if defense_lines:
            lines.append('')
            lines.append('<b>자동 방어 액션:</b>')
            lines.extend(defense_lines)
        lines.append('')
        lines.append('👉 추가 조치 필요 시 Vercel 대시보드·로그 확인.')
        send_telegram_urgent('\n'.join(lines))

    state['last_alerts'] = alerts
    state['last_check'] = datetime.now().isoformat(timespec='seconds')
    save_state(state)

    if debug:
        for a in alerts:
            print(f"  {a['severity'].upper()} {a['service']}: {a['msg']}")

    return alerts


if __name__ == '__main__':
    debug = '--debug' in sys.argv
    alerts = run(debug=debug)
    print(f'이상 탐지: {len(alerts)}건')
