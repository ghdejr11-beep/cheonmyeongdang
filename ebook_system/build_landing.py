"""
landing.html 의 자리표시자(GUMROAD_*_URL, 가격)를 config.py 값으로 채워
output/landing.html 로 출력한다.

이걸 GitHub Pages / Netlify / 천명당 사이트에 그대로 올리면 됨.
"""

import sys
from pathlib import Path

import config

ROOT = Path(__file__).parent
SRC = ROOT / "landing.html"
OUT_DIR = ROOT / config.OUTPUT_DIR
OUT = OUT_DIR / "landing.html"
OUT_DIR.mkdir(exist_ok=True)


def fmt_won(n: int) -> str:
    return f"{n:,}"


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} 없음")
        return 1

    html = SRC.read_text(encoding="utf-8")

    # 결제 링크 치환
    replacements = {
        "GUMROAD_LITE_URL": config.GUMROAD_LITE,
        "GUMROAD_STANDARD_URL": config.GUMROAD_STANDARD,
        "GUMROAD_PREMIUM_URL": config.GUMROAD_PREMIUM,
        # 가격 (랜딩 템플릿에 들어있는 기본값을 config 값으로 덮어쓰기)
        ">19,900<": f">{fmt_won(config.PRICE_LITE)}<",
        ">99,000<": f">{fmt_won(config.PRICE_STANDARD)}<",
        ">299,000<": f">{fmt_won(config.PRICE_PREMIUM)}<",
    }

    for old, new in replacements.items():
        html = html.replace(old, new)

    OUT.write_text(html, encoding="utf-8")
    print(f"  ✓ 랜딩 페이지 빌드 완료: {OUT}")
    print()
    print("  다음 단계:")
    print("    1. config.py 의 GUMROAD_*_URL 을 실제 판매 링크로 바꾼다")
    print("    2. python build_landing.py 다시 실행")
    print("    3. output/landing.html 을 다음 중 한 곳에 업로드:")
    print("       - GitHub Pages (무료)")
    print("       - Netlify (무료)")
    print("       - 천명당 사이트의 /book 경로")
    return 0


if __name__ == "__main__":
    sys.exit(main())
