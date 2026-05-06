# Deprecated influencer outreach artifacts (2026-05-06)

These files were retired by user decision on 2026-05-06.

| File | Reason |
|------|--------|
| `candidates_2026_05_06_DEPRECATED_unverified.json` | All 50 candidates were email-unverified guesses. Replaced by the curated `global_50_2026_05_06.json` set in the parent folder, which gates first-batch sends to public-listed business emails only. |
| `dm_batch_1_2026_05_06_DEPRECATED.md` | DM-style outreach (TikTok/IG cold DM) ran into anti-spam friction. Replaced by language-specific email drafts in `drafts_global_2026_05_06/` plus the polite `dm_templates_2026_05_06.md` for the few platforms (PTT/Dcard/X/LINE) that have no email path. |

**Live successors (parent folder)**:
- `global_50_2026_05_06.json` — 50 curated candidates, 4 languages, verification-gated
- `drafts_global_2026_05_06/` — 50 personalized email drafts (txt)
- `send_global_50.py` — Gmail SMTP sender (per-minute pacing, 100/day cap)
- `outreach_log.json` — single source of truth for sent records (already 1 success: `@chelc_cooky` Philippines)
- `sent_log_global_2026_05_06.json` — campaign-specific log (currently empty — all 50 still pending email verification)

Do not delete this folder — kept for audit trail and pattern reference.
