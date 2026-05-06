"""KORLENS — 한국 여행 가이드 다채널 SNS 자동 포스팅 (Bluesky/Discord/Mastodon/X/Threads/Facebook)."""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from multi_poster import send_all_direct

URL = "https://korlens.app"

VARIANTS_KO = [
    "🇰🇷 한국 여행 처음이세요? KORLENS — 17개 도시 여행지/맛집/숙소를 현지인 픽으로 안내합니다.",
    "🌸 봄 한국 여행 가이드 — 서울·부산·경주·제주까지, 4개 언어 한 곳에서.",
    "한국 여행 정보 흩어져서 답답하셨나요? KORLENS 가 모았습니다 (영/일/중 지원).",
]

VARIANTS_EN = [
    "🇰🇷 First time in Korea? KORLENS — locally curated picks for restaurants, stays, and itineraries across 17 regions.",
    "🌸 Spring travel in Korea — Seoul, Busan, Gyeongju, Jeju & more. Free guide, 4 languages.",
    "Stop scrolling 30 blogs for one Korea trip. KORLENS has it in one place.",
]

# 채널별 다른 톤: x/threads = 영문, bluesky = 한+영, discord = 한국어
def message():
    ko = random.choice(VARIANTS_KO)
    en = random.choice(VARIANTS_EN)
    return (
        f"{en}\n\n"
        f"{ko}\n\n"
        f"👉 {URL}\n\n"
        "#Korea #KoreaTravel #VisitKorea #한국여행 #SeoulTravel #JejuIsland #Gyeongju"
    )

if __name__ == "__main__":
    print("=" * 50)
    print("KORLENS 런칭/홍보 SNS 자동 포스팅")
    print("=" * 50)
    res = send_all_direct(message(), image_url=None, skip_coupang=True)
    for ch, ok in res.items():
        emoji = "OK" if ok else "FAIL"
        print(f"  [{emoji}] {ch}")
    print(f"성공: {sum(1 for v in res.values() if v)}/{len(res)}")
