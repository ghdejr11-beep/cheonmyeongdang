"""medium_crosspost — 영문 SEO 블로그 → Medium 자동 cross-post (canonical 보존).

Medium API: 사용자 integration token 필요 → https://medium.com/me/settings → "Integration tokens"
.secrets에 MEDIUM_API_TOKEN= 추가 후 자동 가동.

기능:
- SEO 블로그 글 (cheonmyeongdang/blog/en/*.html) → markdown 추출 → Medium API 게시
- canonicalUrl=원본 → 중복 콘텐츠 페널티 X (rel=canonical 자동)
- tags 자동 매핑
- 이미 게시된 글 스킵 (medium_published.json 체크)
"""
import os, sys, json, re, datetime, urllib.request
from pathlib import Path
from html.parser import HTMLParser

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON_ROOT = Path(r"D:\cheonmyeongdang")
BLOG_DIR = CHEON_ROOT / "blog" / "en"
PUBLISHED = ROOT / "medium_published.json"
LOG = ROOT / "logs" / f"medium_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_secrets():
    env = {}
    p = CHEON_ROOT / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def me(token):
    req = urllib.request.Request(
        "https://api.medium.com/v1/me",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())["data"]


class Strip(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""; self.desc = ""; self.tags = []; self.body = []
        self.in_article = False
        self.in_h1 = False
        self._buf = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name") == "description":
            self.desc = attrs.get("content", "")
        if tag == "meta" and attrs.get("name") == "keywords":
            self.tags = [t.strip() for t in attrs.get("content", "").split(",") if t.strip()][:5]
        if tag == "article": self.in_article = True
        if tag == "h1": self.in_h1 = True
        if self.in_article and tag in ("h2","h3","p","ul","ol","li","strong","em","blockquote"):
            if tag == "h2": self.body.append("\n## ")
            elif tag == "h3": self.body.append("\n### ")
            elif tag == "li": self.body.append("\n- ")
            elif tag == "strong": self.body.append("**")
            elif tag == "em": self.body.append("*")
            elif tag == "p": self.body.append("\n\n")
    def handle_endtag(self, tag):
        if tag == "article": self.in_article = False
        if tag == "h1": self.in_h1 = False
        if self.in_article and tag in ("strong",): self.body.append("**")
        if self.in_article and tag in ("em",): self.body.append("*")
    def handle_data(self, data):
        if self.in_h1 and not self.title:
            self.title = data.strip()
        if self.in_article:
            self.body.append(data)


def parse_html(path: Path):
    raw = path.read_text(encoding="utf-8", errors="ignore")
    s = Strip()
    s.feed(raw)
    md_body = "".join(s.body).strip()
    return {"title": s.title, "description": s.desc, "tags": s.tags, "content": md_body}


def post_to_medium(token, user_id, post, canonical_url):
    body = {
        "title": post["title"],
        "contentFormat": "markdown",
        "content": f"# {post['title']}\n\n{post['content']}\n\n---\n\n*Originally published at [KunStudio]({canonical_url})*",
        "canonicalUrl": canonical_url,
        "tags": post.get("tags", [])[:5],
        "publishStatus": "public",
    }
    req = urllib.request.Request(
        f"https://api.medium.com/v1/users/{user_id}/posts",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["data"]


def load_published():
    if PUBLISHED.exists():
        return json.loads(PUBLISHED.read_text(encoding="utf-8"))
    return {"posted": []}


def main():
    env = load_secrets()
    token = env.get("MEDIUM_API_TOKEN")
    if not token:
        print("[INIT] MEDIUM_API_TOKEN missing in .secrets")
        print("       → https://medium.com/me/settings → 'Integration tokens' → 'Get integration token'")
        print("       → 발급 후 .secrets 에 추가: MEDIUM_API_TOKEN=...")
        return

    user = me(token)
    log(f"[Medium] user={user['username']} id={user['id']}")

    pub = load_published()
    posted = {x["html"] for x in pub.get("posted", [])}

    files = sorted(BLOG_DIR.glob("*.html"))
    candidates = [f for f in files if f.name not in posted]
    if not candidates:
        log("All blogs already cross-posted")
        return

    f = candidates[0]
    log(f"=== {f.name} ===")
    post = parse_html(f)
    if not post["title"]:
        log("  no title, skip")
        return

    canonical = f"https://cheonmyeongdang.vercel.app/blog/en/{f.name}"
    try:
        result = post_to_medium(token, user["id"], post, canonical)
        log(f"  posted → {result.get('url')}")
        pub["posted"].append({
            "html": f.name,
            "title": post["title"],
            "url": result.get("url"),
            "posted_at": datetime.datetime.now().isoformat(),
        })
        PUBLISHED.write_text(json.dumps(pub, ensure_ascii=False, indent=2), encoding="utf-8")
    except urllib.error.HTTPError as e:
        log(f"  HTTPError {e.code}: {e.read().decode('utf-8','ignore')[:200]}")


if __name__ == "__main__":
    main()
