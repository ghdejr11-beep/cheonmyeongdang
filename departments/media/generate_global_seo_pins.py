#!/usr/bin/env python3
"""
글로벌 영문 SEO Pinterest 핀 생성기 (2026-05-06).

5개 영문 SEO 페이지를 Pinterest 핀(1000x1500)으로 자동 변환:
  - en/saju-vs-western-astrology.html
  - en/four-pillars-of-destiny.html
  - en/korean-zodiac-2026-year-of-red-horse.html
  - en/saju-compatibility-test.html
  - en/ten-heavenly-stems.html

⚠️ 자동 발행 X — 핀 PNG + 메타 JSON만 생성. 사용자 검토 후 Pinterest UI에서 발행.

배경 패턴:
  1. Pollinations Flux로 K-aesthetics 배경 이미지 생성 (4-5초)
  2. PIL로 텍스트 오버레이 (제목 + 부제 + URL)
  3. departments/media/output/global_seo_pins/ 에 저장

사용:
    python departments/media/generate_global_seo_pins.py            # 5개 모두 생성
    python departments/media/generate_global_seo_pins.py --slug zodiac
    python departments/media/generate_global_seo_pins.py --dry-run  # API 호출 없이 manifest만
"""
import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
from datetime import datetime

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
OUT = os.path.join(ROOT, 'departments', 'media', 'output', 'global_seo_pins')
os.makedirs(OUT, exist_ok=True)

PINS = [
    {
        'slug': 'saju-vs-western',
        'page': 'en/saju-vs-western-astrology.html',
        'pin_title': 'Korean Saju vs Western Astrology',
        'pin_subtitle': "Why 12 zodiac signs feel shallow once you've seen 4 pillars",
        'overlay_color': '#c9a84c',
        'bg_prompt': 'mystical korean palace at twilight, golden lanterns, deep navy sky with stars, traditional hanok roof, cinematic',
        'pinterest_title': 'Korean Saju vs Western Astrology — Why 12 Zodiacs Feel Shallow',
        'pinterest_desc': 'The Four Pillars of Destiny give 60x more granularity than Western sun signs. Compare them side-by-side and find out which system actually fits your life-strategy questions. Free English calculator inside.',
        'hashtags': '#KoreanAstrology #SajuReading #FourPillarsOfDestiny #KoreanZodiac #FortuneTelling #Astrology2026 #KCulture #Gunghap',
    },
    {
        'slug': 'four-pillars',
        'page': 'en/four-pillars-of-destiny.html',
        'pin_title': 'Four Pillars of Destiny',
        'pin_subtitle': 'Year · Month · Day · Hour — your eight-character map',
        'overlay_color': '#e8c97a',
        'bg_prompt': 'four ancient korean wooden columns rising from mist, golden hour, painterly, ink wash style, muted colors',
        'pinterest_title': 'Four Pillars of Destiny Explained — Read Your Korean Saju Chart',
        'pinterest_desc': 'Your Korean Saju chart is just 8 characters arranged in 4 pillars. This guide tells you what each pillar means + how to find your Day Master. Free calculator in plain English.',
        'hashtags': '#FourPillarsOfDestiny #SajuPalja #KoreanAstrology #DayMaster #ChineseAstrology #BaZi #KoreanCulture #SelfDiscovery',
    },
    {
        'slug': 'red-horse-2026',
        'page': 'en/korean-zodiac-2026-year-of-red-horse.html',
        'pin_title': 'Year of the Red Horse 2026',
        'pin_subtitle': '병오 (Byeong-O) — only once every 60 years',
        'overlay_color': '#d96d5d',
        'bg_prompt': 'majestic red horse silhouette at sunrise, korean ink painting style, vermillion and gold, dramatic clouds',
        'pinterest_title': 'Year of the Red Horse 2026 — Korean Zodiac Forecast for All 12 Signs',
        'pinterest_desc': "2026 is 병오 (Byeong-O), Yang Fire Horse. The full forecast for all 12 Korean zodiac signs — lucky months, cautious months, and what the Red Horse year means for your career, love, and money.",
        'hashtags': '#YearOfTheRedHorse #KoreanZodiac2026 #SajuForecast #ChineseZodiac #LunarNewYear2026 #KoreanAstrology #FortuneTelling #ByeongO',
    },
    {
        'slug': 'compatibility',
        'page': 'en/saju-compatibility-test.html',
        'pin_title': 'Korean Compatibility Test',
        'pin_subtitle': 'Gunghap (궁합) — the 1,000-year-old marriage check',
        'overlay_color': '#e08fa6',
        'bg_prompt': 'two delicate korean paper lanterns floating side by side over still water, soft pink and gold, romantic, ink wash',
        'pinterest_title': 'Free Korean Compatibility Test — Gunghap (궁합) Method',
        'pinterest_desc': 'Korean families have used Saju compatibility for 1,000 years before approving marriages. Compare two birth charts using Five Elements harmony. Free 60-second test in plain English.',
        'hashtags': '#KoreanCompatibility #Gunghap #SajuLove #RelationshipCompatibility #LoveCompatibility #KoreanAstrology #Marriage #DatingTips',
    },
    {
        'slug': 'ten-stems',
        'page': 'en/ten-heavenly-stems.html',
        'pin_title': 'The 10 Heavenly Stems',
        'pin_subtitle': 'The alphabet of Korean Saju — find your Day Master',
        'overlay_color': '#4a9e8e',
        'bg_prompt': 'ten ancient korean calligraphy characters carved on weathered jade tablets, golden lighting, museum aesthetic',
        'pinterest_title': '10 Heavenly Stems — Find Your Korean Day Master',
        'pinterest_desc': 'The 10 Heavenly Stems are the alphabet of Korean Saju. Yang Wood, Yin Wood, Yang Fire... Each stem is a distinct personality. Find your Day Master and read what your chart actually means.',
        'hashtags': '#HeavenlyStems #DayMaster #KoreanAstrology #SajuReading #FourPillars #Cheongan #ChineseAstrology #SelfDiscovery',
    },
]

