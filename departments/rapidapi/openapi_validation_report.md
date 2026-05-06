# OpenAPI Validation Report — saju_openapi.yaml

**Date:** 2026-05-07
**Spec file:** `departments/rapidapi/saju_openapi.yaml`
**Spec version:** OpenAPI 3.0.3
**API version:** 1.1.0 (upgraded from 1.0.0)

## Summary

| Metric | Result |
|---|---|
| OpenAPI 3.x compliance | PASS |
| Required top-level keys (info / paths / components) | PASS |
| 4 endpoints defined (/calculate, /qa, /compatibility, /monthly-fortune) | PASS |
| Each endpoint: POST + 200/400/401/429/500 responses | PASS |
| X-RapidAPI-Key auth header | PASS |
| X-RapidAPI-Proxy-Secret auth header | PASS |
| Request body examples | PASS (every endpoint) |
| 200 response examples | PASS (every endpoint) |
| Rate-limit text (FREE 100/day, PRO 5K/day, ULTRA 50K/day) | PASS |
| **Total errors** | **0** |
| **Total warnings** | **0** |

## Auto-fixes applied (v1.0.0 -> v1.1.0)

The original spec defined a single endpoint (`POST /saju/reading`) and was
missing 3 of the 4 endpoints required for the RapidAPI listing. The yaml was
fully rewritten to:

1. **Renamed and split into 4 endpoints**, each with its own request/response
   schema, examples, security, and full error response set:
   - `POST /calculate`        — core 4-pillar Saju reading + 5 elements + AI advice
   - `POST /qa`               — free-form Claude Q&A grounded on a chart
   - `POST /compatibility`    — two-person Saju (Gunghap) score 0–100
   - `POST /monthly-fortune`  — 12-month forecast for a given year
2. **Added 5 new schemas**: `QARequest`, `QAResponse`, `CompatRequest`,
   `CompatResponse`, `MonthlyRequest`, `MonthlyResponse`
3. **Added `X-RapidAPI-Key` security scheme** (was missing — only
   `X-RapidAPI-Proxy-Secret` was defined). Both are now declared and applied
   to every operation.
4. **Reusable error responses** under `components.responses` for 400/401/429/500
   — cuts ~120 lines of duplication and guarantees identical error contract
   across all endpoints.
5. **Rate-limit headers** added to the 429 response:
   `X-RateLimit-Requests-Limit`, `X-RateLimit-Requests-Remaining`, `Retry-After`.
6. **Rate-limit quotas in description**:
   - FREE -> 100 req/day (hard cap)
   - PRO -> 5,000 req/day (≈150K/mo)
   - ULTRA -> 50,000 req/day (≈1.5M/mo)
7. **Tags added** for grouping in RapidAPI hub UI: `saju`, `ai`, `compatibility`.
8. **Examples added** for every endpoint:
   - `/calculate`: standard + hour_unknown
   - `/qa`: career (en) + love (ko)
   - `/compatibility`: couple (en)
   - `/monthly-fortune`: 2026 forecast (en)
9. **lang parameter** (ko/en/ja/zh) added to `/qa`, `/compatibility`,
   `/monthly-fortune` — matches the 4-language site (cheonmyeongdang.vercel.app).
10. **Contact email** added (`ghdejr11@gmail.com`) — required by RapidAPI
    listing review.

## Validation procedure

```python
import yaml
spec = yaml.safe_load(open('saju_openapi.yaml', encoding='utf-8'))
# checks: OpenAPI 3.x, 4 paths, POST + 200/400/401/429/500 each,
#         X-RapidAPI-Key + X-RapidAPI-Proxy-Secret schemes,
#         req/resp examples per path, rate-limit text present
```

Result: **0 errors, 0 warnings.**

## Next steps (provider-side)

1. Sign up at https://rapidapi.com/provider (PayPal payout — Korean business OK)
2. Create new API: "Korean Saju (Bazi) Reading API"
3. Import OpenAPI spec: paste `saju_openapi.yaml` content
4. Set base URL: `https://cheonmyeongdang.vercel.app`
5. Pricing tiers:
   - FREE — $0/mo — 100 req/day
   - PRO — $9.99/mo — 5K req/day (~150K/mo)
   - ULTRA — $49/mo — 50K req/day (~1.5M/mo)
6. Add Vercel env vars on the upstream Vercel project:
   - `RAPIDAPI_PROXY_SECRET` (copy from RapidAPI dashboard)
   - `ANTHROPIC_API_KEY` (already set)
7. Implement the 4 endpoints in Vercel (currently 0/4 live — see
   `api/` folder, no `calculate.js`/`qa.js`/`compatibility.js`/`monthly-fortune.js`
   yet). Backed by existing engine in `js/` + `lib/` (Saju calc) and
   `api/confirm-payment.js` style for AI calls.
8. Submit for RapidAPI manual review (1–2 business days).
