#!/usr/bin/env python3
"""
Uptime Monitor — Vercel + Cloudflare + GitHub Pages 자동 감시.

- HTTP GET / (timeout 10s)
- 실패 조건: 5xx, timeout, DNS fail
- 응답시간 ms 기록 → security/data/uptime_log.jsonl
- 3회 연속 실패시 텔레그램 알림 (false positive 방지)
- 복구시 다운타임 합계 알림
- 모니터 대상 자동 발견: departments/*/src/*.html grep + monitor_targets.json 누적

사용:
    python uptime_monitor.py            # 1회 체크 + 알림
    python uptime_monitor.py --once     # 조용히 1회 (cron)
    python uptime_monitor.py --discover # 자동발견만 실행, 결과 출력
    python uptime_monitor.py --status   # 현재 상태 표 출력
"""
import os
import sys
import json
import re
import socket
import time
import urllib.request
import urllib.error
import datetime
from pathlib import Path

# Windows 콘솔 한글 안전
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(os.path.expanduser("~/Desktop/cheonmyeongdang"))
DEPT_ROOT = ROOT / "departments"
SEC_DIR = DEPT_ROOT / "security"
DATA_DIR = SEC_DIR / "data"
LOG_PATH = DATA_DIR / "uptime_log.jsonl"
STATE_PATH = DATA_DIR / "uptime_state.json"
TARGETS_PATH = DATA_DIR / "monitor_targets.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────
# 시드(고정) 모니터 대상 — 사용자 명시 + 코드 grep 검증된 실가동 URL
# ──────────────────────────────────────────────────────────────
SEED_TARGETS = [
    {"name": "KORLENS",            "url": "https://korlens.vercel.app/",                                    "type": "vercel"},
    {"name": "Tax API",            "url": "https://tax-n-benefit-api.vercel.app/api/connect",               "type": "vercel-api"},
    {"name": "Tax Front",          "url": "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/tax/src/app.html",  "type": "ghpages"},
    {"name": "Insurance Customer", "url": "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/index.html", "type": "ghpages"},
    {"name": "Insurance Agent",    "url": "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/agent.html", "type": "ghpages"},
    {"name": "Cheonmyeongdang Web","url": "https://ghdejr11-beep.github.io/cheonmyeongdang/",                "type": "ghpages"},
]

TIMEOUT_SEC = 10
USER_AGENT = "KunStudio-UptimeMonitor/1.0 (+https://github.com/ghdejr11-beep)"
FAIL_THRESHOLD = 3  # 연속 실패 횟수


