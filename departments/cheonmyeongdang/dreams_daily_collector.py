#!/usr/bin/env python3
"""
천명당 꿈해몽 일일 자동 확장.
Claude에 트렌드 기반 새 꿈 5개 생성 요청 → index.html 해당 카테고리에 append.

매일 3~5개씩, 중복 제거, 카테고리 밸런스 유지.

Task Scheduler: 매일 08:15
"""
import sys, os, json, random, re, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

INDEX_HTML = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\index.html")
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Claude 생성 모듈 경로
YT_SHARED = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\youtube\shared")
sys.path.insert(0, str(YT_SHARED))
from claude_script import generate as claude_gen

CATEGORIES = {
    "situation": {"label": "상황꿈", "missing": ["치아 빠지기", "사랑니", "시험", "면접", "합격", "불합격", "이별", "재회", "결혼식", "이혼", "임신 발견", "출산", "교통사고", "추락", "절벽", "비행기 추락", "돈 줍기", "강도 만남"]},
    "body": {"label": "신체꿈", "missing": ["흰머리", "탈모", "상처", "수술", "피부병", "눈 실명", "귀 안들림", "목소리 안나옴"]},
    "people": {"label": "사람꿈", "missing": ["전 남친", "전 여친", "첫사랑", "짝사랑", "상사", "부하직원", "선생님", "연예인", "외국인", "쌍둥이"]},
    "food": {"label": "음식꿈", "missing": ["짜장면", "치킨", "피자", "떡", "케이크", "술(소주/맥주)", "생선회", "매운음식"]},
    "animal": {"label": "동물꿈", "missing": ["돼지", "소", "개(강아지)", "고양이", "닭", "거북이", "사슴", "토끼", "곰", "코끼리"]},
    "place": {"label": "장소꿈", "missing": ["기차역", "공항", "호텔", "병원", "학교", "교회", "절", "지하", "옥상"]},
    "object": {"label": "물건꿈", "missing": ["휴대폰", "노트북", "반지", "열쇠", "우산", "거울", "책", "편지"]},
}


def load_existing_names():
    """index.html에서 기존 꿈 name 전부 추출"""
    txt = INDEX_HTML.read_text(encoding="utf-8")
    # { name: '...' 패턴
    names = re.findall(r"name:\s*['\"]([^'\"]+)['\"]", txt)
    return set(names)


def generate_dreams(category_key, existing_names, count=5):
    cat = CATEGORIES[category_key]
    avoid_list = ", ".join(sorted(existing_names)[:40])  # 과거 회피 예시
    missing_hint = ", ".join(random.sample(cat["missing"], min(5, len(cat["missing"]))))

    prompt = f"""한국 꿈해몽 DB에 추가할 **{cat['label']}** 카테고리 새 꿈 {count}개 만들어.

우선 추천 키워드: {missing_hint}

기존 DB에 이미 있는 이름 절대 금지 (예: {avoid_list})

각 항목 JSON 스키마 정확히 맞춰:
{{
  "name": "짧은 명사 1~4자",
  "icon": "&#xxxx;" 형식 HTML entity (unicode emoji, 예: &#128128; &#127808; &#127879; &#128123; &#9917;),
  "meaning": "150~250자 따뜻한 해석",
  "luck": "길" 또는 "흉" 또는 "평",
  "advice": "40~80자 실용 조언",
  "lotto": [6개 서로 다른 숫자, 1~45 범위, 오름차순]
}}

출력: 오직 JSON 배열만. 마크다운/설명 금지. 한국 문화·일상·심리 반영."""

    raw = claude_gen(prompt, max_tokens=2500).strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    dreams = json.loads(raw)
    # 검증 + 중복 제거
    valid = []
    for d in dreams:
        if not isinstance(d, dict):
            continue
        n = d.get("name", "").strip()
        if not n or n in existing_names:
            continue
        if not all(k in d for k in ("icon", "meaning", "luck", "advice", "lotto")):
            continue
        if not isinstance(d["lotto"], list) or len(d["lotto"]) != 6:
            continue
        valid.append(d)
        existing_names.add(n)
    return valid


