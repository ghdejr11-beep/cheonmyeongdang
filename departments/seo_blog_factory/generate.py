"""seo_blog_factory — 다언어 long-tail SEO 블로그 자동 생성기 (en/ja/zh, ko 예약).

매일 1편씩 keyword_pool[_lang].json 에서 미발행 키워드 선택 → Claude API로 1500~2500단어 글
→ Pollinations Flux 이미지 1장 → cheonmyeongdang/blog/{lang}/{slug}.html 저장
→ IndexNow ping (Bing/Naver/Yandex)
→ 발행 기록 published.json (lang 필드 포함) 업데이트

CLI 사용:
    python generate.py            # 기본 en (기존 schtask 호환)
    python generate.py --lang ja  # 일본어
    python generate.py --lang zh  # 번체 중국어 (TW/HK/SG/MY)
"""
import os
import sys
import json
import re
import argparse
import urllib.request
import urllib.parse
import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON_ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
PUBLISHED = ROOT / "published.json"
LOG = ROOT / "logs" / f"factory_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)

# Language config: keyword pool file, blog output dir, html lang, og locale,
# system prompt persona, prompt instructions.
LANG_CONFIG = {
    "en": {
        "pool_file": "keyword_pool.json",
        "blog_subdir": "en",
        "html_lang": "en",
        "og_locale": "en_US",
        "system": (
            "You are a Korean culture content expert writing high-quality SEO blog posts in English "
            "for Western readers (US/UK/EU). Write engaging, factually accurate, and easy-to-read content. "
            "Use H2/H3 structure, short paragraphs, bullet lists, and natural keyword integration. "
            "Word count 1500-2500. Markdown format. NO promotional fluff. Educational, helpful tone."
        ),
        "prompt_lang_note": "Write the entire post in natural English.",
        "site_tagline": "Korean Culture Insights",
        "cta_html": (
            '<strong>Want more Korean culture insights?</strong><br>'
            'Explore our <a href="https://cheonmyeongdang.vercel.app/bundle">'
            'Korean Wisdom Mega Bundle</a> — 20 ebooks + audiobooks for $70 (lifetime access).'
        ),
        "footer_home": "Home",
        "footer_blog": "Blog",
        "footer_contact": "Contact",
    },
    "ja": {
        "pool_file": "keyword_pool_ja.json",
        "blog_subdir": "ja",
        "html_lang": "ja",
        "og_locale": "ja_JP",
        "system": (
            "あなたは韓国文化・四柱推命・K-POPに精通したSEOコンテンツライターです。"
            "日本人読者向けに、自然で読みやすい日本語でSEOブログ記事を執筆してください。"
            "H2/H3構造、短い段落、箇条書き、自然なキーワード統合を使用。"
            "文字数1500〜2500文字。Markdown形式。誇大広告なし、教育的・親切なトーン。"
            "敬体（です・ます調）で統一。漢字・ひらがな・カタカナのバランスに注意。"
        ),
        "prompt_lang_note": "記事は全て自然な日本語で書いてください。タイトルとメタディスクリプションも日本語で。",
        "site_tagline": "韓国文化・占いガイド",
        "cta_html": (
            '<strong>韓国占いをもっと知りたい方へ</strong><br>'
            '<a href="https://cheonmyeongdang.vercel.app/">天命堂</a>で本格的な韓国式四柱推命を体験できます。'
        ),
        "footer_home": "ホーム",
        "footer_blog": "ブログ",
        "footer_contact": "お問い合わせ",
    },
    "zh": {
        "pool_file": "keyword_pool_zh.json",
        "blog_subdir": "zh",
        "html_lang": "zh-Hant",
        "og_locale": "zh_TW",
        "system": (
            "你是精通韓國文化、四柱八字命理、K-POP的SEO內容專家，"
            "為台灣、香港、新加坡、馬來西亞等繁體中文讀者撰寫高品質的SEO部落格文章。"
            "請使用H2/H3結構、短段落、條列式、自然的關鍵字嵌入。"
            "字數1500-2500字。Markdown格式。無誇大宣傳，教育性、親切的語氣。"
            "使用繁體中文（台灣用語為主）。"
        ),
        "prompt_lang_note": "全文請以自然的繁體中文撰寫（台灣用語為主）。標題與meta description也請以繁體中文輸出。",
        "site_tagline": "韓國文化・八字命理指南",
        "cta_html": (
            '<strong>想了解更多韓國八字命理嗎？</strong><br>'
            '前往 <a href="https://cheonmyeongdang.vercel.app/">天命堂</a> 體驗正統韓國四柱八字解析。'
        ),
        "footer_home": "首頁",
        "footer_blog": "部落格",
        "footer_contact": "聯絡我們",
    },
    "ko": {
        # 한국어는 메인 도메인에서 직접 운영. 향후 확장 시 keyword_pool_ko.json 추가.
        "pool_file": "keyword_pool_ko.json",
        "blog_subdir": "ko",
        "html_lang": "ko",
        "og_locale": "ko_KR",
        "system": (
            "당신은 한국 사주 명리학과 K-콘텐츠 전문 SEO 콘텐츠 작가입니다. "
            "한국 독자를 위해 자연스럽고 신뢰감 있는 한국어로 SEO 블로그 글을 작성하세요. "
            "H2/H3 구조, 짧은 문단, 불릿 리스트, 자연스러운 키워드 삽입. "
            "1500~2500자, Markdown 형식, 과장 광고 X, 교육적·친절한 톤."
        ),
        "prompt_lang_note": "전체 글을 자연스러운 한국어로 작성하세요. 제목과 메타 설명도 한국어로.",
        "site_tagline": "한국 사주 · 문화 인사이트",
        "cta_html": (
            '<strong>더 깊은 사주 풀이를 원하신다면?</strong><br>'
            '<a href="https://cheonmyeongdang.vercel.app/">천명당</a>에서 본격 한국식 사주 명리 풀이를 받아보세요.'
        ),
        "footer_home": "홈",
        "footer_blog": "블로그",
        "footer_contact": "문의",
    },
}


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


