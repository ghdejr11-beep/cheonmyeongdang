#!/usr/bin/env python3
"""
travelmap 일일 체크: KORLENS 라이브 응답 + Supabase 핑.
결과: output/health_YYYY-MM-DD.json
"""
import os, sys, json, datetime, urllib.request, urllib.parse, urllib.error
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"D:\cheonmyeongdang")
DEPT = ROOT / "departments" / "travelmap"
OUT = DEPT / "output"
OUT.mkdir(exist_ok=True)

TODAY = datetime.date.today().isoformat()


def load_secrets():
    env = {}
    p = ROOT / ".secrets"
    if not p.exists(): return env
    for line in p.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def send_telegram(msg):
    e = load_secrets()
    token, chat = e.get("TELEGRAM_BOT_TOKEN"), e.get("TELEGRAM_CHAT_ID")
    if not token or not chat: return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat, "text": msg[:4000]}).encode()
    try:
        urllib.request.urlopen(url, data=data, timeout=10)
        return True
    except Exception:
        return False


def http_check(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TravelmapHealth/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"status": r.status, "ok": 200 <= r.status < 400}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "ok": False, "error": str(e)[:80]}
    except Exception as e:
        return {"status": None, "ok": False, "error": str(e)[:80]}


def check():
    report = {"date": TODAY, "checks": {}}

    # KORLENS 라이브
    report["checks"]["korlens_live"] = http_check("https://korlens.vercel.app/")

    # Supabase 헬스 (401은 응답함 = 정상, API 키 필요한 엔드포인트)
    sup_url = "https://yhvchyctcaxcrjesutdb.supabase.co/rest/v1/"
    sup = http_check(sup_url, timeout=8)
    if sup.get("status") in (401, 403):
        sup["ok"] = True
        sup["note"] = "responds with auth-required (alive)"
    report["checks"]["supabase"] = sup

    out_path = OUT / f"health_{TODAY}.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")

    alerts = []
    for k, v in report["checks"].items():
        if not v.get("ok"):
            alerts.append(f"⚠️ {k}: {v.get('status')} {v.get('error','')}")
    if alerts:
        send_telegram(f"[travelmap {TODAY}]\n" + "\n".join(alerts))
        print("ALERT:", alerts)


if __name__ == "__main__":
    check()
