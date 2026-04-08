"""
'퇴사 후 1인 사업 플레이북' 50개 챕터 자동 생성.

기존 ebook_system/generate_book.py 와 동일한 패턴.
config.py 만 다르고 로직은 같음.

사용법:
    python generate_book.py

비용: Opus 4.6 기준 약 $5~10 (sonnet 으로 바꾸면 $2~5)
시간: 30~40분
"""

import os
import sys
import json
import time
import random
from pathlib import Path

import anthropic
import config

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

_api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
if not _api_key:
    print("ERROR: ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
    sys.exit(1)

client = anthropic.Anthropic(api_key=_api_key)


def generate_outline() -> dict:
    if config.OUTLINE_PATH.exists():
        print(f"  목차 캐시 존재 (재사용)")
        return json.loads(config.OUTLINE_PATH.read_text(encoding="utf-8"))

    prompt = f"""너는 한국 1인 사업·창업 분야 베스트셀러 작가다.
다음 책의 목차를 작성하라.

[책 정보]
제목: {config.BOOK_TITLE}
부제: {config.BOOK_SUBTITLE}
대상 독자: {config.TARGET_AUDIENCE}
약속: {config.PROMISE}

[4부 구조 — 이대로 따라 작성]
{config.PART_STRUCTURE}

[요구사항]
- 정확히 {config.NUM_CHAPTERS}개 챕터
- 각 챕터는 직장인이 1인 사업가로 변신하는 12개월 여정의 1단계
- 감정적 공감 + 실전 가이드 균형
- 추상 ❌, 구체적 액션 ✅

[출력]
JSON 만 출력 (다른 설명 금지):
{{
  "chapters": [
    {{"num": 1, "title": "...", "summary": "이 챕터에서 독자가 얻는 결과 한 줄"}},
    ...
  ]
}}"""

    print("  Claude API 호출 중 (목차 생성)...")
    msg = client.messages.create(
        model=config.MODEL_OUTLINE,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    )

    text = "".join(b.text for b in msg.content if b.type == "text")
    s = text.find("{")
    e = text.rfind("}") + 1
    outline = json.loads(text[s:e])
    config.OUTLINE_PATH.write_text(
        json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  ✓ {len(outline['chapters'])}개 챕터 목차 저장")
    return outline


def generate_chapter(num: int, title: str, summary: str) -> str:
    prompt = f"""너는 한국 1인 사업·창업 분야 베스트셀러 작가다.
다음 챕터의 본문을 작성하라.

[책 제목]
{config.BOOK_TITLE}

[챕터 정보]
챕터 {num}: {title}
이 챕터의 약속: {summary}

[작성 요구사항]
- 분량: 약 {config.WORDS_PER_CHAPTER}자 (±200자)
- 구조: 도입(독자의 진짜 고통 묘사) → 핵심 통찰 → 단계별 실행법 → 실제 사례 → 체크리스트
- 톤: 친구처럼 진심 어린, "당신" 호칭, "~합니다"체
- 직장인 → 1인 사업가 변신 12개월 여정의 한 단계로 자연스럽게 연결
- 감정 공감 + 실전 액션 균형 (50:50)
- 한국 직장 문화·세무·법무 정확하게 반영
- 챕터 끝에 "## 이 챕터의 핵심" 박스 (불릿 3~5개)

[출력]
마크다운만 출력. 메타 코멘트 금지.
"# 챕터 N. 제목" 헤딩으로 시작.

지금 작성하라."""

    full_text = ""
    with client.messages.stream(
        model=config.MODEL_CHAPTER,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for chunk in stream.text_stream:
            full_text += chunk
    return full_text.strip()


def generate_all_chapters(outline: dict) -> None:
    chapters = outline["chapters"]
    total = len(chapters)
    print(f"  {total}개 챕터 생성 중...")

    for i, ch in enumerate(chapters, 1):
        num = ch["num"]
        path = config.CHAPTERS_PATH / f"ch{num:02d}.md"
        if path.exists() and path.stat().st_size > 200:
            print(f"  [{i}/{total}] 챕터 {num:02d}: 캐시 (건너뜀)")
            continue
        print(f"  [{i}/{total}] 챕터 {num:02d}: {ch['title']}")
        for attempt in range(1, 6):
            try:
                body = generate_chapter(num, ch["title"], ch.get("summary", ""))
                if len(body) < 300:
                    raise RuntimeError("본문이 너무 짧음")
                path.write_text(body + "\n", encoding="utf-8")
                print(f"        ✓ {len(body)}자")
                break
            except anthropic.RateLimitError:
                wait = min(2**attempt + random.random(), 60)
                time.sleep(wait)
            except Exception as e:
                print(f"        오류 ({attempt}/5): {e}")
                if attempt == 5:
                    print(f"        ✗ 포기")
                else:
                    time.sleep(2**attempt)
        time.sleep(0.5)


def merge_book(outline: dict) -> None:
    parts = []
    parts.append(f"# {config.BOOK_TITLE}\n\n")
    parts.append(f"## {config.BOOK_SUBTITLE}\n\n")
    parts.append(f"**저자: {config.AUTHOR}**\n\n")
    parts.append("---\n\n")
    parts.append("## 목차\n\n")
    for ch in outline["chapters"]:
        parts.append(f"- 챕터 {ch['num']}. {ch['title']}\n")
    parts.append("\n---\n\n")
    for ch in outline["chapters"]:
        path = config.CHAPTERS_PATH / f"ch{ch['num']:02d}.md"
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
            parts.append("\n\n---\n\n")
    config.BOOK_MD_PATH.write_text("".join(parts), encoding="utf-8")
    print(f"  ✓ {config.BOOK_MD_PATH} ({config.BOOK_MD_PATH.stat().st_size//1024} KB)")


def main() -> int:
    print("=" * 70)
    print(f" {config.BOOK_TITLE}")
    print(f" 챕터: {config.NUM_CHAPTERS}개")
    print("=" * 70)

    print("\n[1/3] 목차 생성")
    outline = generate_outline()

    print("\n[2/3] 챕터 본문 생성")
    generate_all_chapters(outline)

    print("\n[3/3] 합치기")
    merge_book(outline)

    print("\n완료. 다음: python make_pdf.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
