#!/usr/bin/env python3
"""
천명당 월회원 일일 운세 생성기.

입력: subscriber 1명 (생년월일/생시/성별/음양력)
출력: 오늘의 운세 텍스트 (총운/애정/재물/건강/조언 + 행운 색상/숫자)

전략:
  1) Python 측에서는 saju-engine.js를 포팅하지 않고, Claude API에 생년월일+성별+오늘
     날짜를 넘겨 한국식 사주 운세를 생성한다 (saju-engine.js의 정밀 계산은 폴백
     없이 Claude의 사주 지식에 의존 — TODO: Node.js 헤드리스 호출로 정확도 ↑).
  2) 응답 길이/말투를 통제하여 일관된 카톡 메시지 폼.
  3) 실패 시 일반 12간지 일운세로 폴백.
"""
import os, sys, json, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
YT_SHARED = ROOT / "departments" / "media" / "youtube" / "shared"
sys.path.insert(0, str(YT_SHARED))
from claude_script import generate as claude_gen


SYSTEM = """너는 30년 경력의 한국 명리학자다.
사주팔자(년주·월주·일주·시주)와 오행 균형, 십신, 일운(日運) 기반으로
오늘 하루의 운세를 따뜻하고 구체적으로 전한다.
미신적·점술적 단정 표현 대신 "~할 가능성", "~조심" 같은 부드러운 표현을 사용한다.
법·의료·금융 단정 금지."""


PROMPT_TEMPLATE = """오늘 날짜: {today} ({weekday})

회원 정보:
- 생년월일: {birth_date} ({calendar})
- 출생시각: {birth_time}
- 성별: {gender_kr}

이 사람의 오늘 일일 운세를 아래 JSON 스키마로 생성해.

{{
  "headline": "30자 이내 한 줄 요약",
  "summary": "총운 2~3문장 (100자 내외)",
  "love": "애정·관계 운 한 문장",
  "wealth": "재물·일 운 한 문장",
  "health": "건강·컨디션 한 문장",
  "advice": "오늘 행동 조언 한 문장 (실용적·구체적)",
  "lucky_color": "한국어 색상명 (예: 청록, 황금)",
  "lucky_number": [3개 숫자 1~45],
  "lucky_direction": "동/서/남/북/동남/서북 등",
  "caution": "오늘 주의할 한 가지 (선택, 없으면 빈 문자열)"
}}

규칙:
- 사주 일주(日柱) 기준 + 오늘 일진(日辰) 합/충 고려
- 모든 응답은 한국어
- JSON 외 텍스트 금지 (마크다운 코드펜스도 금지)
- 따뜻하고 격려하는 어조
"""

WEEKDAY_KR = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]


def generate_fortune(subscriber, today=None):
    """
    subscriber: dict with birth_date, birth_time, birth_calendar, gender (M/F)
    return: dict (headline, summary, love, wealth, health, advice,
                  lucky_color, lucky_number, lucky_direction, caution)
    """
    if today is None:
        today = datetime.date.today()
    weekday = WEEKDAY_KR[today.weekday()]
    gender_kr = "남성" if subscriber.get("gender") == "M" else "여성"
    cal = "양력" if subscriber.get("birth_calendar", "solar") == "solar" else "음력"

    prompt = PROMPT_TEMPLATE.format(
        today=today.isoformat(),
        weekday=weekday,
        birth_date=subscriber.get("birth_date", ""),
        calendar=cal,
        birth_time=subscriber.get("birth_time", "12:00"),
        gender_kr=gender_kr,
    )

    raw = claude_gen(prompt, system=SYSTEM, max_tokens=1200).strip()
    # 코드펜스 제거
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # 폴백: 텍스트 그대로 summary에 박음
        data = {
            "headline": "오늘은 평온한 하루",
            "summary": raw[:200],
            "love": "", "wealth": "", "health": "",
            "advice": "마음의 중심을 잡고 본분에 집중하세요.",
            "lucky_color": "청색",
            "lucky_number": [3, 17, 28],
            "lucky_direction": "동",
            "caution": "",
        }
    # 필드 보정
    if not isinstance(data.get("lucky_number"), list):
        data["lucky_number"] = [3, 17, 28]
    return data


def format_message(fortune, name=""):
    """카카오톡/텔레그램 발송용 메시지 포맷"""
    today = datetime.date.today()
    title = f"🪷 {name}님 오늘의 운세" if name else "🪷 오늘의 운세"
    lucky_nums = ", ".join(str(n) for n in (fortune.get("lucky_number") or [])[:3])

    lines = [
        f"{title} ({today:%Y.%m.%d %a})",
        "",
        f"✨ {fortune.get('headline', '')}",
        "",
        fortune.get("summary", ""),
        "",
        f"💕 애정·관계: {fortune.get('love', '-')}",
        f"💰 재물·일:   {fortune.get('wealth', '-')}",
        f"🌿 건강:      {fortune.get('health', '-')}",
        "",
        f"📌 오늘의 조언",
        f"   {fortune.get('advice', '-')}",
    ]
    if fortune.get("caution"):
        lines += ["", f"⚠️ 주의: {fortune.get('caution')}"]
    lines += [
        "",
        f"🎨 행운의 색: {fortune.get('lucky_color', '-')}",
        f"🔢 행운의 숫자: {lucky_nums}",
        f"🧭 행운의 방향: {fortune.get('lucky_direction', '-')}",
        "",
        "—",
        "천명당 (cheonmyeongdang) | 매일 08:00 발송",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # CLI 테스트
    test_sub = {
        "birth_date": "1985-09-26",
        "birth_time": "06:00",
        "birth_calendar": "solar",
        "gender": "M",
    }
    f = generate_fortune(test_sub)
    print(json.dumps(f, ensure_ascii=False, indent=2))
    print("\n--- 메시지 미리보기 ---\n")
    print(format_message(f, name="홍덕훈"))
