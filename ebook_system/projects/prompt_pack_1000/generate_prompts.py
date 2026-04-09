"""
Claude API 로 카테고리별 100개 × 10 카테고리 = 총 1,000개 프롬프트 자동 생성.

사용법:
    cd ebook_system/projects/prompt_pack_1000
    python generate_prompts.py

환경변수 ANTHROPIC_API_KEY 필수.
예상 비용: Haiku 4.5 기준 약 $1~2 (모델 기본), Sonnet 으로 바꾸면 $3~5
예상 시간: 15~30분

중간에 끊겨도 output/prompts.json 에 누적되므로 다시 실행하면 이어서 진행.
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
# 클라이언트 (환경변수에서 키 읽기, 공백/줄바꿈 자동 제거)
# ============================================================
_api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
if not _api_key:
    print("ERROR: ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
    print("       Windows PowerShell:")
    print('         $env:ANTHROPIC_API_KEY = "sk-ant-api03-..."')
    sys.exit(1)

client = anthropic.Anthropic(api_key=_api_key)


# ============================================================
# 배치 단위 프롬프트 생성
# ============================================================
BATCH_SIZE = 20  # 한 번의 API 호출에서 생성할 프롬프트 수 (토큰 한계 내로 안정)


def build_batch_prompt(cat: dict, batch_size: int, existing_titles: list) -> str:
    avoid_block = ""
    if existing_titles:
        titles_str = ", ".join(f'"{t}"' for t in existing_titles[-60:])
        avoid_block = f"\n\n[이미 만든 것 — 중복 금지]\n{titles_str}\n\n위와 겹치지 않는 새로운 주제로 만들어라."

    return f"""너는 한국 AI 활용 전문가다.
ChatGPT·Claude 같은 LLM 을 실무에 활용하는 **{cat['name']}** 분야의
프롬프트 **{batch_size}개**를 작성해야 한다.

[요구사항]
1. 각 프롬프트는 실무자가 **복붙해서 바로 쓸 수 있어야** 한다.
2. **구체적 상황 → 구체적 프롬프트 → 예상 결과**의 3단 구조.
3. 한국어로 작성. 한국인이 실제로 겪는 상황 중심.
4. {cat['description']} 영역을 골고루 커버.
5. 프롬프트 본문에는 [제품명], [고객명] 같은 **플레이스홀더** 를 사용.
6. 난이도는 초급 30% / 중급 50% / 고급 20%.
7. 서로 중복되지 않게 다양하게.{avoid_block}

[출력 형식]
JSON 배열만 출력 (다른 설명 금지):

```json
[
  {{
    "num": 1,
    "title": "프롬프트 이름 (20자 이내)",
    "situation": "이 프롬프트를 쓰는 상황 (50자 이내)",
    "prompt": "복붙해서 바로 쓸 수 있는 실제 프롬프트 본문. [플레이스홀더]를 사용한 재사용 가능 형태. 여러 줄 가능.",
    "expected": "이 프롬프트로 얻을 수 있는 결과 (30자 이내)"
  }},
  ...
]
```

