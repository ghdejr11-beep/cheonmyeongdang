#!/usr/bin/env python3
"""
seasonal_poster.py — 5월 시즌 콘텐츠 자동 송출 (종소세 / 어버이날 / KDP 가정의달)

채널: Bluesky / Discord / Mastodon / Telegram (multi_poster 재사용)
스케줄 (Windows Task Scheduler):
  - 매일 09:00  jongsose       (종소세 LP, 5/1~5/31)
  - 매일 18:00  eobonal        (어버이날 LP, 5/1~5/8) → 5/9부터 자동 비활성
  - 매일 21:00  kdp_family     (KDP 4종, 5/1~5/31)

URL 추적:
  ?utm_source={channel}&utm_medium=organic&utm_campaign={campaign_tag}

Idempotency:
  state file `seasonal_state.json` 에 사용 메시지 인덱스 기록 → 회전, 같은 날 동일 메시지 X.

사용:
  python seasonal_poster.py jongsose                # 본 송출
  python seasonal_poster.py eobonal --dry-run       # 미리보기
  python seasonal_poster.py kdp_family --telegram-only   # 텔레그램만 송출 (검증)
"""
from __future__ import annotations
import os
import sys
import json
import random
import datetime
import urllib.parse
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
SRC = ROOT / "departments" / "media" / "src"
LOG_DIR = ROOT / "departments" / "media" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "seasonal_poster.log"
MSG_FILE = SRC / "seasonal_messages.json"
STATE_FILE = SRC / "seasonal_state.json"

sys.path.insert(0, str(SRC))


def log(msg: str) -> None:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_secrets() -> dict:
    p = ROOT / ".secrets"
    env: dict = {}
    if not p.exists():
        return env
    for line in p.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def load_messages() -> dict:
    return json.loads(MSG_FILE.read_text(encoding="utf-8"))


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def utm_url(base: str, channel: str, campaign_tag: str) -> str:
    sep = "&" if "?" in base else "?"
    qs = urllib.parse.urlencode({
        "utm_source": channel,
        "utm_medium": "organic",
        "utm_campaign": campaign_tag,
    })
    return f"{base}{sep}{qs}"


def _redact_phone(text: str) -> str:
    """SNS/Telegram 자동 송출 전 사용자 전화번호 마스킹."""
    import re
    if not text:
        return text
    text = re.sub(r'070[\s\-\.]?8018[\s\-\.]?7832', '070-****-****', text)
    text = re.sub(r'010[\s\-\.]?4244[\s\-\.]?6992', '010-****-****', text)
    return text


def telegram_notify(text: str, env: dict | None = None) -> tuple[bool, str]:
    env = env or load_secrets()
    tok = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = env.get("TELEGRAM_CHAT_ID", "").strip()
    if not tok or not chat:
        return False, "no TELEGRAM_BOT_TOKEN/CHAT_ID"
    text = _redact_phone(text)
    url = f"https://api.telegram.org/bot{tok}/sendMessage"
    body = urllib.parse.urlencode({
        "chat_id": chat,
        "text": text[:4000],
        "disable_web_page_preview": "false",
    }).encode()
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return (r.status == 200), r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def is_active(camp: dict) -> bool:
    today = datetime.date.today()
    end = datetime.datetime.strptime(camp["active_until"], "%Y-%m-%d").date()
    return today <= end


def pick_message(camp_key: str, msgs: list[str], state: dict) -> tuple[int, str]:
    """idempotent: 사용 인덱스 추적, 모두 사용 시 리셋."""
    used_root = state.setdefault("used", {})
    used = used_root.setdefault(camp_key, [])
    avail = [i for i in range(len(msgs)) if i not in used]
    if not avail:
        used.clear()
        avail = list(range(len(msgs)))
    pick = random.choice(avail)
    used.append(pick)
    return pick, msgs[pick]


def render_for_channel(template: str, url: str, hashtags: str, channel: str) -> str:
    """채널별 글자수 한도 적용."""
    text = template.replace("{URL}", url)
    limit = {
        "bluesky": 290,
        "mastodon": 480,
        "discord": 1800,
        "telegram": 3800,
    }.get(channel, 500)
    if hashtags and len(text) + len(hashtags) + 2 <= limit:
        text = f"{text}\n\n{hashtags}"
    return text[:limit]


