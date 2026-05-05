"""Beehiiv auto-publisher: read Hashnode RSS → push posts to Beehiiv via API.

Two modes:
  1. RSS import: paste Hashnode RSS URL into Beehiiv settings (manual one-time setup).
  2. API publish: when API key available, push each new SEO blog post directly.

After user signs up at beehiiv.com, they paste BEEHIIV_API_KEY + BEEHIIV_PUB_ID into .secrets.
Schtask: KunStudio_Beehiiv_Daily 09:00 — pushes new posts since last_published.json.
"""
import os, sys, json, urllib.request, datetime, re, html
from pathlib import Path
import xml.etree.ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "logs" / f"beehiiv_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)
STATE = ROOT / "data" / "last_published.json"
STATE.parent.mkdir(exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
HASHNODE_RSS = "https://kunstudio-kr.hashnode.dev/rss.xml"


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_secrets():
    env = {}
    p = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets")
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"published_links": []}


def save_state(s):
    STATE.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch_hashnode_rss():
    req = urllib.request.Request(HASHNODE_RSS, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        xml = r.read().decode("utf-8")
    root = ET.fromstring(xml)
    items = []
    for item in root.findall(".//item"):
        items.append({
            "title": (item.findtext("title") or "").strip(),
            "link": (item.findtext("link") or "").strip(),
            "description": (item.findtext("description") or "").strip(),
            "pubDate": (item.findtext("pubDate") or "").strip(),
        })
    return items


def beehiiv_create_post(api_key, pub_id, title, content_html, slug):
    """POST /publications/{pub_id}/posts (Beehiiv v2 API)."""
    url = f"https://api.beehiiv.com/v2/publications/{pub_id}/posts"
    body = json.dumps({
        "title": title,
        "subtitle": "",
        "content_html": content_html,
        "status": "draft",  # draft → user reviews → publishes manually
        "thumbnail": None,
        "slug": slug,
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": UA,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode("utf-8", errors="ignore")[:200]}


def main():
    secrets = load_secrets()
    api_key = secrets.get("BEEHIIV_API_KEY")
    pub_id = secrets.get("BEEHIIV_PUB_ID")
    if not api_key or not pub_id:
        log("[skip] BEEHIIV_API_KEY/BEEHIIV_PUB_ID missing — fall back to RSS import only")
        log(f"[guide] Beehiiv signup: https://www.beehiiv.com/sign-up — then paste API key + pub ID into .secrets")
        log(f"[guide] OR easier: Beehiiv settings → Import → RSS → paste {HASHNODE_RSS}")
        return

    state = load_state()
    seen = set(state["published_links"])

    items = fetch_hashnode_rss()
    log(f"hashnode rss: {len(items)} items")

    pushed = 0
    for it in items:
        if it["link"] in seen:
            continue
        slug = re.sub(r"[^a-z0-9-]", "", it["link"].rsplit("/", 1)[-1].lower()) or f"post-{datetime.date.today()}"
        result = beehiiv_create_post(api_key, pub_id, it["title"], it["description"], slug)
        if "error" in result:
            log(f"[ERR] {it['title']}: {result}")
            continue
        seen.add(it["link"])
        pushed += 1
        log(f"[OK] pushed: {it['title']} → beehiiv draft")

    state["published_links"] = list(seen)
    save_state(state)
    log(f"[done] {pushed} new posts → beehiiv drafts. total seen: {len(seen)}")


if __name__ == "__main__":
    main()
