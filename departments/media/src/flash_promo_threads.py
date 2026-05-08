"""FLASH507 promo — Threads (Meta Graph API)."""
import os, json, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SECRETS = ROOT / ".secrets"
env = {}
if SECRETS.exists():
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

token = env.get("THREADS_ACCESS_TOKEN", "")
if not token:
    print("[SKIP] THREADS token missing")
    raise SystemExit(0)

text = """🔥 24h FLASH SALE — 50% OFF on all 7 KunStudio digital products!

Code: FLASH507 (limit 20 each)

Korean Saju · Wisdom Planner · Notion 5-Pack · Wall Art · Tax Guide · AI Side Hustle Tracker

👉 https://ghdejr.gumroad.com/

#KoreanCulture #DigitalProduct #Notion #Saju #Productivity"""

# 1. Get user_id (me)
me_url = f"https://graph.threads.net/v1.0/me?fields=id,username&access_token={token}"
try:
    with urllib.request.urlopen(me_url, timeout=15) as r:
        me = json.loads(r.read().decode("utf-8"))
    user_id = me.get("id")
    username = me.get("username")
    print(f"[me] id={user_id} username={username}")
except Exception as e:
    print(f"[me ERR] {e}")
    raise SystemExit(1)

# 2. Create container
create_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
data = urllib.parse.urlencode({
    "media_type": "TEXT",
    "text": text,
    "access_token": token,
}).encode("utf-8")
try:
    req = urllib.request.Request(create_url, data=data)
    with urllib.request.urlopen(req, timeout=15) as r:
        c = json.loads(r.read().decode("utf-8"))
    container_id = c.get("id")
    print(f"[container] id={container_id}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    print(f"[container HTTPError {e.code}] {body[:300]}")
    raise SystemExit(1)
except Exception as e:
    print(f"[container ERR] {e}")
    raise SystemExit(1)

# 3. Publish container
publish_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
publish_data = urllib.parse.urlencode({
    "creation_id": container_id,
    "access_token": token,
}).encode("utf-8")
try:
    req = urllib.request.Request(publish_url, data=publish_data)
    with urllib.request.urlopen(req, timeout=15) as r:
        p = json.loads(r.read().decode("utf-8"))
    post_id = p.get("id")
    print(f"[OK] Threads posted")
    print(f"  post_id={post_id}")
    if username and post_id:
        print(f"  view: https://www.threads.net/@{username}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    print(f"[publish HTTPError {e.code}] {body[:300]}")
except Exception as e:
    print(f"[publish ERR] {e}")
