#!/usr/bin/env python3
"""
may_promo_runner.py — 5월 KunStudio 3사이트(천명당/세금N혜택/KORLENS) 회전 발송기.

스케줄:
  - 5/1 ~ 5/31, 매일 09:00 + 19:00 (Windows Task Scheduler)
  - 7채널 (Bluesky/Discord/Mastodon/X/Threads/Instagram/Telegram)
  - 사이트 라운드로빈: (월일 * 2 + slot) % 3 → cheonmyeongdang/tax_n_benefit/korlens

URL 추적:
  ?utm_source={channel}&utm_medium=social&utm_campaign=may2026&utm_content={site_key}

사용:
  python may_promo_runner.py                     # 현재 시각 슬롯 자동 발송
  python may_promo_runner.py --dry-run           # 발송 X, 메시지만 출력
  python may_promo_runner.py --site cheonmyeongdang --slot 0  # 강제 지정
  python may_promo_runner.py --once-now          # 즉시 1회 (천명당 라이브 알림 모드)
  python may_promo_runner.py --launch-cheon      # 천명당 정식 오픈 단발 발송 (모든 채널)
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

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
SRC = ROOT / "departments" / "media" / "src"
LOG_DIR = ROOT / "departments" / "media" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "may_promo.log"
MSG_FILE = SRC / "promo_messages_may.json"
STATE_FILE = SRC / "may_promo_state.json"

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
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def telegram_notify(msg: str, env: dict | None = None) -> bool:
    env = env or load_secrets()
    tok = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = env.get("TELEGRAM_CHAT_ID", "").strip()
    if not tok or not chat:
        return False
    url = f"https://api.telegram.org/bot{tok}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat, "text": msg[:4000]}).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception as e:
        log(f"[tg] {e}")
        return False


def utm_url(base: str, channel: str, site_key: str, campaign: str = "may2026") -> str:
    sep = "&" if "?" in base else "?"
    qs = urllib.parse.urlencode({
        "utm_source": channel,
        "utm_medium": "social",
        "utm_campaign": campaign,
        "utm_content": site_key,
    })
    return f"{base}{sep}{qs}"


def pick_site(cfg: dict, slot: int | None = None, force_key: str | None = None) -> dict:
    sites = cfg["sites"]
    if force_key:
        for s in sites:
            if s["key"] == force_key:
                return s
    if slot is None:
        # 시각 기준 09:00 → 0, 19:00 → 1
        h = datetime.datetime.now().hour
        slot = 1 if h >= 14 else 0
    today = datetime.date.today()
    idx = (today.day * 2 + slot) % len(sites)
    return sites[idx]


def pick_message(cfg: dict, site_key: str, state: dict) -> str:
    msgs = cfg["messages"][site_key]
    used = state.setdefault("used", {}).setdefault(site_key, [])
    avail = [i for i in range(len(msgs)) if i not in used]
    if not avail:
        used.clear()
        avail = list(range(len(msgs)))
    pick = random.choice(avail)
    used.append(pick)
    return msgs[pick]


def render_for_channel(template: str, site: dict, channel: str) -> str:
    url = utm_url(site["url_base"], channel, site["key"])
    text = template.replace("{URL}", url)
    # Bluesky/X 짧게, Threads/Mastodon 중간, Discord 길게
    tag = site.get("hashtags", "")
    limit = {
        "x": 270,
        "bluesky": 290,
        "mastodon": 480,
        "threads": 490,
        "instagram": 2100,
        "discord": 1800,
        "telegram": 3800,
    }.get(channel, 500)
    if tag and len(text) + len(tag) + 2 <= limit:
        text = f"{text}\n\n{tag}"
    return text[:limit]


def send_one(site: dict, base_msg: str, env: dict, dry_run: bool = False) -> dict:
    """채널별로 텍스트 다르게 렌더해서 send_all_direct 우회 — 직접 채널 호출."""
    import multi_poster as mp

    results = {}
    channel_funcs = [
        ("bluesky", lambda t: mp.post_bluesky(t, env)),
        ("discord", lambda t: mp.post_discord(t, env)),
        ("mastodon", lambda t: mp.post_mastodon(t, env)),
        ("x", lambda t: mp.post_x(t, env)),
        ("threads", lambda t: mp.post_threads(t, env)),
    ]
    for name, fn in channel_funcs:
        text = render_for_channel(base_msg, site, name)
        if dry_run:
            log(f"[dry][{name}] {text[:100]}…")
            results[name] = "dry"
            continue
        try:
            ok, _ = fn(text)
            results[name] = bool(ok)
            log(f"[{name}] {'OK' if ok else 'FAIL'}")
        except Exception as e:
            results[name] = False
            log(f"[{name}] ERR {type(e).__name__}: {e}")

    # Instagram (이미지 필요 — 첫 슬라이드 또는 site 로고 없으면 skip)
    ig_text = render_for_channel(base_msg, site, "instagram")
    ig_image = _site_image(site)
    if dry_run:
        log(f"[dry][instagram] image={ig_image} text={ig_text[:80]}…")
        results["instagram"] = "dry"
    elif ig_image:
        try:
            ok, _ = mp.post_instagram(ig_text, image_url=ig_image, env=env)
            results["instagram"] = bool(ok)
            log(f"[instagram] {'OK' if ok else 'FAIL'}")
        except Exception as e:
            results["instagram"] = False
            log(f"[instagram] ERR {e}")
    else:
        results["instagram"] = "skip-no-image"

    # Telegram (광고 보고용)
    tg_text = render_for_channel(base_msg, site, "telegram")
    if dry_run:
        results["telegram"] = "dry"
    else:
        ok = telegram_notify(tg_text, env)
        results["telegram"] = bool(ok)
        log(f"[telegram] {'OK' if ok else 'FAIL'}")

    return results


def _site_image(site: dict) -> str | None:
    """사이트별 IG 첫 이미지 — 있으면 로컬, 없으면 None (IG skip)."""
    candidates = {
        "cheonmyeongdang": [
            ROOT / "feature_graphic_1024x500.png",
            ROOT / "app_icon_512.png",
        ],
        "tax_n_benefit": [
            Path(r"D:\kunstudio-promo\tax_assets\shorts1_price_cards") / "slide_1.png",
            Path(r"D:\kunstudio-promo\tax_cards") / "shorts1_price_cards.zip",  # zip은 IG 비호환 — skip
        ],
        "korlens": [
            Path(r"C:\Users\hdh02\Desktop\KORLENS\public\og.png"),
            Path(r"C:\Users\hdh02\Desktop\KORLENS\public\hero.png"),
        ],
    }
    for c in candidates.get(site["key"], []):
        if str(c).endswith(".png") or str(c).endswith(".jpg"):
            if c.exists():
                return str(c)
    return None


def cmd_run(slot: int | None = None, force_site: str | None = None, dry_run: bool = False):
    cfg = load_messages()
    state = load_state()
    env = load_secrets()
    site = pick_site(cfg, slot=slot, force_key=force_site)
    msg = pick_message(cfg, site["key"], state)
    log(f"=== run site={site['key']} slot={slot} dry={dry_run} ===")
    log(f"[msg] {msg}")
    results = send_one(site, msg, env, dry_run=dry_run)
    state.setdefault("history", []).append({
        "ts": datetime.datetime.now().isoformat(),
        "site": site["key"],
        "slot": slot,
        "msg": msg[:200],
        "results": results,
    })
    save_state(state)
    if not dry_run:
        ok_count = sum(1 for v in results.values() if v is True)
        telegram_notify(
            f"[5월 마케팅 발송 완료]\n사이트: {site['name']}\n성공: {ok_count}/7 채널\n결과: {json.dumps(results, ensure_ascii=False)}"[:3500],
            env,
        )
    return results


def cmd_launch_cheon(dry_run: bool = False):
    """천명당 정식 오픈 단발 발송."""
    cfg = load_messages()
    env = load_secrets()
    site = next(s for s in cfg["sites"] if s["key"] == "cheonmyeongdang")
    msg = "천명당 정식 오픈! 무료 사주·관상·손금·꿈해몽·타로 한 곳에서 — 회원가입 없이 바로 사용. {URL}"
    log("=== LAUNCH 천명당 정식 오픈 ===")
    results = send_one(site, msg, env, dry_run=dry_run)
    if not dry_run:
        ok = sum(1 for v in results.values() if v is True)
        telegram_notify(
            f"[천명당 정식 라이브 발송 완료]\n성공: {ok}/7 채널\n결과: {json.dumps(results, ensure_ascii=False)}"[:3500],
            env,
        )
    return results


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    if "--launch-cheon" in args:
        cmd_launch_cheon(dry_run=dry)
        return
    slot = None
    if "--slot" in args:
        slot = int(args[args.index("--slot") + 1])
    site = None
    if "--site" in args:
        site = args[args.index("--site") + 1]
    cmd_run(slot=slot, force_site=site, dry_run=dry)


if __name__ == "__main__":
    main()
