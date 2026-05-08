#!/usr/bin/env python3
"""
KORLENS 일일 관광지 자동 수집.
매일 1건 한국관광공사 TourAPI 4.0에서 새 관광지 추출 → mock-places.ts 자동 append.

Task Scheduler: 매일 08:00
"""
import os, sys, json, random, re, urllib.request, urllib.parse, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

KORLENS_ENV = Path(r"D:\korlens\.env.local")
MOCK_PLACES = Path(r"D:\korlens\lib\mock-places.ts")
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

ENDPOINT = "https://apis.data.go.kr/B551011/KorService2"

# areaCode → regionId (regions.ts와 매핑)
AREA_TO_REGION = {
    "1": "seoul", "2": "incheon", "3": "daejeon", "4": "daegu", "5": "gwangju",
    "6": "busan", "7": "ulsan", "8": "sejong", "31": "gyeonggi", "32": "gangwon",
    "33": "chungbuk", "34": "chungnam", "35": "gyeongbuk", "36": "gyeongnam",
    "37": "jeonbuk", "38": "jeonnam", "39": "jeju",
}


def load_env():
    env = {}
    for line in KORLENS_ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def fetch_area_places(api_key, area_code, page=1, num=20):
    params = {
        "serviceKey": api_key, "MobileOS": "ETC", "MobileApp": "KORLENS",
        "_type": "json", "numOfRows": str(num), "pageNo": str(page),
        "arrange": "O",  # 수정일순 (최신)
        "contentTypeId": "12",  # 12=관광지
        "areaCode": str(area_code),
    }
    url = f"{ENDPOINT}/areaBasedList2?{urllib.parse.urlencode(params, safe='%')}"
    req = urllib.request.Request(url, headers={"User-Agent": "KORLENS-Collector/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    body = data.get("response", {}).get("body", {})
    items = body.get("items")
    if not items or items == "":
        return []
    item = items.get("item", [])
    return item if isinstance(item, list) else [item]


def fetch_detail(api_key, content_id):
    params = {
        "serviceKey": api_key, "MobileOS": "ETC", "MobileApp": "KORLENS",
        "_type": "json", "contentId": str(content_id),
    }
    url = f"{ENDPOINT}/detailCommon2?{urllib.parse.urlencode(params, safe='%')}"
    req = urllib.request.Request(url, headers={"User-Agent": "KORLENS-Collector/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    body = data.get("response", {}).get("body", {})
    items = body.get("items")
    if not items or items == "":
        return None
    item = items.get("item", [])
    return (item[0] if isinstance(item, list) else item) if item else None


def existing_place_ids():
    txt = MOCK_PLACES.read_text(encoding="utf-8")
    return set(re.findall(r'id:\s*"([^"]+)"', txt))


def slugify(title, content_id):
    slug = re.sub(r"[^a-z0-9가-힣]+", "-", title.lower()).strip("-")[:30]
    if not slug:
        slug = f"p{content_id}"
    return f"{slug}-{content_id[-4:]}"


def generate_highlights(title, overview, area_region):
    """간단한 템플릿 기반 4종 하이라이트 (외국인/커플/가족/솔로)"""
    short = overview[:80] if overview else title
    return {
        "foreigner": f"한국관광공사 공식 등록 명소 · {title} 방문 시 다국어 안내 자료 확인 권장 · 대중교통 접근 가능",
        "couple": f"{title} 포토스팟 · 커플 데이트 코스 추천 · 인근 카페/식당 연계",
        "family": f"{title} 어린이/가족 관람 가능 · 유모차 접근성 현장 확인 권장 · 주차시설",
        "solo": f"{title} 평일 한산 · 혼자 사진 촬영 추천 · 주변 한적한 골목 탐방",
    }


def to_place_block(item, detail):
    content_id = item["contentid"]
    title = item.get("title", "").strip()
    addr = item.get("addr1", "").strip()
    area = item.get("areacode", "")
    region = AREA_TO_REGION.get(area, "seoul")
    lat = float(item.get("mapy", "0"))
    lng = float(item.get("mapx", "0"))
    image = item.get("firstimage") or item.get("firstimage2") or ""
    overview = (detail.get("overview", "") if detail else "").strip()
    overview = re.sub(r"<[^>]+>", "", overview)[:180]
    if not overview:
        overview = f"{title} — 한국관광공사 등록 관광지."

    slug = slugify(title, content_id)
    highlights = generate_highlights(title, overview, region)

    def escape(s):
        return (s or "").replace("\\", "\\\\").replace('"', '\\"')

    block = f'''  {{
    id: "{slug}",
    contentId: "{content_id}",
    nameKo: "{escape(title)}",
    regionId: "{region}",
    address: "{escape(addr)}",
    imageUrl: "{escape(image)}",
    lat: {lat},
    lng: {lng},
    overview:
      "{escape(overview)}",
    highlights: {{
      foreigner: "{escape(highlights['foreigner'])}",
      couple: "{escape(highlights['couple'])}",
      family: "{escape(highlights['family'])}",
      solo: "{escape(highlights['solo'])}",
    }},
    tags: ["자동수집", "TourAPI", "관광지"],
    crowdLevel: "medium",
  }},'''
    return slug, block


def main():
    env = load_env()
    api_key = env.get("TOUR_API_KEY")
    if not api_key:
        print("❌ TOUR_API_KEY 없음 (.env.local)")
        sys.exit(1)

    existing = existing_place_ids()
    print(f"📍 기존 {len(existing)}개")

    # 오늘 랜덤 지역 1개 선정 (날짜 기반 재현성)
    today = datetime.date.today()
    area_codes = list(AREA_TO_REGION.keys())
    random.seed(today.toordinal())
    random.shuffle(area_codes)

    added = 0
    log_entries = []
    for area in area_codes[:3]:  # 상위 3개 지역 순회하며 미수집 건 찾기
        try:
            places = fetch_area_places(api_key, area)
        except Exception as e:
            print(f"⚠️ area {area}: {e}")
            continue
        for p in places:
            cid = p.get("contentid", "")
            if not cid or any(cid[-4:] in eid for eid in existing):
                continue
            if not p.get("title") or not p.get("mapx") or not p.get("mapy"):
                continue
            try:
                detail = fetch_detail(api_key, cid)
            except Exception:
                detail = None
            slug, block = to_place_block(p, detail)
            if slug in existing:
                continue
            # append
            txt = MOCK_PLACES.read_text(encoding="utf-8")
            insertion = txt.rfind("];")
            if insertion < 0:
                print("❌ mock-places.ts 말미 '];' 못찾음")
                return
            new_txt = txt[:insertion] + block + "\n" + txt[insertion:]
            MOCK_PLACES.write_text(new_txt, encoding="utf-8")
            existing.add(slug)
            added += 1
            log_entries.append({"slug": slug, "title": p.get("title"), "region": AREA_TO_REGION[area]})
            print(f"  ✅ {p.get('title')} ({AREA_TO_REGION[area]})")
            if added >= 1:  # 매일 1건
                break
        if added >= 1:
            break

    # 로그
    log_file = LOG_DIR / f"korlens_{today.isoformat()}.json"
    log_file.write_text(json.dumps({"date": today.isoformat(), "added": log_entries},
                                   indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ 오늘 {added}건 추가 · 총 {len(existing)}개 · {log_file}")


if __name__ == "__main__":
    main()
