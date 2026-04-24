#!/usr/bin/env python3
"""
매주 월요일 실행. Claude에게 최신 AI 부업 트렌드 토픽 15개 재생성 요청.
결과를 topics.json 저장 → orchestrator.py가 우선 로드.

실패 시 orchestrator.py 내장 기본 TOPICS로 폴백 (내결함성).
"""
import sys, json, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DEPT = Path(__file__).parent
sys.path.insert(0, str(DEPT.parent / "shared"))
from claude_script import generate

TOPICS_FILE = DEPT / "topics.json"
HISTORY_FILE = DEPT / "topics_history.jsonl"


def gen_topics(prior_topics=None):
    prior_block = ""
    if prior_topics:
        prior_block = "\n\nAlready used (avoid duplicates):\n" + "\n".join(f"- {t}" for t in prior_topics[-30:])

    prompt = f"""Generate 15 YouTube Shorts title ideas about AI side hustles and making money with AI tools in 2026.

Requirements:
- Each title 6-12 words, strong curiosity gap
- Mix of: (a) listicles ("3 AI tools that..."), (b) contrarian takes ("Why ChatGPT is..."), (c) how-tos, (d) myth-busting, (e) beginner hooks
- Target audience: people who want passive/side income with zero coding
- Must be specific enough to generate a focused 60-second script
- No clickbait promises ("guaranteed $10k"), but strong hooks allowed
- Topics should be TIMELY to 2026 (Claude 4.6, Sonnet, Agent SDK era, Gumroad, KDP, Shopify AI)
{prior_block}

Return ONLY a JSON array of 15 strings. No markdown, no explanations.
Example: ["3 AI tools that...", "The passive income trick...", ...]"""

    raw = generate(prompt, max_tokens=900).strip()

    # 코드펜스 제거
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    # JSON 파싱
    topics = json.loads(raw)
    if not isinstance(topics, list) or len(topics) < 10:
        raise ValueError(f"bad response: {raw[:200]}")
    return [str(t).strip() for t in topics][:15]


def load_history():
    if not HISTORY_FILE.exists():
        return []
    lines = HISTORY_FILE.read_text(encoding="utf-8").splitlines()
    prior = []
    for line in lines:
        if line.strip():
            try:
                prior += json.loads(line).get("topics", [])
            except Exception:
                pass
    return prior


def main():
    prior = load_history()
    print(f"📚 과거 토픽 {len(prior)}개 회피 대상")

    topics = gen_topics(prior)
    print(f"🆕 새 토픽 {len(topics)}개")
    for i, t in enumerate(topics, 1):
        print(f"  {i:2d}. {t}")

    # 저장
    TOPICS_FILE.write_text(
        json.dumps({"refreshed": datetime.date.today().isoformat(), "topics": topics},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    # 히스토리 append
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"date": datetime.date.today().isoformat(), "topics": topics}, ensure_ascii=False) + "\n")
    print(f"✅ {TOPICS_FILE}")


if __name__ == "__main__":
    main()
