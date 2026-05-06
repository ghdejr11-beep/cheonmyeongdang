# -*- coding: utf-8 -*-
"""정부지원 결과 발표 모니터 — 매일 11:00 자동 실행
- K-Startup AI 리그 결과: 5월말~6월초 발표 예정
- 관광 AI 결과: 6월~7월 발표 예정
- KoDATA 회신: 5/12 예상

Gmail MCP 또는 imap을 통한 메일 키워드 알림 + Telegram 푸시 (외출 시그널 시).
"""
import os, sys, datetime, json, urllib.request
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

KEYWORDS = {
    "kstartup": ["K-Startup", "AI 리그", "AI리그", "올해의", "선정", "통과", "결과"],
    "tourism_ai": ["관광AI", "관광 AI", "한국관광공사", "관광기업", "데이터·AI"],
    "kodata": ["KoDATA", "한국데이터산업진흥원", "관광데이터", "사전등록"],
    "modoo": ["모두의창업", "modoo", "Tech Track"],
    "kglobal": ["K-Global", "KGlobal", "글로벌화"],
}

URLS = {
    "k_startup_pms": "https://www.k-startup.go.kr/",
    "tour_kr_grant": "https://api.visitkorea.or.kr/",
    "modoo_or_kr": "https://modoo.or.kr/",
}

def log_status():
    today = datetime.date.today()
    deadlines = {
        "K-Startup AI 리그 결과 발표": datetime.date(2026, 6, 5),
        "관광 AI 결과 발표": datetime.date(2026, 7, 1),
        "KoDATA 회신": datetime.date(2026, 5, 12),
    }
    log_path = LOG_DIR / f"grant_monitor_{today.isoformat()}.log"
    lines = [f"[{datetime.datetime.now().isoformat()}] Grant Result Monitor"]
    for name, dt in deadlines.items():
        days = (dt - today).days
        if days < 0:
            mark = "PAST"
        elif days <= 3:
            mark = "URGENT"
        else:
            mark = f"D-{days}"
        lines.append(f"  [{mark}] {name} -> {dt.isoformat()}")
    log_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return lines

def main():
    try:
        log_status()
    except Exception as e:
        err_path = LOG_DIR / f"grant_monitor_error_{datetime.date.today().isoformat()}.log"
        err_path.write_text(str(e), encoding="utf-8")
        sys.exit(1)

if __name__ == "__main__":
    main()
