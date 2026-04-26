#!/usr/bin/env python3
"""
통합 매출 집계기 (5채널 합산):
  • AdMob       — admob_collector.daily_summary()       (USD)
  • YouTube     — yt_dashboard.daily_summary()           (USD, 추정/실측)
  • Gumroad     — gumroad_collector.daily_summary()      (USD)
  • KDP         — kdp_scraper.daily_summary()            (USD)
  • 크티(수동)  — kreatie_manual.daily_summary()         (KRW)

결과:
- data/unified_revenue_daily.json — 날짜별 누적

사용:
    python unified_revenue.py              # 어제 통합 매출 출력
    python unified_revenue.py --collect    # 모든 콜렉터 호출 + 저장
    python unified_revenue.py --json       # 텔레그램 섹션용 dict 출력
"""
import os
import sys
import json
import datetime
import importlib
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
UNIFIED_JSON = DATA_DIR / "unified_revenue_daily.json"

# USD → KRW 환산 (수동 갱신; 매일 자동 환율 호출은 제외)
FX_USD_KRW = 1380


# ─────────────────────────────────────────────────────────
# 안전 import: 모듈 없거나 에러나면 fallback dict
# ─────────────────────────────────────────────────────────
def _safe_call(module_name, func_name="daily_summary"):
    try:
        mod = importlib.import_module(module_name)
        fn = getattr(mod, func_name, None)
        if not fn:
            return {"status": "no_function", "module": module_name}
        return fn()
    except Exception as e:
        return {"status": "import_error", "module": module_name, "error": str(e)[:200]}


# ─────────────────────────────────────────────────────────
# 채널별 net 추출 (USD/KRW 통일)
# ─────────────────────────────────────────────────────────
def _admob_yest_usd(d):
    if d.get("status") != "ok":
        return 0
    return d.get("yesterday", {}).get("total_usd", 0) or 0


def _yt_yest_usd(d):
    """yt_dashboard 의 yesterday.estimated_revenue_usd 또는 .total_usd 추정."""
    if not isinstance(d, dict) or d.get("status") not in ("ok", "estimated"):
        return 0
    y = d.get("yesterday", {})
    return (
        y.get("estimated_revenue_usd")
        or y.get("total_usd")
        or y.get("revenue_usd")
        or 0
    ) or 0


def _gumroad_yest_usd(d):
    if d.get("status") != "ok":
        return 0
    return d.get("yesterday", {}).get("net_usd", 0) or 0


def _kdp_yest_usd(d):
    if d.get("status") not in ("ok", "login_ok_no_parse"):
        return 0
    return d.get("yesterday", {}).get("royalty_usd", 0) or 0


def _kreatie_yest_krw(d):
    if d.get("status") not in ("ok", "awaiting_input"):
        return 0
    return d.get("yesterday", {}).get("net_krw", 0) or 0


# ─────────────────────────────────────────────────────────
# 메인 집계
# ─────────────────────────────────────────────────────────
def collect_all_channels():
    """모든 채널의 daily_summary() 호출."""
    return {
        "admob": _safe_call("admob_collector"),
        "youtube": _safe_call("yt_dashboard"),
        "gumroad": _safe_call("gumroad_collector"),
        "kdp": _safe_call("kdp_scraper"),
        "kreatie": _safe_call("kreatie_manual"),
    }


