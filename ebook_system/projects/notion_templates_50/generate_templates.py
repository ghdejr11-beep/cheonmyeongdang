"""
Claude API 로 50개 노션 템플릿 상세 가이드 자동 생성.

각 템플릿마다:
- 이름 + 한 줄 설명
- 타깃 사용자 + 사용 상황
- 핵심 구조 (DB, 페이지, 속성 리스트)
- 단계별 제작법 (5~7단계)
- 판매 가격 + 마케팅 카피
- 예상 월 매출

사용법:
    python generate_templates.py

비용: Sonnet 4.5 기준 약 $3~5
시간: 20~40분
"""

import os
import sys
import json
import time
import random
from pathlib import Path

import anthropic
import config

_api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
if not _api_key:
    print("ERROR: ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
    sys.exit(1)

client = anthropic.Anthropic(api_key=_api_key)


def build_prompt(cat: dict) -> str:
    return f"""너는 노션 템플릿 디자이너이자 디지털 상품 사업 전문가다.
{cat['name']} 카테고리의 노션 템플릿 {cat['count']}개를 상세 설계해야 한다.

[참고 예시]
{cat['examples']}

[각 템플릿마다 작성할 내용]
1. **이름** (20자 이내, 임팩트 있게)
2. **한 줄 설명** (40자 이내)
3. **타깃 사용자** (구체적: 25~35세 직장인 여성 등)
4. **사용 시나리오** (어떤 상황에서, 왜 필요한지)
5. **핵심 구조**: 데이터베이스 / 페이지 / 속성 리스트 (불릿 5~10개)
6. **제작 단계** (5~7단계, 각 단계 1~2문장)
7. **판매 가격** (Gumroad/크몽 기준 원화)
8. **마케팅 카피** (Instagram 캡션 100자)
9. **예상 월 매출** (현실적 추정)

[출력 형식]
JSON 배열만 출력 (다른 설명 금지):

```json
[
  {{
    "num": 1,
    "name": "...",
    "tagline": "...",
    "target": "...",
    "scenario": "...",
    "structure": ["속성1", "속성2", ...],
    "build_steps": ["1단계: ...", "2단계: ...", ...],
    "price_krw": 9900,
    "marketing_copy": "...",
    "expected_revenue_monthly_krw": 500000
  }},
  ...
]
```

지금 {cat['name']} 카테고리의 {cat['count']}개 템플릿을 설계하라."""


def extract_json_array(text: str) -> list:
    if "```json" in text:
        s = text.find("```json") + 7
        e = text.find("```", s)
        if e > s:
            text = text[s:e]
    s = text.find("[")
    e = text.rfind("]") + 1
    if s < 0 or e <= s:
        raise ValueError(f"JSON 파싱 실패: {text[:300]}")
    return json.loads(text[s:e])


def generate_category(cat: dict) -> list:
    print(f"  ▶ [{cat['id']}] {cat['name']} — {cat['count']}개 생성 중...")
    for attempt in range(1, 5):
        try:
            full_text = ""
            with client.messages.stream(
                model=config.MODEL,
                max_tokens=config.MAX_TOKENS_PER_TEMPLATE * cat["count"],
                messages=[{"role": "user", "content": build_prompt(cat)}],
            ) as stream:
                for chunk in stream.text_stream:
                    full_text += chunk
            templates = extract_json_array(full_text)
            for i, t in enumerate(templates, 1):
                t["category"] = cat["id"]
                t["category_name"] = cat["name"]
                t["num"] = i
            print(f"    ✓ {len(templates)}개 생성 완료")
            return templates
        except anthropic.RateLimitError:
            wait = min(2**attempt + random.random(), 60)
            time.sleep(wait)
        except Exception as e:
            print(f"    오류 ({attempt}/4): {e}")
            if attempt == 4:
                return []
            time.sleep(2**attempt)
    return []


def main() -> int:
    print("=" * 70)
    print(f" {config.PRODUCT_TITLE}")
    print(f" 목표: 50개 템플릿 (10 카테고리 × 5개)")
    print("=" * 70)

    all_templates = []
    if config.TEMPLATES_JSON.exists():
        try:
            data = json.loads(config.TEMPLATES_JSON.read_text(encoding="utf-8"))
            all_templates = data.get("templates", [])
            print(f"기존 {len(all_templates)}개 불러옴\n")
        except Exception:
            pass

    for cat in config.CATEGORIES:
        existing_for_cat = [t for t in all_templates if t.get("category") == cat["id"]]
        if len(existing_for_cat) >= cat["count"]:
            print(f"  ✓ [{cat['id']}] 이미 {len(existing_for_cat)}개 존재 (건너뜀)")
            continue

        templates = generate_category(cat)
        all_templates = [t for t in all_templates if t.get("category") != cat["id"]]
        all_templates.extend(templates)

        config.TEMPLATES_JSON.write_text(
            json.dumps({"templates": all_templates}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        time.sleep(1)

    print(f"\n✓ 총 {len(all_templates)}개 템플릿 저장: {config.TEMPLATES_JSON}")
    print("다음: python make_pdf.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
