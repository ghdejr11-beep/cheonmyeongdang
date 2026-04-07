"""
output/book.md → output/book.pdf 변환.
한국어 폰트(나눔고딕)는 처음 1회만 자동 다운로드한다.
"""

import re
import sys
import urllib.request
from pathlib import Path

from fpdf import FPDF

import config

ROOT = Path(__file__).parent
OUT = ROOT / config.OUTPUT_DIR
FONTS = ROOT / config.FONTS_DIR
FONTS.mkdir(exist_ok=True)

NANUM_REGULAR_URL = (
    "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
)
NANUM_BOLD_URL = (
    "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
)


def ensure_fonts() -> tuple[Path, Path]:
    reg = FONTS / "NanumGothic-Regular.ttf"
    bold = FONTS / "NanumGothic-Bold.ttf"
    if not reg.exists():
        print(f"  나눔고딕 Regular 다운로드 중...")
        urllib.request.urlretrieve(NANUM_REGULAR_URL, reg)
    if not bold.exists():
        print(f"  나눔고딕 Bold 다운로드 중...")
        urllib.request.urlretrieve(NANUM_BOLD_URL, bold)
    return reg, bold


def md_to_pdf(md_path: Path, out_path: Path) -> None:
    reg, bold = ensure_fonts()

    pdf = FPDF(format="A4")
    pdf.add_font("Nanum", "", str(reg))
    pdf.add_font("Nanum", "B", str(bold))
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(left=18, top=20, right=18)
    pdf.add_page()

    md = md_path.read_text(encoding="utf-8")
    in_code = False

    for raw_line in md.split("\n"):
        line = raw_line.rstrip()

        # 코드 블록 토글
        if line.startswith("```"):
            in_code = not in_code
            pdf.ln(2)
            continue

        if in_code:
            pdf.set_font("Nanum", "", 9)
            # 코드 한 줄이 너무 길면 자동 줄바꿈
            pdf.multi_cell(0, 5, line if line else " ")
            continue

        if not line:
            pdf.ln(3)
            continue

        if line.startswith("---"):
            pdf.add_page()
            continue

        # 헤딩
        if line.startswith("# "):
            pdf.set_font("Nanum", "B", 22)
            pdf.ln(4)
            pdf.multi_cell(0, 12, line[2:].strip())
            pdf.ln(3)
            continue
        if line.startswith("## "):
            pdf.set_font("Nanum", "B", 16)
            pdf.ln(3)
            pdf.multi_cell(0, 9, line[3:].strip())
            pdf.ln(2)
            continue
        if line.startswith("### "):
            pdf.set_font("Nanum", "B", 13)
            pdf.multi_cell(0, 8, line[4:].strip())
            continue

        # 불릿
        if line.startswith(("- ", "* ")):
            pdf.set_font("Nanum", "", 11)
            pdf.multi_cell(0, 7, "• " + line[2:].strip())
            continue

        # 번호 리스트
        if re.match(r"^\d+\.\s", line):
            pdf.set_font("Nanum", "", 11)
            pdf.multi_cell(0, 7, line)
            continue

        # 굵게 (간단 처리: ** 제거)
        if "**" in line:
            line = line.replace("**", "")

        # 본문
        pdf.set_font("Nanum", "", 11)
        pdf.multi_cell(0, 7, line)

    pdf.output(str(out_path))
    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"  ✓ PDF 저장: {out_path} ({size_mb:.2f} MB)")


def main() -> int:
    md_path = OUT / "book.md"
    if not md_path.exists():
        print(f"ERROR: {md_path} 없음. 먼저 'python generate_book.py' 실행")
        return 1

    out_path = OUT / "book.pdf"
    print("=" * 60)
    print(f" PDF 변환: {md_path.name} → {out_path.name}")
    print("=" * 60)
    md_to_pdf(md_path, out_path)
    print("\n완료. 이 PDF 를 Gumroad/크몽에 업로드하면 됩니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
