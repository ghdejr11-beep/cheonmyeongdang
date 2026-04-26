#!/usr/bin/env python3
"""
YouTube 4채널 통합 대시보드 — Healing Sleep Realm / Whisper Atlas / Wealth Blueprint / Inner Archetypes

특징:
- YouTube Data API v3 (channels.list / search.list / videos.list / playlistItems.list)
- 선택적: YouTube Analytics API v2 (estimatedRevenue / averageViewDuration if YPP 가입)
- 4채널 분리 추적 → JSON 누적 (data/yt_4ch_daily.json)
- 채널 ID 자동 해상도 (search.list q="<채널명>" type=channel)
- 어제 조회수 / 어제 구독자 변화 = 시계열 diff
- 매출 추정: CPM $1~$3 가정 (YPP 가입시 정확값 자동 대체)

토큰 우선순위:
1. .secrets_youtube_token.json (글로벌, 사용자 메인 채널 — youtube.readonly + yt-analytics.readonly)
2. departments/media/youtube/shared/token_*.pickle (브랜드별 OAuth)
3. 위 둘 다 없으면 graceful fallback {"status": "auth_required"}

사용:
    python yt_dashboard.py             # 자동 (채널ID 해상도 + 스냅샷 + JSON 갱신)
    python yt_dashboard.py --resolve   # 채널ID 강제 재해상도
    python yt_dashboard.py --preview   # 텍스트 미리보기 (전송 X)
"""
import os
import sys
import json
import datetime
import argparse
import traceback
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DAILY_JSON = DATA_DIR / "yt_4ch_daily.json"
CHANNEL_MAP_JSON = BASE / "yt_channel_map.json"

SECRETS_PATH = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets")
GLOBAL_TOKEN = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets_youtube_token.json")
SHARED_TOKEN_DIR = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\youtube\shared")

YT_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

# CPM 추정 (USD per 1000 views) — 카테고리별 industry standard 평균
CPM_ESTIMATE = {
    "sleep_meditation": 1.5,
    "asmr": 1.2,
    "finance_education": 5.0,  # 금융 카테고리는 CPM 높음
    "psychology_spiritual": 2.0,
    "default": 2.0,
}


# ─── secrets 로더 ───────────────────────────────────────────────
def _load_secrets():
    env = {}
    if not SECRETS_PATH.exists():
        return env
    for line in SECRETS_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


# ─── 채널 매핑 ────────────────────────────────────────────────
def _load_channel_map():
    if not CHANNEL_MAP_JSON.exists():
        return {"channels": []}
    return json.loads(CHANNEL_MAP_JSON.read_text(encoding="utf-8"))


def _save_channel_map(data):
    CHANNEL_MAP_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ─── OAuth credentials 로더 ────────────────────────────────────
