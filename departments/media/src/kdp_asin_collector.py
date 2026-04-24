#!/usr/bin/env python3
"""
KDP 20권 ASIN 자동 수집.

저자 브랜드명 "Deokgu Studio" + 책 제목으로 Amazon 검색 → /dp/XXXXX 패턴 파싱.
rate limit 존중 (요청 간 3초 대기). CAPTCHA 감지 시 중단.

⚠️ 법적 경고:
- Amazon ToS는 자동 스크래핑을 명시적으로 금지
- 본 스크립트는 **소유한 상품의 ASIN 수동 확인** 목적만 사용
- 대량/고빈도 사용 금지. 권장: 주 1회 최대
- 더 안전한 길: KDP 대시보드 (kdp.amazon.com) 에서 수동 복사

실행: python kdp_asin_collector.py
출력: kdp_books.json 업데이트 + D:\state\kdp_asin_collection.json 로그
"""
import json, re, time, sys, urllib.request, urllib.parse, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BOOKS_JSON = Path(__file__).parent / "kdp_books.json"
LOG_FILE = Path(r"D:\state\kdp_asin_collection.json")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

AUTHOR = "Deokgu Studio"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
DELAY = 3.0  # 초


def search_asin(title, author):
    q = urllib.parse.quote_plus(f"{title} {author}")
    url = f"https://www.amazon.com/s?k={q}&i=digital-text"  # Kindle books section
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return None, f"fetch failed: {e}"

    if "captcha" in html.lower() or "api-services-support" in html.lower():
        return None, "CAPTCHA or block detected — STOP"

    # search result: data-asin="BXXXXX"
    asins = re.findall(r'data-asin="(B[A-Z0-9]{9})"', html)
    # 첫 번째 non-empty 결과
    asins = [a for a in asins if a]
    if not asins:
        return None, "no match"
    return asins[0], "ok"


def main():
    books = json.loads(BOOKS_JSON.read_text(encoding="utf-8"))
    print(f"📚 책 {len(books)}권 · 저자 {AUTHOR}")

    results = []
    updated = 0
    blocked = False
    for i, b in enumerate(books, 1):
        if b.get("asin"):
            print(f"  {i:2d}. {b['title'][:40]:40s} · ASIN {b['asin']} (skip)")
            results.append({"slug": b["slug"], "asin": b["asin"], "status": "cached"})
            continue
        if blocked:
            results.append({"slug": b["slug"], "asin": None, "status": "blocked"})
            continue
        asin, msg = search_asin(b["title"], AUTHOR)
        print(f"  {i:2d}. {b['title'][:40]:40s} · {asin or '---'} ({msg})")
        if msg.startswith("CAPTCHA"):
            blocked = True
            print("  ⛔ Amazon 차단 감지 — 수동 경로 권장")
        if asin:
            b["asin"] = asin
            updated += 1
        results.append({"slug": b["slug"], "asin": asin, "status": msg})
        time.sleep(DELAY)

    if updated:
        BOOKS_JSON.write_text(json.dumps(books, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✅ {updated}권 ASIN 업데이트")
    else:
        print("ℹ️ 업데이트 없음")

    # 로그 (D:)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "date": datetime.date.today().isoformat(),
            "updated": updated,
            "blocked": blocked,
            "results": results,
        }, ensure_ascii=False) + "\n")
    print(f"📝 로그: {LOG_FILE}")
    print()
    print("⚠️ 차단 감지 또는 누락분은 KDP 대시보드에서 수동 확인 권장:")
    print("   https://kdp.amazon.com/en_US/bookshelf")


if __name__ == "__main__":
    main()
