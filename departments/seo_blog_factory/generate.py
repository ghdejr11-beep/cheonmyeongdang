"""seo_blog_factory — 영문 long-tail SEO 블로그 자동 생성기.

매일 1편씩 keyword_pool.json에서 미발행 키워드 선택 → Claude API로 1500~2500단어 글
→ Pollinations Flux 이미지 1장 → cheonmyeongdang/blog/en/{slug}.html 저장
→ IndexNow ping (Bing/Naver/Yandex)
→ 발행 기록 published.json 업데이트
"""
import os
import sys
import json
import re
import urllib.request
import urllib.parse
import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON_ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
BLOG_DIR = CHEON_ROOT / "blog" / "en"
BLOG_DIR.mkdir(parents=True, exist_ok=True)
PUBLISHED = ROOT / "published.json"
LOG = ROOT / "logs" / f"factory_{datetime.date.today()}.log"
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


def slugify(text):
    s = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:80]


def load_keyword_pool():
    pool_file = ROOT / "keyword_pool.json"
    pool = json.loads(pool_file.read_text(encoding="utf-8"))
    flat = []
    for category, items in pool.items():
        if category.startswith("_"):
            continue
        for it in items:
            flat.append({**it, "category": category})
    return flat


def load_published():
    if PUBLISHED.exists():
        return json.loads(PUBLISHED.read_text(encoding="utf-8"))
    return {"published": []}


def save_published(data):
    PUBLISHED.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def pick_next_keyword(pool, published):
    done_kws = {p["kw"] for p in published.get("published", [])}
    remaining = [k for k in pool if k["kw"] not in done_kws]
    if not remaining:
        return None
    # informational + transactional 균등 분배
    remaining.sort(key=lambda k: (-k.get("vol", 0)))
    return remaining[0]


def claude_generate(api_key, kw, category):
    """Anthropic Claude API로 1500~2500단어 SEO 글 생성."""
    intent = kw.get("intent", "informational")
    keyword = kw["kw"]

    system = (
        "You are a Korean culture content expert writing high-quality SEO blog posts in English "
        "for Western readers (US/UK/EU). Write engaging, factually accurate, and easy-to-read content. "
        "Use H2/H3 structure, short paragraphs, bullet lists, and natural keyword integration. "
        "Word count 1500-2500. Markdown format. NO promotional fluff. Educational, helpful tone."
    )

    prompt = f"""Write a comprehensive SEO blog post for the keyword: "{keyword}"

Category: {category}
Intent: {intent}

Requirements:
- Title: catchy, keyword in title, under 60 chars
- Meta description: 150-160 chars
- 6-10 H2 sections with subsections
- Include real Korean cultural context, history, modern relevance
- Include 1-2 personal/anecdotal hooks (without making up specific people)
- End with a soft CTA mentioning related Korean culture resources (no specific brand push)
- 1500-2500 words

Output format (strict JSON, no extra text):
{{
  "title": "...",
  "meta_description": "...",
  "slug": "kebab-case-slug",
  "tags": ["tag1","tag2","tag3"],
  "content_md": "## H2 ... markdown body ...",
  "image_prompt": "concise English image generation prompt for hero image, 16:9, photographic style"
}}"""

    body = json.dumps({
        "model": "claude-sonnet-4-5",
        "max_tokens": 8000,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read())

    text = data["content"][0]["text"]
    # JSON 추출 (코드 블록 안에 있을 수 있음)
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise RuntimeError(f"no JSON in: {text[:200]}")
    return json.loads(match.group(0))


def fetch_image(prompt, slug):
    seed = abs(hash(slug)) % 100000
    url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
        f"?width=1280&height=720&seed={seed}&nologo=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def md_to_html(md):
    """매우 간단한 Markdown → HTML (h2/h3/list/bold/em/p)."""
    html = md
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"(<li>.*?</li>\n?)+", lambda m: f"<ul>{m.group(0)}</ul>", html, flags=re.DOTALL)
    # paragraphs
    paras = []
    for block in html.split("\n\n"):
        b = block.strip()
        if not b:
            continue
        if b.startswith("<h") or b.startswith("<ul"):
            paras.append(b)
        else:
            paras.append(f"<p>{b}</p>")
    return "\n\n".join(paras)


def write_html(post, image_filename):
    slug = post["slug"]
    title = post["title"]
    meta = post["meta_description"]
    tags = post.get("tags", [])
    content = md_to_html(post["content_md"])
    today = datetime.date.today().isoformat()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | KunStudio</title>
<meta name="description" content="{meta}">
<meta name="keywords" content="{', '.join(tags)}">
<meta name="author" content="KunStudio">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="https://cheonmyeongdang.vercel.app/blog/en/{slug}.html">

<!-- Open Graph -->
<meta property="og:type" content="article">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="KunStudio">
<meta property="og:url" content="https://cheonmyeongdang.vercel.app/blog/en/{slug}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta}">
<meta property="og:image" content="https://cheonmyeongdang.vercel.app/blog/en/{image_filename}">
<meta property="og:image:width" content="1280">
<meta property="og:image:height" content="720">
<meta property="article:published_time" content="{today}T00:00:00Z">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{meta}">
<meta name="twitter:image" content="https://cheonmyeongdang.vercel.app/blog/en/{image_filename}">

