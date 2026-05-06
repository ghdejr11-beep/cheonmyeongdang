"""devto_crosspost — KORLENS 영문 SEO blog → dev.to 자동 cross-post.

Forem (dev.to) API V1: https://developers.forem.com/api/v1
- canonical_url 필드로 SEO 보존 (KORLENS 원글이 검색 엔진 정본으로 인식됨)
- API key 발급: dev.to/settings/extensions → 'DEV API Keys' → Generate

사용자 1회 작업 (검증 2026-05-06):
  1) https://dev.to/enter 가입 (free, GitHub/Twitter/Email 가능)
  2) https://dev.to/settings/extensions → 'DEV API Keys' → 'Generate API Key'
  3) C:\\Users\\hdh02\\Desktop\\cheonmyeongdang\\.secrets 에 추가:
       DEVTO_API_KEY=<생성된 키>
  4) 매일 schtask가 자동으로 1편씩 cross-post

KORLENS blog 데이터 출처:
- Source: C:\\Users\\hdh02\\Desktop\\korlens\\lib\\blog-posts.ts (TypeScript)
- HTML 변환: 배포된 https://korlens.app/blog/<slug> 페이지 fetch (canonical 보존)
- Markdown body: TS source 파싱하여 sections를 마크다운으로 변환
"""
import os, sys, json, re, datetime, urllib.request, urllib.error
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON_ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
BLOG_TS = Path(r"C:\Users\hdh02\Desktop\korlens\lib\blog-posts.ts")
PUBLISHED = ROOT / "devto_published.json"
LOG = ROOT / "logs" / f"devto_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True, parents=True)

KORLENS_BASE = "https://korlens.app/blog"


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


def parse_blog_posts():
    """Parse blog-posts.ts to extract per-post slug/title/description/tags/sections."""
    text = BLOG_TS.read_text(encoding="utf-8")
    # Match each post object — robust enough for the existing structure
    # Each post starts with `slug: "..."` and ends with the next `slug:` or array close.
    posts = []
    # Split into per-post chunks at the boundary `},\n  {` between objects
    # Simpler: regex extract per slug
    pattern = re.compile(
        r'\{\s*slug:\s*"([^"]+)",.*?\}\s*(?=,\s*\{|\s*\];)',
        re.DOTALL,
    )
    for m in pattern.finditer(text):
        chunk = m.group(0)
        slug = m.group(1)
        title_m = re.search(r'title:\s*"((?:[^"\\]|\\.)*)"', chunk)
        desc_m = re.search(r'description:\s*\n?\s*"((?:[^"\\]|\\.)*)"', chunk)
        tags_m = re.search(r'tags:\s*\[(.*?)\]', chunk, re.DOTALL)
        title = title_m.group(1).encode().decode("unicode_escape") if title_m else slug
        desc = desc_m.group(1).encode().decode("unicode_escape") if desc_m else ""
        tags = []
        if tags_m:
            tags = [t.strip().strip('"') for t in re.findall(r'"([^"]+)"', tags_m.group(1))]
        # Extract sections — paragraphs and headings
        sections_m = re.search(r'sections:\s*\[(.*?)\]\s*,?\s*\}\s*(?=,\s*\{|\s*\];)', chunk, re.DOTALL)
        body_md = build_markdown(chunk, title, desc)
        posts.append({
            "slug": slug,
            "title": title,
            "description": desc,
            "tags": tags,
            "body_markdown": body_md,
        })
    return posts


def build_markdown(chunk, title, desc):
    """Convert sections array to markdown."""
    lines = [f"# {title}", "", f"*{desc}*", ""]
    # Walk sections: heading (optional) + body blocks (p/list/ol/callout)
    for sec in re.finditer(r'\{\s*(?:heading:\s*"([^"]*)",\s*)?body:\s*\[(.*?)\]\s*,?\s*\}', chunk, re.DOTALL):
        heading = sec.group(1)
        body_chunk = sec.group(2)
        if heading:
            lines.append(f"## {heading}")
            lines.append("")
        for blk in re.finditer(r'\{\s*kind:\s*"(p|list|ol|callout)",\s*(?:text:\s*\n?\s*"((?:[^"\\]|\\.)*)"|items:\s*\[(.*?)\])\s*\}', body_chunk, re.DOTALL):
            kind = blk.group(1)
            text = blk.group(2)
            items_raw = blk.group(3)
            if kind == "p" and text:
                lines.append(_unescape(text))
                lines.append("")
            elif kind == "callout" and text:
                lines.append(f"> {_unescape(text)}")
                lines.append("")
            elif kind in ("list", "ol") and items_raw:
                for i, item in enumerate(re.findall(r'"((?:[^"\\]|\\.)*)"', items_raw), 1):
                    prefix = f"{i}. " if kind == "ol" else "- "
                    lines.append(f"{prefix}{_unescape(item)}")
                lines.append("")
    return "\n".join(lines).strip()


def _unescape(s):
    return s.encode().decode("unicode_escape").replace('\\"', '"')


def devto_publish(api_key, post, canonical_url):
    """POST /api/articles — create + publish article on dev.to."""
    body = {
        "article": {
            "title": post["title"][:128],
            "body_markdown": post["body_markdown"],
            "published": True,
            "canonical_url": canonical_url,
            "tags": [t.lower().replace(" ", "")[:30] for t in post.get("tags", [])[:4]],
            "description": post.get("description", "")[:280],
        }
    }
    req = urllib.request.Request(
        "https://dev.to/api/articles",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/vnd.forem.api-v1+json",
            "User-Agent": "KunStudio-Crosspost/1.0",
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
    api_key = env.get("DEVTO_API_KEY")
    if not api_key:
        print("[INIT] DEVTO_API_KEY missing in .secrets")
        print("       1) https://dev.to/enter 가입 (free, GitHub/Twitter/Email)")
        print("       2) https://dev.to/settings/extensions → 'DEV API Keys' → 'Generate API Key'")
        print("       3) .secrets 에 추가: DEVTO_API_KEY=<생성된 키>")
        print("       4) 다시 실행")
        return

    posts = parse_blog_posts()
    log(f"Parsed {len(posts)} posts from blog-posts.ts")

    pub = load_published()
    posted_slugs = {x["slug"] for x in pub.get("posted", [])}

    candidates = [p for p in posts if p["slug"] not in posted_slugs]
    if not candidates:
        log("All KORLENS blogs already cross-posted to dev.to")
        return

    p = candidates[0]
    log(f"=== {p['slug']} ===")

    canonical = f"{KORLENS_BASE}/{p['slug']}"
    try:
        result = devto_publish(api_key, p, canonical)
        if "error" in result:
            log(f"  API error: {result}")
            return
        log(f"  posted → {result.get('url', result.get('id'))}")
        pub["posted"].append({
            "slug": p["slug"],
            "title": p["title"],
            "url": result.get("url", ""),
            "id": result.get("id"),
            "posted_at": datetime.datetime.now().isoformat(),
        })
        PUBLISHED.write_text(json.dumps(pub, ensure_ascii=False, indent=2), encoding="utf-8")
    except urllib.error.HTTPError as e:
        log(f"  HTTPError {e.code}: {e.read().decode('utf-8','ignore')[:300]}")


if __name__ == "__main__":
    main()
