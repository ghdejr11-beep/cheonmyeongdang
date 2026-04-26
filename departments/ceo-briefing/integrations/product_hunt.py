"""
Product Hunt RSS 수집 — 오늘 TOP 제품 + 쿤스튜디오 매칭도 점수
인증 불필요
"""
import feedparser
import re
from datetime import datetime

# 쿤스튜디오 포트폴리오 매칭 키워드 (점수 가중)
MATCH_KEYWORDS = {
    "ai": 3, "artificial intelligence": 3, "llm": 3, "gpt": 2, "claude": 2,
    "saas": 2, "tool": 1, "automat": 3, "productivity": 2,
    "notion": 3, "template": 3, "prompt": 3,
    "newsletter": 2, "ebook": 3, "book": 2,
    "saju": 5, "fortune": 4, "horoscope": 4, "astrology": 3,
    "tax": 4, "insurance": 4, "finance": 2, "money": 2,
    "korean": 3, "korea": 3,
    "faceless": 3, "youtube": 2, "video": 1,
    "tourism": 3, "travel": 2, "tour": 2,
    "bookkeeping": 3, "accounting": 2,
}

# 노이즈 필터 (쿤스튜디오와 무관한 제품 걸러냄)
NOISE_PATTERNS = ["dating", "nft", "crypto wallet", "gaming guild"]


def fetch_feed(url="https://www.producthunt.com/feed"):
    try:
        feed = feedparser.parse(url)
        return feed.entries
    except Exception as e:
        return []


def score_entry(entry):
    """제품 매칭 점수 계산"""
    text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
    # 노이즈 필터
    for noise in NOISE_PATTERNS:
        if noise in text:
            return -1
    score = 0
    matched = []
    for kw, weight in MATCH_KEYWORDS.items():
        if kw in text:
            score += weight
            matched.append(kw)
    return score, matched


def parse_entry(entry):
    """엔트리 파싱"""
    title = entry.get("title", "")
    link = entry.get("link", "")
    summary = entry.get("summary", "")
    # summary HTML 제거
    summary_text = re.sub(r"<[^>]+>", " ", summary)
    summary_text = re.sub(r"\s+", " ", summary_text).strip()[:200]
    pub = entry.get("published", "")
    return {
        "title": title,
        "link": link,
        "summary": summary_text,
        "published": pub,
    }


def daily_summary(top_n=10):
    """브리핑용 TOP N + 쿤스튜디오 매칭 추천"""
    entries = fetch_feed()
    all_items = []
    for e in entries:
        score_result = score_entry(e)
        if score_result == -1:
            continue  # 노이즈
        score, matched = score_result
        parsed = parse_entry(e)
        parsed["kun_score"] = score
        parsed["matched_keywords"] = matched
        all_items.append(parsed)

    # TOP N (Product Hunt 자체 정렬 유지)
    top = all_items[:top_n]
    # 쿤스튜디오 매칭 TOP (score 기준)
    high_match = sorted(
        [i for i in all_items if i["kun_score"] >= 3],
        key=lambda x: x["kun_score"],
        reverse=True,
    )[:5]

    return {
        "total_entries": len(all_items),
        "top_today": top,
        "high_match_for_kun": high_match,
        "fetched_at": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import sys, json
    sys.stdout.reconfigure(encoding="utf-8")
    result = daily_summary()
    print(f"총 수집: {result['total_entries']}건")
    print(f"\n=== Today TOP 5 ===")
    for i, item in enumerate(result["top_today"][:5], 1):
        print(f"{i}. {item['title']} (매칭 {item['kun_score']})")
        print(f"   {item['summary'][:100]}")
    print(f"\n=== 쿤스튜디오 매칭 TOP 5 ===")
    for i, item in enumerate(result["high_match_for_kun"], 1):
        print(f"{i}. [{item['kun_score']}점] {item['title']}")
        print(f"   키워드: {item['matched_keywords']}")
        print(f"   {item['summary'][:100]}")
