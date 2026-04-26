#!/usr/bin/env python3
"""
KDP 전자책 긴급 홍보 — 플랫폼별 최적화된 메시지를 즉시 다채널 발사.

플랫폼 특성:
  Bluesky    : 300자, 영문, 해시태그 3개, 텍스트 중심
  Mastodon   : 500자, 영문, 해시태그 5개, 커뮤니티 톤
  X (Twitter): 280자, 영문, 공격적 CTA + 해시태그
  Discord    : 2000자 여유, 한글, 긴 호흡 리뷰
  Telegram   : 4096자 여유, 한글, 한영 병기 + 링크
  Instagram  : 이미지 URL 있으면 포함 (표지 이미지 필요)

사용:
  python kdp_boost.py                    # 오늘 순번 3권 발사
  python kdp_boost.py --books adhd-planner,introvert-confidence
  python kdp_boost.py --dry-run          # 메시지만 출력, 발사 X
"""
import json
import sys
import os
import argparse
import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_poster import send_all_direct

BASE = Path(__file__).resolve().parents[1]
BOOKS_PATH = BASE / "src" / "kdp_books.json"


def amazon_link(asin):
    if asin:
        return f"https://www.amazon.com/dp/{asin}"
    return "https://www.amazon.com/s?k=Deokgu+Studio&i=digital-text"


def amazon_cover_url(asin):
    if not asin:
        return None
    return f"https://m.media-amazon.com/images/P/{asin}.01.L.jpg"


def load_books():
    return json.loads(BOOKS_PATH.read_text(encoding="utf-8"))


# ───────── 플랫폼별 메시지 빌더 ─────────
def build_bluesky(book):
    title = book["title"]
    one = book["one_liner_en"]
    price = book.get("price_usd", "")
    link = amazon_link(book.get("asin"))
    tags = book.get("hashtags_en", "#KDP").split()[:3]
    body = f"📚 {title}\n{one}\n${price} → {link}\n{' '.join(tags)}"
    return body[:300]


def build_mastodon(book):
    title = book["title"]
    one = book["one_liner_en"]
    price = book.get("price_usd", "")
    link = amazon_link(book.get("asin"))
    tags = book.get("hashtags_en", "#KDP")
    body = (
        f"📚 New release: {title}\n\n"
        f"{one}\n\n"
        f"💵 ${price} on Amazon Kindle\n"
        f"🔗 {link}\n\n"
        f"{tags}"
    )
    return body[:500]


def build_x(book):
    title = book["title"]
    one = book["one_liner_en"]
    link = amazon_link(book.get("asin"))
    tags = book.get("hashtags_en", "#KDP").split()[:3]
    body = f"{title}\n\n{one}\n\n👉 {link}\n{' '.join(tags)}"
    if len(body) > 280:
        # 영문 한줄 강제 단축
        short = f"{title} — {one[:100]}\n{link}\n{' '.join(tags[:2])}"
        return short[:280]
    return body


def build_discord(book):
    title = book["title"]
    one_ko = book.get("one_liner_ko", "")
    one_en = book["one_liner_en"]
    price = book.get("price_usd", "")
    link = amazon_link(book.get("asin"))
    return (
        f"📚 **신작 전자책 — {title}**\n\n"
        f"🇰🇷 {one_ko}\n"
        f"🇺🇸 {one_en}\n\n"
        f"💵 가격: ${price}\n"
        f"🔗 {link}\n\n"
        f"_Deokgu Studio / KunStudio Presents_"
    )


def build_telegram(book):
    title = book["title"]
    one_ko = book.get("one_liner_ko", "")
    one_en = book["one_liner_en"]
    price = book.get("price_usd", "")
    link = amazon_link(book.get("asin"))
    return (
        f"📚 <b>{title}</b>\n\n"
        f"🇰🇷 {one_ko}\n"
        f"🇺🇸 {one_en}\n\n"
        f"💵 ${price} | Amazon Kindle\n"
        f"👉 {link}"
    )


