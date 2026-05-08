# -*- coding: utf-8 -*-
"""Fetch latest photo from Telegram and download to local."""
import os, sys, json, urllib.request, urllib.parse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# Read secrets
secrets = {}
for line in open(r"D:\cheonmyeongdang\.secrets", encoding="utf-8"):
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.strip().split("=", 1)
        secrets[k] = v.strip().strip('"').strip("'")

TOKEN = secrets["TELEGRAM_BOT_TOKEN"]
CHAT = secrets["TELEGRAM_CHAT_ID"]
OFFSET_FILE = r"D:\cheonmyeongdang\departments\ceo-briefing\bot_offset.txt"


def api(method, params=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


# Try getUpdates with offset=0 and timeout=0 (short polling, won't conflict)
# Strategy: use a specific offset just before the latest, scan for photo
try:
    # First, check current offset from the existing bot
    if os.path.exists(OFFSET_FILE):
        last_offset = int(open(OFFSET_FILE).read().strip() or 0)
        print(f"existing bot offset: {last_offset}")
    else:
        last_offset = 0

    # Try getUpdates with offset slightly before to catch latest
    # Use offset=last_offset-30 to scan recent (existing bot may have processed text)
    # Use negative offset to get last 100 updates (Telegram quirk)
    resp = api("getUpdates", {"offset": -100, "timeout": 0, "limit": 100})
except urllib.error.HTTPError as e:
    print(f"[ERR getUpdates] {e.code}: {e.read().decode()[:200]}")
    sys.exit(1)

if not resp.get("ok"):
    print(f"[ERR] {resp}")
    sys.exit(1)

updates = resp.get("result", [])
print(f"got {len(updates)} updates")

# Find photo messages, latest first
photo_updates = []
for u in updates:
    msg = u.get("message") or u.get("edited_message") or u.get("channel_post")
    if not msg:
        continue
    if msg.get("photo") and str((msg.get("chat") or {}).get("id")) == str(CHAT):
        photo_updates.append((u.get("update_id", 0), msg))

if not photo_updates:
    print("[!] no photo found in last 30 updates")
    sys.exit(2)

# Use latest photo
photo_updates.sort(key=lambda x: x[0], reverse=True)
update_id, msg = photo_updates[0]
photos = msg["photo"]
# Pick highest resolution (largest file_size)
photos.sort(key=lambda p: p.get("file_size", 0), reverse=True)
file_id = photos[0]["file_id"]
caption = msg.get("caption", "")
print(f"latest photo update_id={update_id} file_id={file_id[:30]}... caption='{caption}'")

# getFile to get file_path
file_info = api("getFile", {"file_id": file_id})
if not file_info.get("ok"):
    print(f"[ERR getFile] {file_info}")
    sys.exit(1)
file_path = file_info["result"]["file_path"]
print(f"file_path: {file_path}")

# Download
url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
ext = file_path.split(".")[-1] if "." in file_path else "jpg"
out_path = Path(r"C:\Users\hdh02\Desktop") / f"linkedin_profile_pic.{ext}"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=60) as r:
    img_bytes = r.read()
out_path.write_bytes(img_bytes)
print(f"[OK] downloaded {len(img_bytes)//1024}KB → {out_path}")
print(f"OUT={out_path}")
