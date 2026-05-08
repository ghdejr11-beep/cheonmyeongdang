"""FLASH507 promo — X (Twitter) 직접 push (OAuth 1.0a v2 endpoint)."""
import json, os, time, hmac, hashlib, base64, secrets, urllib.parse, urllib.request
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

CK = env.get("X_API_KEY", "")
CS = env.get("X_API_SECRET", "")
AT = env.get("X_ACCESS_TOKEN", "")
AS = env.get("X_ACCESS_SECRET", "")
if not all([CK, CS, AT, AS]):
    print("[SKIP] X credentials missing")
    raise SystemExit(0)

text = """🔥 24h FLASH SALE — 50% OFF on all 7 KunStudio digital products!

Code: FLASH507 (limit 20 each)

Korean Saju · Wisdom Planner · Notion 5-Pack · Wall Art · Tax Guide · AI Side Hustle Tracker

👉 https://ghdejr.gumroad.com/

#Saju #KoreanCulture #Notion #DigitalProduct"""

# OAuth 1.0a signing for POST /2/tweets
url = "https://api.twitter.com/2/tweets"
method = "POST"
oauth = {
    "oauth_consumer_key": CK,
    "oauth_nonce": secrets.token_hex(16),
    "oauth_signature_method": "HMAC-SHA1",
    "oauth_timestamp": str(int(time.time())),
    "oauth_token": AT,
    "oauth_version": "1.0",
}

# For JSON body POST, body is NOT included in signature base string per Twitter v2 docs
def percent_encode(s):
    return urllib.parse.quote(str(s), safe="-._~")

params = sorted(oauth.items())
param_string = "&".join(f"{percent_encode(k)}={percent_encode(v)}" for k, v in params)
base_string = "&".join([
    method,
    percent_encode(url),
    percent_encode(param_string),
])
signing_key = f"{percent_encode(CS)}&{percent_encode(AS)}"
signature = base64.b64encode(
    hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
).decode()
oauth["oauth_signature"] = signature

auth_header = "OAuth " + ", ".join(
    f'{percent_encode(k)}="{percent_encode(v)}"' for k, v in sorted(oauth.items())
)

body = json.dumps({"text": text}).encode("utf-8")
req = urllib.request.Request(
    url,
    data=body,
    headers={
        "Authorization": auth_header,
        "Content-Type": "application/json",
    },
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read().decode("utf-8"))
    tid = resp.get("data", {}).get("id")
    print(f"[OK] X posted")
    print(f"  tweet_id={tid}")
    if tid:
        print(f"  view: https://x.com/i/web/status/{tid}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode("utf-8", errors="replace")
    print(f"[HTTPError {e.code}] {err_body[:300]}")
except Exception as e:
    print(f"[ERR] {type(e).__name__}: {str(e)[:200]}")
