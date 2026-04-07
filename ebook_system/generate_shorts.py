"""
숏폼(릴스/틱톡/숏츠) 후크 100개 + 30~45초 스크립트를 자동 생성한다.
output/shorts/ 폴더에 short_001.md ~ short_100.md 로 저장.
"""

import os
import sys
import json
import time
import random
from pathlib import Path

import anthropic

import config

ROOT = Path(__file__).parent
OUT = ROOT / config.OUTPUT_DIR
SHORTS = OUT / config.SHORTS_SUBDIR
OUT.mkdir(exist_ok=True)
SHORTS.mkdir(exist_ok=True)

HOOKS_PATH = OUT / "hooks.json"

# 환경변수에서 API 키 읽을 때 앞뒤 공백/줄바꿈 자동 제거
_api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
client = anthropic.Anthropic(api_key=_api_key) if _api_key else anthropic.Anthropic()


# ============================================================
# 1단계: 후크 100개 생성
# ============================================================
def generate_hooks(n: int = 100) -> list[str]:
    if HOOKS_PATH.exists():
        data = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))
        if len(data.get("hooks", [])) >= n:
            print(f"  후크 캐시 존재: {len(data['hooks'])}개 (재사용)")
            return data["hooks"][:n]

    user_prompt = f"""한국어 숏폼(릴스/틱톡/유튜브 숏츠) 후크 정확히 {n}개를 만들어라.

[주제]
{config.BOOK_TITLE}
({config.PROMISE})

[대상]
{config.TARGET_AUDIENCE}

[후크 작성 원칙]
- 5초 안에 시청자를 잡는 첫 한 문장
- MZ세대 한국어 톤
- 구체적 숫자/결과 강조 ("월 300만원", "30분 만에", "직장 관두지 않고")
- 호기심 / 공포 / 욕심 / 사회적 지위 트리거 사용
- 클릭베이트지만 책 본문에서 약속을 지킬 수 있는 수준
- 100개 모두 서로 다른 각도/패턴 (반복 금지)

[출력]
JSON 만 출력 (다른 설명 금지):
{{"hooks": ["후크1", "후크2", ...]}}"""

    print(f"  Claude API 호출 중 (후크 {n}개)...")
    full_text = ""
    with client.messages.stream(
        model=config.MODEL_SHORTS,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for chunk in stream.text_stream:
            full_text += chunk

    s = full_text.find("{")
    e = full_text.rfind("}") + 1
    if s < 0 or e <= s:
        raise RuntimeError(f"후크 JSON 파싱 실패:\n{full_text[:500]}")
    data = json.loads(full_text[s:e])
    hooks = data.get("hooks", [])
    if len(hooks) < n:
        print(f"  [경고] 요청 {n}개 / 받은 {len(hooks)}개")
    HOOKS_PATH.write_text(
        json.dumps({"hooks": hooks}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  ✓ {len(hooks)}개 후크 저장: {HOOKS_PATH}")
    return hooks


# ============================================================
# 2단계: 후크별 스크립트 생성
# ============================================================
def generate_script(num: int, hook: str) -> str:
    user_prompt = f"""다음 후크로 30~45초 한국어 숏폼 영상 스크립트를 작성하라.

후크: {hook}

[주제]
{config.BOOK_TITLE}

[구조]
1. HOOK (0~3초): 후크 한 문장 (자막 + 화면 지시)
2. 문제 (3~8초): 시청자 진짜 고통 1줄
3. 해결 (8~30초): AI 로 어떻게 가능한지 3단계
4. CTA (30~45초): "프로필 링크에서 무료 가이드 받으세요"

[출력 형식]
마크다운. 각 구간마다:
- **자막**: 화면에 띄울 텍스트
- **화면**: 어떤 영상/캡처/움직임이 있어야 하는지
- **나레이션**: 음성으로 읽을 문장 (없으면 생략)

다른 설명 금지. 스크립트만 출력하라."""

    msg = client.messages.create(
        model=config.MODEL_SHORTS,
        max_tokens=2000,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def generate_all_scripts(hooks: list[str]) -> None:
    total = len(hooks)
    for i, hook in enumerate(hooks, 1):
        path = SHORTS / f"short_{i:03d}.md"
        if path.exists() and path.stat().st_size > 100:
            continue

        print(f"  [{i:03d}/{total}] {hook[:40]}...")
        for attempt in range(1, 5):
            try:
                script = generate_script(i, hook)
                content = f"# 숏츠 {i:03d}\n\n## 후크\n{hook}\n\n## 스크립트\n{script}\n"
                path.write_text(content, encoding="utf-8")
                break
            except anthropic.RateLimitError:
                wait = 2**attempt + random.random()
                print(f"        rate limit, {wait:.1f}초 후 재시도")
                time.sleep(wait)
            except Exception as e:
                print(f"        오류: {e}")
                if attempt == 4:
                    print(f"        ✗ 포기")
                else:
                    time.sleep(2**attempt)

        time.sleep(0.3)


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        return 1

    print("=" * 60)
    print(" 숏폼 후크 + 스크립트 자동 생성")
    print("=" * 60)

    print("\n[1/2] 후크 100개")
    hooks = generate_hooks(100)

    print("\n[2/2] 각 후크별 30~45초 스크립트")
    generate_all_scripts(hooks)

    print(f"\n완료. {SHORTS}/ 폴더에 short_001.md ~ short_100.md")
    print("\n다음: 각 스크립트를 보고 1일 1~3개씩 릴스/틱톡 제작 → 업로드")
    return 0


if __name__ == "__main__":
    sys.exit(main())
