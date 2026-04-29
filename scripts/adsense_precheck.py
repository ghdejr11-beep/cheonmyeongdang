# -*- coding: utf-8 -*-
"""
adsense_precheck.py — Google AdSense 신청 전 사이트 정책 점검 스크립트

사용법:
    python scripts/adsense_precheck.py
    python scripts/adsense_precheck.py --base https://cheonmyeongdang.vercel.app
    python scripts/adsense_precheck.py --local

검증 항목 (10가지):
    1. privacy.html / terms.html 파일 존재 + HTTP 200
    2. 콘텐츠 분량 (단어 수, 1500자 이상 권장)
    3. 메타태그 (title / description / og)
    4. HTTPS 프로토콜 (Vercel 자동)
    5. 모바일 viewport 메타
    6. AdSense 광고 슬롯 6곳 위치 정상 (ca-pub-PLACEHOLDER)
    7. ads.txt 파일 존재
    8. sitemap.xml / robots.txt
    9. 콘텐츠 정책 위반 키워드 (도박/사행성/19금) 검출
   10. 외부 접근성 (HTTP HEAD 200)

종료 코드:
    0 = 모두 통과
    1 = 일부 미충족 (리포트 출력)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

# Windows cp949 콘솔에서 한국어 + em-dash 출력 보장
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = "https://cheonmyeongdang.vercel.app"

# AdSense 정책 위반 위험 키워드 (한국어 + 영어)
RISK_KEYWORDS = {
    "도박/사행성": ["도박", "베팅", "betting", "casino", "카지노", "토토"],
    "성인/19금": ["19금", "성인전용", "포르노", "porn", "adult only"],
    "위험약물": ["마약", "대마", "코카인"],
    "혐오/차별": ["혐오발언"],
}

# 한국어 단어 카운트용 (공백 + 한자/한글/영문 토큰 단순 카운트)
def count_words(text: str) -> int:
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"&[a-z#0-9]+;", " ", cleaned)
    tokens = re.findall(r"[가-힣]+|[a-zA-Z]+|[0-9]+", cleaned)
    return len(tokens)


def color(code: int, msg: str) -> str:
    if not sys.stdout.isatty():
        return msg
    return f"\033[{code}m{msg}\033[0m"


def green(s: str) -> str:
    return color(32, s)


def red(s: str) -> str:
    return color(31, s)


def yellow(s: str) -> str:
    return color(33, s)


def cyan(s: str) -> str:
    return color(36, s)


def http_check(url: str, timeout: float = 10.0) -> tuple[bool, int, str]:
    """URL이 200을 반환하는지 GET 요청으로 확인."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AdSense-PreCheck/1.0 (Mozilla/5.0)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return (resp.status == 200, resp.status, "")
    except urllib.error.HTTPError as e:
        return (False, e.code, str(e.reason))
    except Exception as e:  # noqa: BLE001
        return (False, 0, str(e))


class CheckResult:
    def __init__(self, name: str, ok: bool, detail: str = "") -> None:
        self.name = name
        self.ok = ok
        self.detail = detail

    def render(self) -> str:
        mark = green("PASS") if self.ok else red("FAIL")
        line = f"  [{mark}] {self.name}"
        if self.detail:
            line += f"\n         -> {self.detail}"
        return line


def check_local_files() -> list[CheckResult]:
    results: list[CheckResult] = []
    must_exist = {
        "privacy.html": PROJECT_ROOT / "privacy.html",
        "terms.html": PROJECT_ROOT / "terms.html",
        "index.html": PROJECT_ROOT / "index.html",
        "ads.txt": PROJECT_ROOT / "ads.txt",
        "sitemap.xml": PROJECT_ROOT / "sitemap.xml",
        "robots.txt": PROJECT_ROOT / "robots.txt",
    }
    for label, path in must_exist.items():
        results.append(
            CheckResult(
                f"파일 존재: {label}",
                path.exists(),
                f"경로: {path}" if not path.exists() else "",
            )
        )
    return results


def check_index_meta() -> list[CheckResult]:
    results: list[CheckResult] = []
    index = PROJECT_ROOT / "index.html"
    if not index.exists():
        results.append(CheckResult("index.html 메타 검사", False, "index.html 없음"))
        return results
    html = index.read_text(encoding="utf-8")
    word_count = count_words(html)

    checks = [
        ("title 태그", bool(re.search(r"<title>[^<]{5,}</title>", html))),
        (
            "meta description (50자 이상)",
            bool(re.search(r'name="description"\s+content="([^"]{50,})"', html)),
        ),
        ("og:title", "og:title" in html),
        ("og:image", "og:image" in html),
        ("viewport (모바일 반응형)", 'name="viewport"' in html),
        ("HTTPS canonical", 'rel="canonical"' in html and "https://" in html),
        ("AdSense 스크립트 헤드 삽입", "adsbygoogle.js?client=" in html),
        ("AdSense 슬롯 6곳", html.count("data-ad-slot=") >= 6),
        ("PLACEHOLDER 미교체 (신청 전 정상)", "ca-pub-PLACEHOLDER" in html),
        (
            f"콘텐츠 분량 충분 (단어 {word_count:,}개, 1500개+ 권장)",
            word_count >= 1500,
        ),
    ]
    for name, ok in checks:
        results.append(CheckResult(name, ok))
    return results