def _get_credentials():
    """글로벌 토큰 우선, 실패시 None."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
    except ImportError:
        return None, "google-auth 라이브러리 없음 (pip install google-api-python-client)"

    if GLOBAL_TOKEN.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(GLOBAL_TOKEN), YT_SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # 갱신된 토큰 저장
                GLOBAL_TOKEN.write_text(creds.to_json(), encoding="utf-8")
            if creds and creds.valid:
                return creds, None
        except Exception as e:
            return None, f"글로벌 토큰 로드 실패: {str(e)[:100]}"

    return None, f"YouTube 토큰 없음 — {GLOBAL_TOKEN} 또는 채널별 pickle 필요"


def _get_yt_service():
    creds, err = _get_credentials()
    if err:
        return None, err
    try:
        from googleapiclient.discovery import build
        return build("youtube", "v3", credentials=creds), None
    except Exception as e:
        return None, f"youtube 서비스 생성 실패: {str(e)[:100]}"


def _get_analytics_service():
    creds, err = _get_credentials()
    if err:
        return None, err
    try:
        from googleapiclient.discovery import build
        return build("youtubeAnalytics", "v2", credentials=creds), None
    except Exception as e:
        return None, f"analytics 서비스 생성 실패: {str(e)[:100]}"


# ─── 채널 ID 자동 해상도 ───────────────────────────────────────
def auto_resolve_channel_ids(force=False):
    """
    yt_channel_map.json 의 channel_id 가 비어있으면 search.list 로 해상도.
    인증된 계정의 channels().list(mine=True) 로 본인 소유 채널부터 매칭 시도.
    """
    yt, err = _get_yt_service()
    if err:
        return {"status": "error", "error": err, "resolved": []}

    cmap = _load_channel_map()
    resolved = []

    # 1) mine=true 로 본인 소유 채널 한 번 fetch (4채널이면 mine=true 1번이면 충분)
    try:
        owned_resp = yt.channels().list(
            part="snippet,statistics",
            mine=True,
            maxResults=50,
        ).execute()
        owned = owned_resp.get("items", [])
    except Exception as e:
        owned = []

    owned_titles = {c["snippet"]["title"].lower(): c["id"] for c in owned}

    # 2) 각 채널 매핑
    for ch in cmap["channels"]:
        if ch.get("channel_id") and not force:
            resolved.append({"key": ch["key"], "channel_id": ch["channel_id"], "via": "cached"})
            continue

        # 본인 소유 채널 title 매칭
        title_lower = ch["title"].lower()
        cid = None
        via = None
        if title_lower in owned_titles:
            cid = owned_titles[title_lower]
            via = "mine"

        # 못 찾으면 public search
        if not cid:
            try:
                q = ch.get("search_terms", [ch["title"]])[0]
                sr = yt.search().list(
                    part="snippet",
                    q=q,
                    type="channel",
                    maxResults=5,
                ).execute()
                items = sr.get("items", [])
                # 정확한 title 일치 우선
                for it in items:
                    sn_title = it["snippet"]["title"].lower()
                    if sn_title == title_lower:
                        cid = it["snippet"]["channelId"]
                        via = "search_exact"
                        break
                if not cid and items:
                    cid = items[0]["snippet"]["channelId"]
                    via = "search_first"
            except Exception as e:
                via = f"search_error:{str(e)[:60]}"

        if cid:
            ch["channel_id"] = cid
        resolved.append({
            "key": ch["key"],
            "title": ch["title"],
            "channel_id": cid or "",
            "via": via or "not_found",
        })

    _save_channel_map(cmap)
    return {"status": "ok", "resolved": resolved}


# ─── 채널 통계 가져오기 ───────────────────────────────────────
def fetch_channel_stats(channel_id):
    """channels.list — 구독자/총 조회수/영상 수."""
    yt, err = _get_yt_service()
    if err:
        return {"status": "error", "error": err}
    try:
        resp = yt.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id,
        ).execute()
        items = resp.get("items", [])
        if not items:
            return {"status": "not_found", "channel_id": channel_id}
        ch = items[0]
        return {
            "status": "ok",
            "channel_id": channel_id,
            "title": ch["snippet"]["title"],
            "subscriber_count": int(ch["statistics"].get("subscriberCount", 0)),
            "view_count_total": int(ch["statistics"].get("viewCount", 0)),
            "video_count": int(ch["statistics"].get("videoCount", 0)),
            "uploads_playlist": ch["contentDetails"]["relatedPlaylists"]["uploads"],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


def fetch_recent_videos(uploads_playlist_id, max_count=20):
    """playlistItems.list 로 최근 영상 ID 목록."""
    yt, err = _get_yt_service()
    if err:
        return []
    try:
        resp = yt.playlistItems().list(
            part="contentDetails,snippet",
            playlistId=uploads_playlist_id,
            maxResults=max_count,
        ).execute()
        return [
            {
                "video_id": it["contentDetails"]["videoId"],
                "title": it["snippet"]["title"],
                "published_at": it["contentDetails"].get("videoPublishedAt", ""),
            }
            for it in resp.get("items", [])
        ]
    except Exception as e:
        return []


def fetch_video_stats(video_ids):
    """videos.list — viewCount/likeCount/commentCount."""
    if not video_ids:
        return []
    yt, err = _get_yt_service()
    if err:
        return []
    try:
        # API limit: max 50 ids per call
        results = []
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i : i + 50]
            resp = yt.videos().list(
                part="statistics,snippet,contentDetails",
                id=",".join(chunk),
            ).execute()
            for it in resp.get("items", []):
                stats = it.get("statistics", {})
                results.append({
                    "video_id": it["id"],
                    "title": it["snippet"]["title"],
                    "published_at": it["snippet"]["publishedAt"],
                    "duration": it["contentDetails"].get("duration", ""),
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                })
        return results
    except Exception as e:
        return []


def fetch_analytics_revenue(channel_id, start_date, end_date):
    """
    YouTube Analytics API — estimatedRevenue / averageViewDuration.
    YPP 가입 채널만 가능. 미가입시 403 → {"status": "ypp_not_joined"}.
    """
    svc, err = _get_analytics_service()
    if err:
        return {"status": "no_auth", "error": err}
    try:
        resp = svc.reports().query(
            ids=f"channel=={channel_id}",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost,estimatedRevenue",
        ).execute()
        rows = resp.get("rows", [])
        if not rows:
            return {"status": "no_data"}
        r = rows[0]
        return {
            "status": "ok",
            "views": int(r[0]) if len(r) > 0 else 0,
            "minutes_watched": int(r[1]) if len(r) > 1 else 0,
            "avg_view_duration_sec": int(r[2]) if len(r) > 2 else 0,
            "subs_gained": int(r[3]) if len(r) > 3 else 0,
            "subs_lost": int(r[4]) if len(r) > 4 else 0,
            "estimated_revenue_usd": float(r[5]) if len(r) > 5 else 0.0,
        }
    except Exception as e:
        msg = str(e)
        if "403" in msg or "forbidden" in msg.lower() or "ypp" in msg.lower():
            return {"status": "ypp_not_joined", "error": msg[:150]}
        return {"status": "error", "error": msg[:200]}


# ─── 일일 스냅샷 ───────────────────────────────────────────────
def _load_daily():
    if DAILY_JSON.exists():
        try:
            return json.loads(DAILY_JSON.read_text(encoding="utf-8"))
        except Exception:
            return {"snapshots": []}
    return {"snapshots": []}


def _save_daily(data):
    DAILY_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _get_yesterday_diff(snapshots, channel_key, today_value, field):
    """어제 스냅샷이 있으면 today - yesterday, 없으면 0."""
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    for s in reversed(snapshots):
        if s["date"] == yesterday and channel_key in s.get("channels", {}):
            prev = s["channels"][channel_key].get(field, 0)
            return today_value - prev
    return 0


def collect_snapshot():
    """4채널 통합 스냅샷."""
    cmap = _load_channel_map()
    daily = _load_daily()
    today = datetime.date.today().isoformat()

    # 채널 ID 비어있으면 자동 해상도
    needs_resolve = any(not c.get("channel_id") for c in cmap["channels"])
    if needs_resolve:
        rr = auto_resolve_channel_ids(force=False)
        if rr.get("status") == "error":
            return {"status": "error", "error": rr.get("error"), "date": today}
        cmap = _load_channel_map()  # reload after save

    snap = {"date": today, "channels": {}, "totals": {}}

    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    total_views = 0
    total_subs = 0
    total_yesterday_views = 0
    total_yesterday_subs_gained = 0
    total_revenue_estimate = 0.0

    for ch in cmap["channels"]:
        key = ch["key"]
        cid = ch.get("channel_id", "")
        if not cid:
            snap["channels"][key] = {
                "status": "no_channel_id",
                "title": ch.get("title", key),
            }
            continue

        cs = fetch_channel_stats(cid)
        if cs.get("status") != "ok":
            snap["channels"][key] = {
                "status": cs.get("status", "error"),
                "title": ch.get("title", key),
                "error": cs.get("error", ""),
            }
            continue

        # 시계열 diff (전일 대비)
        view_diff = _get_yesterday_diff(
            daily.get("snapshots", []), key, cs["view_count_total"], "view_count_total"
        )
        sub_diff = _get_yesterday_diff(
            daily.get("snapshots", []), key, cs["subscriber_count"], "subscriber_count"
        )

        # 최근 영상 + top 5
        videos = fetch_recent_videos(cs["uploads_playlist"], max_count=20)
        vids = fetch_video_stats([v["video_id"] for v in videos])
        vids_sorted = sorted(vids, key=lambda x: x["view_count"], reverse=True)
        top5 = vids_sorted[:5]

        # 매출 추정 (CPM 기반, 어제 조회수)
        cpm = CPM_ESTIMATE.get(ch.get("category", "default"), CPM_ESTIMATE["default"])
        revenue_est_low = max(0, view_diff) * (cpm * 0.5) / 1000.0  # low: cpm*0.5
        revenue_est_high = max(0, view_diff) * (cpm * 1.5) / 1000.0  # high: cpm*1.5

        # YouTube Analytics API (YPP 가입시 정확)
        analytics = fetch_analytics_revenue(cid, yesterday, yesterday)
        if analytics.get("status") == "ok":
            actual_revenue = analytics.get("estimated_revenue_usd", 0.0)
            snap_revenue = actual_revenue
            revenue_source = "youtube_analytics"
        else:
            snap_revenue = (revenue_est_low + revenue_est_high) / 2
            revenue_source = f"cpm_estimate(${cpm}/1k)"

        snap["channels"][key] = {
            "status": "ok",
            "title": cs["title"],
            "channel_id": cid,
            "subscriber_count": cs["subscriber_count"],
            "view_count_total": cs["view_count_total"],
            "video_count": cs["video_count"],
            "yesterday_views_diff": view_diff,
            "yesterday_subs_diff": sub_diff,
            "top_videos": [
                {
                    "title": v["title"][:80],
                    "video_id": v["video_id"],
                    "view_count": v["view_count"],
                    "like_count": v["like_count"],
                    "comment_count": v["comment_count"],
                }
                for v in top5
            ],
            "revenue_estimate_usd": round(snap_revenue, 2),
            "revenue_source": revenue_source,
            "revenue_low_high": [round(revenue_est_low, 2), round(revenue_est_high, 2)],
            "analytics_full": analytics,
        }

        total_views += cs["view_count_total"]
        total_subs += cs["subscriber_count"]
        total_yesterday_views += max(0, view_diff)
        total_yesterday_subs_gained += max(0, sub_diff)
        total_revenue_estimate += snap_revenue

    snap["totals"] = {
        "view_count_total_all": total_views,
        "subscriber_count_all": total_subs,
        "yesterday_views_all": total_yesterday_views,
        "yesterday_subs_gained_all": total_yesterday_subs_gained,
        "revenue_estimate_usd_all": round(total_revenue_estimate, 2),
    }

    # 누적 저장 (오늘 날짜 중복 시 교체)
    daily["snapshots"] = [s for s in daily.get("snapshots", []) if s["date"] != today]
    daily["snapshots"].append(snap)
    # 90일 이상 잘라내기
    cutoff = (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
    daily["snapshots"] = [s for s in daily["snapshots"] if s["date"] >= cutoff]
    _save_daily(daily)

    return snap


# ─── briefing_v2 호출용 공개 API ──────────────────────────────
def daily_summary():
    """
    briefing_v2.py 가 호출.
    실패해도 brief 안 깨지게 graceful return.
    """
    try:
        creds, err = _get_credentials()
        if err:
            return {"status": "auth_required", "message": err}
        snap = collect_snapshot()
        if snap.get("status") == "error":
            return snap
        # 압축 요약본 반환 (top 영상 1개씩만)
        compact = {
            "status": "ok",
            "date": snap["date"],
            "totals": snap["totals"],
            "channels": {},
        }
        for k, v in snap["channels"].items():
            if v.get("status") != "ok":
                compact["channels"][k] = {"status": v.get("status"), "title": v.get("title", k)}
                continue
            best = v["top_videos"][0] if v["top_videos"] else None
            compact["channels"][k] = {
                "status": "ok",
                "title": v["title"],
                "subs": v["subscriber_count"],
                "views_total": v["view_count_total"],
                "yesterday_views": v["yesterday_views_diff"],
                "yesterday_subs": v["yesterday_subs_diff"],
                "best_video": (
                    {"title": best["title"], "views": best["view_count"]} if best else None
                ),
                "revenue_usd": v["revenue_estimate_usd"],
                "revenue_source": v["revenue_source"],
            }
        return compact
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)[:200],
            "trace": traceback.format_exc()[-400:],
        }


# ─── CLI 미리보기 포매터 ─────────────────────────────────────
def format_summary_text(summary):
    lines = []
    lines.append("📺 YouTube 4채널 (어제)")
    if summary.get("status") != "ok":
        lines.append(f"  ⚠ {summary.get('status')}: {summary.get('message', summary.get('error', ''))}")
        return "\n".join(lines)
    t = summary["totals"]
    lines.append(
        f"  합계: 조회 +{t['yesterday_views_all']:,} / 구독 +{t['yesterday_subs_gained_all']:,} / 추정 매출 ${t['revenue_estimate_usd_all']:.2f}"
    )
    lines.append(f"  누적: 구독 {t['subscriber_count_all']:,} / 누적조회 {t['view_count_total_all']:,}")
    for key, c in summary["channels"].items():
        if c.get("status") != "ok":
            lines.append(f"  • {c.get('title', key)}: ({c.get('status')})")
            continue
        bv = c.get("best_video") or {}
        lines.append(
            f"  • {c['title']}: 조회 +{c['yesterday_views']:,} / 구독 +{c['yesterday_subs']:,} / ${c['revenue_usd']:.2f} ({c['revenue_source']})"
        )
        if bv:
            lines.append(f"      best: {bv.get('title', '')[:50]} ({bv.get('views', 0):,} 조회)")
    return "\n".join(lines)


# ─── CLI ────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolve", action="store_true", help="채널 ID 강제 재해상도")
    ap.add_argument("--preview", action="store_true", help="텍스트 미리보기만")
    args = ap.parse_args()

    if args.resolve:
        rr = auto_resolve_channel_ids(force=True)
        print(json.dumps(rr, ensure_ascii=False, indent=2))
        return

    summary = daily_summary()
    if args.preview:
        print(format_summary_text(summary))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
