"""influencer_outreach — affiliate cold email 자동 생성기 (수동 검토 후 발송).

흐름:
1. targets/manual.csv 에 사용자가 직접 영문 K-culture 크리에이터 추가 (name, email, channel, niche, sub_count)
2. 본 스크립트가 각 row 별로 personalize 영문 cold email 생성 → output/{idx}_{name}.txt
3. 사용자가 review 후 send_emails.py 실행 → Gmail send (이미 라이브)

Affiliate URL: Gumroad/Mega Bundle 에 ?ref=<creator-handle> 추가하면 자동 30%
"""
import os
import sys
import csv
import json
import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
TARGETS_CSV = ROOT / "targets" / "manual.csv"
OUTPUT_DIR = ROOT / "sent" / f"drafts_{datetime.date.today()}"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EMAIL_TEMPLATE = """Subject: 30% commission per sale — Korean culture content collab (no upfront fee, just affiliate link)

Hi {first_name},

I've been watching your {channel_type} channel covering {niche} — {personalized_hook}.

I'm {sender_name}, a Korean indie creator (KunStudio) running a small library of English-language Korean culture digital products:
- Korean Saju Birth Chart Reading ($9.99)
- K-Beauty 10-Step Skincare Guide ($7.99)
- K-Drama Character Saju Decoder ($9.99)
- Korean Recipe Meal Planner ($7.99)
- Mega Bundle (20 ebooks + audiobooks) — $70
- Lifetime (every future ebook forever) — $497

→ https://cheonmyeongdang.vercel.app/bundle

{specific_product_for_niche} — feels like a natural fit for your audience.

Affiliate offer (zero risk for you):
- **30% commission** on every sale through your unique link (Gumroad tracks automatically)
- **No cash upfront** — purely revenue share
- **Free copy** for honest review before promoting (just say yes)
- Custom UTM-tracked link with your handle: e.g. https://cheonmyeongdang.vercel.app/bundle?ref={creator_handle}

If interested, just reply "send the free copy" and I'll send within 24h. No pressure if not.

Best,
{sender_name}
KunStudio · Korean Culture Digital Products
ghdejr11@gmail.com · https://cheonmyeongdang.vercel.app
"""


def render(row):
    first_name = row.get("name", "").split()[0] or "there"
    niche = row.get("niche", "Korean culture")
    channel_type = row.get("channel", "YouTube")
    handle = row.get("creator_handle", first_name.lower())

    # niche → product mapping
    niche_lower = niche.lower()
    if "k-pop" in niche_lower or "kpop" in niche_lower:
        product = "Our K-Pop Idol Saju Decoder breaks down 4-pillar charts of BTS, BLACKPINK and other major group members"
    elif "beauty" in niche_lower or "skincare" in niche_lower:
        product = "Our K-Beauty 10-Step Skincare Guide ($7.99) covers product layering science with Korean-only ingredient breakdown"
    elif "drama" in niche_lower or "kdrama" in niche_lower:
        product = "Our K-Drama Character Saju Decoder maps personality types of beloved K-drama leads through Saju framework"
    elif "travel" in niche_lower or "vlog" in niche_lower:
        product = "Our Korea Travel Phrases ebook + Hidden Gems guide complements travel content with practical companion material"
    elif "food" in niche_lower or "recipe" in niche_lower or "cook" in niche_lower:
        product = "Our Korean Recipe Meal Planner gives 4-week meal plans with banchan rotation"
    elif "language" in niche_lower or "learn" in niche_lower:
        product = "Our Korean cultural context ebook complements language learning with the 'why' behind expressions"
    elif "saju" in niche_lower or "astro" in niche_lower or "fortune" in niche_lower:
        product = "Our Korean Saju Birth Chart Reading ebook is the most accessible English-language Saju primer"
    else:
        product = "Our Korean culture catalog has a fit for many K-content niches"

    hook = row.get("personalized_hook", "your content quality stands out for the niche")

    return EMAIL_TEMPLATE.format(
        first_name=first_name,
        channel_type=channel_type,
        niche=niche,
        personalized_hook=hook,
        sender_name="Deokgu (Hong Deokgu)",
        specific_product_for_niche=product,
        creator_handle=handle,
    )


def main():
    if not TARGETS_CSV.exists():
        print(f"[INIT] {TARGETS_CSV} 없음. 빈 CSV 작성.")
        TARGETS_CSV.parent.mkdir(parents=True, exist_ok=True)
        TARGETS_CSV.write_text(
            "name,email,channel,niche,sub_count,personalized_hook,creator_handle\n"
            "EXAMPLE Jane Doe,jane@example.com,YouTube,k-beauty review,42000,your retinol layering vid was super clear,janedoe\n",
            encoding="utf-8"
        )
        print(f"      → {TARGETS_CSV} 에 영문 K-culture 크리에이터 row 추가 후 재실행")
        print(f"      → 행마다 1 메일 draft → {OUTPUT_DIR}/")
        return

    rows = list(csv.DictReader(TARGETS_CSV.open(encoding="utf-8")))
    rows = [r for r in rows if r.get("email") and not r["name"].startswith("EXAMPLE")]
    if not rows:
        print(f"[WARN] {TARGETS_CSV} 에 EXAMPLE 외 row 없음. 추가 후 재실행")
        return

    print(f"[OK] {len(rows)} target → drafting...")
    for i, row in enumerate(rows, 1):
        text = render(row)
        out = OUTPUT_DIR / f"{i:03d}_{row.get('name','x').replace(' ','_')}.txt"
        out.write_text(text, encoding="utf-8")
        print(f"  [{i:03d}] {row['name']} ({row.get('niche','?')}) → {out.name}")

    print(f"\n[DONE] {len(rows)} drafts → {OUTPUT_DIR}/")
    print(f"       Review them, then run: python send_emails.py {OUTPUT_DIR.name}")


if __name__ == "__main__":
    main()
