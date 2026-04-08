"""
output/book.md 를 mentor_bot/book.md 로 복사한다.
(book.md 가 배포에 포함되어야 멘토봇이 책 내용을 답변할 수 있음)

사용법:
    cd ebook_system
    python mentor_bot/prepare_book.py

이 스크립트를 실행한 후 git add + commit + push 하면
Render.com 이 자동 재배포하고, 새 책 내용으로 멘토봇이 갱신됨.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # ebook_system/
SRC = ROOT / "output" / "book.md"
DST = ROOT / "mentor_bot" / "book.md"


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} 없음")
        print("       먼저 'python generate_book.py' 로 책 생성하세요")
        return 1

    shutil.copy2(SRC, DST)
    size_kb = DST.stat().st_size / 1024
    print(f"✓ 책 복사 완료: {DST} ({size_kb:.1f} KB)")
    print()
    print("다음 단계:")
    print("  1. git add ebook_system/mentor_bot/book.md")
    print("  2. git commit -m 'update mentor bot book content'")
    print("  3. git push")
    print("  → Render.com 이 자동으로 재배포합니다 (3~5분)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
