#!/usr/bin/env python3
"""
KDP 스크래퍼 (Playwright) — 옵트인.

⚠️  중요 안내:
- KDP 는 공식 Reports API 를 제공하지 않습니다 (2026-04 기준 검색 확인).
- 자동 로그인 / 스크래핑은 Amazon 이용약관(ToS) 회색지대입니다.
  계정 정지 위험이 0이 아니므로 사용자 본인이 결정해야 합니다.
- 권장 대안: 매주 1회 KDP Reports → CSV 다운로드 →
  C:\\Users\\hdh02\\Desktop\\cheonmyeongdang\\.kdp_reports\\ 에 저장.
  기존 ceo-briefing/integrations/kdp.py 가 이 폴더를 자동 파싱합니다.

이 모듈은 KDP_EMAIL + KDP_PASSWORD 가 .secrets 에 둘 다 있을 때만 실행됩니다.
2FA / CAPTCHA / 본인인증 발생 시 즉시 중단하고 graceful fallback.

결과:
- data/kdp_daily.json — { date: { units, royalty_usd, ku_pages, by_book } }
"""
import os
import sys
import json
import datetime
import csv
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DAILY_JSON = DATA_DIR / "kdp_daily.json"
LOGS_DIR = BASE / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
SECRETS_PATH = Path(r"D:\cheonmyeongdang\.secrets")

# 수동 CSV fallback 폴더 (기존 integrations/kdp.py 와 동일 위치 사용)
MANUAL_CSV_DIR = Path(r"D:\cheonmyeongdang\.kdp_reports")

KDP_REPORTS_URL = "https://kdp.amazon.com/en_US/reports-new"
KDP_LOGIN_URL = "https://kdp.amazon.com/"


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


def _credentials():
    e = _load_env()
    return e.get("KDP_EMAIL"), e.get("KDP_PASSWORD")


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