def send_one(camp_key: str, camp: dict, dry_run: bool, telegram_only: bool,
             state: dict, env: dict) -> dict:
    if not is_active(camp):
        log(f"[{camp_key}] inactive (active_until={camp['active_until']}) — skip")
        return {"status": "inactive"}

    msgs = camp.get("messages") or []
    if not msgs:
        log(f"[{camp_key}] no messages")
        return {"status": "no_messages"}

    pick_idx, template = pick_message(camp_key, msgs, state)
    log(f"[{camp_key}] pick #{pick_idx}: {template[:80]}…")

    base_url = camp["url_base"]
    campaign_tag = camp["campaign_tag"]
    hashtags = camp.get("hashtags", "")

    results = {"pick_idx": pick_idx, "template": template[:200]}

    # 텔레그램 (가장 안전)
    tg_url = utm_url(base_url, "telegram", campaign_tag)
    tg_text = render_for_channel(template, tg_url, hashtags, "telegram")
    if dry_run:
        log(f"[dry][telegram] {tg_text[:120]}…")
        results["telegram"] = "dry"
    else:
        ok, info = telegram_notify(tg_text, env)
        results["telegram"] = bool(ok)
        log(f"[telegram] {'OK' if ok else 'FAIL: ' + str(info)[:200]}")

    if telegram_only:
        return results

    # 나머지 직접 채널
    try:
        import multi_poster as mp  # type: ignore
    except ImportError:
        log("[ERR] multi_poster import 실패 — bluesky/discord/mastodon skip")
        return results

    for name, fn in [
        ("bluesky", lambda t: mp.post_bluesky(t, env)),
        ("discord", lambda t: mp.post_discord(t, env)),
        ("mastodon", lambda t: mp.post_mastodon(t, env)),
    ]:
        ch_url = utm_url(base_url, name, campaign_tag)
        text = render_for_channel(template, ch_url, hashtags, name)
        if dry_run:
            log(f"[dry][{name}] {text[:120]}…")
            results[name] = "dry"
            continue
        try:
            ok, _ = fn(text)
            results[name] = bool(ok)
            log(f"[{name}] {'OK' if ok else 'FAIL'}")
        except Exception as e:
            results[name] = False
            log(f"[{name}] ERR {type(e).__name__}: {e}")

    return results


def cmd_run(camp_key: str, dry_run: bool = False, telegram_only: bool = False) -> dict:
    cfg = load_messages()
    state = load_state()
    env = load_secrets()

    camps = cfg["campaigns"]
    if camp_key not in camps:
        log(f"[ERR] unknown campaign: {camp_key} (available: {list(camps)})")
        return {"error": f"unknown campaign: {camp_key}"}

    log(f"=== seasonal_poster run camp={camp_key} dry={dry_run} tg_only={telegram_only} ===")
    res = send_one(camp_key, camps[camp_key], dry_run, telegram_only, state, env)
    state.setdefault("history", []).append({
        "ts": datetime.datetime.now().isoformat(),
        "camp": camp_key,
        "dry": dry_run,
        "telegram_only": telegram_only,
        "results": res,
    })
    save_state(state)

    # 송출 후 알림 텔레그램 (감독용) — 본 송출만
    if not dry_run and not telegram_only and res.get("status") not in ("inactive", "no_messages"):
        ok_count = sum(1 for k, v in res.items() if v is True)
        summary = (
            f"[seasonal/{camp_key}] 발송 완료\n"
            f"성공 {ok_count}개 채널 — {json.dumps({k: v for k, v in res.items() if k not in ('template',)}, ensure_ascii=False)}"
        )
        # 감독 알림은 chat 직접
        # (이미 본문이 텔레그램으로 갔으니 굳이 두 번 안 보냄 — skip)
    return res


def cmd_dry_all() -> dict:
    """모든 캠페인에 대한 dry-run 미리보기 (검증용)."""
    cfg = load_messages()
    state = load_state()  # 인덱스만 미리 사용 — copy 사용
    env = load_secrets()
    out = {}
    for camp_key, camp in cfg["campaigns"].items():
        # 임시 state로 dry-run (실제 state에 영향 X)
        tmp_state = {"used": {}}
        res = send_one(camp_key, camp, dry_run=True, telegram_only=False,
                       state=tmp_state, env=env)
        out[camp_key] = res
    return out


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: seasonal_poster.py <jongsose|eobonal|kdp_family|--dry-all> [--dry-run] [--telegram-only]")
        sys.exit(2)
    if args[0] == "--dry-all":
        out = cmd_dry_all()
        report_path = Path(r"D:\reports") / "sns_seasonal_dryrun_2026_05_01.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[OK] dry-run report: {report_path}")
        return
    camp = args[0]
    dry = "--dry-run" in args
    tg_only = "--telegram-only" in args
    cmd_run(camp, dry_run=dry, telegram_only=tg_only)


if __name__ == "__main__":
    main()
