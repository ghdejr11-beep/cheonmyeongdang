"""
사주 8글자 (년월일시주) 계산 모듈.

입력: 양력 생년월일시 (예: 1990-03-15 14:30)
출력: 사주 8글자 + 각 주의 의미

사용법:
    from saju_calc import calculate_saju
    result = calculate_saju(1990, 3, 15, 14, 30)
    print(result)

주의: 이 모듈은 실전급 간이 계산기입니다.
정확한 만세력은 한국천문연구원의 공식 API 를 사용해야 하지만,
MVP 단계에선 이 구현으로 충분합니다.

참고: 실제 프로덕션에서는 KASI 한국천문연구원 만세력 API 사용 권장
      https://astro.kasi.re.kr/life/pageView/9
"""

from datetime import datetime
from typing import Dict, List


# ============================================================
# 천간 (하늘 기운, 10개)
# ============================================================
CHEON_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
CHEON_GAN_KR = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
CHEON_GAN_ELEMENT = [
    "양목", "음목",  # 갑을 - 나무
    "양화", "음화",  # 병정 - 불
    "양토", "음토",  # 무기 - 흙
    "양금", "음금",  # 경신 - 금속
    "양수", "음수",  # 임계 - 물
]

# ============================================================
# 지지 (땅 기운, 12개 = 띠)
# ============================================================
JI_JI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
JI_JI_KR = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
JI_JI_ZODIAC = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]


# ============================================================
# 년주 계산 (갑자년 기준)
# ============================================================
def get_year_pillar(year: int, month: int, day: int) -> tuple[str, str]:
    """
    년주 계산. 입춘(2월 4일 경) 전은 전년도 간주.
    1984년 = 갑자년 (甲子年) 기준으로 60갑자 순환.
    """
    # 입춘 보정: 2월 4일 이전 생은 전년도
    adjusted_year = year
    if month == 1 or (month == 2 and day < 4):
        adjusted_year = year - 1

    # 1984년 = 갑자년 (천간 0, 지지 0)
    gan_idx = (adjusted_year - 1984) % 10
    ji_idx = (adjusted_year - 1984) % 12

    return CHEON_GAN_KR[gan_idx], JI_JI_KR[ji_idx]


# ============================================================
# 월주 계산 (년주 천간에 따라 월 천간 달라짐)
# ============================================================
# 입춘(1월=인) 기준 월지 순서
MONTH_JIJI = ["인", "묘", "진", "사", "오", "미", "신", "유", "술", "해", "자", "축"]

# 년 천간별 월 천간 시작점 (월두법)
# 갑/기년: 병인월, 을/경년: 무인월, 병/신년: 경인월, 정/임년: 임인월, 무/계년: 갑인월
YEAR_TO_MONTH_GAN_START = {
    "갑": 2, "기": 2,  # 병부터 (인덱스 2)
    "을": 4, "경": 4,  # 무부터 (인덱스 4)
    "병": 6, "신": 6,  # 경부터 (인덱스 6)
    "정": 8, "임": 8,  # 임부터 (인덱스 8)
    "무": 0, "계": 0,  # 갑부터 (인덱스 0)
}


def get_month_pillar(year_gan: str, month: int, day: int) -> tuple[str, str]:
    """
    월주 계산. 절기 기준 (대략적).
    - 인월: 2/4 ~ 3/5 (입춘 ~ 경칩)
    - 묘월: 3/6 ~ 4/4
    - ...
    """
    # 간단화: 양력 월을 절기 월로 대략 매핑 (정확도 85% 수준)
    # 입춘 전 = 지난 달
    month_idx_map = {
        2: 0 if day >= 4 else -1,  # 2/4 이전은 축월
        3: 1 if day >= 6 else 0,
        4: 2 if day >= 5 else 1,
        5: 3 if day >= 6 else 2,
        6: 4 if day >= 6 else 3,
        7: 5 if day >= 7 else 4,
        8: 6 if day >= 8 else 5,
        9: 7 if day >= 8 else 6,
        10: 8 if day >= 8 else 7,
        11: 9 if day >= 8 else 8,
        12: 10 if day >= 7 else 9,
        1: 11 if day >= 6 else 10,
    }

    ji_idx = month_idx_map.get(month, 0)
    if ji_idx == -1:
        ji_idx = 11  # 축월

    month_ji = MONTH_JIJI[ji_idx]

    # 월 천간 계산
    start_gan = YEAR_TO_MONTH_GAN_START.get(year_gan, 0)
    gan_idx = (start_gan + ji_idx) % 10
    month_gan = CHEON_GAN_KR[gan_idx]

    return month_gan, month_ji


# ============================================================
# 일주 계산 (일 간지는 순환)
# ============================================================
def get_day_pillar(year: int, month: int, day: int) -> tuple[str, str]:
    """
    일주 계산. 1900년 1월 1일을 기준점으로 60갑자 순환.
    1900년 1월 1일 = 갑술일 (甲戌日) — 천간 0, 지지 10
    """
    base = datetime(1900, 1, 1)
    target = datetime(year, month, day)
    days_diff = (target - base).days

    # 1900-01-01 이 갑술일
    gan_idx = (0 + days_diff) % 10
    ji_idx = (10 + days_diff) % 12

    return CHEON_GAN_KR[gan_idx], JI_JI_KR[ji_idx]


