"""
『AI 에이전트 사업 — Claude Agent SDK 로 월 500만원 자동화』 설정.

월 49,900원 Gumroad 상품용.
타깃: Claude API 써본 개발자·1인 창업가·SaaS 운영자.
핵심 약속: 3개월 안에 자동화 에이전트로 월 500만원 번다.
"""

from pathlib import Path

BOOK_TITLE = "AI 에이전트 사업"
BOOK_SUBTITLE = "Claude Agent SDK 로 월 500만원 자동화"
AUTHOR = "홍덕훈 (덕구네 출판)"

PRICE_KRW = 49_900

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
FONTS_DIR = PROJECT_DIR / "fonts"

OUTPUT_DIR.mkdir(exist_ok=True)
