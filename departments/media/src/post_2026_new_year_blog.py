"""신년운세 2026 블로그 출시 — 다채널 SNS 자동 포스팅 (Bluesky / Discord / Mastodon / X / Threads / Instagram)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from multi_poster import send_all_direct

URL = "https://cheonmyeongdang.vercel.app/blog/2026-new-year-fortune-saju.html"

CONTENT = (
    "🐎 2026 병오년(丙午) 신년운세 무료 분석\n\n"
    "12개월 타임라인 + 12띠 흐름까지 한번에. 정통 명리학 기반.\n"
    "정밀 종합 풀이는 ₩29,900 (24시간 환불 보장)\n\n"
    f"👉 {URL}\n\n"
    "#신년운세2026 #병오년 #사주 #천명당 #무료운세"
)

if __name__ == "__main__":
    print("=" * 50)
    print("신년운세 2026 SNS 자동 포스팅 시작")
    print("=" * 50)
    res = send_all_direct(CONTENT, image_url=None, skip_coupang=True)
    for ch, ok in res.items():
        emoji = "OK" if ok else "FAIL"
        print(f"  [{emoji}] {ch}")
    print(f"성공: {sum(1 for v in res.values() if v)}/{len(res)}")
