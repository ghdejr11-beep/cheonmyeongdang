"""
KDP 매출·리뷰 데이터 수집
- KDP 공식 Reports API 없음 → scrapling + 세션 쿠키 필요 or 수동 CSV
- 지금은 수동 CSV 다운로드 파싱 방식 (KDP Reports → Excel 다운 → 폴더 저장)
"""
import csv
from pathlib import Path
from datetime import datetime


CSV_DIR = Path(r"D:\cheonmyeongdang\.kdp_reports")


def _latest_csv():
    if not CSV_DIR.exists():
        return None
    files = sorted(CSV_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def parse_sales_csv(csv_path):
    """KDP Sales Dashboard 에서 다운받은 CSV 파싱"""
    result = {"total_units": 0, "total_royalty_usd": 0.0, "by_book": {}}
    if not csv_path or not Path(csv_path).exists():
        return result
    try:
        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("Title") or row.get("제목") or "?"
                units = int(row.get("Net Units Sold") or row.get("순판매") or 0)
                royalty = float(row.get("Royalty") or row.get("로열티") or 0)
                result["total_units"] += units
                result["total_royalty_usd"] += royalty
                result["by_book"].setdefault(title, {"units": 0, "royalty": 0})
                result["by_book"][title]["units"] += units
                result["by_book"][title]["royalty"] += royalty
    except Exception:
        pass
    return result


def daily_summary():
    """브리핑용 KDP 요약"""
    csv_file = _latest_csv()
    if not csv_file:
        return {
            "status": "no_data",
            "message": f"수동 CSV 다운로드 필요 — {CSV_DIR} 에 저장",
            "how_to": "kdp.amazon.com/reports → Sales Dashboard → Download → .csv → 해당 폴더 저장",
        }
    data = parse_sales_csv(csv_file)
    age_hours = (datetime.now().timestamp() - csv_file.stat().st_mtime) / 3600
    return {
        "status": "ok",
        "csv_file": csv_file.name,
        "csv_age_hours": round(age_hours, 1),
        "total_units": data["total_units"],
        "total_royalty_usd": round(data["total_royalty_usd"], 2),
        "top_books": sorted(
            data["by_book"].items(), key=lambda x: x[1]["royalty"], reverse=True
        )[:5],
    }


if __name__ == "__main__":
    import sys, json
    sys.stdout.reconfigure(encoding="utf-8")
    CSV_DIR.mkdir(exist_ok=True)
    print(json.dumps(daily_summary(), ensure_ascii=False, indent=2))