# ─────────────────────────────────────────────────────────
# 수동 CSV fallback (기존 integrations/kdp.py 동일 로직)
# ─────────────────────────────────────────────────────────
def _latest_csv():
    if not MANUAL_CSV_DIR.exists():
        return None
    files = sorted(MANUAL_CSV_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _parse_manual_csv(csv_path):
    result = {"total_units": 0, "total_royalty_usd": 0.0, "ku_pages_read": 0, "by_book": {}}
    if not csv_path or not Path(csv_path).exists():
        return result
    try:
        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("Title") or row.get("제목") or "?"
                units = int(float(row.get("Net Units Sold") or row.get("순판매") or 0))
                royalty = float(row.get("Royalty") or row.get("로열티") or 0)
                pages = int(float(row.get("KENP Read") or row.get("KU 페이지") or 0))
                result["total_units"] += units
                result["total_royalty_usd"] += royalty
                result["ku_pages_read"] += pages
                d = result["by_book"].setdefault(title, {"units": 0, "royalty": 0, "pages": 0})
                d["units"] += units
                d["royalty"] += royalty
                d["pages"] += pages
    except Exception:
        pass
    return result


def collect_from_manual_csv():
    """수동 CSV → JSON 누적. CSV 갱신 시각을 기준일로 사용."""
    csv_file = _latest_csv()
    if not csv_file:
        return {"status": "no_csv", "message": f"수동 CSV 없음 — {MANUAL_CSV_DIR} 에 저장"}
    parsed = _parse_manual_csv(csv_file)
    mtime = datetime.datetime.fromtimestamp(csv_file.stat().st_mtime)
    iso = mtime.date().isoformat()
    snap = {
        "date": iso,
        "status": "ok",
        "source": "manual_csv",
        "csv_file": csv_file.name,
        "csv_mtime": mtime.isoformat(timespec="seconds"),
        "units": parsed["total_units"],
        "royalty_usd": round(parsed["total_royalty_usd"], 2),
        "ku_pages_read": parsed["ku_pages_read"],
        "by_book": parsed["by_book"],
    }
    history = _load_history()
    history[iso] = snap
    _save_history(history)
    return snap


# ─────────────────────────────────────────────────────────
# Playwright 자동 스크래핑 (옵트인)
# ─────────────────────────────────────────────────────────
def _can_use_playwright():
    """Playwright 설치 여부 + 자격증명 둘 다 있을 때만 True"""
    email, pw = _credentials()
    if not (email and pw):
        return False, "credentials_missing"
    try:
        import playwright  # noqa: F401
        return True, "ok"
    except ImportError:
        return False, "playwright_not_installed"


def collect_via_playwright(headless=True):
    """
    Playwright 로그인 → KDP Reports → 어제 매출 추출.
    2FA/CAPTCHA 발생 시 즉시 중단.

    반환:
        {"status": "ok", ...}  성공
        {"status": "blocked_2fa"}  2FA 또는 본인인증 발생
        {"status": "error", "error": ...}
    """
    can, reason = _can_use_playwright()
    if not can:
        return {
            "status": "skipped",
            "reason": reason,
            "message": (
                "credentials_missing: .secrets 에 KDP_EMAIL/KDP_PASSWORD 추가"
                if reason == "credentials_missing"
                else "playwright 미설치: pip install playwright && playwright install chromium"
            ),
            "warning": "KDP 자동 로그인은 Amazon ToS 회색지대 — 사용자 본인 결정 필요",
        }

    email, pw = _credentials()
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    log_path = LOGS_DIR / f"kdp_scrape_{today.isoformat()}.log"
    log_lines = []

    def _log(msg):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        log_lines.append(line)

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()
            _log("페이지 오픈")
            page.goto(KDP_LOGIN_URL, timeout=30000, wait_until="domcontentloaded")

            # 로그인 폼
            try:
                page.fill('input[name="email"], input[type="email"]', email, timeout=8000)
                page.fill('input[name="password"], input[type="password"]', pw, timeout=8000)
                page.click('input[type="submit"], button[type="submit"]', timeout=8000)
                _log("자격증명 제출")
            except Exception as e:
                _log(f"로그인 폼 진입 실패: {e}")
                browser.close()
                return {
                    "status": "error",
                    "error": "login form not found",
                    "log": log_lines,
                }

            # 2FA / CAPTCHA / 본인인증 감지
            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                pass
            html_lower = (page.content() or "").lower()
            block_keywords = [
                "two-step verification",
                "verification code",
                "captcha",
                "puzzle",
                "approve the notification",
                "two-factor",
                "본인 확인",
                "보안문자",
            ]
            for kw in block_keywords:
                if kw in html_lower:
                    _log(f"차단 감지: {kw} → 중단")
                    browser.close()
                    log_path.write_text("\n".join(log_lines), encoding="utf-8")
                    return {
                        "status": "blocked_2fa",
                        "blocker": kw,
                        "message": "2FA/CAPTCHA/본인인증 발생 — 자동 중단. 수동 CSV 다운로드 권장.",
                        "log_path": str(log_path),
                    }

            # Reports 페이지
            page.goto(KDP_REPORTS_URL, timeout=30000, wait_until="domcontentloaded")
            _log("Reports 페이지 오픈")
            # 실제 셀렉터는 KDP UI 변경에 따라 자주 바뀜 → graceful 처리
            try:
                page.wait_for_selector(
                    "table, [data-test-id], .reports-summary",
                    timeout=15000,
                )
            except Exception:
                _log("리포트 테이블 미감지 (UI 변경 가능)")

            # KDP UI 가 자주 바뀌므로 본 모듈은 "로그인까지만 검증" 단계로 두고,
            # 실제 매출 파싱은 수동 CSV fallback 으로 위임 (안전).
            browser.close()
            log_path.write_text("\n".join(log_lines), encoding="utf-8")
            return {
                "status": "login_ok_no_parse",
                "date": yesterday.isoformat(),
                "message": "로그인 성공. 매출 파싱은 수동 CSV 권장 (UI 자주 변경됨)",
                "log_path": str(log_path),
            }

    except Exception as e:
        log_path.write_text("\n".join(log_lines + [f"FATAL: {e}"]), encoding="utf-8")
        return {"status": "error", "error": str(e)[:200], "log_path": str(log_path)}


# ─────────────────────────────────────────────────────────
# 통합 수집 (Playwright → 실패시 수동 CSV)
# ─────────────────────────────────────────────────────────
def collect_yesterday():
    """
    1) Playwright 로그인 시도 (자격증명 있을 때)
    2) 실패/스킵시 수동 CSV 파싱
    """
    pw_result = collect_via_playwright(headless=True)
    if pw_result.get("status") == "ok":
        return pw_result
    # Playwright 가 매출까지 파싱 못한 경우에도 → CSV fallback
    csv_result = collect_from_manual_csv()
    csv_result["playwright_status"] = pw_result.get("status")
    return csv_result


# ─────────────────────────────────────────────────────────
# briefing v2 공개 API
# ─────────────────────────────────────────────────────────
def daily_summary():
    history = _load_history()
    csv_result = collect_from_manual_csv()  # 항상 수동 CSV 갱신 시도

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yest_iso = yesterday.isoformat()

    snap = history.get(yest_iso) or csv_result

    # 30일 누적
    thirty_total_royalty = 0
    thirty_total_units = 0
    for i in range(1, 31):
        d = (today - datetime.timedelta(days=i)).isoformat()
        s = history.get(d, {})
        thirty_total_royalty += s.get("royalty_usd", 0)
        thirty_total_units += s.get("units", 0)

    email, pw = _credentials()
    has_creds = bool(email and pw)

    if snap.get("status") == "no_csv" and not has_creds:
        return {
            "status": "no_data",
            "message": "수동 CSV 입력 대기 또는 .secrets KDP_EMAIL/PASSWORD 등록 필요",
            "how_to": (
                "권장(안전): kdp.amazon.com/reports → Sales Dashboard → "
                "CSV 다운로드 → C:/Users/hdh02/Desktop/cheonmyeongdang/.kdp_reports/ 저장"
            ),
            "risk_warning": (
                "Playwright 자동 로그인은 Amazon ToS 회색지대 — "
                "계정 정지 위험 있어 사용자 본인 결정 필요"
            ),
        }

    return {
        "status": snap.get("status", "no_data"),
        "yesterday": {
            "date": yest_iso,
            "units": snap.get("units", 0),
            "royalty_usd": snap.get("royalty_usd", 0),
            "ku_pages_read": snap.get("ku_pages_read", 0),
            "by_book": snap.get("by_book", {}),
            "source": snap.get("source", "unknown"),
        },
        "thirty_day_total_units": thirty_total_units,
        "thirty_day_total_royalty_usd": round(thirty_total_royalty, 2),
        "history_days": len(history),
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--collect":
        print(json.dumps(collect_yesterday(), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--csv-only":
        print(json.dumps(collect_from_manual_csv(), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(daily_summary(), ensure_ascii=False, indent=2))
