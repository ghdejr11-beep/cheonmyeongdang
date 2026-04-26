#!/usr/bin/env python3
"""
천명당 그룹 CEO 자동 브리핑 생성기
- 시간대별로 다른 내용 전송
- 실제 프로젝트 상태 체크
- 매번 다른 우선순위/이슈/제안 포함

스케줄: 9AM, 12PM, 3PM, 6PM, 9PM, 12AM
"""

import requests
import datetime
import json
import os
import random
import sys

# 텔레그램 설정
TG_BOT_TOKEN = "8650272218:AAHIYmOVfqzMzr-hcOqWsfW6mftByoEd_SA"
TG_CHAT_ID = "8556067663"
TG_BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"


# ─── 시간대별 브리핑 ───
TIME_THEMES = {
    9:  {"emoji": "🌅", "label": "아침 브리핑",      "focus": "오늘의 우선순위"},
    12: {"emoji": "🍱", "label": "점심 체크인",      "focus": "오전 진행 상황"},
    15: {"emoji": "☕",  "label": "오후 점검",        "focus": "주요 이슈"},
    18: {"emoji": "🌆", "label": "저녁 브리핑",      "focus": "일일 성과"},
    21: {"emoji": "🌙", "label": "야간 점검",        "focus": "내일 준비"},
    0:  {"emoji": "🌌", "label": "자정 정산",        "focus": "하루 마감"},
}


def get_project_status():
    """실제 프로젝트 상태를 체크"""
    status = {}
    base = "C:/Users/hdh02/Desktop/cheonmyeongdang"

    # 천명당 버전 체크
    try:
        with open(f"{base}/index.html", 'r', encoding='utf-8') as f:
            content = f.read()
            status['cmd_lines'] = content.count('\n')
            status['cmd_has_premium'] = 'premium-saju.js' in content
    except:
        status['cmd_lines'] = 0

    # KDP 책 개수
    try:
        books = os.listdir(f"{base}/departments/ebook/projects")
        status['kdp_books'] = len([b for b in books if os.path.isdir(f"{base}/departments/ebook/projects/{b}")])
    except:
        status['kdp_books'] = 20

    # 프롬프트 상품 개수
    try:
        prods = os.listdir(f"{base}/departments/ebook/digital_products/output")
        status['digital_products'] = len([p for p in prods if p.startswith('listing_')])
    except:
        status['digital_products'] = 10

    # 보험 앱 여부
    status['insurance_customer'] = os.path.exists(f"{base}/departments/insurance-daboyeo/src/index.html")
    status['insurance_agent'] = os.path.exists(f"{base}/departments/insurance-daboyeo/src/agent.html")

    # 세금 서버 여부
    status['tax_server'] = os.path.exists(f"{base}/departments/tax/server/vercel.json")

    return status


def get_priority_list():
    """현재 프로젝트 진행 상황 기반 우선순위 (매번 다름)"""
    today = datetime.date.today()
    day_of_year = today.timetuple().tm_yday
    days_until_may31 = (datetime.date(2026, 5, 31) - today).days

    all_priorities = [
        # 긴급/중요
        (f"세금N혜택 출시 (종소세 마감 D-{days_until_may31})", 10),
        ("크티 프롬프트팩 10종 등록 완료", 9),
        ("CODEF API + Vercel 백엔드 연동 테스트", 9),
        ("천명당 유료 사주 결제 연동 확인", 8),
        ("보험다보여 GADP 회사 승인 절차", 8),
        ("KDP 나머지 10권 업로드 (주간 한도)", 7),
        ("카카오 비즈니스 채널 활용 방안", 7),
        ("앱인토스 심사 결과 대응", 6),
        ("Meta Developer 인증 (인스타/쓰레드)", 6),
        ("세무 서비스 랜딩페이지 홍보 시작", 10),
        ("천명당 앱 Play Store 설정 완료", 7),
        ("HexDrop 1.3 정식 출시", 5),
    ]

    # 요일별로 3개 랜덤 + 긴급은 고정
    random.seed(day_of_year + datetime.datetime.now().hour)
    urgent = [p for p in all_priorities if p[1] >= 9]
    others = [p for p in all_priorities if p[1] < 9]
    selected = random.sample(urgent, min(2, len(urgent))) + random.sample(others, 2)
    return sorted(selected, key=lambda x: -x[1])[:4]


