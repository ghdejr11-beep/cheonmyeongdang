#!/usr/bin/env python3
"""
KDP 20권 홍보 포스트를 posts_unified_queue.json 에 투입.

사용:
    python kdp_promo.py --dry-run    # 큐 수정 없이 미리보기
    python kdp_promo.py               # 실제 큐에 append
    python kdp_promo.py --days 7 --per-day 3   # 기간·하루당 분산

기존 unified_poster.py가 매시간 실행되며 scheduled_at 도달분만 자동 발송.
"""
import json, sys, os, argparse, datetime, random
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"D:\cheonmyeongdang\departments\media")
BOOKS_PATH = BASE / "src" / "kdp_books.json"
QUEUE_PATH = BASE / "scheduler" / "posts_unified_queue.json"


def amazon_link(asin: str | None) -> str:
    if asin:
        return f"https://www.amazon.com/dp/{asin}"
    # ASIN 미입력시 저자 검색 페이지로 fallback (Deokgu Studio)
    return "https://www.amazon.com/s?k=Deokgu+Studio&i=digital-text"


def build_korean(book) -> str:
    one = book["one_liner_ko"]
    title = book["title"]
    link = amazon_link(book.get("asin"))
    return f"📚 {title}\n\n{one}\n\n🔗 아마존에서 보기: {link}"


def build_english(book) -> str:
    one = book["one_liner_en"]
    title = book["title"]
    link = amazon_link(book.get("asin"))
    tags = book.get("hashtags_en", "#KDP #eBook")
    # X 280자 제한 대응
    body = f"📚 {title}\n\n{one}\n\n{link}\n\n{tags}"
    return body[:280]


def load_queue():
    if QUEUE_PATH.exists():
        try:
            return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_queue(q):
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_PATH.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")


def make_schedule(n_posts: int, days: int, per_day: int):
    """오늘 이후 days일간 매일 per_day개씩 slot 생성. 9시/13시/19시 KST."""
    slots_per_day = [9, 13, 19][:per_day]
    if len(slots_per_day) < per_day:
        # per_day > 3 이면 자연 분포
        step = 12 // per_day
        slots_per_day = [9 + i * step for i in range(per_day)]
    out = []
    today = datetime.date.today()
    for d in range(days):
        date = today + datetime.timedelta(days=d + 1)  # 내일부터
        for h in slots_per_day:
            out.append(datetime.datetime(date.year, date.month, date.day, h, 0))
            if len(out) >= n_posts:
                return out
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--per-day", type=int, default=3)
    args = parser.parse_args()

    books = json.loads(BOOKS_PATH.read_text(encoding="utf-8"))
    queue = load_queue()
    existing_ids = {p.get("id") for p in queue if isinstance(p, dict)}

    schedules = make_schedule(len(books), args.days, args.per_day)
    new_posts = []
    for i, book in enumerate(books):
        if i >= len(schedules):
            break
        slot = schedules[i]
        pid_ko = f"kdp-{book['slug']}-ko"
        pid_en = f"kdp-{book['slug']}-en"

        for pid, builder, targets in [
            (pid_ko, build_korean, ["telegram"]),
            (pid_en, build_english, ["x"]),
        ]:
            if pid in existing_ids:
                continue
            new_posts.append({
                "id": pid,
                "service": "kdp",
                "targets": targets,
                "body": builder(book),
                "scheduled_at": slot.isoformat() + "+09:00",
                "created_at": datetime.datetime.now().isoformat() + "+09:00",
            })

    print(f"기존 큐: {len(queue)}개 / 신규 {len(new_posts)}개 / 스케줄 기간: {args.days}일")
    print()
    print("─── 샘플 3개 미리보기 ───")
    for p in new_posts[:3]:
        print(f"[{p['scheduled_at']}] {p['targets']} {p['id']}")
        print("  " + p["body"][:100].replace("\n", " / "))
        print()

    if args.dry_run:
        print("⚠️  dry-run: 큐 저장 안 함.")
        return

    queue.extend(new_posts)
    save_queue(queue)
    print(f"✅ {QUEUE_PATH} 에 {len(new_posts)}개 append 완료. (총 {len(queue)}개)")
    asin_missing = sum(1 for b in books if not b.get("asin"))
    if asin_missing:
        print(f"ℹ️  ASIN 미입력 {asin_missing}권 → 저자 검색 URL로 fallback. KDP Bookshelf에서 ASIN 수집 후 kdp_books.json 업데이트 권장.")


if __name__ == "__main__":
    main()