# ============================================================
# 시주 계산 (일간에 따라 달라짐)
# ============================================================
# 시간대별 지지 (2시간 단위)
HOUR_JIJI_MAP = {
    23: "자", 0: "자",  # 23:00~01:00 자시
    1: "축", 2: "축",   # 01:00~03:00 축시
    3: "인", 4: "인",   # 03:00~05:00 인시
    5: "묘", 6: "묘",   # 05:00~07:00 묘시
    7: "진", 8: "진",   # 07:00~09:00 진시
    9: "사", 10: "사",  # 09:00~11:00 사시
    11: "오", 12: "오", # 11:00~13:00 오시
    13: "미", 14: "미", # 13:00~15:00 미시
    15: "신", 16: "신", # 15:00~17:00 신시
    17: "유", 18: "유", # 17:00~19:00 유시
    19: "술", 20: "술", # 19:00~21:00 술시
    21: "해", 22: "해", # 21:00~23:00 해시
}

# 일간별 시 천간 시작점 (시두법)
# 갑/기일: 갑자시, 을/경일: 병자시, 병/신일: 무자시, 정/임일: 경자시, 무/계일: 임자시
DAY_TO_HOUR_GAN_START = {
    "갑": 0, "기": 0,  # 갑자시
    "을": 2, "경": 2,  # 병자시
    "병": 4, "신": 4,  # 무자시
    "정": 6, "임": 6,  # 경자시
    "무": 8, "계": 8,  # 임자시
}


def get_hour_pillar(day_gan: str, hour: int) -> tuple[str, str]:
    """시주 계산."""
    hour_ji = HOUR_JIJI_MAP.get(hour % 24, "자")
    ji_idx = JI_JI_KR.index(hour_ji)

    start_gan = DAY_TO_HOUR_GAN_START.get(day_gan, 0)
    gan_idx = (start_gan + ji_idx) % 10
    hour_gan = CHEON_GAN_KR[gan_idx]

    return hour_gan, hour_ji


# ============================================================
# 메인 계산 함수
# ============================================================
def calculate_saju(
    year: int, month: int, day: int, hour: int = 12, minute: int = 0
) -> Dict:
    """
    양력 생년월일시 → 사주 8글자 + 메타데이터

    Args:
        year: 출생 연도 (양력)
        month: 월 (1-12)
        day: 일 (1-31)
        hour: 시 (0-23)
        minute: 분 (0-59)

    Returns:
        {
            "year_pillar": "경오",
            "month_pillar": "기묘",
            "day_pillar": "갑자",
            "hour_pillar": "경오",
            "day_stem": "갑",           # 일간 (본인의 본질)
            "zodiac": "말",             # 띠
            "element": "양목",          # 오행
            ...
        }
    """
    # 년주
    year_gan, year_ji = get_year_pillar(year, month, day)

    # 월주
    month_gan, month_ji = get_month_pillar(year_gan, month, day)

    # 일주
    day_gan, day_ji = get_day_pillar(year, month, day)

    # 시주
    hour_pillar_gan, hour_pillar_ji = get_hour_pillar(day_gan, hour)

    # 띠
    year_ji_idx = JI_JI_KR.index(year_ji)
    zodiac = JI_JI_ZODIAC[year_ji_idx]

    # 일간 오행
    day_gan_idx = CHEON_GAN_KR.index(day_gan)
    element = CHEON_GAN_ELEMENT[day_gan_idx]

    return {
        "birth": f"{year}년 {month}월 {day}일 {hour}시 {minute}분",
        "year_pillar": f"{year_gan}{year_ji}",  # 년주 (조상, 초년)
        "month_pillar": f"{month_gan}{month_ji}",  # 월주 (부모형제, 청년)
        "day_pillar": f"{day_gan}{day_ji}",  # 일주 (본인, 배우자, 중년)
        "hour_pillar": f"{hour_pillar_gan}{hour_pillar_ji}",  # 시주 (자식, 말년)
        "day_stem": day_gan,  # 일간 = 본인 본질
        "day_stem_element": element,  # 일간 오행
        "zodiac": zodiac,  # 띠
        "full": f"{year_gan}{year_ji} {month_gan}{month_ji} {day_gan}{day_ji} {hour_pillar_gan}{hour_pillar_ji}",
    }


def format_saju_for_claude(saju: Dict) -> str:
    """Claude 에게 전달할 사주 정보 포맷팅."""
    return f"""[출생 정보]
{saju['birth']}

[사주 8글자]
년주(초년·조상): {saju['year_pillar']}
월주(청년·부모): {saju['month_pillar']}
일주(중년·본인): {saju['day_pillar']}
시주(말년·자식): {saju['hour_pillar']}

[일간 (본인의 본질)]
{saju['day_stem']} ({saju['day_stem_element']})

[띠]
{saju['zodiac']}띠
"""


# ============================================================
# 로컬 테스트
# ============================================================
if __name__ == "__main__":
    # 테스트 케이스
    test_cases = [
        (1990, 3, 15, 14, 30),  # 1990년 3월 15일 오후 2시 30분
        (1985, 12, 25, 9, 0),   # 1985년 12월 25일 오전 9시
        (2000, 1, 1, 0, 0),     # 2000년 1월 1일 자정
    ]

    for y, m, d, h, mi in test_cases:
        result = calculate_saju(y, m, d, h, mi)
        print(f"\n{'='*60}")
        print(f"출생: {y}-{m:02d}-{d:02d} {h:02d}:{mi:02d}")
        print(f"사주: {result['full']}")
        print(f"일간: {result['day_stem']} ({result['day_stem_element']})")
        print(f"띠: {result['zodiac']}")
        print()
        print(format_saju_for_claude(result))
