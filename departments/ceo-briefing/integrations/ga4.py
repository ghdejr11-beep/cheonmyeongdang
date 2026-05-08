"""
Google Analytics 4 Data API v1beta — 일일 트래픽 수집
- 어제 PV / UV / 세션 / Top5 페이지
- 3개 사이트(tax-n-benefit / korlens / cheonmyeongdang) 모두 처리
- 키 미설정 / 패키지 미설치 / API 오류 시 stub 반환 (절대 throw X)

Docs: https://developers.google.com/analytics/devguides/reporting/data/v1
Package: pip install google-analytics-data
"""
import datetime
import json
from pathlib import Path


SECRETS_PATH = Path(r"D:\cheonmyeongdang\.secrets")


def _load_env():
    """ .secrets KEY=VALUE 라인을 dict 로 로드. 파일 없으면 빈 dict."""
    env = {}
    try:
        if not SECRETS_PATH.exists():
            return env
        for line in SECRETS_PATH.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    except Exception:
        pass
    return env


def _stub(property_id, reason="GA4 키 미설정"):
    """키 없거나 API 실패 시 안전한 stub 데이터"""
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    return {
        "status": "stub",
        "reason": reason,
        "property_id": property_id,
        "date": yesterday,
        "page_views": 0,
        "active_users": 0,
        "sessions": 0,
        "top_pages": [],
    }


def fetch_ga4_daily(property_id):
    """
    어제 하루 GA4 트래픽 요약.
    Returns dict:
      status: "ok" | "stub" | "error"
      date, page_views, active_users, sessions, top_pages [{path, title, views}]
    """
    if not property_id:
        return _stub(property_id, "property_id 없음")

    env = _load_env()
    sa_json = env.get("GA4_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        return _stub(property_id, "GA4_SERVICE_ACCOUNT_JSON 미설정")
    sa_path = Path(sa_json)
    if not sa_path.exists():
        return _stub(property_id, f"서비스 계정 JSON 없음: {sa_json}")

    # 패키지 import (없으면 stub)
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
            OrderBy,
        )
        from google.oauth2 import service_account
    except ImportError as e:
        return _stub(property_id, f"패키지 미설치 (pip install google-analytics-data): {e}")

    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    try:
        creds = service_account.Credentials.from_service_account_file(str(sa_path))
        client = BetaAnalyticsDataClient(credentials=creds)

        # 1) 합계 메트릭
        totals_req = RunReportRequest(
            property=f"properties/{property_id}",
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="activeUsers"),
                Metric(name="sessions"),
            ],
            date_ranges=[DateRange(start_date=yesterday, end_date=yesterday)],
        )
        totals_resp = client.run_report(totals_req)

        pv = uv = sess = 0
        if totals_resp.rows:
            row = totals_resp.rows[0]
            vals = [v.value for v in row.metric_values]
            try:
                pv = int(vals[0])
                uv = int(vals[1])
                sess = int(vals[2])
            except (ValueError, IndexError):
                pass

        # 2) Top 5 페이지 (path + title)
        top_req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="pagePath"),
                Dimension(name="pageTitle"),
            ],
            metrics=[Metric(name="screenPageViews")],
            date_ranges=[DateRange(start_date=yesterday, end_date=yesterday)],
            order_bys=[
                OrderBy(
                    metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"),
                    desc=True,
                )
            ],
            limit=5,
        )
        top_resp = client.run_report(top_req)
        top_pages = []
        for row in top_resp.rows or []:
            dims = [d.value for d in row.dimension_values]
            mets = [m.value for m in row.metric_values]
            try:
                views = int(mets[0])
            except (ValueError, IndexError):
                views = 0
            top_pages.append({
                "path": dims[0] if len(dims) > 0 else "",
                "title": dims[1] if len(dims) > 1 else "",
                "views": views,
            })

        return {
            "status": "ok",
            "property_id": property_id,
            "date": yesterday,
            "page_views": pv,
            "active_users": uv,
            "sessions": sess,
            "top_pages": top_pages,
        }
    except Exception as e:
        return {
            "status": "error",
            "property_id": property_id,
            "date": yesterday,
            "page_views": 0,
            "active_users": 0,
            "sessions": 0,
            "top_pages": [],
            "error": str(e)[:200],
        }


def daily_summary():
    """3개 사이트 일괄 수집 — briefing_v2 가 호출하는 진입점"""
    env = _load_env()
    sites = {
        "tax-n-benefit": env.get("GA4_PROPERTY_ID_TAX", ""),
        "korlens": env.get("GA4_PROPERTY_ID_KORLENS", ""),
        "cheonmyeongdang": env.get("GA4_PROPERTY_ID_CMD", ""),
    }
    results = {}
    for name, pid in sites.items():
        results[name] = fetch_ga4_daily(pid)
    # 합산
    total_pv = sum(r.get("page_views", 0) for r in results.values())
    total_uv = sum(r.get("active_users", 0) for r in results.values())
    total_sess = sum(r.get("sessions", 0) for r in results.values())
    return {
        "sites": results,
        "totals": {
            "page_views": total_pv,
            "active_users": total_uv,
            "sessions": total_sess,
        },
        "fetched_at": datetime.datetime.now().isoformat(),
    }


def build_ga4_section(data):
    """09:00 브리핑용 텍스트 섹션 빌더 (HTML, 텔레그램 parse_mode=HTML)"""
    msg = "📊 <b>GA4 트래픽 (어제)</b>\n"
    if not isinstance(data, dict) or "sites" not in data:
        msg += "  (데이터 없음)\n\n"
        return msg
    totals = data.get("totals", {})
    msg += (
        f"  • 합계: PV {totals.get('page_views', 0):,} / "
        f"UV {totals.get('active_users', 0):,} / "
        f"세션 {totals.get('sessions', 0):,}\n"
    )
    for name, r in data.get("sites", {}).items():
        status = r.get("status", "?")
        if status == "ok":
            msg += (
                f"    └ <b>{name}</b>: PV {r['page_views']:,} / "
                f"UV {r['active_users']:,} / 세션 {r['sessions']:,}\n"
            )
            for tp in r.get("top_pages", [])[:3]:
                title = (tp.get("title") or tp.get("path") or "")[:40]
                msg += f"        · {title} ({tp['views']:,})\n"
        elif status == "stub":
            msg += f"    └ {name}: ⚙ {r.get('reason', '미설정')}\n"
        elif status == "error":
            msg += f"    └ {name}: ⚠ {str(r.get('error', ''))[:80]}\n"
        else:
            msg += f"    └ {name}: ({status})\n"
    msg += "\n"
    return msg


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== GA4 daily_summary() ===")
    result = daily_summary()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()
    print("=== Telegram section preview ===")
    print(build_ga4_section(result))
