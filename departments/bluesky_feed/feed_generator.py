"""Bluesky K-Culture Custom Feed Generator (AT Protocol).

Run an HTTP service that Bluesky calls to compute a feed of K-culture posts.
Bluesky 사용자가 'K-Culture' 피드를 구독하면 → kunstudio.bsky.social 도메인의
endpoint에 query 보냄 → 우리가 큐레이션한 post URI 리스트 반환.

Two-phase build:
  Phase 1 (this script): JSONL of K-culture posts collected via firehose, write to data/.
  Phase 2 (separate): Cloudflare Worker / Vercel function exposing /xrpc/app.bsky.feed.getFeedSkeleton.

Run on schtask hourly: collect new K-culture posts (Korean, k-pop, kdrama, korean food,
saju, hanbok keywords) from Bluesky firehose-lite endpoint.
"""
import os, sys, json, urllib.request, datetime, re
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
LOG = ROOT / "logs" / f"feed_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)

KEYWORDS = [
    "kpop", "k-pop", "kdrama", "k-drama", "kculture", "k-culture",
    "korean food", "kimchi", "bibimbap", "bts", "blackpink", "newjeans",
    "stray kids", "twice", "hanbok", "saju", "korean tradition",
    "seoul", "busan", "jeju", "korean beauty", "kbeauty", "k-beauty",
    "korean drama", "korean movie", "한국", "케이팝", "한복",
]

def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

_session_cache = {"jwt": None, "did": None}

def bluesky_login(handle, password):
    """Create authenticated session for AppView access."""
    if _session_cache["jwt"]:
        return _session_cache["jwt"]
    body = json.dumps({"identifier": handle, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": UA},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    _session_cache["jwt"] = data["accessJwt"]
    _session_cache["did"] = data["did"]
    log(f"[auth] logged in as {data['handle']}")
    return data["accessJwt"]


def search_bluesky(keyword, jwt, limit=25):
    """Authenticated AppView search — public endpoint returns 403 since 2025."""
    url = f"https://bsky.social/xrpc/app.bsky.feed.searchPosts?q={urllib.parse.quote(keyword)}&limit={limit}&sort=latest"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "application/json", "Authorization": f"Bearer {jwt}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        return data.get("posts", [])
    except Exception as e:
        log(f"[ERR] {keyword}: {e}")
        return []


def load_secrets():
    env = {}
    p = Path(r"D:\cheonmyeongdang\.secrets")
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def collect():
    import urllib.parse  # noqa
    secrets = load_secrets()
    handle = secrets.get("BLUESKY_HANDLE")
    pw = secrets.get("BLUESKY_APP_PASSWORD")
    if not handle or not pw:
        log("[ERR] BLUESKY_HANDLE/APP_PASSWORD missing in .secrets")
        return []
    jwt = bluesky_login(handle, pw)

    today_file = DATA / f"posts_{datetime.date.today().isoformat()}.jsonl"
    seen = set()
    if today_file.exists():
        for line in today_file.read_text(encoding="utf-8").splitlines():
            try:
                seen.add(json.loads(line)["uri"])
            except:
                pass
    log(f"start: {len(seen)} already collected today")

    new_posts = []
    for kw in KEYWORDS:
        posts = search_bluesky(kw, jwt, limit=25)
        for p in posts:
            uri = p.get("uri")
            if not uri or uri in seen:
                continue
            seen.add(uri)
            new_posts.append({
                "uri": uri,
                "cid": p.get("cid"),
                "keyword": kw,
                "text": (p.get("record", {}).get("text", "") or "")[:200],
                "author": p.get("author", {}).get("handle"),
                "indexed_at": p.get("indexedAt"),
                "collected_at": datetime.datetime.now().isoformat(),
            })

    if new_posts:
        with today_file.open("a", encoding="utf-8") as f:
            for p in new_posts:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

    log(f"[OK] +{len(new_posts)} new K-culture posts. total today: {len(seen)}")
    return new_posts


def build_feed_skeleton():
    """Build the latest 100 posts JSON for /xrpc/app.bsky.feed.getFeedSkeleton response."""
    today_file = DATA / f"posts_{datetime.date.today().isoformat()}.jsonl"
    posts = []
    if today_file.exists():
        for line in today_file.read_text(encoding="utf-8").splitlines():
            try:
                posts.append(json.loads(line))
            except:
                pass

    # Sort by collected_at desc, keep top 100
    posts.sort(key=lambda p: p.get("collected_at", ""), reverse=True)
    skeleton = {
        "feed": [{"post": p["uri"]} for p in posts[:100]],
    }
    out = DATA / "skeleton.json"
    out.write_text(json.dumps(skeleton, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"[skeleton] {len(skeleton['feed'])} posts → {out}")
    return out


if __name__ == "__main__":
    import urllib.parse
    collect()
    build_feed_skeleton()
