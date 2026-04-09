"""
『클로드 코드 실전 가이드 — 코딩 몰라도 앱 만드는 법』 설정.

월 39,900원 Gumroad 상품용.
타깃: 코딩 경험 없거나 적은 직장인·부업러·1인 사업자.
핵심 약속: 이 책 읽고 하루 안에 첫 앱 만든다.
"""

from pathlib import Path

BOOK_TITLE = "클로드 코드 실전 가이드"
BOOK_SUBTITLE = "코딩 몰라도 하루 만에 앱 만드는 법"
AUTHOR = "홍덕훈 (덕구네 출판)"

PRICE_KRW = 39_900

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
FONTS_DIR = PROJECT_DIR / "fonts"

OUTPUT_DIR.mkdir(exist_ok=True)