def load_keyword_pool(lang="en"):
    cfg = LANG_CONFIG[lang]
    pool_file = ROOT / cfg["pool_file"]
    if not pool_file.exists():
        raise FileNotFoundError(f"keyword pool missing for lang={lang}: {pool_file}")
    pool = json.loads(pool_file.read_text(encoding="utf-8"))
    flat = []
    for category, items in pool.items():
        if category.startswith("_"):
            continue
        for it in items:
            flat.append({**it, "category": category, "lang": lang})
    return flat


def load_published():
    if PUBLISHED.exists():
        return json.loads(PUBLISHED.read_text(encoding="utf-8"))
    return {"published": []}


def save_published(data):
    PUBLISHED.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def pick_next_keyword(pool, published, lang="en"):
    # legacy entries (no lang field) are treated as 'en'
    done_kws = {
        (p.get("lang", "en"), p["kw"])
        for p in published.get("published", [])
    }
    remaining = [k for k in pool if (lang, k["kw"]) not in done_kws]
    if not remaining:
        return None
    # informational + transactional 균등 분배
    remaining.sort(key=lambda k: (-k.get("vol", 0)))
    return remaining[0]


def claude_generate(api_key, kw, category, lang="en"):
    """Anthropic Claude API로 1500~2500단어 SEO 글 생성. lang에 따라 system/instruction 변경."""
    cfg = LANG_CONFIG[lang]
    intent = kw.get("intent", "informational")
    keyword = kw["kw"]

    system = cfg["system"]
    lang_note = cfg["prompt_lang_note"]

    prompt = f"""Write a comprehensive SEO blog post for the keyword: "{keyword}"

Category: {category}
Intent: {intent}
Target language: {lang}

LANGUAGE INSTRUCTION (critical):
{lang_note}

Requirements:
- Title: catchy, keyword in title, under 60 chars (in target language)
- Meta description: 150-160 chars (in target language)
- 6-10 H2 sections with subsections
- Include real Korean cultural context, history, modern relevance
- Include 1-2 personal/anecdotal hooks (without making up specific people)
- End with a soft CTA mentioning related Korean culture resources (no specific brand push)
- 1500-2500 words

Output format (strict JSON, no extra text):
{{
  "title": "... (in target language)",
  "meta_description": "... (in target language)",
  "slug": "kebab-case-slug (ASCII only — transliterate non-Latin scripts)",
  "tags": ["tag1","tag2","tag3"],
  "content_md": "## H2 ... markdown body in target language ...",
  "image_prompt": "concise English image generation prompt for hero image, 16:9, photographic style"
}}"""

    body = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 8000,
        # Prompt caching: system cached 5min → 5 daily blogs share cache (~90% input cost off)
        "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
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


def write_html(post, image_filename, lang="en"):
    cfg = LANG_CONFIG[lang]
    blog_subdir = cfg["blog_subdir"]
    html_lang = cfg["html_lang"]
    og_locale = cfg["og_locale"]
    site_tagline = cfg["site_tagline"]
    cta_html = cfg["cta_html"]

    slug = post["slug"]
    title = post["title"]
    meta = post["meta_description"]
    tags = post.get("tags", [])
    content = md_to_html(post["content_md"])
    today = datetime.date.today().isoformat()

    base_url = f"https://cheonmyeongdang.vercel.app/blog/{blog_subdir}/{slug}.html"
    img_url = f"https://cheonmyeongdang.vercel.app/blog/{blog_subdir}/{image_filename}"

    html = f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | KunStudio</title>
<meta name="description" content="{meta}">
<meta name="keywords" content="{', '.join(tags)}">
<meta name="author" content="KunStudio">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{base_url}">