POLL_BASE = 'https://image.pollinations.ai/prompt/'
USER_AGENT = 'Mozilla/5.0 (KunStudio-Pinterest-SEO/1.0)'


def fetch_bg(prompt, out_path, w=1000, h=1500, timeout=60):
    """Pollinations Flux background fetch (free, no API key)."""
    url = POLL_BASE + urllib.parse.quote(prompt) + f'?width={w}&height={h}&nologo=true&enhance=true&model=flux'
    print(f'  ↘ {url[:90]}...')
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    with open(out_path, 'wb') as f:
        f.write(data)
    return len(data)


def overlay_text(bg_path, out_path, title, subtitle, url, color):
    """PIL 텍스트 오버레이. 없으면 graceful skip."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print('  ⚠️ PIL (Pillow) not installed — skipping overlay. Install: pip install Pillow')
        # Just copy bg to out as fallback
        with open(bg_path, 'rb') as src, open(out_path, 'wb') as dst:
            dst.write(src.read())
        return False

    img = Image.open(bg_path).convert('RGBA')
    W, H = img.size
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Bottom dark gradient panel
    panel_h = int(H * 0.42)
    for i in range(panel_h):
        a = int(220 * (i / panel_h) ** 1.4)
        draw.line([(0, H - panel_h + i), (W, H - panel_h + i)], fill=(8, 10, 16, a))

    # Try to load a font (fallback to default)
    title_font = None
    sub_font = None
    url_font = None
    candidates = [
        'C:/Windows/Fonts/malgunbd.ttf',
        'C:/Windows/Fonts/malgun.ttf',
        'C:/Windows/Fonts/seguibl.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                title_font = ImageFont.truetype(c, 78)
                sub_font = ImageFont.truetype(c, 38)
                url_font = ImageFont.truetype(c, 26)
                break
            except Exception:
                pass
    if title_font is None:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        url_font = ImageFont.load_default()

    # Title (wrap to ~22 chars/line)
    margin_x = 60
    y = int(H * 0.62)
    for line in _wrap(title, 22):
        draw.text((margin_x, y), line, font=title_font, fill=color)
        y += 88

    y += 14
    for line in _wrap(subtitle, 38):
        draw.text((margin_x, y), line, font=sub_font, fill='#e8e0d0')
        y += 48

    # URL stripe at very bottom
    draw.rectangle([(0, H - 70), (W, H)], fill=(201, 168, 76, 230))
    draw.text((margin_x, H - 52), url, font=url_font, fill='#1a1206')

    out = Image.alpha_composite(img, overlay).convert('RGB')
    out.save(out_path, 'PNG', optimize=True)
    return True


def _wrap(text, width):
    """Naive word-wrap."""
    words = text.split()
    lines, cur = [], ''
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + ' ' + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def generate(pin, dry_run=False):
    slug = pin['slug']
    bg = os.path.join(OUT, f'{slug}_bg.png')
    final = os.path.join(OUT, f'{slug}_pin.png')

    print(f'\n[PIN] {slug}')
    print(f'  Page : {pin["page"]}')
    print(f'  Title: {pin["pin_title"]}')

    if dry_run:
        print('  [dry-run] would fetch + overlay')
    else:
        if not os.path.exists(bg):
            sz = fetch_bg(pin['bg_prompt'], bg)
            print(f'  bg.png {sz//1024} KB')
        else:
            print('  bg.png cached')
        ok = overlay_text(
            bg, final,
            pin['pin_title'], pin['pin_subtitle'],
            'cheonmyeongdang.vercel.app/en/',
            pin['overlay_color'],
        )
        print(f'  pin.png {"OK" if ok else "fallback"}')

    # Manifest entry
    return {
        'slug': slug,
        'page': pin['page'],
        'pin_path': final,
        'pinterest_title': pin['pinterest_title'],
        'pinterest_description': pin['pinterest_desc'],
        'hashtags': pin['hashtags'],
        'destination_url': f'https://cheonmyeongdang.vercel.app/{pin["page"]}?utm_source=pinterest&utm_campaign=global_seo&utm_content={slug}',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--slug', help='generate only this slug')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()

    pins = PINS
    if args.slug:
        pins = [x for x in PINS if args.slug in x['slug']]
        if not pins:
            print(f'No match for slug "{args.slug}"')
            return 1

    results = []
    for pin in pins:
        try:
            results.append(generate(pin, dry_run=args.dry_run))
        except Exception as e:
            print(f'  ✗ {pin["slug"]} failed: {e}')
            results.append({'slug': pin['slug'], 'error': str(e)})
        time.sleep(1.5)

    manifest = os.path.join(OUT, 'manifest.json')
    with open(manifest, 'w', encoding='utf-8') as f:
        json.dump({'generated_at': datetime.utcnow().isoformat() + 'Z', 'pins': results}, f, ensure_ascii=False, indent=2)
    print(f'\n[DONE] {len(results)} pins -> {OUT}')
    print(f'       manifest -> {manifest}')
    print(f'\n>> Next: review PNGs in {OUT}, then post to Pinterest manually (or via Pinterest API once approved).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
