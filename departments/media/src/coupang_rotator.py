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

# 쿠팡 파트너스 링크 풀 (AI 부업/크리에이터 맥락 상품만)
PRODUCTS = [
    {
        "name": "실버바 100g 프라임 투자",
        "url": "https://link.coupang.com/a/emjC0T",
        "hashtags": "#재테크 #실버바 #쿠팡",
    },
    # 추후 확장: 키보드/마우스/AI 서적 등 링크 발급 시 이곳에 추가
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