def build_threads(book):
    title = book["title"]
    one_en = book["one_liner_en"]
    one_ko = book.get("one_liner_ko", "")
    price = book.get("price_usd", "")
    link = amazon_link(book.get("asin"))
    tags = " ".join(book.get("hashtags_en", "#KDP").split()[:3])
    body = (
        f"📚 {title}\n\n"
        f"{one_en}\n\n"
        f"🇰🇷 {one_ko}\n"
        f"💵 ${price} | {link}\n\n"
        f"{tags}"
    )
    return body[:500]


def build_instagram(book):
    title = book["title"]
    one_en = book["one_liner_en"]
    price = book.get("price_usd", "")
    link = amazon_link(book.get("asin"))
    tags = book.get("hashtags_en", "#KDP")
    return (
        f"📚 {title}\n\n"
        f"{one_en}\n\n"
        f"💵 ${price}\n"
        f"🔗 Link in bio → {link}\n\n"
        f"{tags} #Kindle #eBook #ReadMore #SelfHelp #NewRelease"
    )


# ───────── 발사 ─────────
def promote_book(book, dry_run=False):
    asin = book.get("asin")
    cover = amazon_cover_url(asin)

    messages = {
        "bluesky": build_bluesky(book),
        "discord": build_discord(book),
        "mastodon": build_mastodon(book),
        "x": build_x(book),
        "threads": build_threads(book),
        "instagram": build_instagram(book),
    }

    print(f"\n{'=' * 60}")
    print(f"📚 {book['title']}  ({asin or 'no-ASIN'})")
    print(f"{'=' * 60}")
    for k, v in messages.items():
        print(f"\n[{k.upper()}] ({len(v)} chars)")
        print(v)

    if dry_run:
        return {"dry_run": True, "messages": messages}

    from multi_poster import post_bluesky, post_discord, post_mastodon, post_x, post_threads, post_instagram, _load_secrets
    env = _load_secrets()
    results = {}

    for name, fn in [
        ("bluesky", lambda: post_bluesky(messages["bluesky"], env)),
        ("discord", lambda: post_discord(messages["discord"], env)),
        ("mastodon", lambda: post_mastodon(messages["mastodon"], env)),
        ("x", lambda: post_x(messages["x"], env)),
        ("threads", lambda: post_threads(messages["threads"], env)),
    ]:
        try:
            ok, _ = fn()
            results[name] = ok
        except Exception as e:
            results[name] = False
            print(f"[{name}] {e}")

    if cover:
        try:
            ok, _ = post_instagram(messages["instagram"], cover, env)
            results["instagram"] = ok
        except Exception as e:
            results["instagram"] = False
            print(f"[instagram] {e}")

    # Telegram은 auto_promo.send_telegram() 경로로 가는데 여기서 별도 안 함
    # (Postiz가 Telegram 담당 — send_telegram text는 html이라 여기 쓰면 안 됨)

    return results


def pick_books(books, filter_slugs=None, limit=3):
    if filter_slugs:
        return [b for b in books if b["slug"] in filter_slugs]
    # 기본: 가격 높은 순 상위 limit
    return sorted(books, key=lambda b: float(b.get("price_usd", 0)), reverse=True)[:limit]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--books", default="", help="쉼표 구분 slug 목록. 빈값이면 가격 상위 3권")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    books = load_books()
    slugs = [s.strip() for s in args.books.split(",") if s.strip()] if args.books else None
    selected = pick_books(books, slugs, args.limit)

    print(f"\n선정 {len(selected)}권:")
    for b in selected:
        print(f"  - {b['slug']}: {b['title']} (${b.get('price_usd')})")

    all_results = {}
    for b in selected:
        r = promote_book(b, dry_run=args.dry_run)
        all_results[b["slug"]] = r

    print(f"\n{'=' * 60}")
    print("최종 결과:")
    print("=" * 60)
    print(json.dumps(all_results, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