<!-- Schema.org Article -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{meta}",
  "image": "https://cheonmyeongdang.vercel.app/blog/en/{image_filename}",
  "datePublished": "{today}T00:00:00Z",
  "dateModified": "{today}T00:00:00Z",
  "author": {{ "@type": "Organization", "name": "KunStudio" }},
  "publisher": {{ "@type": "Organization", "name": "KunStudio", "url": "https://cheonmyeongdang.vercel.app/" }},
  "inLanguage": "en"
}}
</script>

<!-- AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2954177434416880" crossorigin="anonymous"></script>

<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Inter,sans-serif;max-width:760px;margin:0 auto;padding:24px;color:#222;line-height:1.7;background:#fafafa}}
header{{margin-bottom:24px;padding-bottom:14px;border-bottom:1px solid #e5e5e5}}
h1{{font-size:2.1rem;line-height:1.25;color:#111;margin-bottom:10px}}
h2{{font-size:1.45rem;color:#1a1a1a;margin-top:36px;margin-bottom:12px}}
h3{{font-size:1.15rem;color:#333;margin-top:24px;margin-bottom:8px}}
p{{margin-bottom:14px}}
ul{{margin:12px 0 18px 22px}}
li{{margin:5px 0}}
.hero{{width:100%;height:auto;border-radius:10px;margin:18px 0}}
.meta{{color:#888;font-size:0.85rem}}
.cta{{margin-top:36px;padding:18px 22px;background:#fff;border:1px solid #ddd;border-radius:10px}}
.cta a{{color:#2563eb;text-decoration:none;font-weight:600}}
footer{{margin-top:48px;padding-top:16px;border-top:1px solid #e5e5e5;color:#888;font-size:0.82rem}}
.tags{{margin-top:8px}}
.tag{{display:inline-block;padding:2px 9px;background:#eef2f6;border-radius:4px;font-size:0.74rem;color:#555;margin-right:5px}}
</style>
</head>
<body>
<header>
<div class="meta">{today} · KunStudio · Korean Culture Insights</div>
<h1>{title}</h1>
<div class="tags">{''.join(f'<span class="tag">{t}</span>' for t in tags)}</div>
</header>
<img src="{image_filename}" alt="{title}" class="hero" loading="lazy">
<article>
{content}
</article>
<div class="cta">
<strong>Want more Korean culture insights?</strong><br>
Explore our <a href="https://cheonmyeongdang.vercel.app/bundle">Korean Wisdom Mega Bundle</a> — 20 ebooks + audiobooks for $70 (lifetime access).
</div>
<footer>
KunStudio © 2026 · <a href="https://cheonmyeongdang.vercel.app/">Home</a> · <a href="https://cheonmyeongdang.vercel.app/blog/">Blog</a> · <a href="mailto:ghdejr11@gmail.com">Contact</a>
</footer>
</body>
</html>
"""
    out = BLOG_DIR / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    return out


def indexnow_ping(slug):
    KEY = "d36c6c00cec20261eabe2e1ea32164e0"
    HOST = "cheonmyeongdang.vercel.app"
    url = f"https://{HOST}/blog/en/{slug}.html"
    body = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": [url],
    }).encode("utf-8")
    for ep in [
        "https://api.indexnow.org/indexnow",
        "https://www.bing.com/indexnow",
        "https://yandex.com/indexnow",
        "https://searchadvisor.naver.com/indexnow",
    ]:
        try:
            req = urllib.request.Request(ep, data=body,
                headers={"Content-Type": "application/json", "User-Agent": "KunStudioFactory/1.0"},
                method="POST")
            with urllib.request.urlopen(req, timeout=15) as r:
                log(f"  IndexNow [{r.status}] {ep[:50]}")
        except Exception as e:
            log(f"  IndexNow FAIL {ep[:30]}: {type(e).__name__}")


def main():
    env = load_secrets()
    api_key = env.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        sys.exit("[ERR] ANTHROPIC_API_KEY missing in .secrets")

    pool = load_keyword_pool()
    pub = load_published()
    kw = pick_next_keyword(pool, pub)
    if not kw:
        log("All keywords published. Done.")
        return

    log(f"=== Generating: {kw['kw']} ({kw['category']}) ===")
    post = claude_generate(api_key, kw, kw["category"])
    slug = post.get("slug") or slugify(kw["kw"])
    post["slug"] = slug
    log(f"  title: {post['title']}")
    log(f"  slug: {slug}")

    # 이미지
    img_data = fetch_image(post.get("image_prompt", post["title"]), slug)
    img_filename = f"{slug}.jpg"
    (BLOG_DIR / img_filename).write_bytes(img_data)
    log(f"  image: {len(img_data)//1024}KB")

    # HTML 작성
    out = write_html(post, img_filename)
    log(f"  written: {out.name} ({out.stat().st_size//1024}KB)")

    # IndexNow
    indexnow_ping(slug)

    # 발행 기록
    pub["published"].append({
        "kw": kw["kw"],
        "slug": slug,
        "title": post["title"],
        "category": kw["category"],
        "vol": kw.get("vol"),
        "published_at": datetime.datetime.now().isoformat(),
    })
    save_published(pub)
    log(f"=== DONE — {len(pub['published'])} total ===")


if __name__ == "__main__":
    main()
