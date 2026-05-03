"""
쿠팡 파트너스 매출 수집
- Open API: 최종 승인 후 자동 활성화 (AccessKey + SecretKey 필요)
- 승인 전: 수동 CSV 또는 web 대시보드 스크래핑 대체
"""
import hmac, hashlib, time, urllib.request, urllib.parse, json
from pathlib import Path


def _secrets():
    env = {}
    for line in Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def _signed_request(method, path, query="", body=""):
    env = _secrets()
    access = env.get("COUPANG_ACCESS_KEY")
    secret = env.get("COUPANG_SECRET_KEY")
    if not access or not secret:
        return None

    datetime_str = time.strftime("%y%m%dT%H%M%SZ", time.gmtime())
    message = datetime_str + method + path + query
    signature = hmac.new(
        secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    auth = (
        f"CEA algorithm=HmacSHA256, access-key={access}, "
        f"signed-date={datetime_str}, signature={signature}"
    )
    url = f"https://api-gateway.coupang.com{path}"
    if query:
        url += f"?{query}"
    req = urllib.request.Request(
        url, headers={"Authorization": auth, "Content-Type": "application/json"},
        data=body.encode("utf-8") if body else None, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def get_revenue_report(days=1):
    """파트너스 실적 리포트 (승인된 경우)"""
    # 쿠팡 파트너스 Open API 매출 조회 엔드포인트
    # (공식 문서 확인 필요: 파트너스는 상품 추천 API 주력, 매출은 제한적)
    return None  # 승인 후 구현


def daily_summary():
    env = _secrets()
    has_key = bool(env.get("COUPANG_ACCESS_KEY"))
    if not has_key:
        return {
            "status": "waiting_approval",
            "message": "쿠팡 Open API 심사 대기 중 (웹사이트/스크린샷 검수)",
            "fallback": "심사 승인 후 COUPANG_ACCESS_KEY, COUPANG_SECRET_KEY 저장 시 자동 활성화",
        }
    # 승인 후에는 여기서 실제 매출 조회
    report = get_revenue_report()
    return {
        "status": "active",
        "revenue_data": report,
    }


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(daily_summary(), ensure_ascii=False, indent=2))
