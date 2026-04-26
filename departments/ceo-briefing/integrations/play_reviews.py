"""
Google Play 리뷰 수집 (우리 앱 + 경쟁사)
앱 미출시 상태면 "대기" 반환 — 출시 후 자동 활성화
"""
from google_play_scraper import app, reviews, Sort
import json
from pathlib import Path

CONFIG = {
    "our_apps": {
        "천명당": "com.cheonmyeongdang.app",
        "HexDrop": "com.yourname.hexdrop",
    },
    "competitors": {
        # 실제 패키지명 확인 후 채울 것 (Play Store URL → id= 뒤)
        # "점신": "kr.co.point.jeomshin",
        # "포스텔러": "...",
    },
}


def fetch_app(package_id, lang="ko", country="kr"):
    try:
        info = app(package_id, lang=lang, country=country)
        return {
            "ok": True,
            "title": info.get("title"),
            "score": info.get("score"),
            "ratings": info.get("ratings"),
            "reviews": info.get("reviews"),
            "installs": info.get("installs"),
            "updated": info.get("updated"),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def fetch_recent_reviews(package_id, count=10, lang="ko", country="kr"):
    try:
        result, _ = reviews(
            package_id,
            lang=lang, country=country,
            sort=Sort.NEWEST, count=count
        )
        return [
            {
                "score": r.get("score"),
                "user": (r.get("userName") or "?")[:15],
                "text": (r.get("content") or "").replace("\n", " ")[:200],
                "at": str(r.get("at")),
            }
            for r in result
        ]
    except Exception as e:
        return []


def daily_summary():
    """매일 브리핑용 요약"""
    out = {"our_apps": {}, "competitors": {}, "warnings": []}

    for name, pkg in CONFIG["our_apps"].items():
        info = fetch_app(pkg)
        if info["ok"]:
            recent = fetch_recent_reviews(pkg, count=10)
            negative = [r for r in recent if r["score"] <= 2]
            out["our_apps"][name] = {
                "status": "live",
                "info": info,
                "recent_reviews_count": len(recent),
                "negative_reviews_24h": len(negative),
                "top_negatives": negative[:3],
            }
        else:
            out["our_apps"][name] = {"status": "unlisted_or_404", "error": info["error"]}
            out["warnings"].append(f"📱 {name} Play Store 미출시 (리뷰 수집 불가)")

    for name, pkg in CONFIG["competitors"].items():
        info = fetch_app(pkg)
        if info["ok"]:
            recent = fetch_recent_reviews(pkg, count=20)
            complaints = [r for r in recent if r["score"] <= 2]
            out["competitors"][name] = {
                "score": info["score"],
                "ratings": info["ratings"],
                "complaints_24h": len(complaints),
                "top_complaints": complaints[:5],
            }

    return out


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(daily_summary(), ensure_ascii=False, indent=2))
