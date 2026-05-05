"""hashnode_crosspost — 영문 SEO 블로그 → Hashnode 자동 cross-post (canonical 보존).

Hashnode GraphQL API: 무료, 자체 publication 필요.
사용자 1회 작업:
  1) https://hashnode.com 가입 + publication 만들기 (free)
  2) https://hashnode.com/settings/developer → "Generate New Token"
  3) .secrets 에 HASHNODE_API_TOKEN=... 추가
  4) .secrets 에 HASHNODE_PUBLICATION_ID=... 추가 (publication 설정에서 확인)

기능: SEO 글 1편 → Hashnode publication 게시 (canonical=cheonmyeongdang URL).
"""
import os, sys, json, datetime, urllib.request
from pathlib import Path
from html.parser import HTMLParser

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON_ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
BLOG_DIR = CHEON_ROOT / "blog" / "en"
PUBLISHED = ROOT / "hashnode_published.json"
LOG = ROOT / "logs" / f"hashnode_{datetime.date.today()}.log"
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


class Strip(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""; self.desc = ""; self.tags = []; self.body = []
        self.in_article = False; self.in_h1 = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name") == "description":
            self.desc = attrs.get("content", "")
        if tag == "meta" and attrs.get("name") == "keywords":
            self.tags = [t.strip() for t in attrs.get("content", "").split(",") if t.strip()][:5]
        if tag == "article": self.in_article = True
        if tag == "h1": self.in_h1 = True
        if self.in_article:
            if tag == "h2": self.body.append("\n\n## ")
            elif tag == "h3": self.body.append("\n\n### ")
            elif tag == "li": self.body.append("\n- ")
            elif tag == "strong": self.body.append("**")
            elif tag == "em": self.body.append("*")
            elif tag == "p": self.body.append("\n\n")
    def handle_endtag(self, tag):
        if tag == "article": self.in_article = False
        if tag == "h1": self.in_h1 = False
        if self.in_article and tag == "strong": self.body.append("**")
        if self.in_article and tag == "em": self.body.append("*")
    def handle_data(self, data):
        if self.in_h1 and not self.title:
            self.title = data.strip()
        if self.in_article:
            self.body.append(data)


def parse_html(path: Path):
    s = Strip()
    s.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return {"title": s.title, "description": s.desc, "tags": s.tags, "content": "".join(s.body).strip()}


def hashnode_publish(token, pub_id, post, canonical_url):
    """Hashnode GraphQL — publishPost mutation."""
    query = """
    mutation PublishPost($input: PublishPostInput!) {
        publishPost(input: $input) {
            post { id title url }
        }
    }"""
    variables = {
        "input": {
            "publicationId": pub_id,
            "title": post["title"],
            "contentMarkdown": post["content"],
            "tags": [{"slug": t.replace(" ", "-").lower()[:80], "name": t[:80]} for t in post.get("tags", [])[:5]],
            "originalArticleURL": canonical_url,
        }
    }
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        "https://gql.hashnode.com",
        data=body,
        headers={
            "Authorization": token,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def load_published():
    if PUBLISHED.exists():
        return json.loads(PUBLISHED.read_text(encoding="utf-8"))
    return {"posted": []}


def main():
    env = load_secrets()
    token = env.get("HASHNODE_API_TOKEN")
    pub_id = env.get("HASHNODE_PUBLICATION_ID")
    if not token or not pub_id:
        print("[INIT] HASHNODE_API_TOKEN or HASHNODE_PUBLICATION_ID missing in .secrets")
        print("       1) https://hashnode.com 가입 + publication 만들기 (free)")
        print("       2) https://hashnode.com/settings/developer → Generate New Token")
        print("       3) Publication settings → Publication ID 복사")
        print("       4) .secrets 에 HASHNODE_API_TOKEN=... + HASHNODE_PUBLICATION_ID=... 추가")
        return

    pub = load_published()
    posted = {x["html"] for x in pub.get("posted", [])}

    files = sorted(BLOG_DIR.glob("*.html"))
    candidates = [f for f in files if f.name not in posted]
    if not candidates:
        log("All blogs already cross-posted to Hashnode")
        return

    f = candidates[0]
    log(f"=== {f.name} ===")
    post = parse_html(f)
    if not post["title"]:
        log("  no title, skip")
        return

    canonical = f"https://cheonmyeongdang.vercel.app/blog/en/{f.name}"
    try:
        result = hashnode_publish(token, pub_id, post, canonical)
        if "errors" in result:
            log(f"  GraphQL errors: {result['errors']}")
            return
        post_data = result["data"]["publishPost"]["post"]
        log(f"  posted → {post_data['url']}")
        pub["posted"].append({
            "html": f.name,
            "title": post["title"],
            "url": post_data["url"],
            "posted_at": datetime.datetime.now().isoformat(),
        })
        PUBLISHED.write_text(json.dumps(pub, ensure_ascii=False, indent=2), encoding="utf-8")
    except urllib.error.HTTPError as e:
        log(f"  HTTPError {e.code}: {e.read().decode('utf-8','ignore')[:200]}")


if __name__ == "__main__":
    main()
