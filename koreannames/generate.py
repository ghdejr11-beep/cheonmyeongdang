"""koreannames — Korean baby names SEO 정적 사이트 자동 생성기.

100일 목표: 5,000 이름 페이지 → "korean baby names" 60K mo 검색 → AdSense + Mega Bundle 업셀.
매일 schtask: 50 이름 batch 자동 생성 (Claude API + Pollinations).
배포: cheonmyeongdang.vercel.app/names/{name}.html (Vercel 정적 호스팅 재활용)
"""
import os, sys, json, urllib.request, urllib.parse, datetime, re
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
NAMES_DIR = CHEON / "names"
NAMES_DIR.mkdir(exist_ok=True)
LOG = ROOT / "logs" / f"names_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)
DB = ROOT / "data" / "names_db.json"
DB.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_secrets():
    env = {}
    p = CHEON / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def load_db():
    if DB.exists():
        return json.loads(DB.read_text(encoding="utf-8"))
    return {"names": []}


def save_db(d):
    DB.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def claude_batch_names(api_key, count=50, exclude_set=None):
    """Claude API: 한국 이름 batch 생성 (이미 만든 거 제외)."""
    excl = list(exclude_set or [])[:100]
    prompt = f"""Generate {count} Korean baby names with full SEO-optimized data.

EXCLUDE (already generated): {', '.join(excl) if excl else '(none yet)'}

Return STRICT JSON array, no extra text:
[
  {{
    "romanized": "Ji-hoo",
    "hangul": "지후",
    "hanja": "智厚",
    "gender": "male",
    "meaning_short": "Wisdom and generosity",
    "meaning_long": "지(智) means wisdom and intellect; 후(厚) means generosity and depth of character. Together: a child of wise heart and generous spirit.",
    "popularity_2026": "rising",
    "famous_examples": "Common in modern K-drama leads",
    "kpop_match": "BTS Jin (similar feel)",
    "saju_meaning": "Strong wood element, balanced yang energy",
    "pronunciation_guide": "JEE-hoo (rhymes with 'see-who')",
    "personality_traits": ["intelligent", "warm", "trustworthy"]
  }},
  ...
]

Mix: 50% male, 50% female. Vary across traditional/modern/unisex. Include K-pop idol-inspired names. NO duplicates."""

    body = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 16000,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read())
    text = data["content"][0]["text"]
    m = re.search(r"\[[\s\S]*\]", text)
    if not m:
        raise RuntimeError(f"no JSON array in: {text[:200]}")
    return json.loads(m.group(0))


def slug(romanized):
    return re.sub(r"[^a-z0-9-]", "", romanized.lower().replace(" ", "-").replace("'", ""))


def build_html(name):
    s = slug(name["romanized"])
    title = f"{name['romanized']} — Korean Name Meaning, Hangul, Hanja, Pronunciation"
    desc = f"{name['romanized']} ({name['hangul']}) is a {name['gender']} Korean name meaning '{name.get('meaning_short','')}'. Hanja: {name.get('hanja','')}. Pronunciation guide + cultural context."

    traits = ", ".join(name.get("personality_traits", []))
    today = datetime.date.today().isoformat()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc[:160]}">
<meta name="keywords" content="korean baby name, {name['romanized']}, {name['hangul']}, korean {name['gender']} name, korean name meaning">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="https://cheonmyeongdang.vercel.app/names/{s}.html">

<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc[:160]}">
<meta property="og:url" content="https://cheonmyeongdang.vercel.app/names/{s}.html">
<meta name="twitter:card" content="summary_large_image">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "DefinedTerm",
  "name": "{name['romanized']} ({name['hangul']})",
  "description": "{desc.replace('"','')[:300]}",
  "inDefinedTermSet": {{ "@type": "DefinedTermSet", "name": "Korean Baby Names" }},
  "inLanguage": "en"
}}
</script>

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2954177434416880" crossorigin="anonymous"></script>

