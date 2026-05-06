# SEO Blog Factory — Multi-Language

Long-tail SEO blog auto-generator for cheonmyeongdang. Picks an unpublished keyword,
calls Claude Sonnet 4.6, fetches a Pollinations Flux hero image, writes an SEO-optimized
HTML page (Open Graph + Twitter + Schema.org Article + AdSense), and pings IndexNow
(Bing / Naver / Yandex / api.indexnow.org).

## Languages

| Lang  | Pool file               | Output dir            | Keywords | Status     |
| ----- | ----------------------- | --------------------- | -------- | ---------- |
| `en`  | `keyword_pool.json`     | `blog/en/<slug>.html` | 56+      | live       |
| `ja`  | `keyword_pool_ja.json`  | `blog/ja/<slug>.html` | 50       | live       |
| `zh`  | `keyword_pool_zh.json`  | `blog/zh/<slug>.html` | 50       | live (zh-Hant, TW/HK/SG/MY) |
| `ko`  | `keyword_pool_ko.json`  | `blog/ko/<slug>.html` | 0        | reserved (file not yet created) |

## CLI

```powershell
# default — English (backward compatible with existing schtasks)
python generate.py

# Japanese
python generate.py --lang ja

# Traditional Chinese
python generate.py --lang zh
```

## published.json schema

Legacy entries (no `lang` key) are treated as `en` for de-duplication. New entries:

```json
{
  "kw": "韓国 占い 当たる 種類",
  "slug": "korean-fortune-types",
  "title": "...",
  "category": "korean_astrology_intro",
  "lang": "ja",
  "vol": 22000,
  "published_at": "2026-05-06T13:00:00"
}
```

## Recommended schtask split (5x daily — already exists)

The 5 daily Windows scheduled tasks were registered for `en`-only. You can rebalance
without re-registering by editing each task's argument list to add `--lang <code>`.
Recommended distribution:

| Time   | Task name                          | Arg suggestion         | Rationale                              |
| ------ | ---------------------------------- | ---------------------- | -------------------------------------- |
| 06:00  | `KunStudio_SEO_BlogFactory_0600`   | `--lang ko`            | Korean morning peak (when ko pool added) |
| 09:00  | `KunStudio_SEO_BlogFactory_0900`   | `--lang en`            | EU/UK morning + US East late night     |
| 13:00  | `KunStudio_SEO_BlogFactory_1300`   | `--lang ja`            | Japan afternoon peak                   |
| 17:00  | `KunStudio_SEO_BlogFactory_1700`   | `--lang zh`            | Greater China afternoon peak           |
| 21:00  | `KunStudio_SEO_BlogFactory_2100`   | `--lang en` (fallback) | US prime time + free slot              |

Until a `keyword_pool_ko.json` is added, the 06:00 slot will safely log
`[SKIP] keyword pool missing` and exit with no work. Existing schtasks calling
`generate.py` with no args continue to produce English posts as before.

## Schtask edit (when ready)

Do **not** delete and re-register the schtasks (CRON_SECRET / startup boundary safety).
Use `schtasks /Change /TN <name> /TR "<new command>"` to swap arguments only.

```powershell
schtasks /Change /TN KunStudio_SEO_BlogFactory_1300 /TR `
  "python C:\Users\hdh02\Desktop\cheonmyeongdang\departments\seo_blog_factory\generate.py --lang ja"
```

## Files

- `generate.py` — multi-lang generator (defaults to `en` for backward-compat)
- `keyword_pool.json` — English (56+ keywords across saju / k-culture / k-beauty / k-food / etc.)
- `keyword_pool_ja.json` — Japanese (50 keywords, 5 categories × 10)
- `keyword_pool_zh.json` — Traditional Chinese (50 keywords, 5 categories × 10)
- `published.json` — append-only history with `lang` field (legacy entries default to `en`)
- `logs/factory_YYYY-MM-DD.log` — per-day log

## Category breakdown

### Japanese (`keyword_pool_ja.json`)
- `korean_astrology_intro` — 韓国占い入門 (10)
- `saju_technical` — 四柱推命の技術解説 (10)
- `kpop_kdrama_hook` — K-POP/韓ドラ占い (10)
- `marriage_compatibility` — 結婚・相性 (10)
- `career_money_health` — 仕事/金運/健康 (10)

### Traditional Chinese (`keyword_pool_zh.json`)
- `korean_bazi_intro` — 韓國八字命理入門 (10)
- `saju_technical` — 四柱命理技術 (10)
- `kpop_kdrama_hook` — K-POP/韓劇命盤 (10)
- `marriage_compatibility` — 八字合婚 (10)
- `career_wealth_health` — 事業/財運/健康 (10)

## Next steps (out of scope for this commit)

- Vercel route handling for `/blog/ja/*` and `/blog/zh/*` (currently markdown produced
  but main domain `vercel.json` rewrites untouched per task scope)
- `keyword_pool_ko.json` to enable Korean slot at 06:00
- Hreflang tag injection for cross-language discovery
- sitemap.xml multi-language entries