def check_risk_keywords() -> list[CheckResult]:
    """AdSense 정책 위반 위험 키워드 검출 (있어도 즉시 fail은 아님 — 경고용)."""
    results: list[CheckResult] = []
    index = PROJECT_ROOT / "index.html"
    if not index.exists():
        return results
    html = index.read_text(encoding="utf-8").lower()
    for category, words in RISK_KEYWORDS.items():
        hits = [w for w in words if w.lower() in html]
        if hits:
            results.append(
                CheckResult(
                    f"위험 키워드 [{category}]",
                    False,
                    f"검출: {', '.join(hits)} — 면책 문구 명시 필요",
                )
            )
        else:
            results.append(CheckResult(f"위험 키워드 [{category}] 미검출", True))
    return results


def check_http(base: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    paths = ["/", "/privacy.html", "/terms.html", "/sitemap.xml", "/robots.txt", "/ads.txt"]
    for p in paths:
        url = base.rstrip("/") + p
        ok, code, err = http_check(url)
        detail = "" if ok else f"HTTP {code} {err}"
        results.append(CheckResult(f"HTTP 200: {url}", ok, detail))
    # HTTPS 검증
    results.append(
        CheckResult("HTTPS 강제", base.startswith("https://"), f"base={base}")
    )
    return results


def check_adsense_slot_layout() -> list[CheckResult]:
    """광고 슬롯 6곳이 무료 콘텐츠 결과 영역 직후에 배치되었는지 휴리스틱 점검."""
    results: list[CheckResult] = []
    index = PROJECT_ROOT / "index.html"
    if not index.exists():
        return results
    html = index.read_text(encoding="utf-8")
    expected_slots = ["0000000001", "0000000002", "0000000003", "0000000004", "0000000005", "0000000006"]
    for slot in expected_slots:
        results.append(
            CheckResult(
                f"광고 슬롯 ID {slot} 존재",
                f'data-ad-slot="{slot}"' in html,
            )
        )
    # 신청 단계에서는 PLACEHOLDER 그대로 두는 것이 정상 — AdSense 스니펫만 head에 있으면 OK
    head_snippet = "adsbygoogle.js?client=ca-pub-PLACEHOLDER" in html or re.search(
        r"adsbygoogle\.js\?client=ca-pub-\d{16}", html
    )
    results.append(CheckResult("AdSense head 스니펫 삽입 정상", bool(head_snippet)))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="AdSense 신청 사전 점검")
    parser.add_argument("--base", default=DEFAULT_BASE_URL, help="라이브 사이트 base URL")
    parser.add_argument("--local", action="store_true", help="HTTP 검증 생략 (오프라인)")
    parser.add_argument("--json", action="store_true", help="JSON 결과 출력")
    args = parser.parse_args()

    print(cyan("=" * 70))
    print(cyan(" Google AdSense 신청 사전 점검 — 천명당 (cheonmyeongdang)"))
    print(cyan("=" * 70))
    print(f"  프로젝트 경로: {PROJECT_ROOT}")
    print(f"  라이브 base : {args.base}")
    print()

    sections: dict[str, list[CheckResult]] = {
        "1. 로컬 필수 파일": check_local_files(),
        "2. index.html 메타/콘텐츠": check_index_meta(),
        "3. AdSense 슬롯 배치": check_adsense_slot_layout(),
        "4. 정책 위험 키워드": check_risk_keywords(),
    }
    if not args.local:
        sections["5. 라이브 HTTP 접근성"] = check_http(args.base)

    total = 0
    failed = 0
    for title, results in sections.items():
        print(yellow(f"[{title}]"))
        for r in results:
            print(r.render())
            total += 1
            if not r.ok:
                failed += 1
        print()

    print(cyan("=" * 70))
    if failed == 0:
        print(green(f"  통과: {total}/{total} — AdSense 신청 가능 상태 OK"))
        print(cyan("=" * 70))
        if args.json:
            print(json.dumps({"ok": True, "total": total, "failed": 0}, ensure_ascii=False))
        return 0
    else:
        print(red(f"  미충족: {failed}/{total} — 리포트 위 항목 확인 후 재실행"))
        print(cyan("=" * 70))
        if args.json:
            print(json.dumps({"ok": False, "total": total, "failed": failed}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
