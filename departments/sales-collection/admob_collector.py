#!/usr/bin/env python3
"""
AdMob Reporting API v1 - 일별 광고 매출 자동 수집
- 천명당 (com.cheonmyeongdang)
- HexDrop (com.hexdrop)

요구사항:
- pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
- .secrets 에 ADMOB_PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX
- .secrets 에 ADMOB_OAUTH_TOKEN_PATH=C:/.../token.json
- 최초 1회 admob_auth_setup.py 실행하여 토큰 발급

결과:
- data/admob_daily.json 누적 저장 (날짜별 + 앱별)
- daily_summary() 가 briefing_v2 에서 호출됨
"""
import os
import sys
import json
import datetime
import traceback
from pathlib import Path

# UTF-8 출력 (스크립트 단독 실행시)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DAILY_JSON = DATA_DIR / "admob_daily.json"
SECRETS_PATH = Path(r"D:\cheonmyeongdang\.secrets")

ADMOB_API_SCOPES = ["https://www.googleapis.com/auth/admob.readonly"]

# 앱 매핑 (package_name → 표시명)
APP_DISPLAY_NAMES = {
    "com.cheonmyeongdang": "천명당",
    "com.hexdrop": "HexDrop",
    # 가능한 변형 패키지명 (실 등록 시 보정)
    "com.cheonmyeongdang.app": "천명당",
    "com.kunstudio.hexdrop": "HexDrop",
}


# ─────────────────────────────────────────────────────────
# secrets 로더
# ─────────────────────────────────────────────────────────
def _load_env():
    """.secrets 파일 → dict. 파일 없으면 빈 dict."""
    env = {}
    if not SECRETS_PATH.exists():
        return env
    for line in SECRETS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def _get_publisher_id():
    return _load_env().get("ADMOB_PUBLISHER_ID")


def _get_token_path():
    p = _load_env().get("ADMOB_OAUTH_TOKEN_PATH")
    if not p:
        return None
    return Path(p)


# ─────────────────────────────────────────────────────────
# 인증 (저장된 token.json 로드 → google-auth Credentials)
# ─────────────────────────────────────────────────────────
def _load_credentials():
    """저장된 OAuth 토큰을 google.oauth2.credentials.Credentials 로 로드.
    실패 시 None 반환 (graceful)."""
    token_path = _get_token_path()
    if not token_path or not token_path.exists():
        return None
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        creds = Credentials.from_authorized_user_file(str(token_path), ADMOB_API_SCOPES)
        # 만료시 자동 갱신
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds
    except Exception:
        return None


# ─────────────────────────────────────────────────────────
# AdMob API 호출
# ─────────────────────────────────────────────────────────
def _build_service():
    creds = _load_credentials()
    if not creds:
        return None
    try:
        from googleapiclient.discovery import build
        return build("admob", "v1", credentials=creds, cache_discovery=False)
    except Exception:
        return None


def _date_to_proto(d):
    """datetime.date → AdMob API DateProto"""
    return {"year": d.year, "month": d.month, "day": d.day}


def fetch_network_report(start_date, end_date):
    """
    AdMob Network Report (account 단위 collation).
    Dimensions: APP, DATE
    Metrics: ESTIMATED_EARNINGS, AD_REQUESTS, IMPRESSIONS, CLICKS, MATCH_RATE

    Returns:
        list[dict] of rows or {"error": "..."} 형식
    """
    pub_id = _get_publisher_id()
    if not pub_id:
        return {"error": "ADMOB_PUBLISHER_ID 미설정 (.secrets)"}

    service = _build_service()
    if not service:
        return {"error": "AdMob API 인증 필요 (admob_auth_setup.py 실행)"}

    body = {
        "reportSpec": {
            "dateRange": {
                "startDate": _date_to_proto(start_date),
                "endDate": _date_to_proto(end_date),
            },
            "dimensions": ["APP", "DATE"],
            "metrics": [
                "ESTIMATED_EARNINGS",
                "AD_REQUESTS",
                "IMPRESSIONS",
                "CLICKS",
                "MATCH_RATE",
            ],
            "localizationSettings": {
                "currencyCode": "USD",
                "languageCode": "en-US",
            },
        }
    }

    try:
        # account name 형식: accounts/pub-XXXXXXXXXXXXXXXX
        if not pub_id.startswith("pub-"):
            account_name = f"accounts/pub-{pub_id}"
        else:
            account_name = f"accounts/{pub_id}"

        request = service.accounts().networkReport().generate(
            parent=account_name, body=body
        )
        response = request.execute()
    except Exception as e:
        return {"error": f"AdMob API 호출 실패: {str(e)[:200]}"}

    # 응답은 stream 형태(list of dict). row 항목만 추출
    rows = []
    if isinstance(response, list):
        for chunk in response:
            row = chunk.get("row")
            if row:
                rows.append(row)
    elif isinstance(response, dict):
        # 단일 응답인 경우
        if "row" in response:
            rows.append(response["row"])
    return rows


