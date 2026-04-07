"""
전체 파이프라인을 한 번에 실행한다.

순서:
  1. generate_book.py   — 책 본문 생성 (옵션: 처음 1회)
  2. make_pdf.py        — PDF 변환
  3. generate_shorts.py — 숏폼 100개 생성
  4. build_landing.py   — 랜딩 페이지 빌드

각 단계는 독립적이며, 이미 결과물이 있으면 건너뛴다.
중간에 끊겨도 다시 실행하면 이어서 진행된다.

Windows Task Scheduler 에 등록하면 손 안 대고 매일 자동 실행 가능.
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent

STEPS = [
    ("책 본문 생성", "generate_book.py"),
    ("PDF 변환", "make_pdf.py"),
    ("숏폼 100개 생성", "generate_shorts.py"),
    ("랜딩 페이지 빌드", "build_landing.py"),
]


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        print()
        print("Windows PowerShell:")
        print('   $env:ANTHROPIC_API_KEY = "sk-ant-..."')
        print()
        print("Windows 영구 설정 (한 번만):")
        print('   [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")')
        return 1

    print("=" * 70)
    print(" 전자책 자동화 풀 파이프라인 시작")
    print("=" * 70)

    for label, script in STEPS:
        print(f"\n{'━' * 70}")
        print(f"▶ {label}  ({script})")
        print(f"{'━' * 70}")
        result = subprocess.run(
            [sys.executable, str(ROOT / script)],
            cwd=str(ROOT),
        )
        if result.returncode != 0:
            print(f"\n✗ {script} 실패 (exit {result.returncode})")
            print(f"  → 문제 해결 후 'python {script}' 만 다시 실행하면 됩니다.")
            return result.returncode

    print("\n" + "=" * 70)
    print(" ✓ 모든 단계 완료")
    print("=" * 70)
    print()
    print("결과물:")
    print(f"   - output/book.pdf      ← Gumroad/크몽에 업로드할 PDF")
    print(f"   - output/landing.html  ← GitHub Pages/Netlify에 업로드")
    print(f"   - output/shorts/       ← 100개 숏폼 스크립트")
    print()
    print("다음 액션:")
    print("   1. Gumroad 계정 만들기 → PDF 업로드 → 결제 링크 받기")
    print("   2. config.py 의 GUMROAD_* 링크 채우기 → run_all.py 다시 실행")
    print("   3. 랜딩 페이지 호스팅 → SNS 프로필에 링크 등록")
    print("   4. 매일 숏폼 1~3개 업로드 (output/shorts/ 에서 가져오기)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
