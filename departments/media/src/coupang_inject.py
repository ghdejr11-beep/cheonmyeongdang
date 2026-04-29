#!/usr/bin/env python3
"""
쿠팡 파트너스 자동 삽입 모듈.

규칙:
  - 5회 발행당 1회 (settings.frequency_n) 쿠팡 링크 삽입
  - 공정위 문구 필수 (compliance_text)
  - 발행 텍스트의 키워드(context_tags) 매칭으로 가장 적합한 active 상품 선택
  - active=false 상품은 제외 (사용자가 link 채우고 active=true로 전환)
  - 채널별 글자수 한도 고려 — 너무 길면 hook 줄이고 link만 유지

사용:
    from coupang_inject import maybe_inject
    new_text, injected = maybe_inject("AI 부업으로 월 100만원...")
    # injected=True 이면 카운터 증가됨

JSON 위치: 같은 폴더의 coupang_products.json
"""
import os
import json
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRODUCTS_FILE = ROOT / 'coupang_products.json'


# ───────── State / Config 로드 ─────────
def _load():
    if not PRODUCTS_FILE.exists():
        raise FileNotFoundError(f'coupang_products.json 없음: {PRODUCTS_FILE}')
    return json.loads(PRODUCTS_FILE.read_text(encoding='utf-8'))


def _save(data):
    PRODUCTS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


# ───────── 핵심 함수 ─────────
def should_inject(state, freq_n=5):
    """5회당 1회 True 반환. post_count가 freq_n의 배수일 때.

    호출 순서:
      post 1 → count=1 → inject? (1%5==0? NO)
      ...
      post 5 → count=5 → inject? (5%5==0? YES)
      post 10 → inject? YES
    """
    pc = int(state.get('post_count', 0)) + 1  # 이번 호출 기준
    return (pc % freq_n) == 0


def pick_product(context_text, products):
    """발행 텍스트의 키워드 기반 매칭.

    1) active=true + link 있는 상품만 후보
    2) context_tags가 텍스트에 가장 많이 매칭되는 상품 우선
    3) 매칭 0개면 첫 번째 active 상품 fallback
    4) active 상품 0개면 None 반환
    """
    actives = [p for p in products if p.get('active') and p.get('link')]
    if not actives:
        return None

    text_low = (context_text or '').lower()
    scored = []
    for p in actives:
        score = 0
        for tag in p.get('context_tags', []):
            if tag.lower() in text_low:
                score += 1
        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])
    if scored[0][0] > 0:
        return scored[0][1]
    return actives[0]


# ───────── 채널별 글자수 한도 ─────────
CHANNEL_LIMITS = {
    'x': 280,
    'bluesky': 300,
    'threads': 500,
    'mastodon': 500,
    'discord': 2000,
    'telegram': 4096,
    'instagram': 2200,
}


def inject_link(text, product, compliance_text, max_len=None):
    """텍스트 끝에 공정위 문구 + 쿠팡 링크 추가.

    max_len 지정 시 한도 초과 방지: 본문을 잘라서 footer 끼움.
    공정위 문구는 절대 생략 X (법적 필수).
    """
    if not product or not product.get('link'):
        return text
    if not compliance_text:
        raise ValueError('compliance_text 필수 (공정위 문구 누락 금지)')

    footer = f"\n\n{compliance_text}\n👉 {product['name']}: {product['link']}"
    full = (text or '') + footer

    if max_len and len(full) > max_len:
        # 본문을 잘라서 footer를 끼움
        avail = max_len - len(footer) - 3  # ... 여유
        if avail <= 0:
            # 본문이 들어갈 자리가 없을 정도로 footer가 큼 → 짧은 footer로
            short_footer = f"\n[광고/쿠팡파트너스] {product['link']}"
            avail2 = max_len - len(short_footer) - 3
            if avail2 <= 0:
                return product['link']  # 극단적: 링크만
            body = (text or '')[:avail2].rstrip()
            return body + '...' + short_footer
        body = (text or '')[:avail].rstrip()
        full = body + '...' + footer

    return full


def update_state(data, picked_product):
    """post_count++, 삽입 시 last_inserted_idx/at, total_inserted++."""
    state = data.setdefault('_state', {})
    state['post_count'] = int(state.get('post_count', 0)) + 1
    if picked_product:
        # products 리스트 내 인덱스
        try:
            idx = data['products'].index(picked_product)
        except ValueError:
            idx = -1
        state['last_inserted_idx'] = idx
        state['last_inserted_at'] = datetime.datetime.now().isoformat()
        state['total_inserted'] = int(state.get('total_inserted', 0)) + 1
    _save(data)
    return state


