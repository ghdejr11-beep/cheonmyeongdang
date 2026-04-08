"""
본책 PDF (output/book.pdf) 에서 처음 일부 챕터만 잘라
output/teaser.pdf (무료 미끼 상품) 을 만든다.

기본값: 챕터 1~5 만 추출 (약 30p)
사용법:
    python launch/extract_teaser.py            # 기본값 (챕터 1~5)
    python launch/extract_teaser.py 10         # 챕터 1~10

make_pdf.py 와 동일한 방식으로 마크다운을 PDF 변환하므로
한국어 폰트 자동 처리가 그대로 작동한다.
"""

import sys
import json
from pathlib import Path

# ebook_system 폴더를 모듈 경로에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config
from make_pdf import md_to_pdf  # 기존 PDF 변환기 재사용

OUT = ROOT / config.OUTPUT_DIR
OUTLINE_PATH = OUT / "outline.json"
CHAPTERS = OUT / config.CHAPTERS_SUBDIR


def main() -> int:
    # 몇 챕터까지 추출할지
    try:
        max_chapter = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    except ValueError:
        print(f"사용법: python {sys.argv[0]} [챕터수]")
        return 1

    if not OUTLINE_PATH.exists():
        print(f"ERROR: {OUTLINE_PATH} 없음. 먼저 'python generate_book.py' 실행")
        return 1

    outline = json.loads(OUTLINE_PATH.read_text(encoding="utf-8"))
    chapters = outline.get("chapters", [])
    if not chapters:
        print("ERROR: outline.json 에 챕터 없음")
        return 1

    target = [c for c in chapters if c["num"] <= max_chapter]
    if not target:
        print(f"ERROR: 챕터 1~{max_chapter} 이 없음")
        return 1

    print(f"티저 PDF 생성: 챕터 1~{max_chapter} ({len(target)}개 챕터)")

    # 티저용 마크다운 조립
    parts = []
    parts.append(f"# {config.BOOK_TITLE}\n\n")
    parts.append(f"## {config.BOOK_SUBTITLE}\n\n")
    parts.append(f"**저자: {config.AUTHOR}**\n\n")
    parts.append("---\n\n")
    parts.append("## 무료 미리보기 (Chapter 1~{}) \n\n".format(max_chapter))
    parts.append(
        "> 이 PDF 는 본책의 **무료 샘플**입니다.\n"
        "> 전체 50개 챕터 중 앞부분 {}개를 무료로 제공합니다.\n\n".format(max_chapter)
    )
    parts.append("## 이 책에서 얻는 것\n\n")
    parts.append("- AI(Claude·ChatGPT)로 디지털 상품 자동화 시스템 구축\n")
    parts.append("- 100일 안에 월 500만원 부업 수익 만드는 단계별 로드맵\n")
    parts.append("- 한국어 실전 프롬프트 100개 (복붙해서 바로 사용)\n")
    parts.append("- 랜딩페이지·광고·SEO 전환 시스템\n")
    parts.append("- 자동화 + 세무 + 스케일 완전 가이드\n\n")
    parts.append("---\n\n")
    parts.append("## 목차 (전체 50장)\n\n")
    for c in chapters:
        marker = "✓" if c["num"] <= max_chapter else " "
        parts.append(f"- [{marker}] 챕터 {c['num']}. {c['title']}\n")
    parts.append("\n")
    parts.append("> **✓** 표시된 챕터는 이 무료 샘플에 포함되어 있습니다.\n\n")
    parts.append("---\n\n")

    # 각 챕터 본문 추가
    missing = []
    for c in target:
        path = CHAPTERS / f"ch{c['num']:02d}.md"
        if not path.exists():
            missing.append(c["num"])
            continue
        parts.append(path.read_text(encoding="utf-8"))
        parts.append("\n\n---\n\n")

    if missing:
        print(f"[경고] 누락 챕터: {missing}")

    # 마지막 판매 CTA 페이지
    parts.append("\n# 여기까지 읽으셨다면\n\n")
    parts.append(
        "이 책은 총 50개 챕터로 구성되어 있고, 지금 보신 것은 약 10% 입니다. "
        "나머지 90% 에는 다음이 들어있습니다:\n\n"
    )
    parts.append("- 디지털 상품 5종 실전 제작법 (전자책/노션/강의/봇/SaaS)\n")
    parts.append("- 한국어 프롬프트 100개 (복붙용)\n")
    parts.append("- 릴스/틱톡 후크 100개 + 30초 스크립트\n")
    parts.append("- Meta/카카오 광고 카피 50개\n")
    parts.append("- 100일 단계별 실행 로드맵\n")
    parts.append("- 자동화·세무·스케일 완전 가이드\n\n")
    parts.append("## 전체 200페이지 + 템플릿 받기\n\n")
    parts.append("**LITE**: 19,900원 — 본책 핵심 50p\n\n")
    parts.append("**STANDARD**: 99,000원 — 본책 전체 + 템플릿 5종 + 프롬프트 100개\n\n")
    parts.append("**PREMIUM**: 299,000원 — 위 전체 + 1:1 카톡 30일 + 평생 업데이트\n\n")
    parts.append("## 7일 100% 환불 보장\n\n")
    parts.append(
        "부담 없이 시작하세요. 7일 안에 \"도움 안 됐다\"고 판단되면 이유 없이 100% 환불해드립니다. "
        "다운로드한 PDF는 그대로 가지셔도 됩니다.\n\n"
    )
    parts.append("---\n\n")
    parts.append("_본 샘플을 끝까지 읽어주셔서 감사합니다._\n")

    # 티저 마크다운 저장
    teaser_md = OUT / "teaser.md"
    teaser_md.write_text("".join(parts), encoding="utf-8")
    print(f"  ✓ 티저 마크다운: {teaser_md} ({teaser_md.stat().st_size // 1024} KB)")

    # PDF 변환
    teaser_pdf = OUT / "teaser.pdf"
    print("  PDF 변환 중...")
    md_to_pdf(teaser_md, teaser_pdf)

    print()
    print("완료. 다음 단계:")
    print(f"  1. {teaser_pdf} 를 Gumroad 에 '무료 상품' 으로 추가 등록")
    print(f"  2. 랜딩 페이지의 '무료 샘플 받기' 폼 → 이 URL 로 연결")
    print(f"  3. 이메일 퍼널 (launch/email_sequence.md) 자동 발송 설정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
