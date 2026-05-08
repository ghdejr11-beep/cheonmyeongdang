"""FLASH507 promo — Bluesky 직접 push (kunstudio.bsky.social)."""
import json, os, urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / ".secrets"
env = {}
if SECRETS.exists():
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

handle = env.get("BLUESKY_HANDLE", "")
password = env.get("BLUESKY_APP_PASSWORD", "")
if not handle or not password:
    print("[SKIP] BLUESKY creds missing")
    raise SystemExit(0)

text = """🔥 24h FLASH SALE — 50% OFF on all 7 KunStudio digital products! Code: FLASH507 (limit 20 each)

Korean Saju · Wisdom Planner · Notion 5-Pack · Wall Art · Tax Guide · AI Side Hustle Tracker

ghdejr.gumroad.com"""

# 1. Login
auth_data = json.dumps({"identifier": handle, "password": password}).encode("utf-8")
auth_req = urllib.request.Request(
    "https://bsky.social/xrpc/com.atproto.server.createSession",
    data=auth_data,
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(auth_req, timeout=15) as r:
        auth_body = json.loads(r.read().decode("utf-8"))
    jwt = auth_body.get("accessJwt")
    did = auth_body.get("did")
    if not jwt:
        print("[ERR] No JWT received")
        raise SystemExit(1)
except Exception as e:
    print(f"[Login ERR] {type(e).__name__}: {e}")
    raise SystemExit(1)

# 2. Detect URL facets (clickable hyperlink for ghdejr.gumroad.com)
import re
url_match = re.search(r"ghdejr\.gumroad\.com", text)
facets = []
if url_match:
    byte_start = len(text[:url_match.start()].encode("utf-8"))
    byte_end = len(text[:url_match.end()].encode("utf-8"))
    facets.append({
        "index": {"byteStart": byte_start, "byteEnd": byte_end},
        "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "https://ghdejr.gumroad.com/"}],
    })

# 3. Create post
post_data = json.dumps({
    "repo": did,
    "collection": "app.bsky.feed.post",
    "record": {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "langs": ["en"],
        "facets": facets,
    }
}).encode("utf-8")
post_req = urllib.request.Request(
    "https://bsky.social/xrpc/com.atproto.repo.createRecord",
    data=post_data,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {jwt}"},
)
try:
    with urllib.request.urlopen(post_req, timeout=15) as r:
        post_body = json.loads(r.read().decode("utf-8"))
    uri = post_body.get("uri", "")
    cid = post_body.get("cid", "")
    print(f"[OK] Bluesky posted")
    print(f"  uri={uri}")
    print(f"  cid={cid[:30]}...")
    # User-friendly URL
    rkey = uri.split("/")[-1] if uri else ""
    if rkey:
        print(f"  view: https://bsky.app/profile/{handle}/post/{rkey}")
except Exception as e:
    print(f"[Post ERR] {type(e).__name__}: {e}")
