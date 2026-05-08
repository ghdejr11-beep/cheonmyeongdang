#!/usr/bin/env python3
"""
IG + Threads 장기 액세스 토큰 자동 갱신.

Meta 토큰은 60일 만료. 갱신 엔드포인트:
- Instagram Graph (threads.net/instagram.com 기반):
    GET https://graph.instagram.com/refresh_access_token
      ?grant_type=ig_refresh_token
      &access_token={old_token}
- Threads:
    GET https://graph.threads.net/refresh_access_token
      ?grant_type=th_refresh_token
      &access_token={old_token}

반환 예: {"access_token": "...", "token_type": "bearer", "expires_in": 5183944}

매주 1회 실행하면 만료 걱정 없음. .secrets 파일 인라인 수정.
Windows Task: refresh_meta_tokens.bat 매주 월요일 08:00

사용:
    python refresh_meta_tokens.py         # 양쪽 다 갱신
    python refresh_meta_tokens.py --dry   # 갱신만 확인, 파일 수정 X
"""
import os
import sys
import json
import argparse
import urllib.request
import urllib.error
import urllib.parse
import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SECRETS = Path(r"D:\cheonmyeongdang\.secrets")
LOG = Path(__file__).resolve().parent / "logs" / "refresh_meta_tokens.log"
LOG.parent.mkdir(parents=True, exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_secrets():
    env = {}
    lines = SECRETS.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env, lines


def save_secret(lines, key, new_value):
    """기존 라인 중 key= 로 시작하는 것을 new_value로 교체."""
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={new_value}"
            break
    else:
        lines.append(f"{key}={new_value}")
    SECRETS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def refresh(base_url, grant_type, old_token, label):
    params = urllib.parse.urlencode({
        "grant_type": grant_type,
        "access_token": old_token,
    })
    url = f"{base_url}/refresh_access_token?{params}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "KunStudio-TokenRefresh/1.0 (+https://kunstudio.bsky.social)",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
        new_token = data.get("access_token")
        expires = data.get("expires_in", 0)
        if not new_token:
            log(f"[{label}] FAIL: no access_token in response. raw={data}")
            return None
        days = expires // 86400
        log(f"[{label}] OK: new token (length {len(new_token)}), expires in {expires}s ({days}d)")
        return new_token
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        log(f"[{label}] HTTP {e.code}: {body[:200]}")
        return None
    except Exception as e:
        log(f"[{label}] ERROR: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="갱신만 확인, 파일 수정 X")
    args = parser.parse_args()

    log(f"=== Meta 토큰 갱신 시작 (dry={args.dry}) ===")
    env, lines = load_secrets()

    ig_old = env.get("IG_ACCESS_TOKEN", "").strip()
    th_old = env.get("THREADS_ACCESS_TOKEN", "").strip()

    results = {}

    if ig_old:
        new = refresh("https://graph.instagram.com", "ig_refresh_token", ig_old, "Instagram")
        results["instagram"] = bool(new)
        if new and not args.dry:
            save_secret(lines, "IG_ACCESS_TOKEN", new)
            env, lines = load_secrets()
            log("[Instagram] .secrets 업데이트됨")

    if th_old:
        new = refresh("https://graph.threads.net", "th_refresh_token", th_old, "Threads")
        results["threads"] = bool(new)
        if new and not args.dry:
            save_secret(lines, "THREADS_ACCESS_TOKEN", new)
            log("[Threads] .secrets 업데이트됨")

    log(f"=== 완료: {results} ===")
    return results


if __name__ == "__main__":
    main()