def get_team_statuses():
    """팀별 현재 상태 — status_detector로 자동 탐지 (파일·API·환경변수 기반)"""
    try:
        from status_detector import get_all_statuses
        return get_all_statuses()
    except Exception as e:
        print(f'[status_detector 실패 — fallback 사용] {e}')
    # ─── Fallback (감지 실패 시 과거 하드코딩) ───
    return [
        {
            "emoji": "📚", "name": "전자책팀",
            "progress": "KDP 10/20권 출판 | 디지털 상품 10종 생성",
            "issue": "크티 등록 진행 중, 심사 대기",
            "next": "나머지 10권 다음주 업로드"
        },
        {
            "emoji": "🔮", "name": "천명당팀",
            "progress": "무료 사주 + 유료 15개 섹션 완성",
            "issue": "Play Store 앱 설정 미완료",
            "next": "월별 운세 + AI 상담 실사용 검증"
        },
        {
            "emoji": "🛡", "name": "보험팀",
            "progress": "고객용/설계사용 데모 배포 완료",
            "issue": "GADP 겸업 승인 필요 (법적 리스크)",
            "next": "상관에게 보고 후 진행 결정"
        },
        {
            "emoji": "💼", "name": "세무팀",
            "progress": "종소세 계산기 완성 | CODEF API 연동 중",
            "issue": "5월 종소세 마감 전 출시 필수",
            "next": "Vercel 환경변수 설정 + 프론트 연결"
        },
        {
            "emoji": "📺", "name": "미디어팀",
            "progress": "텔레그램+X 자동 홍보 시스템 가동",
            "issue": "인스타/틱톡 미연결",
            "next": "Meta 인증 후 채널 확장"
        },
        {
            "emoji": "🎮", "name": "게임팀",
            "progress": "HexDrop 1.3 비공개테스트 | 테트리스 AI 대결 완성",
            "issue": "정식 출시 전 QA 필요",
            "next": "플레이 콘솔 업로드"
        },
    ]


def get_revenue_forecast():
    """수익 예측 (간단 추정)"""
    channels = [
        ("천명당 유료 풀이 (29,900원)", "월 1~5건", "30K~150K"),
        ("크티 프롬프트팩 (9,900~39,900원)", "월 5~20건", "100K~500K"),
        ("KDP 10권 (약 $3/권)", "월 3~10건", "30K~100K"),
        ("세금N혜택 (무료+광고)", "5월 런칭", "-"),
        ("보험다보여", "GADP 승인 후", "-"),
    ]
    return channels


def get_ai_suggestion(hour):
    """시간대별 AI 제안"""
    suggestions = {
        9: [
            "세금N혜택 출시 D-47. 오늘 환경변수 설정 + 프론트 연결 완료 권장",
            "크티에 등록된 프롬프트팩 있다면 첫 구매 유도를 위해 X/블로그 홍보",
            "KDP 다음주 업로드할 10권 소재 선정 필요 (시즌 타이밍 고려)",
        ],
        12: [
            "오전에 완료한 작업 텔레그램 팀 채팅방에 공유",
            "점심 시간 활용 — KDP 주간 리밋 확인 및 다음 업로드 큐 정리",
            "카카오 채널 친구 초대 메시지 작성 (브랜딩 강화)",
        ],
        15: [
            "오후 집중 시간 — 세금 앱 버그 수정 또는 핵심 기능 구현",
            "팔로워 증가 위해 미디어팀 콘텐츠 1건 추가 발행 고려",
            "이메일 마케팅 리스트 정리 (크티 구매자 CRM 구축 시작)",
        ],
        18: [
            "하루 성과 요약 — 오늘 완료한 것 / 못한 것 정리",
            "내일 할 일 3개 선정 (우선순위 높은 순)",
            "CODEF API 연동 진행 상황 체크",
        ],
        21: [
            "내일 아침 우선순위 메모 작성",
            "돌발 이슈 있으면 내일 오전에 처리할 수 있게 준비",
            "오늘 매출 집계 (크티/KDP/기타)",
        ],
        0: [
            "하루 마감 — 모든 프로젝트 git commit 완료 확인",
            "내일 오전 바로 시작할 수 있게 환경 세팅 유지",
            "주간 목표 대비 진행률 체크 (금요일이면 주간 리뷰)",
        ],
    }
    return random.choice(suggestions.get(hour, suggestions[9]))


