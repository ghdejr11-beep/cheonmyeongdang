"""
Google Trends 수익 아이템 탐지
- 쿤스튜디오 핵심 키워드 주간 상승률
- 급상승 키워드 (breakout)
"""
from pytrends.request import TrendReq
import datetime


TRACKED_KEYWORDS = [
    # 쿤스튜디오 도메인
    "ai side hustle",
    "사주 앱",
    "세금 환급",
    "보험 비교",
    "faceless youtube",
    "notion template",
    # 기회 키워드
    "ai agent",
    "claude code",
    "passive income",
    "digital product",
]


def get_trending_keywords(keywords=None, timeframe="now 7-d", geo=""):
    """
    Args:
        keywords: 비교할 키워드 (최대 5개)
        timeframe: 'now 7-d' | 'today 1-m' | 'today 3-m'
        geo: '' (전세계) | 'KR' | 'US'
    Returns:
        {keyword: {avg, latest, trend_direction}}
    """
    if keywords is None:
        keywords = TRACKED_KEYWORDS[:5]  # 5개 제한
    keywords = keywords[:5]

    pytrends = TrendReq(hl="en-US", tz=540)  # KST
    try:
        pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
        df = pytrends.interest_over_time()
        if df.empty:
            return {}
        result = {}
        for kw in keywords:
            if kw not in df.columns:
                continue
            vals = df[kw].tolist()
            if not vals:
                continue
            avg = sum(vals) / len(vals)
            latest = vals[-1]
            first_half = sum(vals[: len(vals) // 2])
            second_half = sum(vals[len(vals) // 2 :])
            direction = "📈 상승" if second_half > first_half * 1.15 else "📉 하락" if second_half < first_half * 0.85 else "➡️ 유지"
            result[kw] = {
                "avg": round(avg, 1),
                "latest": latest,
                "direction": direction,
                "change_pct": round((second_half - first_half) / max(first_half, 1) * 100, 1) if first_half else 0,
            }
        return result
    except Exception as e:
        return {"error": str(e)}


def get_rising_queries(keyword, timeframe="now 7-d", geo=""):
    """특정 키워드의 연관 급상승 검색어"""
    pytrends = TrendReq(hl="en-US", tz=540)
    try:
        pytrends.build_payload([keyword], timeframe=timeframe, geo=geo)
        related = pytrends.related_queries()
        if keyword not in related or related[keyword] is None:
            return []
        rising = related[keyword].get("rising")
        if rising is None or rising.empty:
            return []
        return rising.head(10).to_dict(orient="records")
    except Exception as e:
        return []


def daily_summary():
    """브리핑용 요약"""
    # 쿤스튜디오 핵심 5개 키워드 추이
    core = get_trending_keywords(
        ["ai side hustle", "사주 앱", "세금 환급", "ai agent", "notion template"],
        timeframe="now 7-d",
        geo="",
    )
    # 상승세 아이템만 추천
    rising_items = []
    for kw, data in core.items():
        if isinstance(data, dict) and "direction" in data and "📈" in data["direction"]:
            rising_items.append({
                "keyword": kw,
                "change_pct": data["change_pct"],
                "direction": data["direction"],
            })

    # "ai side hustle" 연관 급상승 (시장 힌트)
    related_rising = get_rising_queries("ai side hustle", timeframe="today 1-m")[:5]

    return {
        "core_keywords": core,
        "rising_items": sorted(rising_items, key=lambda x: x["change_pct"], reverse=True),
        "related_rising_queries": related_rising,
    }


if __name__ == "__main__":
    import sys, json
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(daily_summary(), ensure_ascii=False, indent=2, default=str))
