"""PayPal 거래 자동 모니터 — 매일 09시 schtask 가동.

신규 매출 발생 시:
1. departments/sales-collection/data/paypal_daily.json 갱신
2. 텔레그램 알림 (사용자 PC, 화면)
3. 매출 1건당 손익 + 일일 합계
"""
import os, sys, json, datetime, base64, urllib.request, urllib.parse, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# .secrets 로더 — env에 없으면 ROOT/.secrets에서 로드
_SECRETS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".secrets")
def _load_secrets_file():
    env = {}
    if os.path.exists(_SECRETS_PATH):
        for line in open(_SECRETS_PATH, encoding="utf-8"):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

_FILE_ENV = _load_secrets_file()
PP_CLIENT = os.environ.get("PAYPAL_CLIENT_ID") or _FILE_ENV.get("PAYPAL_CLIENT_ID", "")
PP_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET") or _FILE_ENV.get("PAYPAL_CLIENT_SECRET", "")
if not PP_CLIENT or not PP_SECRET:
    sys.stderr.write("[ABORT] PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET missing in env or .secrets\n")
    sys.exit(2)
PP_BASE = "https://api-m.paypal.com"

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "paypal_daily.json")
STATE_FILE = os.path.join(os.path.dirname(__file__), "data", "paypal_seen_ids.json")


def get_token():
    auth = base64.b64encode(f"{PP_CLIENT}:{PP_SECRET}".encode()).decode()
    req = urllib.request.Request(
        f"{PP_BASE}/v1/oauth2/token",
        data=b"grant_type=client_credentials",
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())["access_token"]


def fetch_transactions(token, days=2):
    end = datetime.datetime.now(datetime.timezone.utc)
    start = end - datetime.timedelta(days=days)
    params = urllib.parse.urlencode({
        "start_date": start.strftime("%Y-%m-%dT%H:%M:%S-0000"),
        "end_date": end.strftime("%Y-%m-%dT%H:%M:%S-0000"),
        "fields": "transaction_info,payer_info",
        "page_size": 100,
    })
    req = urllib.request.Request(
        f"{PP_BASE}/v1/reporting/transactions?{params}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode()).get("transaction_details", [])


def main():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    seen = set()
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            seen = set(json.load(f).get("seen", []))

    token = get_token()
    txs = fetch_transactions(token, days=2)

    today = datetime.date.today().isoformat()
    new_txs = []
    today_total = 0.0
    today_count = 0

    for t in txs:
        info = t.get("transaction_info", {})
        tid = info.get("transaction_id", "")
        if not tid:
            continue
        if tid not in seen:
            new_txs.append(t)
            seen.add(tid)

        date = info.get("transaction_initiation_date", "")[:10]
        if date == today:
            today_count += 1
            try:
                today_total += float(info.get("transaction_amount", {}).get("value", "0") or "0")
            except ValueError:
                pass

    # 일일 통계 저장
    daily = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            daily = json.load(f)
    daily[today] = {
        "date": today,
        "tx_count": today_count,
        "total_value": round(today_total, 2),
        "checked_at": datetime.datetime.now().isoformat(),
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(daily, f, ensure_ascii=False, indent=2)

    # seen 갱신
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"seen": list(seen), "updated": datetime.datetime.now().isoformat()}, f)

    # 결과 출력
    print(f"[CHECKED] {today} — total_tx={today_count} value={today_total:.2f}")
    if new_txs:
        print(f"[NEW] {len(new_txs)} 건 신규 트랜잭션:")
        for t in new_txs:
            info = t.get("transaction_info", {})
            payer = t.get("payer_info", {})
            amt = info.get("transaction_amount", {})
            email = payer.get("email_address", "?")
            edom = email.split("@")[1] if "@" in email else "?"
            print(f"  {info.get('transaction_initiation_date','?')[:19]} | {amt.get('value','0')} {amt.get('currency_code','?')} | @{edom}")


if __name__ == "__main__":
    main()