<!-- Open Graph -->
<meta property="og:type" content="article">
<meta property="og:locale" content="{og_locale}">
<meta property="og:site_name" content="KunStudio">
<meta property="og:url" content="{base_url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta}">
<meta property="og:image" content="{img_url}">
<meta property="og:image:width" content="1280">
<meta property="og:image:height" content="720">
<meta property="article:published_time" content="{today}T00:00:00Z">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{meta}">
<meta name="twitter:image" content="{img_url}">

<!-- Schema.org Article -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{meta}",
  "image": "{img_url}",
  "datePublished": "{today}T00:00:00Z",
  "dateModified": "{today}T00:00:00Z",
  "author": {{ "@type": "Organization", "name": "KunStudio" }},
  "publisher": {{ "@type": "Organization", "name": "KunStudio", "url": "https://cheonmyeongdang.vercel.app/" }},
  "inLanguage": "{html_lang}"
}}
</script>

<!-- AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2954177434416880" crossorigin="anonymous"></script>

<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Inter,'Noto Sans JP','Noto Sans TC','Noto Sans KR',sans-serif;max-width:760px;margin:0 auto;padding:24px;color:#222;line-height:1.7;background:#fafafa}}
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
<div class="meta">{today} · KunStudio · {site_tagline}</div>
<h1>{title}</h1>
<div class="tags">{''.join(f'<span class="tag">{t}</span>' for t in tags)}</div>
</header>
<img src="{image_filename}" alt="{title}" class="hero" loading="lazy">
<article>
{content}
</article>
<div class="cta">
{cta_html}
</div>
<footer>
KunStudio © 2026 · <a href="https://cheonmyeongdang.vercel.app/">{cfg["footer_home"]}</a> · <a href="https://cheonmyeongdang.vercel.app/blog/{blog_subdir}/">{cfg["footer_blog"]}</a> · <a href="mailto:ghdejr11@gmail.com">{cfg["footer_contact"]}</a>
</footer>
</body>
</html>
"""
    blog_dir = CHEON_ROOT / "blog" / blog_subdir
    blog_dir.mkdir(parents=True, exist_ok=True)
    out = blog_dir / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    return out


def indexnow_ping(slug, lang="en"):
    KEY = "d36c6c00cec20261eabe2e1ea32164e0"
    HOST = "cheonmyeongdang.vercel.app"
    blog_subdir = LANG_CONFIG[lang]["blog_subdir"]
    url = f"https://{HOST}/blog/{blog_subdir}/{slug}.html"
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


def parse_args():
    p = argparse.ArgumentParser(description="Multi-language SEO blog factory")
    p.add_argument(
        "--lang",
        default="en",
        choices=list(LANG_CONFIG.keys()),
        help="Target language (default: en — backward compatible with existing schtasks)",
    )
    return p.parse_args()


def main():
    args = parse_args()
    lang = args.lang

    env = load_secrets()
    api_key = env.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        sys.exit("[ERR] ANTHROPIC_API_KEY missing in .secrets")

    log(f"=== Lang: {lang} ===")
    try:
        pool = load_keyword_pool(lang)
    except FileNotFoundError as e:
        log(f"[SKIP] {e}")
        return

    pub = load_published()
    kw = pick_next_keyword(pool, pub, lang=lang)
    if not kw:
        log(f"All keywords published for lang={lang}. Done.")
        return

    log(f"=== Generating [{lang}]: {kw['kw']} ({kw['category']}) ===")
    post = claude_generate(api_key, kw, kw["category"], lang=lang)
    slug = post.get("slug") or slugify(kw["kw"])
    post["slug"] = slug
    log(f"  title: {post['title']}")
    log(f"  slug: {slug}")

    # 이미지
    blog_subdir = LANG_CONFIG[lang]["blog_subdir"]
    blog_dir = CHEON_ROOT / "blog" / blog_subdir
    blog_dir.mkdir(parents=True, exist_ok=True)
    img_data = fetch_image(post.get("image_prompt", post["title"]), slug)
    img_filename = f"{slug}.jpg"
    (blog_dir / img_filename).write_bytes(img_data)
    log(f"  image: {len(img_data)//1024}KB")

    # HTML 작성
    out = write_html(post, img_filename, lang=lang)
    log(f"  written: {out.name} ({out.stat().st_size//1024}KB)")

    # IndexNow
    indexnow_ping(slug, lang=lang)

    # 발행 기록
    pub["published"].append({
        "kw": kw["kw"],
        "slug": slug,
        "title": post["title"],
        "category": kw["category"],
        "lang": lang,
        "vol": kw.get("vol"),
        "published_at": datetime.datetime.now().isoformat(),
    })
    save_published(pub)
    n_lang = sum(1 for p in pub["published"] if p.get("lang", "en") == lang)
    log(f"=== DONE — {len(pub['published'])} total ({n_lang} for {lang}) ===")


if __name__ == "__main__":
    main()
