#!/usr/bin/env python3
"""
AdMob 광고 단위 자동 생성 + 코드 패치 (천명당)

전제: admob_auth_setup.py 를 monetization scope 포함 상태로 1회 재실행한 토큰이 있어야 함.

기능:
1) cheonmyeongdang_banner / cheonmyeongdang_interstitial / cheonmyeongdang_rewarded 자동 생성
2) www/index.html 안의 PLACEHOLDER_BANNER / PLACEHOLDER_INTERSTITIAL / PLACEHOLDER_REWARDED 를
   실제 광고 단위 ID 로 즉시 치환
3) departments/cheonmyeongdang/ad_units.json 에 결과 기록

사용:
    python admob_create_units.py
"""
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

CMD_APP_ID = "ca-app-pub-2954177434416880~7399025784"
WWW_INDEX = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\www\index.html")
RECORD = Path(
    r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\cheonmyeongdang\ad_units.json"
)

UNIT_SPECS = [
    {
        "key": "banner",
        "displayName": "cheonmyeongdang_banner",
        "adFormat": "BANNER",
        "adTypes": ["RICH_MEDIA", "VIDEO"],
        "placeholder": "ca-app-pub-2954177434416880/PLACEHOLDER_BANNER",
    },
    {
        "key": "interstitial",
        "displayName": "cheonmyeongdang_interstitial",
        "adFormat": "INTERSTITIAL",
        "adTypes": ["RICH_MEDIA", "VIDEO"],
        "placeholder": "ca-app-pub-2954177434416880/PLACEHOLDER_INTERSTITIAL",
    },
    {
        "key": "rewarded",
        "displayName": "cheonmyeongdang_rewarded",
        "adFormat": "REWARDED",
        "adTypes": ["VIDEO"],
        "placeholder": "ca-app-pub-2954177434416880/PLACEHOLDER_REWARDED",
    },
]


def _build_v1beta():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    from admob_collector import _get_publisher_id, _get_token_path

    pub = _get_publisher_id()
    token_path = _get_token_path()
    if not pub or not token_path or not token_path.exists():
        raise RuntimeError("Publisher ID / token 누락 (.secrets 확인)")

    scopes = [
        "https://www.googleapis.com/auth/admob.readonly",
        "https://www.googleapis.com/auth/admob.monetization",
        "https://www.googleapis.com/auth/admob.report",
    ]
    creds = Credentials.from_authorized_user_file(str(token_path), scopes)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("admob", "v1beta", credentials=creds, cache_discovery=False), pub


def main():
    try:
        svc, pub = _build_v1beta()
    except Exception as e:
        print(f"[ERROR] AdMob API init 실패: {e}")
        sys.exit(1)

    parent = f"accounts/{pub}"
    results = {}
    print(f"[AdMob] parent={parent}, app={CMD_APP_ID}")

    # 이미 있는 광고 단위는 재사용
    try:
        existing = svc.accounts().adUnits().list(parent=parent).execute()
        existing_units = existing.get("adUnits", [])
    except Exception as e:
        print(f"[ERROR] adUnits.list 실패 (scope 부족 가능): {e}")
        sys.exit(2)

    by_name = {u.get("displayName"): u for u in existing_units}

    for spec in UNIT_SPECS:
        name = spec["displayName"]
        if name in by_name and by_name[name].get("appId") == CMD_APP_ID:
            unit = by_name[name]
            print(f"[SKIP] {name} 이미 존재 — {unit['adUnitId']}")
            results[spec["key"]] = unit["adUnitId"]
            continue

        body = {
            "appId": CMD_APP_ID,
            "displayName": name,
            "adFormat": spec["adFormat"],
            "adTypes": spec["adTypes"],
        }
        try:
            r = svc.accounts().adUnits().create(parent=parent, body=body).execute()
            print(f"[CREATED] {name} → {r.get('adUnitId')}")
            results[spec["key"]] = r.get("adUnitId")
        except Exception as e:
            print(f"[FAIL] {name}: {str(e)[:300]}")
            results[spec["key"]] = None

    # www/index.html 의 placeholder 치환
    if WWW_INDEX.exists():
        text = WWW_INDEX.read_text(encoding="utf-8")
        modified = False
        for spec in UNIT_SPECS:
            new_id = results.get(spec["key"])
            if new_id and spec["placeholder"] in text:
                text = text.replace(spec["placeholder"], new_id)
                modified = True
                print(f"[PATCHED] {spec['key']} placeholder → {new_id}")
        if modified:
            WWW_INDEX.write_text(text, encoding="utf-8")
            print(f"[OK] www/index.html 업데이트 완료")
        else:
            print("[INFO] placeholder 치환 없음 (이미 적용됐거나 광고 단위 생성 실패)")
    else:
        print(f"[WARN] www/index.html 없음: {WWW_INDEX}")

    # 결과 기록
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 결과 기록: {RECORD}")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
