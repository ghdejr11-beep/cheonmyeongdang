#!/usr/bin/env python3
"""
KORLENS 일일 POI 수집기 (v2) — 관광지·맛집·숙소 전수집.

매일 실행:
- 관광지 (contentTypeId=12) → restaurants table은 아니고 기존 mock-places.ts (유지)
- 맛집 (contentTypeId=39) → Supabase `restaurants`
- 숙소 (contentTypeId=32) → Supabase `accommodations`

Supabase SERVICE_ROLE_KEY 필요. 없으면 JSON 캐시만 저장 (D:\tmp\korlens_poi_cache\).

Task Scheduler: 매일 08:10 (관광지 수집 08:00 뒤)
"""
import os, sys, json, re, urllib.request, urllib.parse, urllib.error, datetime, random
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

KORLENS_ENV = Path(r"D:\korlens\.env.local")
CACHE_DIR = Path(r"D:\tmp\korlens_poi_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

TOUR_ENDPOINT = "https://apis.data.go.kr/B551011/KorService2"

AREA_TO_REGION = {
    "1": "seoul", "2": "incheon", "3": "daejeon", "4": "daegu", "5": "gwangju",
    "6": "busan", "7": "ulsan", "8": "sejong", "31": "gyeonggi", "32": "gangwon",
    "33": "chungbuk", "34": "chungnam", "35": "gyeongbuk", "36": "gyeongnam",
    "37": "jeonbuk", "38": "jeonnam", "39": "jeju",
}

# cat3 → category 매핑 (맛집)
RESTAURANT_CATS = {
    "A05020100": "한식", "A05020200": "양식", "A05020300": "일식",
    "A05020400": "중식", "A05020500": "이국적음식", "A05020600": "패스트푸드",
    "A05020700": "카페", "A05020800": "자동판매",
}
# cat3 → type 매핑 (숙소)
ACCOM_TYPES = {
    "B02010100": "관광호텔", "B02010200": "수상관광호텔", "B02010300": "전통호텔",
    "B02010400": "가족호텔", "B02010500": "호스텔", "B02010600": "여관",
    "B02010700": "모텔", "B02010900": "콘도미니엄", "B02011000": "유스호스텔",
    "B02011100": "펜션", "B02011200": "민박", "B02011300": "게스트하우스",
    "B02011400": "홈스테이", "B02011500": "서비스드레지던스", "B02011600": "한옥",
}


def load_env():
    env = {}
    if KORLENS_ENV.exists():
        for line in KORLENS_ENV.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# ---------- TourAPI ----------

def fetch_area_pois(api_key, content_type_id, area_code, page=1, num=30):
    params = {
        "serviceKey": api_key, "MobileOS": "ETC", "MobileApp": "KORLENS",
        "_type": "json", "numOfRows": str(num), "pageNo": str(page),
        "arrange": "O",  # 수정일순
        "contentTypeId": str(content_type_id),
        "areaCode": str(area_code),
    }
    url = f"{TOUR_ENDPOINT}/areaBasedList2?{urllib.parse.urlencode(params, safe='%')}"
    req = urllib.request.Request(url, headers={"User-Agent": "KORLENS-POI/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} area={area_code} ctype={content_type_id}")
        return []
    body = data.get("response", {}).get("body", {})
    items = body.get("items")
    if not items or items == "":
        return []
    item = items.get("item", [])
    return item if isinstance(item, list) else [item]


# ---------- Supabase upsert ----------

def supabase_upsert(supabase_url, service_key, table, rows):
    if not rows:
        return {"ok": True, "count": 0}
    url = f"{supabase_url.rstrip('/')}/rest/v1/{table}?on_conflict=content_id"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    data = json.dumps(rows, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return {"ok": True, "status": r.status, "count": len(rows)}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "body": e.read().decode(errors="ignore")[:400]}


def item_to_restaurant(item):
    return {
        "content_id": item.get("contentid"),
        "name": (item.get("title") or "").strip(),
        "region_id": AREA_TO_REGION.get(item.get("areacode", ""), "seoul"),
        "sigungu_code": item.get("sigungucode"),
        "address": (item.get("addr1") or "").strip() or None,
        "lat": float(item.get("mapy", 0)) or None,
        "lng": float(item.get("mapx", 0)) or None,
        "image_url": item.get("firstimage") or item.get("firstimage2") or None,
        "category": RESTAURANT_CATS.get(item.get("cat3", ""), "기타"),
        "tel": item.get("tel") or None,
        "overview": None,  # 상세 API로 추후 업데이트
        "source": "tour_api",
        "is_active": True,
        "last_updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def item_to_accommodation(item):
    return {
        "content_id": item.get("contentid"),
        "name": (item.get("title") or "").strip(),
        "region_id": AREA_TO_REGION.get(item.get("areacode", ""), "seoul"),
        "sigungu_code": item.get("sigungucode"),
        "address": (item.get("addr1") or "").strip() or None,
        "lat": float(item.get("mapy", 0)) or None,
        "lng": float(item.get("mapx", 0)) or None,
        "image_url": item.get("firstimage") or item.get("firstimage2") or None,
        "type": ACCOM_TYPES.get(item.get("cat3", ""), "기타"),
        "tel": item.get("tel") or None,
        "overview": None,
        "source": "tour_api",
        "is_active": True,
        "last_updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


# ---------- Main ----------

def main():
    env = load_env()
    tour_key = env.get("TOUR_API_KEY")
    supabase_url = env.get("NEXT_PUBLIC_SUPABASE_URL")
    service_key = env.get("SUPABASE_SERVICE_ROLE_KEY") or env.get("SUPABASE_SERVICE_KEY")

    if not tour_key:
        print("❌ TOUR_API_KEY 없음")
        sys.exit(1)

    has_supabase = bool(supabase_url and service_key)
    if not has_supabase:
        print("ℹ️ SUPABASE_SERVICE_ROLE_KEY 없음 → JSON 캐시만 저장")

    today = datetime.date.today()
    random.seed(today.toordinal())
    area_codes = list(AREA_TO_REGION.keys())
    random.shuffle(area_codes)

    # 오늘 2개 지역 × 맛집 5개 + 숙소 5개 수집
    targets = area_codes[:2]
    log = {"date": today.isoformat(), "restaurants": 0, "accommodations": 0, "errors": []}

    all_restaurants, all_accoms = [], []

    for area in targets:
        region = AREA_TO_REGION[area]

        # 맛집 (39)
        try:
            items = fetch_area_pois(tour_key, 39, area, num=10)
            rows = [item_to_restaurant(i) for i in items if i.get("contentid") and i.get("title")]
            rows = [r for r in rows if r["content_id"] and r["lat"] and r["lng"]][:5]
            all_restaurants.extend(rows)
            print(f"  {region} 맛집 {len(rows)}건 수집")
        except Exception as e:
            log["errors"].append(f"{region} restaurant: {e}")

        # 숙소 (32)
        try:
            items = fetch_area_pois(tour_key, 32, area, num=10)
            rows = [item_to_accommodation(i) for i in items if i.get("contentid") and i.get("title")]
            rows = [r for r in rows if r["content_id"] and r["lat"] and r["lng"]][:5]
            all_accoms.extend(rows)
            print(f"  {region} 숙소 {len(rows)}건 수집")
        except Exception as e:
            log["errors"].append(f"{region} accommodation: {e}")

    log["restaurants"] = len(all_restaurants)
    log["accommodations"] = len(all_accoms)

    # Save cache (항상)
    cache_file = CACHE_DIR / f"{today.isoformat()}.json"
    cache_file.write_text(json.dumps({
        "date": today.isoformat(),
        "restaurants": all_restaurants,
        "accommodations": all_accoms,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 cache {cache_file}")

    # Supabase upsert
    if has_supabase:
        if all_restaurants:
            r = supabase_upsert(supabase_url, service_key, "restaurants", all_restaurants)
            log["restaurants_upsert"] = r
            print(f"  restaurants upsert: {r}")
        if all_accoms:
            r = supabase_upsert(supabase_url, service_key, "accommodations", all_accoms)
            log["accommodations_upsert"] = r
            print(f"  accommodations upsert: {r}")

    log_file = LOG_DIR / f"poi_{today.isoformat()}.json"
    log_file.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ total: {log['restaurants']} restaurants + {log['accommodations']} accommodations")


if __name__ == "__main__":
    main()