def _load_unified():
    if not UNIFIED_JSON.exists():
        return {}
    try:
        return json.loads(UNIFIED_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_unified(d):
    UNIFIED_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def daily_summary(persist=True):
    """
    어제 통합 매출 + 전일 대비 + 7일 평균 + 30일 누적.
    모든 금액 KRW 환산 통일.
    """
    today = datetime.date.today()
    yest = (today - datetime.timedelta(days=1)).isoformat()
    day_before = (today - datetime.timedelta(days=2)).isoformat()

    channels = collect_all_channels()

    # 어제 채널별 KRW 환산
    admob_usd = _admob_yest_usd(channels["admob"])
    yt_usd = _yt_yest_usd(channels["youtube"])
    gumroad_usd = _gumroad_yest_usd(channels["gumroad"])
    kdp_usd = _kdp_yest_usd(channels["kdp"])
    kreatie_krw = _kreatie_yest_krw(channels["kreatie"])

    by_channel_krw = {
        "admob": int(admob_usd * FX_USD_KRW),
        "youtube": int(yt_usd * FX_USD_KRW),
        "gumroad": int(gumroad_usd * FX_USD_KRW),
        "kdp": int(kdp_usd * FX_USD_KRW),
        "kreatie": int(kreatie_krw),
    }
    yest_total_krw = sum(by_channel_krw.values())

    # 누적 저장
    history = _load_unified()
    history[yest] = {
        "date": yest,
        "by_channel_krw": by_channel_krw,
        "by_channel_usd": {
            "admob": round(admob_usd, 2),
            "youtube": round(yt_usd, 2),
            "gumroad": round(gumroad_usd, 2),
            "kdp": round(kdp_usd, 2),
            "kreatie_krw": int(kreatie_krw),  # 크티는 KRW 원본
        },
        "total_krw": yest_total_krw,
        "fx": FX_USD_KRW,
    }
    # 90일치 유지
    cutoff = (today - datetime.timedelta(days=90)).isoformat()
    history = {k: v for k, v in history.items() if k >= cutoff}
    if persist:
        _save_unified(history)

    # 전일 대비
    prev = history.get(day_before, {}).get("total_krw", 0)
    if prev > 0:
        pct = (yest_total_krw - prev) / prev * 100
        delta_label = f"{'+' if pct >= 0 else ''}{pct:.1f}%"
    else:
        pct = None
        delta_label = "N/A"

    # 7일 평균
    seven_total = 0
    seven_count = 0
    for i in range(1, 8):
        d = (today - datetime.timedelta(days=i)).isoformat()
        if d in history:
            seven_total += history[d].get("total_krw", 0)
            seven_count += 1
    seven_avg = int(seven_total / seven_count) if seven_count else 0

    # 30일 누적
    thirty_total = 0
    for i in range(1, 31):
        d = (today - datetime.timedelta(days=i)).isoformat()
        thirty_total += history.get(d, {}).get("total_krw", 0)

    return {
        "status": "ok",
        "date": yest,
        "fx_usd_krw": FX_USD_KRW,
        "yesterday_total_krw": yest_total_krw,
        "yesterday_by_channel_krw": by_channel_krw,
        "vs_day_before": {
            "previous_total_krw": prev,
            "delta_pct": round(pct, 1) if pct is not None else None,
            "label": delta_label,
        },
        "seven_day_avg_krw": seven_avg,
        "thirty_day_total_krw": thirty_total,
        "channel_status": {
            "admob": channels["admob"].get("status"),
            "youtube": channels["youtube"].get("status"),
            "gumroad": channels["gumroad"].get("status"),
            "kdp": channels["kdp"].get("status"),
            "kreatie": channels["kreatie"].get("status"),
        },
    }


# ─────────────────────────────────────────────────────────
# 텔레그램 메시지 빌더 (briefing v2 가 import)
# ─────────────────────────────────────────────────────────
def build_unified_revenue_section():
    """
    🤖 briefing_v2.py 가 메시지 최상단에 호출.
    큰 글씨 배너 + 채널별 미니 라인.
    """
    s = daily_summary(persist=False)  # 콜렉트는 별도 스케줄, 여기선 read-only
    total = s.get("yesterday_total_krw", 0)
    delta = s.get("vs_day_before", {}).get("label", "N/A")

    msg = "💰 <b>어제 통합 매출</b>\n"
    msg += f"  <b>₩{total:,}</b>  (전일 대비 {delta})\n"

    by = s.get("yesterday_by_channel_krw", {})
    LABELS = {
        "admob": "📱 AdMob",
        "youtube": "▶️ YouTube",
        "gumroad": "🛒 Gumroad",
        "kdp": "📚 KDP",
        "kreatie": "🎨 크티",
    }
    for k, label in LABELS.items():
        amount = by.get(k, 0)
        if amount > 0:
            msg += f"    {label}: ₩{amount:,}\n"

    # 채널 상태 경고
    cs = s.get("channel_status", {})
    warnings = []
    for k, status in cs.items():
        if status in ("no_token", "no_csv", "import_error", "credentials_missing"):
            warnings.append(f"⚠️ {LABELS.get(k, k)}: {status}")
    if warnings:
        msg += "  " + " · ".join(warnings) + "\n"

    msg += f"\n  📊 7일 평균 ₩{s.get('seven_day_avg_krw', 0):,}"
    msg += f" / 30일 ₩{s.get('thirty_day_total_krw', 0):,}\n\n"
    return msg


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(json.dumps(daily_summary(persist=False), ensure_ascii=False, indent=2))
    elif args[0] == "--collect":
        result = daily_summary(persist=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args[0] == "--json":
        print(json.dumps(daily_summary(persist=False), ensure_ascii=False, indent=2))
    elif args[0] == "--banner":
        print(build_unified_revenue_section())
    else:
        print(__doc__)
