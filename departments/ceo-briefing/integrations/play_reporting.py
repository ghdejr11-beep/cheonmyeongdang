"""
Google Play Developer Reporting API 스켈레톤
- GCP 서비스 계정 JSON 필요 (저장: .secrets/play-service-account.json)
- 앱 출시 후 매출/설치/크래시 자동 수집
"""
import json
from pathlib import Path


SECRET_JSON = Path(
    r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets\play-service-account.json"
)


def has_credentials():
    return SECRET_JSON.exists()


def get_daily_metrics(package_id):
    """일별 매출·설치·크래시 등 지표"""
    if not has_credentials():
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        creds = service_account.Credentials.from_service_account_file(
            str(SECRET_JSON),
            scopes=["https://www.googleapis.com/auth/playdeveloperreporting"],
        )
        service = build("playdeveloperreporting", "v1beta1", credentials=creds)
        # 예: daily crash rate
        # 실제 구현은 앱 출시 + 서비스 계정 Play Console 연결 후 확정
        return {"package": package_id, "note": "API 준비됨, 앱 출시 후 실데이터 조회"}
    except Exception as e:
        return {"error": str(e)}


def daily_summary():
    if not has_credentials():
        return {
            "status": "no_credentials",
            "message": f"GCP 서비스 계정 JSON 저장 필요: {SECRET_JSON}",
            "how_to": (
                "1) console.cloud.google.com 프로젝트 생성 "
                "2) Play Developer Reporting API 활성화 "
                "3) 서비스 계정 생성 + JSON 다운로드 "
                "4) Play Console에서 해당 서비스 계정 연결 + 재무 권한"
            ),
        }
    return {
        "status": "ready",
        "apps": {
            "cheonmyeongdang": get_daily_metrics("com.cheonmyeongdang.app"),
            "hexdrop": get_daily_metrics("com.yourname.hexdrop"),
        },
    }


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(daily_summary(), ensure_ascii=False, indent=2))
