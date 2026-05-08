#!/usr/bin/env python3
"""
Gumroad API v2 일별 매출 수집기
- Endpoint: https://api.gumroad.com/v2/sales
- 인증: .secrets 의 GUMROAD_ACCESS_TOKEN (Bearer)
- 어제 매출 + 상품별 매출 + 환불 추적

결과:
- data/gumroad_daily.json — 날짜별 누적 (date → metrics)

briefing_v2 에서 daily_summary() 직접 호출 가능.
"""
import os
import sys
import json
import datetime
import urllib.request
import urllib.parse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DAILY_JSON = DATA_DIR / "gumroad_daily.json"
SECRETS_PATH = Path(r"D:\cheonmyeongdang\.secrets")

GUMROAD_API = "https://api.gumroad.com/v2"
USER_AGENT = "KunStudio-Revenue/1.0 (+ghdejr11@gmail.com)"


# ─────────────────────────────────────────────────────────
# secrets
# ─────────────────────────────────────────────────────────
def _load_env():
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


def _token():
    return _load_env().get("GUMROAD_ACCESS_TOKEN")


# ─────────────────────────────────────────────────────────
# HTTP
# ─────────────────────────────────────────────────────────
def _request(path, params=None, timeout=15):
    token = _token()
    if not token:
        return {"error": "GUMROAD_ACCESS_TOKEN 미설정 (.secrets)"}
    qs = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{GUMROAD_API}/{path}{qs}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}


# ─────────────────────────────────────────────────────────
# Sales / Refunds
# ─────────────────────────────────────────────────────────
def get_sales(after, before, page_limit=20):
    """
    Args:
        after (str): "YYYY-MM-DD" (포함)
        before (str): "YYYY-MM-DD" (포함, Gumroad 동작 기준)
    Returns:
        list[dict] — 모든 페이지 합산
    """
    page = 1
    all_sales = []
    while page <= page_limit:
        data = _request("sales", {"after": after, "before": before, "page": page})
        if not isinstance(data, dict) or data.get("error") or not data.get("success"):
            break
        sales = data.get("sales", [])
        if not sales:
            break
        all_sales.extend(sales)
        if not data.get("next_page_url"):
            break
        page += 1
    return all_sales


def _date_str(d):
    if isinstance(d, datetime.date):
        return d.isoformat()
    return str(d)


def collect_for_date(target_date):
    """
    한 날짜의 매출 raw → 정제 dict 반환.
    """
    iso = _date_str(target_date)
    next_iso = _date_str(target_date + datetime.timedelta(days=1))

    sales = get_sales(after=iso, before=next_iso)
    if isinstance(sales, dict) and sales.get("error"):
        return {"date": iso, "status": "error", "error": sales["error"]}

    # Gumroad 응답: price 단위 = 화폐 최소단위 (USD = cents, KRW = won)
    # 환불은 `refunded: true` 또는 별도 chargebacked 플래그
    total_cents = 0
    refund_cents = 0
    by_product = {}
    by_currency = {}

    for s in sales:
        # price 가 cents (USD 기준). 환불된 건도 sales 에 포함됨
        price = s.get("price", 0) or 0
        currency = (s.get("currency") or "USD").upper()
        product = s.get("product_name", "?")
        refunded = bool(s.get("refunded") or s.get("chargebacked"))

        d = by_product.setdefault(
            product, {"count": 0, "amount_cents": 0, "refund_count": 0, "refund_cents": 0, "currency": currency}
        )
        d["count"] += 1
        d["amount_cents"] += price
        if refunded:
            d["refund_count"] += 1
            d["refund_cents"] += price
            refund_cents += price
        total_cents += price

        c = by_currency.setdefault(currency, {"count": 0, "amount_cents": 0})
        c["count"] += 1
        c["amount_cents"] += price

    return {
        "date": iso,
        "status": "ok",
        "total_sales_count": len(sales),
        "total_amount_cents": total_cents,
        "total_amount_usd": round(total_cents / 100, 2),
        "refund_count": sum(1 for s in sales if s.get("refunded") or s.get("chargebacked")),
        "refund_amount_cents": refund_cents,
        "refund_amount_usd": round(refund_cents / 100, 2),
        "net_usd": round((total_cents - refund_cents) / 100, 2),
        "by_product": by_product,
        "by_currency": by_currency,
    }


# ─────────────────────────────────────────────────────────
# 누적 저장
# ─────────────────────────────────────────────────────────
def _load_history():
    if not DAILY_JSON.exists():
        return {}
    try:
        return json.loads(DAILY_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_history(d):
    DAILY_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_yesterday():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    snap = collect_for_date(yesterday)
    if snap.get("status") == "ok":
        history = _load_history()
        history[snap["date"]] = snap
        # 90일치만 유지
        cutoff = (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
        history = {k: v for k, v in history.items() if k >= cutoff}
        _save_history(history)
    return snap


# ─────────────────────────────────────────────────────────
# briefing v2 공개 API
# ─────────────────────────────────────────────────────────
def daily_summary():
    """
    어제 매출 + 7일 평균 + 30일 누적 (USD).
    토큰/네트워크 실패 시 graceful fallback.
    """
    if not _token():
        return {
            "status": "no_token",
            "message": "Gumroad 토큰 미설정",
            "how_to": ".secrets 에 GUMROAD_ACCESS_TOKEN=... 추가",
        }

    snap = collect_yesterday()
    history = _load_history()

    today = datetime.date.today()
    yest_iso = (today - datetime.timedelta(days=1)).isoformat()

    # 7일 평균 (어제 포함 직전 7일)
    seven_dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(1, 8)]
    seven_total = sum(history.get(d, {}).get("net_usd", 0) for d in seven_dates)
    seven_avg = seven_total / 7

    # 30일 누적
    thirty_dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(1, 31)]
    thirty_total = sum(history.get(d, {}).get("net_usd", 0) for d in thirty_dates)

    result = {
        "status": snap.get("status", "error"),
        "yesterday": {
            "date": yest_iso,
            "sales_count": snap.get("total_sales_count", 0),
            "gross_usd": snap.get("total_amount_usd", 0),
            "refund_usd": snap.get("refund_amount_usd", 0),
            "net_usd": snap.get("net_usd", 0),
            "by_product": snap.get("by_product", {}),
        },
        "seven_day_avg_usd": round(seven_avg, 2),
        "thirty_day_total_usd": round(thirty_total, 2),
        "history_days": len(history),
    }
    if snap.get("error"):
        result["error"] = snap["error"]
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--collect":
        snap = collect_yesterday()
        print(json.dumps(snap, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(daily_summary(), ensure_ascii=False, indent=2))