<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:760px;margin:0 auto;padding:24px;color:#222;line-height:1.7;background:#fafafa}}
h1{{font-size:2.4rem;margin-bottom:6px;color:#111}}
.hangul{{font-size:3.2rem;color:#c9a84c;font-weight:700;margin:12px 0;line-height:1}}
.hanja{{font-size:1.5rem;color:#888;margin-bottom:18px}}
.meta-grid{{display:grid;grid-template-columns:120px 1fr;gap:8px 16px;margin:18px 0;padding:18px;background:#fff;border:1px solid #ddd;border-radius:10px}}
.meta-grid dt{{font-weight:600;color:#666;font-size:0.85rem}}
.meta-grid dd{{margin:0;color:#222}}
h2{{font-size:1.4rem;margin-top:30px;color:#1a1a1a}}
p{{margin-bottom:14px}}
.traits{{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}}
.tag{{padding:3px 10px;background:#eef2f6;border-radius:99px;font-size:0.8rem;color:#555}}
.cta{{margin-top:36px;padding:18px 22px;background:#fff;border:1px solid #ddd;border-radius:10px}}
.cta a{{color:#2563eb;text-decoration:none;font-weight:600}}
nav a{{color:#666;text-decoration:none;font-size:0.85rem;margin-right:12px}}
footer{{margin-top:48px;padding-top:16px;border-top:1px solid #e5e5e5;color:#888;font-size:0.82rem}}
</style>
</head>
<body>
<nav><a href="../">← KunStudio</a> · <a href="../names/">All Korean Names</a></nav>

<h1>{name['romanized']}</h1>
<div class="hangul">{name['hangul']}</div>
<div class="hanja">한자: {name.get('hanja','')}</div>

<dl class="meta-grid">
<dt>Gender</dt><dd>{name['gender']}</dd>
<dt>Hangul</dt><dd>{name['hangul']}</dd>
<dt>Hanja</dt><dd>{name.get('hanja','')}</dd>
<dt>Pronunciation</dt><dd>{name.get('pronunciation_guide','')}</dd>
<dt>Popularity</dt><dd>{name.get('popularity_2026','')}</dd>
</dl>

<h2>Meaning</h2>
<p>{name.get('meaning_long','')}</p>

<h2>Personality Traits</h2>
<div class="traits">{''.join(f'<span class="tag">{t}</span>' for t in name.get('personality_traits', []))}</div>

<h2>Cultural Context</h2>
<p><strong>K-Pop Match:</strong> {name.get('kpop_match','')}</p>
<p><strong>Famous Examples:</strong> {name.get('famous_examples','')}</p>

<h2>Saju (Four Pillars) Reading</h2>
<p>{name.get('saju_meaning','')}</p>

<div class="cta">
<strong>Looking for the perfect Korean name?</strong><br>
Get our complete <a href="https://cheonmyeongdang.vercel.app/bundle">Korean Naming + Saju Bundle</a> — 20 ebooks including a 5,000-name database with Saju compatibility — $70 lifetime access.
</div>

<footer>
KunStudio © 2026 · <a href="https://cheonmyeongdang.vercel.app/">Home</a> · <a href="https://cheonmyeongdang.vercel.app/blog/">Blog</a> · Korean Baby Names Database
<br>Last updated: {today}
</footer>
</body>
</html>
"""


def build_index_page(all_names):
    """전체 이름 목록 인덱스 페이지."""
    items_html = []
    for n in all_names:
        s = slug(n["romanized"])
        items_html.append(
            f'<li><a href="{s}.html"><b>{n["romanized"]}</b> ({n["hangul"]}) — {n.get("meaning_short", "")[:50]}</a></li>'
        )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>Korean Baby Names Database — {len(all_names)} Names with Meanings | KunStudio</title>
<meta name="description" content="Browse {len(all_names)} Korean baby names with Hangul, Hanja, meaning, pronunciation, and Saju compatibility. Curated by Korean culture experts.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://cheonmyeongdang.vercel.app/names/">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2954177434416880" crossorigin="anonymous"></script>
<style>
body{{font-family:sans-serif;max-width:900px;margin:0 auto;padding:24px;background:#fafafa}}
h1{{color:#111}}
ul{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px}}
li{{padding:12px;background:#fff;border:1px solid #ddd;border-radius:8px}}
li a{{text-decoration:none;color:#222}}
li a:hover{{color:#2563eb}}
</style></head>
<body>
<h1>Korean Baby Names — {len(all_names)} Curated Entries</h1>
<p>Each name includes Hangul, Hanja, meaning, K-pop match, and Saju (Four Pillars) reading.</p>
<ul>{''.join(items_html)}</ul>
<footer style="margin-top:40px;color:#888;font-size:0.85rem">KunStudio © 2026 — Korean Culture for Global Readers</footer>
</body></html>
"""


def main():
    env = load_secrets()
    api_key = env.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("[ERR] ANTHROPIC_API_KEY missing")

    db = load_db()
    existing = {n["romanized"] for n in db.get("names", [])}
    log(f"existing: {len(existing)}")

    # 첫 실행 시 50개, 그 다음부턴 schtask가 daily 50씩 추가
    batch_size = 50
    log(f"requesting {batch_size} new names from Claude...")
    new_names = claude_batch_names(api_key, count=batch_size, exclude_set=existing)
    log(f"received {len(new_names)} names")

    added = 0
    for n in new_names:
        rom = n.get("romanized", "")
        if not rom or rom in existing:
            continue
        # 페이지 작성
        s = slug(rom)
        if not s:
            continue
        page = build_html(n)
        (NAMES_DIR / f"{s}.html").write_text(page, encoding="utf-8")
        db["names"].append(n)
        existing.add(rom)
        added += 1

    # 인덱스 페이지 갱신
    index = build_index_page(db["names"])
    (NAMES_DIR / "index.html").write_text(index, encoding="utf-8")

    save_db(db)
    log(f"[OK] +{added} names. total {len(db['names'])} pages → {NAMES_DIR}")
    log(f"[index] {NAMES_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
