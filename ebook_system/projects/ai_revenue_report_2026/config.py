"""
『2026 AI 부업 수익 리포트 — 13개 카테고리 실제 수익 분석』 설정.

19,900원 Gumroad 상품용.
타깃: AI 부업을 고민 중인 모든 사람. 특히 결정 못하고 탐색 중인 사람.
핵심 약속: 이 리포트 읽고 30분 안에 본인에게 맞는 AI 부업 1개 확정한다.
"""

from pathlib import Path

BOOK_TITLE = "2026 AI 부업 수익 리포트"
BOOK_SUBTITLE = "13개 카테고리 실제 수익 분석 + 시작법"
AUTHOR = "홍덕훈 (덕구네 출판)"

PRICE_KRW = 19_900

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
FONTS_DIR = PROJECT_DIR / "fonts"

OUTPUT_DIR.mkdir(exist_ok=True)
