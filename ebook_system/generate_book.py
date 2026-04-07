"""
전자책 본문을 처음부터 끝까지 자동 생성한다.

1단계: 50개 챕터 목차를 생성
2단계: 각 챕터 본문을 약 1500자씩 작성 (스트리밍 + 실패 시 재시도)
3단계: 모든 챕터를 합쳐 output/book.md 로 저장

이미 만들어진 챕터는 건너뛴다 (중간에 끊겨도 이어서 진행 가능).
"""

import os
import sys
import json
import time
import random
from pathlib import Path

import anthropic

import config

# ============================================================
# 경로
# ============================================================
ROOT = Path(__file__).parent
OUT = ROOT / config.OUTPUT_DIR
CHAPTERS = OUT / config.CHAPTERS_SUBDIR
OUT.mkdir(exist_ok=True)
CHAPTERS.mkdir(exist_ok=True)

OUTLINE_PATH = OUT / "outline.json"
BOOK_MD_PATH = OUT / "book.md"

# ============================================================
# 클라이언트
# ============================================================
client = anthropic.Anthropic()  # ANTHROPIC_API_KEY 환경변수 자동 사용


# ============================================================
# 1단계: 목차 생성
# ============================================================
def generate_outline() -> dict:
    """50개 챕터 목차를 JSON 으로 받는다."""
    if OUTLINE_PATH.exists():
        print(f"  목차 캐시 존재: {OUTLINE_PATH} (재사용)")
        return json.loads(OUTLINE_PATH.read_text(encoding="utf-8"))

    user_prompt = f"""너는 한국 디지털 상품·AI 부업 분야 베스트셀러 작가다.
다음 책의 목차를 작성하라.

[책 정보]
제목: {config.BOOK_TITLE}
부제: {config.BOOK_SUBTITLE}
대상 독자: {config.TARGET_AUDIENCE}
약속: {config.PROMISE}

[요구사항]
- 정확히 {config.NUM_CHAPTERS}개 챕터
- 각 챕터는 "독자가 100일 안에 월 500만원 부업 수익을 만든다" 라는 단 하나의 결과로 수렴해야 함
- 추상 ❌ / 즉시 실행 가능한 구체성 ✅
- 챕터별 구성:
  * 1~10장: 마인드셋 + AI 부업 시장 이해
  * 11~25장: AI 디지털 상품 기획·제작 (전자책·템플릿·노션·강의·자동화)
  * 26~40장: 판매·마케팅·트래픽 (랜딩페이지·SNS·광고·SEO·이메일)
  * 41~50장: 자동화·스케일·재투자·법무·세무

[출력 형식]
JSON 만 출력. 다른 설명 금지:
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
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = "".join(b.text for b in msg.content if b.type == "text")
    start = text.find("{")
    end = text.rfind("}") + 1
    if start < 0 or end <= start:
        raise RuntimeError(f"목차 JSON 파싱 실패. 응답:\n{text[:500]}")

    outline = json.loads(text[start:end])
    if "chapters" not in outline or len(outline["chapters"]) < config.NUM_CHAPTERS // 2:
        raise RuntimeError(f"목차 챕터 수 부족: {len(outline.get('chapters', []))}")

    OUTLINE_PATH.write_text(
        json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  ✓ {len(outline['chapters'])}개 챕터 목차 저장: {OUTLINE_PATH}")
    return outline


# ============================================================
# 2단계: 챕터 본문 생성
# ============================================================
def generate_chapter(num: int, title: str, summary: str) -> str:
    """단일 챕터 본문을 마크다운으로 생성. 스트리밍 + 적응형 사고."""
    user_prompt = f"""너는 한국 AI 부업 분야 베스트셀러 작가다.
다음 챕터의 본문을 작성하라.

[책 제목]
{config.BOOK_TITLE}

[챕터 정보]
챕터 {num}: {title}
이 챕터의 약속: {summary}

[작성 요구사항]
- 분량: 한국어 약 {config.WORDS_PER_CHAPTER}자 (±200자)
- 구조: 도입(독자의 진짜 고통) → 핵심 개념 → 단계별 실행법 → 실제 예시 → 체크리스트
- 톤: 친근하지만 전문적. "~합니다"체.
- 즉시 실행 가능한 구체성. 일반론·뜬구름 금지.
- Claude/ChatGPT 실제 프롬프트 예시 1개 이상 포함 (코드 블록 사용)
- 화면 캡처 자리는 [캡처: 설명] 형식으로 표시
- 챕터 끝에 "## 이 챕터에서 얻은 것" 박스 (불릿 3~5개)