# ───────── 통합 진입점 ─────────
def maybe_inject(text, channel=None, force=False, dry_run=False):
    """5회당 1회 자동 삽입. send_all_direct() 진입 시 호출.

    Args:
      text: 원본 발행 문구
      channel: 'x'/'bluesky'/'threads'/...  글자수 한도 적용
      force: True면 카운터 무시하고 무조건 삽입 (테스트용)
      dry_run: True면 state 저장 안 함

    Returns:
      (new_text, injected_bool, picked_product_or_None)
    """
    try:
        data = _load()
    except Exception as e:
        print(f'[coupang_inject] load 실패: {e}')
        return text, False, None

    settings = data.get('settings', {})
    state = data.get('_state', {})
    products = data.get('products', [])

    freq_n = int(settings.get('frequency_n', 5))
    compliance = settings.get('compliance_text', '').strip()

    do_inject = force or should_inject(state, freq_n)

    if not do_inject:
        # 카운터만 증가
        if not dry_run:
            state['post_count'] = int(state.get('post_count', 0)) + 1
            _save(data)
        return text, False, None

    product = pick_product(text, products)
    if not product:
        # active 상품 없음 → 카운터만 증가
        if not dry_run:
            state['post_count'] = int(state.get('post_count', 0)) + 1
            _save(data)
        return text, False, None

    max_len = CHANNEL_LIMITS.get(channel) if channel else None
    new_text = inject_link(text, product, compliance, max_len=max_len)

    if not dry_run:
        update_state(data, product)
    return new_text, True, product


# ───────── 채널별 분기 헬퍼 ─────────
def inject_per_channel(text, channels=('bluesky', 'discord', 'mastodon', 'x', 'threads', 'instagram', 'telegram')):
    """발행 직전 채널별로 다른 길이의 텍스트 생성.

    같은 호출에서 1번만 카운터 증가 (모든 채널이 동일 발행이라 봄).
    Returns: dict[channel] = text
    """
    data = _load()
    settings = data.get('settings', {})
    state = data.get('_state', {})
    products = data.get('products', [])

    freq_n = int(settings.get('frequency_n', 5))
    compliance = settings.get('compliance_text', '').strip()
    do_inject = should_inject(state, freq_n)
    product = pick_product(text, products) if do_inject else None

    out = {}
    for ch in channels:
        if do_inject and product:
            out[ch] = inject_link(text, product, compliance, max_len=CHANNEL_LIMITS.get(ch))
        else:
            out[ch] = text

    # 카운터 1회만 증가
    if do_inject and product:
        update_state(data, product)
    else:
        state['post_count'] = int(state.get('post_count', 0)) + 1
        _save(data)
    return out


# ───────── CLI / dry-run ─────────
if __name__ == '__main__':
    import sys
    # Windows cp949 → UTF-8 강제 (이모지/한글 깨짐 방지)
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass
    if len(sys.argv) > 1 and sys.argv[1] == 'dry-run':
        # 가짜 텍스트 6개로 5회당 1회 삽입 검증
        sample_texts = [
            'AI 부업으로 월 100만원 달성! ChatGPT 프롬프트 1000개 공유.',
            '재택근무 시작했는데 키보드 추천 부탁드립니다.',
            '실버 투자 어떻게 시작하나요? 재테크 초보입니다.',
            '클로드 코드로 앱 하나 만들었어요. 개발 가이드 정리.',
            '노션 템플릿 50개로 부업 시작! Notion OS 정리법.',
            '유튜브 쇼츠 편집 헤드폰 추천 좀 해주세요.',
        ]
        # state 리셋 (테스트용)
        data = _load()
        original_state = dict(data.get('_state', {}))
        data['_state'] = {'post_count': 0, 'last_inserted_idx': -1, 'last_inserted_at': None, 'total_inserted': 0}
        _save(data)

        print('=== DRY-RUN: 5회당 1회 삽입 검증 ===\n')
        results = []
        for i, t in enumerate(sample_texts, 1):
            new_t, injected, prod = maybe_inject(t, channel='bluesky')
            mark = ' [INJECTED]' if injected else ''
            results.append({'n': i, 'injected': injected, 'product': prod['name'] if prod else None, 'len': len(new_t)})
            print(f'#{i}{mark} ({len(new_t)}자):')
            print('  ' + new_t.replace('\n', '\n  ')[:400])
            print()

        # 글자수 한도 검사
        print('\n=== 글자수 한도 검사 ===')
        long_text = '실버 투자 재테크 자산 보관' * 30  # 일부러 김
        for ch in ('x', 'bluesky', 'threads', 'discord'):
            data2 = _load()
            data2['_state']['post_count'] = 4  # 다음 호출이 5번째 → 삽입
            _save(data2)
            new_t, injected, _ = maybe_inject(long_text, channel=ch)
            limit = CHANNEL_LIMITS.get(ch, 0)
            ok = len(new_t) <= limit
            print(f'  {ch} (limit={limit}): {len(new_t)}자 {"OK" if ok else "OVERFLOW"}')

        # 공정위 문구 누락 검사
        print('\n=== 공정위 문구 검사 ===')
        try:
            inject_link('test', {'name': 'X', 'link': 'http://x'}, '')
            print('  FAIL — 빈 compliance에서 ValueError 안 남')
        except ValueError as e:
            print(f'  OK — ValueError 정상 발생: {e}')

        # 최종 state 복원 (테스트가 카운터 더럽힘 방지)
        data_final = _load()
        data_final['_state'] = original_state if original_state else {'post_count': 0, 'last_inserted_idx': -1, 'last_inserted_at': None, 'total_inserted': 0}
        _save(data_final)
        print(f'\n=== 검증 요약 ===')
        injected_count = sum(1 for r in results if r['injected'])
        print(f'  6회 중 삽입: {injected_count}회 (예상 1회)')
        print(f'  state 복원 완료')
    else:
        print('usage: python coupang_inject.py dry-run')