# ──────────────────────────────────────────────────────────────
# secrets / telegram
# ──────────────────────────────────────────────────────────────
def _load_secrets():
    env = {}
    p = ROOT / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def send_telegram(text: str) -> bool:
    """multi_poster.py 의 인터페이스에 맞추되, 의존성 없이 직접 호출."""
    env = _load_secrets()
    tok = env.get("TELEGRAM_BOT_TOKEN", "")
    chat = env.get("TELEGRAM_CHAT_ID", "")
    if not tok or not chat:
        print(f"[TG SKIP] {text[:120]}")
        return False
    try:
        body = json.dumps({
            "chat_id": chat,
            "text": text[:4000],
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{tok}/sendMessage",
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print(f"[TG ERROR] {e}")
        return False


# ──────────────────────────────────────────────────────────────
# 모니터 대상 자동 발견
# ──────────────────────────────────────────────────────────────
URL_RE = re.compile(
    r"https?://[a-zA-Z0-9._/-]*\.(?:vercel\.app|github\.io)[a-zA-Z0-9._/-]*",
    re.IGNORECASE,
)

# 명시적으로 모니터링 제외할 패턴 (개발용/이미지/대량 dead URL)
# /api/ 는 POST/auth 필수가 많아 자동 발견에서 제외 (시드에서만 명시)
EXCLUDE = re.compile(
    r"/tax-images/|/cheonmyeongdang/tax-images|kunst-studio\.github\.io|/api/(?!connect$)",
    re.IGNORECASE,
)


def discover_targets():
    """departments 하위 .html/.js/.md grep으로 vercel/ghpages URL 추출.
    이미 등록된 URL은 중복 제거. monitor_targets.json 에 누적.
    """
    found = set()
    if not DEPT_ROOT.exists():
        return []

    for path in DEPT_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".html", ".js", ".jsx", ".ts", ".tsx", ".md", ".py"}:
            continue
        # 빌드 산출물 / node_modules 제외
        s = str(path).lower().replace("\\", "/")
        if "/node_modules/" in s or "/.next/" in s or "/dist/" in s or "/build/" in s:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in URL_RE.finditer(text):
            url = m.group(0).rstrip(".,)\"'")
            if EXCLUDE.search(url):
                continue
            # 너무 길거나 query string은 베이스만 사용
            url = url.split("?")[0].split("#")[0]
            # 끝의 노이즈 정리
            while url and url[-1] in ".,;)]}":
                url = url[:-1]
            # 호스트만 있고 경로 없는 URL 제외 (시드에 명시된 것만 모니터)
            host_only = re.match(r"^https?://[^/]+/?$", url)
            if host_only:
                continue
            found.add(url)

    # 기존 누적 + 시드 합치기
    existing = []
    if TARGETS_PATH.exists():
        try:
            existing = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    by_url = {t["url"]: t for t in existing if isinstance(t, dict) and "url" in t}
    for s in SEED_TARGETS:
        by_url.setdefault(s["url"], dict(s))
    for url in sorted(found):
        if url in by_url:
            continue
        # 타입 분류
        if "vercel.app" in url:
            ttype = "vercel"
        elif "github.io" in url:
            ttype = "ghpages"
        else:
            ttype = "other"
        # 이름 자동 생성
        host = url.split("//", 1)[-1].split("/", 1)[0]
        name = host.replace(".vercel.app", "").replace("ghdejr11-beep.github.io", "ghpages")
        # 경로 일부 추가
        path_part = url.split(host, 1)[-1].strip("/")
        if path_part:
            name += ":" + path_part.split("/")[-1][:30]
        by_url[url] = {"name": name[:60], "url": url, "type": ttype, "auto": True}

    targets = list(by_url.values())
    TARGETS_PATH.write_text(
        json.dumps(targets, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return targets


# ──────────────────────────────────────────────────────────────
# 단일 체크
# ──────────────────────────────────────────────────────────────
def check_one(target: dict) -> dict:
    url = target["url"]
    name = target.get("name", url)
    started = time.monotonic()
    status_code = None
    err = None
    ok = False
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as r:
            status_code = r.status
            # 응답 본문 일부만 소비 (대용량 방지)
            r.read(2048)
            ok = 200 <= status_code < 500
    except urllib.error.HTTPError as e:
        status_code = e.code
        # 4xx 는 가용성 문제로 보지 않음 (auth 401/404 등)
        ok = 400 <= e.code < 500
        err = f"HTTP {e.code}"
    except (socket.timeout, urllib.error.URLError) as e:
        err = f"{type(e).__name__}: {e}"
        ok = False
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        ok = False
    elapsed_ms = int((time.monotonic() - started) * 1000)
    return {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "name": name,
        "url": url,
        "type": target.get("type", "other"),
        "ok": bool(ok),
        "status": status_code,
        "ms": elapsed_ms,
        "error": err,
    }


# ──────────────────────────────────────────────────────────────
# 상태 관리 + 알림
# ──────────────────────────────────────────────────────────────
def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(state: dict) -> None:
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _kst_now_str() -> str:
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%H:%M KST")


def update_state_and_alert(check: dict, state: dict) -> None:
    """state 갱신 + 3회 연속 실패 알림 / 복구 즉시 알림.

    state[url] = {
        "fail_streak": int,
        "down_since": iso str | None,
        "alerted_down": bool,
        "last_alert_ts": iso str | None,
        "last_ok": iso str | None,
    }
    """
    url = check["url"]
    name = check["name"]
    status = check.get("status")
    err = check.get("error")
    s = state.get(url, {
        "fail_streak": 0,
        "down_since": None,
        "alerted_down": False,
        "last_alert_ts": None,
        "last_ok": None,
    })
    now_iso = check["ts"]

    if check["ok"]:
        # 복구 처리
        if s.get("alerted_down") and s.get("down_since"):
            try:
                t0 = datetime.datetime.fromisoformat(s["down_since"].replace("Z", "+00:00"))
                t1 = datetime.datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
                downtime_min = max(1, int((t1 - t0).total_seconds() // 60))
            except Exception:
                downtime_min = 0
            send_telegram(
                f"✅ <b>{name}</b> 복구 (다운타임 {downtime_min}분, {_kst_now_str()})"
            )
        s["fail_streak"] = 0
        s["down_since"] = None
        s["alerted_down"] = False
        s["last_ok"] = now_iso
    else:
        s["fail_streak"] = int(s.get("fail_streak", 0)) + 1
        if s.get("down_since") is None:
            s["down_since"] = now_iso

        # 3회 연속 실패시 1차 알림. 이후 5분 1회 rate limit 보장
        # (cron이 5분마다라면 매 호출 1회씩 발생 → 5분 1회 자동 보장)
        # 폭주 방지: alerted_down=True 면 그 이후엔 재알림 X (복구 시점에만 알림)
        if s["fail_streak"] >= FAIL_THRESHOLD and not s.get("alerted_down"):
            tag = f"HTTP {status}" if status else (err or "다운")
            send_telegram(
                f"⚠️ <b>{name}</b> 다운 ({tag}, {_kst_now_str()})\n"
                f"<i>{url}</i>\n"
                f"연속 실패 {s['fail_streak']}회 / 응답 {check['ms']}ms"
            )
            s["alerted_down"] = True
            s["last_alert_ts"] = now_iso

    state[url] = s


# ──────────────────────────────────────────────────────────────
# 로그 append
# ──────────────────────────────────────────────────────────────
def append_log(check: dict) -> None:
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(check, ensure_ascii=False) + "\n")


# ──────────────────────────────────────────────────────────────
# 메인 실행
# ──────────────────────────────────────────────────────────────
def run_once(quiet: bool = False) -> list:
    targets = discover_targets()
    state = _load_state()
    results = []
    for t in targets:
        c = check_one(t)
        append_log(c)
        update_state_and_alert(c, state)
        results.append(c)
        if not quiet:
            mark = "OK" if c["ok"] else "FAIL"
            print(
                f"[{mark}] {c['name'][:30]:30s} {c.get('status')!s:>5}  {c['ms']:>5}ms  {c['url']}"
            )
    _save_state(state)
    return results


def print_status():
    state = _load_state()
    if not state:
        print("(상태 파일 없음 — 먼저 1회 실행)")
        return
    for url, s in state.items():
        flag = "DOWN" if s.get("alerted_down") else ("WARN" if s.get("fail_streak", 0) > 0 else "UP")
        print(f"[{flag}] streak={s.get('fail_streak',0)} since={s.get('down_since')} {url}")


# ──────────────────────────────────────────────────────────────
# 브리핑 v2 통합용 함수
# ──────────────────────────────────────────────────────────────
def build_uptime_section(window_hours: int = 24) -> str:
    """CEO 브리핑 v2 에서 호출. 어제(최근 N시간) 다운타임/평균 응답시간/가장 느린 서비스."""
    if not LOG_PATH.exists():
        return "🛡 <b>가동 상태 (24h)</b>\n  (uptime_log 없음 — 모니터 미가동)\n\n"

    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=window_hours)
    by_name = {}
    try:
        for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            try:
                ts = datetime.datetime.fromisoformat(rec["ts"].replace("Z", "+00:00"))
            except Exception:
                continue
            if ts < cutoff:
                continue
            name = rec.get("name", rec.get("url", "?"))
            d = by_name.setdefault(name, {"checks": 0, "fails": 0, "ms_sum": 0, "ms_max": 0})
            d["checks"] += 1
            if not rec.get("ok"):
                d["fails"] += 1
            ms = int(rec.get("ms") or 0)
            d["ms_sum"] += ms
            if ms > d["ms_max"]:
                d["ms_max"] = ms
    except Exception as e:
        return f"🛡 <b>가동 상태 (24h)</b>\n  (로그 파싱 오류: {str(e)[:80]})\n\n"

    if not by_name:
        return "🛡 <b>가동 상태 (24h)</b>\n  (최근 데이터 없음)\n\n"

    # 5분 1회 체크 가정 → 24h * 12 = 288회 / 서비스
    # 다운타임(분) = fails * 5
    total_down_min = sum(d["fails"] * 5 for d in by_name.values())
    avg_ms = sum(d["ms_sum"] for d in by_name.values()) / max(1, sum(d["checks"] for d in by_name.values()))

    msg = f"🛡 <b>가동 상태 (최근 {window_hours}h)</b>\n"
    msg += f"  • 총 다운타임 합계: {total_down_min}분\n"
    msg += f"  • 평균 응답시간: {int(avg_ms)}ms\n"

    # 다운/느림 TOP3
    by_fail = sorted(by_name.items(), key=lambda kv: -kv[1]["fails"])
    fail_top = [(n, d) for n, d in by_fail if d["fails"] > 0][:3]
    if fail_top:
        msg += "  • 장애 서비스:\n"
        for name, d in fail_top:
            uptime_pct = 100.0 * (d["checks"] - d["fails"]) / max(1, d["checks"])
            msg += f"    – {name}: {uptime_pct:.1f}% (실패 {d['fails']}/{d['checks']})\n"

    by_avg = sorted(
        by_name.items(),
        key=lambda kv: -(kv[1]["ms_sum"] / max(1, kv[1]["checks"])),
    )
    if by_avg:
        slowest_name, slowest = by_avg[0]
        s_avg = slowest["ms_sum"] / max(1, slowest["checks"])
        msg += f"  • 가장 느림: {slowest_name} 평균 {int(s_avg)}ms (피크 {slowest['ms_max']}ms)\n"

    msg += "\n"
    return msg


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]
    if "--discover" in args:
        ts = discover_targets()
        print(f"등록된 모니터 대상 {len(ts)}개:")
        for t in ts:
            print(f"  - {t['name']:30s}  {t['url']}")
        sys.exit(0)
    if "--status" in args:
        print_status()
        sys.exit(0)
    quiet = "--once" in args
    results = run_once(quiet=quiet)
    if not quiet:
        ok_n = sum(1 for r in results if r["ok"])
        print(f"\n총 {len(results)}개 중 정상 {ok_n}개 / 실패 {len(results)-ok_n}개")
