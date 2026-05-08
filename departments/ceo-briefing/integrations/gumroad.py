"""
Gumroad API 매출 + 상품 현황 수집
Docs: https://app.gumroad.com/api
"""
import urllib.request, urllib.parse, json, datetime, os
from pathlib import Path


def _token():
    secrets_path = Path(r"D:\cheonmyeongdang\.secrets")
    for line in secrets_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("GUMROAD_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    return None


def _request(path, params=None):
    token = _token()
    if not token:
        return None
    qs = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"https://api.gumroad.com/v2/{path}{qs}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def get_sales(after=None, before=None):
    """
    Args:
        after: ISO date string (YYYY-MM-DD) - 이 날짜 이후
        before: ISO date string (YYYY-MM-DD)
    Returns:
        list of sales
    """
    params = {"page": 1}
    if after:
        params["after"] = after
    if before:
        params["before"] = before
    all_sales = []
    while True:
        data = _request("sales", params)
        if not data or data.get("error") or not data.get("success"):
            break
        sales = data.get("sales", [])
        all_sales.extend(sales)
        next_page = data.get("next_page_url")
        if not next_page or len(sales) == 0:
            break
        params["page"] += 1
        if params["page"] > 20:  # safety limit
            break
    return all_sales


def get_products():
    """모든 등록 상품 조회"""
    data = _request("products")
    if not data or data.get("error"):
        return []
    return data.get("products", [])


def daily_summary(days_back=1):
    """지정 일수 전부터 오늘까지 매출 요약"""
    today = datetime.date.today()
    start = today - datetime.timedelta(days=days_back)
    sales = get_sales(after=start.isoformat(), before=today.isoformat())

    total_cents = sum(s.get("price", 0) for s in sales)
    by_product = {}
    for s in sales:
        name = s.get("product_name", "?")
        by_product.setdefault(name, {"count": 0, "cents": 0})
        by_product[name]["count"] += 1
        by_product[name]["cents"] += s.get("price", 0)

    return {
        "period": f"{start} ~ {today}",
        "total_sales": len(sales),
        "total_krw": total_cents,  # Gumroad는 cents 단위 (KRW도 소수점 2자리 표기)
        "by_product": by_product,
    }


def product_status():
    """상품별 등록 여부 + 노출 경고 생성"""
    products = get_products()
    total_listed = len(products)
    total_sales_count = sum(p.get("sales_count", 0) for p in products)
    total_revenue_cents = sum(p.get("sales_usd_cents", 0) for p in products)
    zero_sale_products = [p["name"] for p in products if p.get("sales_count", 0) == 0]

    warning = None
    if total_listed > 0 and total_sales_count == 0:
        warning = f"🚨 Gumroad {total_listed}상품 등록돼있지만 누적 판매 0건 — 노출/마케팅 필요"
    elif len(zero_sale_products) > total_listed // 2:
        warning = f"⚠️ {len(zero_sale_products)}/{total_listed}개 상품 판매 0건 — 검토 필요"

    return {
        "total_products": total_listed,
        "total_sales_count": total_sales_count,
        "total_revenue": total_revenue_cents / 100,
        "zero_sale_products": zero_sale_products,
        "warning": warning,
    }


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== Daily Summary (last 1 day) ===")
    print(json.dumps(daily_summary(days_back=1), ensure_ascii=False, indent=2))
    print()
    print("=== Product Status ===")
    print(json.dumps(product_status(), ensure_ascii=False, indent=2))