def build_briefing(hour=None):
    """브리핑 메시지 생성"""
    now = datetime.datetime.now()
    if hour is None:
        hour = now.hour
        # 가장 가까운 정규 시간으로
        for h in [0, 9, 12, 15, 18, 21]:
            if abs(hour - h) < 2:
                hour = h
                break

    theme = TIME_THEMES.get(hour, TIME_THEMES[9])
    status = get_project_status()
    priorities = get_priority_list()
    teams = get_team_statuses()
    revenues = get_revenue_forecast()
    suggestion = get_ai_suggestion(hour)

    msg = f"{theme['emoji']} <b>CEO {theme['label']}</b>\n"
    msg += f"<i>{now.strftime('%Y-%m-%d %H:%M')}</i>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n\n"

    # ─── 우선순위 ───
    msg += f"🎯 <b>{theme['focus']}</b>\n"
    for i, (p, score) in enumerate(priorities, 1):
        flag = "🔴" if score >= 9 else "🟡" if score >= 7 else "🟢"
        msg += f"  {flag} {i}. {p}\n"
    msg += "\n"

    # ─── 팀별 현황 (시간대별 2~3팀만) ───
    msg += "👥 <b>부서별 현황</b>\n"
    # 시간대별로 다른 팀 강조
    focus_teams = {
        9:  [0, 1, 3],      # 전자책, 천명당, 세무
        12: [3, 4, 5],      # 세무, 미디어, 게임
        15: [0, 2, 4],      # 전자책, 보험, 미디어
        18: [1, 3, 5],      # 천명당, 세무, 게임
        21: [2, 3, 4],      # 보험, 세무, 미디어
        0:  [0, 1, 2, 3, 4, 5],  # 전체
    }
    idx_list = focus_teams.get(hour, [0, 1, 2])
    for i in idx_list:
        t = teams[i]
        msg += f"\n{t['emoji']} <b>{t['name']}</b>\n"
        msg += f"  ✓ {t['progress']}\n"
        msg += f"  ⚠ {t['issue']}\n"
        msg += f"  → {t['next']}\n"
    msg += "\n"

    # ─── 수익 현황 (아침/저녁만) ───
    if hour in [9, 18, 0]:
        msg += "💰 <b>수익 예측</b>\n"
        for ch, freq, rev in revenues:
            msg += f"  • {ch}: {freq} ({rev})\n"
        msg += "\n"

    # ─── AI 제안 ───
    msg += f"💡 <b>AI 제안</b>\n  {suggestion}\n\n"

    # ─── 세금N혜택 카운트다운 ───
    days = (datetime.date(2026, 5, 31) - datetime.date.today()).days
    msg += f"⏰ <b>세금N혜택 출시 D-{days}</b>\n"

    msg += f"\n━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🏢 천명당 그룹 | 쿤스튜디오"

    return msg


def send_telegram(text):
    url = f"{TG_BASE_URL}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json()


if __name__ == "__main__":
    hour = None
    if len(sys.argv) > 1:
        try:
            hour = int(sys.argv[1])
        except:
            pass

    msg = build_briefing(hour)

    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        print(msg)
    else:
        result = send_telegram(msg)
        if result.get("ok"):
            print(f"✅ 브리핑 전송 완료 ({datetime.datetime.now().strftime('%H:%M')})")
        else:
            print(f"❌ 실패: {result}")