def dream_to_js(d):
    """dream dict → JS 객체 리터럴 한 줄"""
    def esc(s):
        return str(s).replace("\\", "\\\\").replace("'", "\\'")
    lotto = ", ".join(str(int(x)) for x in d["lotto"])
    return (
        f"        {{ name: '{esc(d['name'])}', icon: '{esc(d['icon'])}', "
        f"meaning: '{esc(d['meaning'])}', luck: '{esc(d['luck'])}', "
        f"advice: '{esc(d['advice'])}', lotto: [{lotto}] }},"
    )


def insert_into_category(category_key, new_items):
    """index.html의 해당 카테고리 items 배열 말미에 삽입"""
    label = CATEGORIES[category_key]["label"]
    txt = INDEX_HTML.read_text(encoding="utf-8")
    # label: '상황꿈', 를 anchor로 items 배열 끝 찾기
    # 구조:
    #   situation: {
    #     label: '상황꿈',
    #     items: [
    #       { ... },
    #       ...
    #     ]
    #   },
    pattern = rf"({category_key}\s*:\s*\{{[^}}]*?label:\s*['\"]{label}['\"][^\[]*?items:\s*\[)"
    m = re.search(pattern, txt, re.DOTALL)
    if not m:
        print(f"⚠️ {category_key} anchor 못찾음")
        return False
    # 해당 items 배열 끝 `]` 찾기 (중첩 객체 없음 가정 — 꿈 데이터는 flat)
    start = m.end()
    depth = 1
    i = start
    while i < len(txt) and depth > 0:
        if txt[i] == '[':
            depth += 1
        elif txt[i] == ']':
            depth -= 1
        i += 1
    close_idx = i - 1
    # items 배열 마지막 `]` 직전에 새 아이템 삽입
    new_lines = "\n" + "\n".join(dream_to_js(d) for d in new_items) + "\n      "
    # 마지막 아이템이 comma 로 끝나도록 보정
    before = txt[:close_idx]
    # 직전 비공백이 `,` 아니면 `,` 추가
    j = close_idx - 1
    while j > 0 and txt[j] in " \n\t":
        j -= 1
    prefix = ""
    if txt[j] not in ",[":
        prefix = ","
    new_txt = txt[:close_idx] + prefix + new_lines + txt[close_idx:]
    INDEX_HTML.write_text(new_txt, encoding="utf-8")
    return True


def main():
    existing = load_existing_names()
    print(f"📚 기존 꿈 {len(existing)}개")

    today = datetime.date.today()
    random.seed(today.toordinal())
    # 오늘 카테고리 2개 선정 (요일별 로테이션 + 랜덤)
    cats = list(CATEGORIES.keys())
    random.shuffle(cats)
    targets = cats[:2]

    added_all = []
    for cat in targets:
        try:
            new_items = generate_dreams(cat, existing, count=3)
        except Exception as e:
            print(f"⚠️ {cat} 생성 실패: {e}")
            continue
        if not new_items:
            print(f"  {cat}: 유효 항목 0개")
            continue
        if insert_into_category(cat, new_items):
            print(f"  ✅ {cat} ({CATEGORIES[cat]['label']}): {len(new_items)}개 추가")
            for d in new_items:
                print(f"     · {d['name']} ({d['luck']})")
            added_all += [{"cat": cat, **d} for d in new_items]

    # 로그
    log_file = LOG_DIR / f"dreams_{today.isoformat()}.json"
    log_file.write_text(json.dumps({"date": today.isoformat(), "added": added_all},
                                   indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ 오늘 총 {len(added_all)}개 꿈 추가 · {log_file}")

    # 로그 회전 (90일 이전 dreams_*.json 삭제)
    cutoff = (today - datetime.timedelta(days=90)).isoformat()
    for old in LOG_DIR.glob("dreams_*.json"):
        try:
            d = old.stem.replace("dreams_", "")
            if d < cutoff:
                old.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    main()
