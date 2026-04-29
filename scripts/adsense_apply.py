# -*- coding: utf-8 -*-
"""
adsense_apply.py — AdSense 승인 후 ca-pub + slot ID 6개 자동 교체 스크립트

사용법:
    # 대화형 입력
    python scripts/adsense_apply.py

    # 인자 직접 전달
    python scripts/adsense_apply.py \\
        --pub 1234567890123456 \\
        --slot1 1111111111 --slot2 2222222222 --slot3 3333333333 \\
        --slot4 4444444444 --slot5 5555555555 --slot6 6666666666

    # dry-run (변경 미반영, diff만 출력)
    python scripts/adsense_apply.py --dry-run --pub 1234567890123456 ...

동작:
    1. index.html 의 ca-pub-PLACEHOLDER 5곳(head 1 + ins 4) → ca-pub-{pub} 로 교체
       (※ ins 태그는 6개라 모두 같은 client 값으로 통일)
    2. data-ad-slot="0000000001..6" → 사용자 입력 slot ID 로 교체
    3. ads.txt 의 pub-PLACEHOLDER → pub-{pub} 로 교체
    4. 백업 파일 (.bak) 생성
    5. Vercel 재배포 안내 출력

안전 장치:
    - pub ID 는 정확히 16자리 숫자만 허용
    - slot ID 는 10자리 숫자 권장 (실제 AdSense 발급 형식)
    - 교체 전 PLACEHOLDER 가 존재하는지 확인 (이미 교체된 파일에는 적용 안 함)
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Windows cp949 콘솔에서 한국어 출력 보장
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "index.html"
ADS_TXT_PATH = PROJECT_ROOT / "ads.txt"

# index.html 안의 placeholder slot ID 순서 (코드 작성 순서)
PLACEHOLDER_SLOTS = [
    "0000000001",  # 사주 결과 하단
    "0000000002",  # 궁합 결과 하단
    "0000000003",  # 타로 결과 하단
    "0000000004",  # 별자리 운세 결과 하단
    "0000000005",  # 꿈해몽 채팅 결과 in-feed
    "0000000006",  # 오늘의 운세 결과 하단
]


def validate_pub(pub: str) -> str:
    pub = pub.strip().replace("ca-pub-", "").replace("pub-", "")
    if not re.fullmatch(r"\d{16}", pub):
        raise ValueError(f"ca-pub ID 는 정확히 16자리 숫자여야 합니다 (입력값: {pub!r})")
    return pub


def validate_slot(slot: str) -> str:
    slot = slot.strip()
    if not re.fullmatch(r"\d{6,12}", slot):
        raise ValueError(f"slot ID 는 6~12자리 숫자여야 합니다 (입력값: {slot!r})")
    return slot


def prompt_inputs() -> tuple[str, list[str]]:
    print("=" * 60)
    print(" AdSense 승인 정보 입력 — 천명당")
    print("=" * 60)
    print(" AdSense 콘솔 -> 광고 -> 광고 단위에서 발급된 정보를 입력하세요.")
    print()
    pub = input(" Publisher ID (ca-pub-XXXXXXXXXXXXXXXX, 16자리 숫자): ").strip()
    pub = validate_pub(pub)

    slot_labels = [
        "사주 결과 하단",
        "궁합 결과 하단",
        "타로 결과 하단",
        "별자리 운세 결과 하단",
        "꿈해몽 in-feed",
        "오늘의 운세 결과 하단",
    ]
    slots = []
    for i, label in enumerate(slot_labels, start=1):
        s = input(f" 광고 슬롯 #{i} ({label}) ID: ").strip()
        slots.append(validate_slot(s))
    return pub, slots


def apply_to_index(pub: str, slots: list[str], dry_run: bool) -> tuple[int, int]:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"index.html 없음: {INDEX_PATH}")
    html = INDEX_PATH.read_text(encoding="utf-8")
    original = html

    # 1) ca-pub-PLACEHOLDER -> ca-pub-{pub}
    pub_replaced = html.count("ca-pub-PLACEHOLDER")
    html = html.replace("ca-pub-PLACEHOLDER", f"ca-pub-{pub}")

    # 2) data-ad-slot="0000000001..6" -> 사용자 슬롯
    slot_replaced = 0
    for ph, real in zip(PLACEHOLDER_SLOTS, slots):
        before = html.count(f'data-ad-slot="{ph}"')
        html = html.replace(f'data-ad-slot="{ph}"', f'data-ad-slot="{real}"')
        slot_replaced += before

    if pub_replaced == 0 and slot_replaced == 0:
        print("[경고] index.html 에 PLACEHOLDER 가 이미 없음 — 이전에 적용된 것으로 보임")

    if dry_run:
        print(f"[dry-run] index.html: pub {pub_replaced}곳, slot {slot_replaced}곳 교체 예정")
        return pub_replaced, slot_replaced

    if html != original:
        backup = INDEX_PATH.with_suffix(".html.bak")
        shutil.copy2(INDEX_PATH, backup)
        INDEX_PATH.write_text(html, encoding="utf-8")
        print(f"[OK] index.html 업데이트 (pub {pub_replaced}곳, slot {slot_replaced}곳)")
        print(f"     백업: {backup.name}")
    return pub_replaced, slot_replaced


def apply_to_ads_txt(pub: str, dry_run: bool) -> int:
    if not ADS_TXT_PATH.exists():
        # 없으면 생성
        text = (
            "# Google AdSense ads.txt\n"
            f"google.com, pub-{pub}, DIRECT, f08c47fec0942fa0\n"
        )
        if dry_run:
            print(f"[dry-run] ads.txt 신규 생성 예정")
            return 1
        ADS_TXT_PATH.write_text(text, encoding="utf-8")
        print(f"[OK] ads.txt 생성")
        return 1

    text = ADS_TXT_PATH.read_text(encoding="utf-8")
    original = text
    text = text.replace("pub-PLACEHOLDER", f"pub-{pub}")
    # 혹시 PLACEHOLDER 가 없는 라인 형태면 라인 추가
    if f"pub-{pub}" not in text:
        text += f"\ngoogle.com, pub-{pub}, DIRECT, f08c47fec0942fa0\n"

    replaced = 1 if text != original else 0
    if dry_run:
        print(f"[dry-run] ads.txt 변경 {replaced}건")
        return replaced
    if replaced:
        backup = ADS_TXT_PATH.with_suffix(".txt.bak")
        shutil.copy2(ADS_TXT_PATH, backup)
        ADS_TXT_PATH.write_text(text, encoding="utf-8")
        print(f"[OK] ads.txt 업데이트  (백업: {backup.name})")
    return replaced


def main() -> int:
    parser = argparse.ArgumentParser(description="AdSense 코드 자동 교체")
    parser.add_argument("--pub", help="Publisher ID (16자리 숫자)")
    for i in range(1, 7):
        parser.add_argument(f"--slot{i}", help=f"슬롯 #{i} ID")
    parser.add_argument("--dry-run", action="store_true", help="변경 미반영 (미리보기)")
    args = parser.parse_args()

    if args.pub and all(getattr(args, f"slot{i}") for i in range(1, 7)):
        pub = validate_pub(args.pub)
        slots = [validate_slot(getattr(args, f"slot{i}")) for i in range(1, 7)]
    else:
        pub, slots = prompt_inputs()

    print()
    print(f"  Publisher: ca-pub-{pub}")
    for i, s in enumerate(slots, start=1):
        print(f"  Slot #{i}: {s}")
    print()

    apply_to_index(pub, slots, args.dry_run)
    apply_to_ads_txt(pub, args.dry_run)

    print()
    print("=" * 60)
    if args.dry_run:
        print(" dry-run 종료 — 실제 적용은 --dry-run 제거 후 재실행")
    else:
        print(" 적용 완료. 다음 명령으로 Vercel 배포:")
        print()
        print("   cd C:/Users/hdh02/Desktop/cheonmyeongdang")
        print("   git add index.html ads.txt")
        print('   git commit -m "AdSense: ca-pub + 6개 slot ID 적용"')
        print("   git push   # Vercel 자동 배포")
        print()
        print(" 또는 Vercel CLI:")
        print("   vercel --prod")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, FileNotFoundError) as e:
        print(f"[오류] {e}", file=sys.stderr)
        sys.exit(2)
