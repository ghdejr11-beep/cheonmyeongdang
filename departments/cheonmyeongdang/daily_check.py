#!/usr/bin/env python3
"""
천명당 일일 건강 체크: index.html 구문 검증 + 꿈해몽 데이터 총량 체크.
결과: output/health_YYYY-MM-DD.json + 이상 시 Telegram 알림.
"""
import os, sys, re, json, datetime, urllib.request, urllib.parse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
DEPT = ROOT / "departments" / "cheonmyeongdang"
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


def check():
    idx = ROOT / "index.html"
    report = {"date": TODAY, "checks": {}}

    if not idx.exists():
        report["checks"]["index.html"] = {"status": "MISSING"}
    else:
        html = idx.read_text(encoding="utf-8", errors="replace")
        size = idx.stat().st_size
        # script 블록 균형 체크 (<script>...</script>)
        opens = html.count("<script")
        closes = html.count("</script>")
        # dream 관련 키워드 존재 (스키마: { name: '...' } 패턴)
        dream_kw = len(re.findall(r"name\s*:\s*['\"]", html))
        report["checks"]["index.html"] = {
            "status": "OK" if opens == closes and dream_kw > 100 else ("SCRIPT_IMBALANCE" if opens != closes else "DREAM_DATA_LOW"),
            "size_bytes": size,
            "script_open": opens,
            "script_close": closes,
            "dream_name_refs": dream_kw,
        }

    # www 동기화 체크
    www = ROOT / "www" / "index.html"
    android_assets = ROOT / "android" / "app" / "src" / "main" / "assets" / "public" / "index.html"
    if www.exists() and android_assets.exists():
        report["checks"]["www_sync"] = {
            "status": "OK" if www.stat().st_size == android_assets.stat().st_size else "DRIFT",
            "www_size": www.stat().st_size,
            "android_size": android_assets.stat().st_size,
        }

    # build.gradle 버전 체크
    gradle = ROOT / "android" / "app" / "build.gradle"
    if gradle.exists():
        t = gradle.read_text(encoding="utf-8")
        vc = re.search(r"versionCode\s+(\d+)", t)
        vn = re.search(r'versionName\s+"([^"]+)"', t)
        report["checks"]["gradle"] = {
            "versionCode": int(vc.group(1)) if vc else None,
            "versionName": vn.group(1) if vn else None,
        }

    # AdMob App ID 체크 (hexdrop과 공유 여부)
    manifest = ROOT / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
    if manifest.exists():
        m = re.search(r'android:value="(ca-app-pub-[^"]+)"', manifest.read_text(encoding="utf-8"))
        if m:
            val = m.group(1)
            report["checks"]["admob_app_id"] = {
                "value": val,
                "status": "OK_CHEONMYEONGDANG" if val.endswith("7399025784") else "SHARED_WITH_HEXDROP" if val.endswith("6389192878") else "UNKNOWN",
            }

    # 저장
    out_path = OUT / f"health_{TODAY}.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")

    # 로그 회전 (90일 이전 health_*.json 삭제)
    cutoff = (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
    for old in OUT.glob("health_*.json"):
        try:
            d = old.stem.replace("health_", "")
            if d < cutoff:
                old.unlink()
        except Exception:
            pass

    # 이상 감지 → 텔레그램
    alerts = []
    for k, v in report["checks"].items():
        if isinstance(v, dict) and v.get("status") not in ("OK", "OK_CHEONMYEONGDANG", None):
            alerts.append(f"⚠️ {k}: {v.get('status')}")
    if alerts:
        send_telegram(f"[천명당 건강 체크 {TODAY}]\n" + "\n".join(alerts))
        print("ALERT sent:", alerts)


if __name__ == "__main__":
    check()