[출력 형식]
- 마크다운만 출력
- "# 챕터 N. 제목" 헤딩으로 시작
- 메타 코멘트·설명 금지

지금 작성하라."""

    full_text = ""
    with client.messages.stream(
        model=config.MODEL_CHAPTER,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text_chunk in stream.text_stream:
            full_text += text_chunk
        # 최종 메시지로 검증
        final = stream.get_final_message()
        if final.stop_reason == "max_tokens":
            print(f"    [경고] 챕터 {num} max_tokens 도달 (출력 잘림 가능)")

    return full_text.strip()


def generate_all_chapters(outline: dict) -> None:
    """모든 챕터를 순회하며 생성. 이미 있는 건 건너뜀. 실패 시 지수 백오프 재시도."""
    chapters = outline["chapters"]
    total = len(chapters)
    print(f"  {total}개 챕터 본문 생성 시작...")

    for i, ch in enumerate(chapters, 1):
        num = ch["num"]
        title = ch["title"]
        summary = ch.get("summary", "")
        path = CHAPTERS / f"ch{num:02d}.md"

        if path.exists() and path.stat().st_size > 200:
            print(f"  [{i}/{total}] 챕터 {num:02d}: 캐시 존재 (건너뜀)")
            continue

        print(f"  [{i}/{total}] 챕터 {num:02d}: {title}")

        # 재시도 루프
        for attempt in range(1, 6):
            try:
                body = generate_chapter(num, title, summary)
                if not body or len(body) < 300:
                    raise RuntimeError(f"본문 너무 짧음 ({len(body)}자)")
                path.write_text(body + "\n", encoding="utf-8")
                print(f"        ✓ 저장 ({len(body)}자)")
                break
            except anthropic.RateLimitError as e:
                wait = min(2**attempt + random.random(), 60)
                print(f"        rate limit, {wait:.1f}초 후 재시도 ({attempt}/5)")
                time.sleep(wait)
            except anthropic.APIStatusError as e:
                if e.status_code >= 500:
                    wait = min(2**attempt + random.random(), 60)
                    print(f"        서버 오류 {e.status_code}, {wait:.1f}초 후 재시도")
                    time.sleep(wait)
                else:
                    print(f"        실패 (재시도 안 함): {e}")
                    raise
            except Exception as e:
                wait = min(2**attempt + random.random(), 30)
                print(f"        오류: {e} → {wait:.1f}초 후 재시도")
                time.sleep(wait)
        else:
            print(f"        ✗ 챕터 {num} 5회 재시도 후 포기")

        # API 매너 있게: 챕터 사이 약간 쉼
        time.sleep(0.5)


# ============================================================
# 3단계: 합치기
# ============================================================
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
        path = CHAPTERS / f"ch{ch['num']:02d}.md"
        if not path.exists():
            print(f"  [경고] 챕터 {ch['num']} 누락")
            continue
        parts.append(path.read_text(encoding="utf-8"))
        parts.append("\n\n---\n\n")

    BOOK_MD_PATH.write_text("".join(parts), encoding="utf-8")
    size_kb = BOOK_MD_PATH.stat().st_size / 1024
    print(f"  ✓ 전체 책 마크다운: {BOOK_MD_PATH} ({size_kb:.1f} KB)")


# ============================================================
# 메인
# ============================================================
def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        print("       https://console.anthropic.com/settings/keys 에서 발급 후")
        print("       Windows PowerShell:  $env:ANTHROPIC_API_KEY='sk-ant-...'")
        return 1

    print("=" * 60)
    print(f" 전자책 자동 생성 시작")
    print(f" 제목: {config.BOOK_TITLE}")
    print(f" 챕터: {config.NUM_CHAPTERS}개")
    print("=" * 60)

    print("\n[1/3] 목차 생성")
    outline = generate_outline()

    print("\n[2/3] 챕터 본문 생성")
    generate_all_chapters(outline)

    print("\n[3/3] 전체 합치기")
    merge_book(outline)

    print("\n완료. 다음 단계: python make_pdf.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
