#!/usr/bin/env python3
"""
쿠팡 파트너스 링크 순환 삽입 헬퍼.
5회 포스트당 1회 쿠팡 링크 + 공정위 필수 고지 반환.

사용:
    from coupang_rotator import maybe_coupang_block
    block = maybe_coupang_block()  # str or None
    if block:
        post_body += "\n\n" + block

상태 파일: D:\state\coupang_rotator.json (카운터 + 마지막 상품 인덱스)

공정위 금지 표현 회피:
- "받을 수 있습니다" 금지 → "받습니다" 확정 표현
- 링크·공정위·본문 한 화면에 노출
"""
import json, datetime
from pathlib import Path

STATE_FILE = Path(r"D:\state\coupang_rotator.json")
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

INTERVAL = 5  # N 회 포스트당 1회

# 쿠팡 파트너스 링크 풀
# 전략 (리서치 기반): 24시간 쿠키 → 랭킹 페이지가 개별 상품보다 CTR 높음.
# 수수료율: 뷰티/패션 3%, 식품/생활 2%, 가전 1%. 고관여 중가 > 저가 대량.
# 크리에이터 페르소나(AI 부업/앱) 매칭: 홈오피스·운동·베스트 랭킹 우선.
PRODUCTS = [
    {
        "name": "쿠팡 BEST 100 (오늘의 인기 상품)",
        "url": "https://www.coupang.com/np/campaigns/82",
        "hashtags": "#쿠팡베스트 #오늘의쇼핑",
        "note": "TODO: 파트너스 대시보드에서 link.coupang.com/a/ 단축링크로 교체",
    },
    {
        "name": "실버바 100g 프라임 투자",
        "url": "https://link.coupang.com/a/emjC0T",
        "hashtags": "#재테크 #실버바 #쿠팡",
    },
    # 추후 확장 (사용자가 파트너스 대시보드에서 단축링크 발급 후 교체):
    # - 홈오피스 BEST (노트북 스탠드/모니터 받침)
    # - 뷰티 BEST (3% 수수료 카테고리)
    # - 운동기구 (폼롤러/밴드, 크리에이터 페르소나 매칭)
    # - AI/생산성 도서 BEST
]

DISCLOSURE_KO = (
    "[광고]\n"
    "이 포스팅은 쿠팡 파트너스 활동의 일환으로,\n"
    "이에 따른 일정액의 수수료를 제공받습니다."
)

DISCLOSURE_EN = (
    "[Ad] As a Coupang Partners affiliate, "
    "I earn a commission on qualifying purchases at no extra cost to you."
)


def _load():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"post_count": 0, "product_idx": 0, "last_injected_at": None}


def _save(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def maybe_coupang_block(lang="ko"):
    """N 회 포스트당 1회 쿠팡 블록 반환, 아니면 None."""
    state = _load()
    state["post_count"] += 1

    should_inject = (state["post_count"] % INTERVAL == 0)

    if not should_inject:
        _save(state)
        return None

    if not PRODUCTS:
        _save(state)
        return None

    product = PRODUCTS[state["product_idx"] % len(PRODUCTS)]
    state["product_idx"] += 1
    state["last_injected_at"] = datetime.datetime.now().isoformat()
    _save(state)

    # 공정위 2024-12 개정: 광고 고지는 본문 상단(첫 줄) 권장.
    # 반환받은 쪽에서 원 포스트 본문 뒤에 붙이면 되도록 블록만 반환.
    # 이 블록 자체의 첫 줄이 [광고] 고지 — 호출측은 이 블록을 맨 앞에 두거나
    # 최소한 링크·고지가 한 화면에 노출되도록 배치해야 한다.
    disclosure = DISCLOSURE_EN if lang == "en" else DISCLOSURE_KO
    tail = f"{product['name']}\n{product['url']}\n{product['hashtags']}"
    return f"{disclosure}\n\n{tail}"


def stats():
    s = _load()
    return {
        "post_count": s.get("post_count", 0),
        "next_injection_in": INTERVAL - (s.get("post_count", 0) % INTERVAL),
        "last_injected_at": s.get("last_injected_at"),
    }


if __name__ == "__main__":
    # 테스트
    print("stats:", stats())
    for i in range(1, 12):
        b = maybe_coupang_block("ko")
        print(f"post #{i}: {'INJECTED' if b else '-'}")
        if b:
            print("  " + b.replace("\n", "\n  "))
    print("final stats:", stats())