def _parse_row(row):
    """API row → flat dict"""
    dim = row.get("dimensionValues", {})
    metrics = row.get("metricValues", {})

    app_id_proto = dim.get("APP", {})
    date_proto = dim.get("DATE", {})

    # APP 디멘션 - displayLabel: 앱 이름, value: app id
    app_id = app_id_proto.get("value") or ""
    app_label = app_id_proto.get("displayLabel") or app_id

    # DATE 디멘션 - value: "YYYYMMDD"
    date_str = date_proto.get("value", "")
    if len(date_str) == 8:
        date_iso = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    else:
        date_iso = date_str

    def _num(key):
        m = metrics.get(key, {})
        # microsValue (수익) / integerValue (count) / doubleValue (rate)
        if "microsValue" in m:
            return int(m["microsValue"]) / 1_000_000  # USD
        if "integerValue" in m:
            return int(m["integerValue"])
        if "doubleValue" in m:
            return float(m["doubleValue"])
        return 0

    return {
        "app_id": app_id,
        "app_label": app_label,
        "date": date_iso,
        "earnings_usd": _num("ESTIMATED_EARNINGS"),
        "ad_requests": _num("AD_REQUESTS"),
        "impressions": _num("IMPRESSIONS"),
        "clicks": _num("CLICKS"),
        "match_rate": _num("MATCH_RATE"),
    }


# ─────────────────────────────────────────────────────────
# 누적 저장 + 조회 헬퍼
# ─────────────────────────────────────────────────────────
def _load_history():
    if not DAILY_JSON.exists():
        return []
    try:
        return json.loads(DAILY_JSON.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_history(rows):
    DAILY_JSON.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _merge_rows(existing, new_rows):
    """(date, app_id) 기준 upsert"""
    key = lambda r: (r.get("date"), r.get("app_id"))
    merged = {key(r): r for r in existing}
    for r in new_rows:
        merged[key(r)] = r
    return sorted(merged.values(), key=lambda r: (r["date"], r["app_id"]))


def collect_yesterday_and_today():
    """어제~오늘 데이터 수집 → 누적 JSON 업데이트 → 반환"""
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    raw = fetch_network_report(yesterday, today)
    if isinstance(raw, dict) and raw.get("error"):
        return {"status": "error", "error": raw["error"]}

    parsed = [_parse_row(r) for r in raw]
    history = _load_history()
    merged = _merge_rows(history, parsed)
    _save_history(merged)

    return {
        "status": "ok",
        "fetched_rows": len(parsed),
        "total_history_rows": len(merged),
        "rows": parsed,
    }


# ─────────────────────────────────────────────────────────
# briefing_v2 에서 import 하는 공개 API
# ─────────────────────────────────────────────────────────
def daily_summary():
    """
    어제 매출 + 7일 평균 + 30일 누적 + 앱별 분리.
    토큰 없거나 API 미연동시 graceful fallback.
    """
    pub_id = _get_publisher_id()
    if not pub_id:
        return {
            "status": "no_publisher_id",
            "message": "AdMob Publisher ID 미설정",
            "how_to": ".secrets 에 ADMOB_PUBLISHER_ID=pub-XXX 추가",
        }

    token_path = _get_token_path()
    if not token_path or not token_path.exists():
        return {
            "status": "no_token",
            "message": "AdMob OAuth 토큰 없음",
            "how_to": "python admob_auth_setup.py 실행 (1회 브라우저 인증)",
        }

    # 최신 데이터 동기화 (실패해도 누적분으로 fallback)
    fetch_result = collect_yesterday_and_today()
    history = _load_history()
    if not history and fetch_result.get("status") == "error":
        return {
            "status": "error",
            "message": fetch_result.get("error", "AdMob API 인증 필요"),
        }

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yest_iso = yesterday.isoformat()

    # 어제 매출 (앱별)
    by_app_yest = {}
    for r in history:
        if r["date"] == yest_iso:
            app_key = APP_DISPLAY_NAMES.get(r["app_id"], r.get("app_label") or r["app_id"])
            d = by_app_yest.setdefault(
                app_key, {"earnings_usd": 0.0, "impressions": 0, "clicks": 0}
            )
            d["earnings_usd"] += r["earnings_usd"]
            d["impressions"] += r["impressions"]
            d["clicks"] += r["clicks"]

    # 7일 평균
    seven_ago = (today - datetime.timedelta(days=7)).isoformat()
    seven_rows = [r for r in history if r["date"] >= seven_ago and r["date"] < today.isoformat()]
    seven_total = sum(r["earnings_usd"] for r in seven_rows)
    seven_avg = seven_total / 7 if seven_rows else 0.0

    # 30일 누적
    thirty_ago = (today - datetime.timedelta(days=30)).isoformat()
    thirty_rows = [r for r in history if r["date"] >= thirty_ago and r["date"] < today.isoformat()]
    thirty_total = sum(r["earnings_usd"] for r in thirty_rows)

    # 어제 총합
    yest_total = sum(d["earnings_usd"] for d in by_app_yest.values())
    yest_impressions = sum(d["impressions"] for d in by_app_yest.values())
    yest_clicks = sum(d["clicks"] for d in by_app_yest.values())

    return {
        "status": "ok",
        "yesterday": {
            "date": yest_iso,
            "total_usd": round(yest_total, 4),
            "impressions": yest_impressions,
            "clicks": yest_clicks,
            "by_app": {k: {**v, "earnings_usd": round(v["earnings_usd"], 4)} for k, v in by_app_yest.items()},
        },
        "seven_day_avg_usd": round(seven_avg, 4),
        "thirty_day_total_usd": round(thirty_total, 4),
        "history_rows": len(history),
    }


if __name__ == "__main__":
    print(json.dumps(daily_summary(), ensure_ascii=False, indent=2))
