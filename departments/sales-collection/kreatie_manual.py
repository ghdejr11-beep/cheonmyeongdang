#!/usr/bin/env python3
"""
크티 (한국 디지털 상품) 수동 입력 CLI.
- 크티는 공식 API 미제공 → 매일 1회 수동 입력
- 입력 안 하면 마지막 값 0 으로 간주 (graceful)

사용:
    python kreatie_manual.py            # 어제 매출 입력 프롬프트
    python kreatie_manual.py --set 어제 50000 --count 3 --refund 0
    python kreatie_manual.py --status   # 최근 7일 입력 현황
"""
import sys
import json
import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DAILY_JSON = DATA_DIR / "kreatie_manual.json"


def _load():
    if not DAILY_JSON.exists():
        return {}
    try:
        return json.loads(DAILY_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(d):
    DAILY_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def set_entry(date_iso, gross_krw, count, refund_krw=0, note=""):
    history = _load()
    history[date_iso] = {
        "date": date_iso,
        "gross_krw": int(gross_krw),
        "count": int(count),
        "refund_krw": int(refund_krw),
        "net_krw": int(gross_krw) - int(refund_krw),
        "note": note,
        "entered_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    _save(history)
    return history[date_iso]


def daily_summary():
    """briefing v2 공개 API. 어제 매출 + 7일 평균 + 30일 누적 (KRW)."""
    history = _load()
    today = datetime.date.today()
    yest = (today - datetime.timedelta(days=1)).isoformat()

    seven_total = 0
    for i in range(1, 8):
        d = (today - datetime.timedelta(days=i)).isoformat()
        seven_total += history.get(d, {}).get("net_krw", 0)
    seven_avg = seven_total / 7

    thirty_total = 0
    for i in range(1, 31):
        d = (today - datetime.timedelta(days=i)).isoformat()
        thirty_total += history.get(d, {}).get("net_krw", 0)

    snap = history.get(yest)
    return {
        "status": "ok" if snap else "awaiting_input",
        "yesterday": snap or {"date": yest, "gross_krw": 0, "count": 0, "net_krw": 0, "note": "수동 입력 대기"},
        "seven_day_avg_krw": int(seven_avg),
        "thirty_day_total_krw": int(thirty_total),
        "history_days": len(history),
    }


def _interactive():
    today = datetime.date.today()
    yest = today - datetime.timedelta(days=1)
    print(f"크티 수동 입력 — {yest.isoformat()} (어제)")
    print("Enter 만 누르면 0 입력")
    try:
        gross = input("총 매출 (원): ").strip() or "0"
        count = input("판매 건수: ").strip() or "0"
        refund = input("환불 (원, 없으면 0): ").strip() or "0"
        note = input("메모 (선택): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n중단")
        return
    snap = set_entry(yest.isoformat(), int(gross), int(count), int(refund), note)
    print(json.dumps(snap, ensure_ascii=False, indent=2))


def _status():
    history = _load()
    today = datetime.date.today()
    print("최근 7일 입력 현황:")
    for i in range(1, 8):
        d = (today - datetime.timedelta(days=i)).isoformat()
        s = history.get(d)
        if s:
            print(f"  {d}: ₩{s['net_krw']:,} ({s['count']}건)")
        else:
            print(f"  {d}: (미입력)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        _interactive()
    elif args[0] == "--status":
        _status()
    elif args[0] == "--set":
        # --set DATE GROSS [--count N] [--refund N] [--note "..."]
        if len(args) < 3:
            print("usage: --set YYYY-MM-DD GROSS [--count N] [--refund N] [--note ...]")
            sys.exit(1)
        date = args[1]
        gross = int(args[2])
        count = 0
        refund = 0
        note = ""
        i = 3
        while i < len(args):
            if args[i] == "--count":
                count = int(args[i + 1]); i += 2
            elif args[i] == "--refund":
                refund = int(args[i + 1]); i += 2
            elif args[i] == "--note":
                note = args[i + 1]; i += 2
            else:
                i += 1
        snap = set_entry(date, gross, count, refund, note)
        print(json.dumps(snap, ensure_ascii=False, indent=2))
    elif args[0] == "--summary":
        print(json.dumps(daily_summary(), ensure_ascii=False, indent=2))
    else:
        print(__doc__)