지금 {cat['name']} 카테고리의 {batch_size}개 프롬프트를 작성하라.
JSON 만 출력, 설명·주석 금지."""


def extract_json_array(text: str) -> list:
    """응답 텍스트에서 JSON 배열 추출."""
    # ```json ... ``` 블록 찾기
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            text = text[start:end]
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end > start:
            text = text[start:end]

    # 배열 범위 찾기
    start = text.find("[")
    end = text.rfind("]") + 1
    if start < 0 or end <= start:
        raise ValueError(f"JSON 배열을 찾을 수 없음. 응답 시작: {text[:300]}")

    # strict=False: 문자열 내부 줄바꿈·탭 등 제어 문자 허용
    # (Claude 가 프롬프트 본문에 raw \n 을 출력하는 경우 대응)
    return json.loads(text[start:end], strict=False)


def generate_batch(cat: dict, batch_size: int, existing_titles: list) -> list:
    """단일 배치 (20개 프롬프트) 생성. 실패 시 재시도."""
    for attempt in range(1, 5):
        try:
            full_text = ""
            with client.messages.stream(
                model=config.MODEL,
                max_tokens=config.MAX_TOKENS_PER_CATEGORY,
                messages=[{"role": "user", "content": build_batch_prompt(cat, batch_size, existing_titles)}],
            ) as stream:
                for chunk in stream.text_stream:
                    full_text += chunk

            return extract_json_array(full_text)

        except anthropic.RateLimitError:
            wait = min(2**attempt + random.random(), 60)
            print(f"      rate limit → {wait:.1f}초 대기 ({attempt}/4)")
            time.sleep(wait)
        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                wait = min(2**attempt + random.random(), 60)
                print(f"      server {e.status_code} → {wait:.1f}초 대기")
                time.sleep(wait)
            else:
                raise
        except Exception as e:
            print(f"      배치 시도 {attempt} 실패: {str(e)[:120]}")
            if attempt == 4:
                print(f"      ✗ 배치 포기")
                return []
            time.sleep(2**attempt)

    return []


def generate_category(cat: dict, existing: list) -> list:
    """카테고리의 프롬프트 생성. BATCH_SIZE 단위로 나눠서 호출."""
    cat_id = cat["id"]
    target_count = cat["count"]

    existing_for_cat = [p for p in existing if p.get("category") == cat_id]
    if len(existing_for_cat) >= target_count:
        print(f"  ✓ [{cat_id}] 이미 {len(existing_for_cat)}개 존재 (건너뜀)")
        return existing_for_cat

    print(f"  ▶ [{cat_id}] {cat['name']} — {target_count}개 생성 중 (배치 {BATCH_SIZE}개씩)")

    collected = list(existing_for_cat)  # 이어서 생성
    batch_num = 0
    while len(collected) < target_count:
        batch_num += 1
        remaining = target_count - len(collected)
        this_batch = min(BATCH_SIZE, remaining)
        existing_titles = [p.get("title", "") for p in collected]

        print(f"    · 배치 {batch_num}: {this_batch}개 요청 중... (누적 {len(collected)}/{target_count})")
        batch_prompts = generate_batch(cat, this_batch, existing_titles)

        if not batch_prompts:
            print(f"    ⚠ 배치 {batch_num} 0개 반환 → 이 카테고리 중단 (다음 실행 시 이어감)")
            break

        collected.extend(batch_prompts)
        time.sleep(0.5)  # 서버 부담 완화

    # num / category 메타데이터 재부여
    for i, p in enumerate(collected, 1):
        p["category"] = cat_id
        p["category_name"] = cat["name"]
        p["num"] = i

    print(f"    ✓ 총 {len(collected)}개 확보")
    return collected


# ============================================================
# 메인
# ============================================================
def main() -> int:
    print("=" * 70)
    print(f" {config.PRODUCT_TITLE}")
    print(f" 목표: {sum(c['count'] for c in config.CATEGORIES):,}개 프롬프트")
    print(f" 모델: {config.MODEL}")
    print("=" * 70)
    print()

    # 기존 저장된 것 불러오기 (재실행 대비)
    all_prompts = []
    if config.PROMPTS_JSON.exists():
        try:
            data = json.loads(config.PROMPTS_JSON.read_text(encoding="utf-8"))
            all_prompts = data.get("prompts", [])
            print(f"기존 {len(all_prompts)}개 프롬프트 불러옴\n")
        except Exception as e:
            print(f"기존 파일 읽기 실패 (무시): {e}\n")

    # 카테고리별 생성
    for cat in config.CATEGORIES:
        prompts = generate_category(cat, all_prompts)
        # 기존 것 중 이 카테고리 제외
        all_prompts = [p for p in all_prompts if p.get("category") != cat["id"]]
        all_prompts.extend(prompts)

        # 중간 저장 (끊겨도 복구 가능)
        config.PROMPTS_JSON.write_text(
            json.dumps({"prompts": all_prompts}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        time.sleep(1)

    print()
    print(f"✓ 총 {len(all_prompts):,}개 프롬프트 저장: {config.PROMPTS_JSON}")
    print()
    print("다음 단계: python make_prompt_pdf.py 로 PDF 변환")
    return 0


if __name__ == "__main__":
    sys.exit(main())
