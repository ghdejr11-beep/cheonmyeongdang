#!/usr/bin/env python3
"""
업로드된 쇼츠의 성과(조회수/좋아요/댓글/평균 시청)를 수집 →
run_history.jsonl에 토픽별 스코어 기록 → topic_refresh의 학습 데이터.

youtube_analyzer.py와 같은 OAuth 패턴 사용 (wealth 채널).
주간 1회 실행 권장.
"""
import sys, json, datetime, pickle
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DEPT = Path(__file__).parent
SHARED = DEPT.parent / "shared"
sys.path.insert(0, str(SHARED))

try:
    from googleapiclient.discovery import build
except ImportError:
    print("❌ google-api-python-client 필요: pip install google-api-python-client")
    sys.exit(2)

TOKEN = SHARED / "token_wealth.pickle"
HISTORY = DEPT / "run_history.jsonl"
ANALYTICS = DEPT / "video_analytics.jsonl"


def get_service():
    if not TOKEN.exists():
        print(f"❌ 토큰 없음: {TOKEN}")
        sys.exit(1)
    with open(TOKEN, "rb") as f:
        creds = pickle.load(f)
    return build("youtube", "v3", credentials=creds)


def load_runs():
    """orchestrator가 남긴 run_history (업로드된 영상 id + 토픽 매핑)"""
    if not HISTORY.exists():
        return []
    rows = []
    for line in HISTORY.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def main():
    runs = load_runs()
    if not runs:
        print("ℹ️ run_history 비어있음. orchestrator 최소 1회 실행 필요")
        return

    yt = get_service()
    video_ids = [r["video_id"] for r in runs if r.get("video_id")]
    if not video_ids:
        print("ℹ️ video_id 기록 없음")
        return

    # 최대 50개씩
    all_stats = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = yt.videos().list(part="statistics,contentDetails,snippet", id=",".join(batch)).execute()
        for item in resp.get("items", []):
            stats = item.get("statistics", {})
            all_stats.append({
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "published": item["snippet"].get("publishedAt"),
            })

    # 토픽 ↔ 성과 매핑
    topic_map = {r["video_id"]: r.get("topic") for r in runs if r.get("video_id")}

    # 간단 스코어: views * 1 + likes * 5 + comments * 10
    scored = []
    for s in all_stats:
        topic = topic_map.get(s["video_id"], "(unknown)")
        score = s["views"] + s["likes"] * 5 + s["comments"] * 10
        scored.append({"topic": topic, "score": score, **s})
    scored.sort(key=lambda x: x["score"], reverse=True)

    print(f"📊 분석 대상 {len(scored)}개")
    print(f"{'VIEWS':>8} {'LIKES':>5} {'CMT':>4} SCORE  TOPIC")
    for s in scored[:20]:
        print(f"{s['views']:>8} {s['likes']:>5} {s['comments']:>4} {s['score']:>6}  {s['topic'][:50]}")

    # 적재
    with open(ANALYTICS, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "date": datetime.date.today().isoformat(),
            "videos": scored,
        }, ensure_ascii=False) + "\n")
    print(f"✅ {ANALYTICS}")


if __name__ == "__main__":
    main()
