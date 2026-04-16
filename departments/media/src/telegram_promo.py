#!/usr/bin/env python3
"""
천명당 그룹 미디어부 — 텔레그램 자동 홍보 시스템
사용 가능 채널: 텔레그램 (봇 API)
향후 추가 예정: 인스타그램, 쓰레드, X(트위터)
"""

import requests
import json
import random
import datetime
import sys
import os

# ─── 설정 ───
BOT_TOKEN = "8650272218:AAHIYmOVfqzMzr-hcOqWsfW6mftByoEd_SA"
CHAT_ID = "8556067663"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ─── 서비스 링크 ───
LINKS = {
    "천명당": "https://ghdejr11-beep.github.io/cheonmyeongdang/",
    "보험한눈에_고객": "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/index.html",
    "보험한눈에_설계사": "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/agent.html",
    "세금N혜택": "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/tax/src/index.html",
    "테트리스AI대결": "https://ghdejr11-beep.github.io/cheonmyeongdang/tetris.html",
}

# ─── 홍보 콘텐츠 템플릿 ───
PROMO_TEMPLATES = {
    "천명당": [
        {
            "title": "🔮 천명당 — AI 사주·관상·손금 분석",
            "body": (
                "내 운명이 궁금하다면?\n"
                "AI가 분석하는 사주팔자, 관상, 손금!\n\n"
                "✅ 사주 궁합 매칭\n"
                "✅ AI 관상 분석 (얼굴 인식)\n"
                "✅ 손금 읽기\n"
                "✅ 오늘의 운세\n\n"
                "무료로 체험해보세요 👇"
            ),
        },
        {
            "title": "💑 AI 궁합 테스트 — 천명당",
            "body": (
                "내 사주와 상대방의 궁합은 몇 점?\n"
                "AI가 사주팔자를 기반으로 궁합을 분석합니다.\n\n"
                "🎯 총 궁합 점수\n"
                "💕 성격 궁합\n"
                "💰 재물 궁합\n"
                "🏠 가정 궁합\n\n"
                "지금 무료 테스트 👇"
            ),
        },
        {
            "title": "📸 AI 관상 분석 — 천명당",
            "body": (
                "셀카 한 장으로 내 관상을 분석!\n"
                "AI가 이목구비를 읽어 성격과 운세를 알려줍니다.\n\n"
                "👁️ 눈 — 지혜와 감성\n"
                "👃 코 — 재물운\n"
                "👄 입 — 대인관계\n"
                "🦻 귀 — 건강과 장수\n\n"
                "무료 관상 분석 받기 👇"
            ),
        },
    ],
    "보험한눈에": [
        {
            "title": "🛡️ 보험 한눈에 — 내 보험 통합 관리",
            "body": (
                "흩어진 보험, 한 곳에서 관리하세요!\n\n"
                "📊 38개 보험사 통합 조회\n"
                "🔍 중복 보장 감지 → 월 절약액 계산\n"
                "🤖 AI 맞춤 추천\n"
                "💰 보험료 계산기\n"
                "⏰ 갱신·만기 알림\n\n"
                "내 보험 점검하기 👇"
            ),
        },
        {
            "title": "💸 보험료 아끼는 방법 — 보험 한눈에",
            "body": (
                "혹시 중복 보장에 돈 낭비하고 있지 않나요?\n\n"
                "보험 한눈에가 자동으로 찾아드립니다:\n"
                "❌ 중복 가입된 보장\n"
                "⚠️ 놓치고 있는 보장 공백\n"
                "💡 더 저렴한 대안 상품\n\n"
                "평균 월 4만원 절약! 👇"
            ),
        },
    ],
    "세금N혜택": [
        {
            "title": "💰 세금N혜택 — 숨은 환급금 찾기",
            "body": (
                "내가 받을 수 있는 세금 환급, 놓치고 있지 않나요?\n\n"
                "🔎 종합소득세 환급 조회\n"
                "📋 절세 전략 AI 분석\n"
                "🏛️ 정부 지원금 매칭\n"
                "💬 AI 세무 상담\n\n"
                "수수료 0원! 무료 조회 👇"
            ),
        },
    ],
    "테트리스": [
        {
            "title": "🎮 테트리스 AI 대결 — 지금 도전!",
            "body": (
                "AI와 1:1 테트리스 대결!\n"
                "당신은 AI를 이길 수 있을까?\n\n"
                "⚡ 실시간 대전\n"
                "🤖 난이도별 AI (Easy/Normal/Hard)\n"
                "🏆 점수 경쟁\n"
                "🎵 레트로 사운드\n\n"
                "지금 바로 플레이 👇"
            ),
        },
    ],
}


def send_telegram_message(text, parse_mode="HTML"):
    """텔레그램 메시지 전송"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False,
    }
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json()


def build_promo_message(service_key, template):
    """홍보 메시지 조립"""
    link = LINKS.get(service_key, LINKS.get(f"{service_key}_고객", ""))
    msg = f"<b>{template['title']}</b>\n\n{template['body']}\n\n🔗 {link}"
    msg += "\n\n━━━━━━━━━━━━━━━\n"
    msg += "🏢 <b>천명당 그룹</b> | 쿤스튜디오\n"
    msg += "📱 더 많은 서비스: " + LINKS["천명당"]
    return msg


def post_daily_promo():
    """일일 홍보 — 서비스별 돌아가며 포스팅"""
    today = datetime.date.today()
    day_of_week = today.weekday()  # 0=월 ~ 6=일

    # 요일별 서비스 로테이션
    schedule = {
        0: "천명당",      # 월
        1: "보험한눈에",   # 화
        2: "세금N혜택",    # 수
        3: "테트리스",     # 목
        4: "천명당",      # 금
        5: "보험한눈에",   # 토
        6: "천명당",      # 일
    }

    service = schedule[day_of_week]
    templates = PROMO_TEMPLATES[service]
    template = random.choice(templates)

    # 서비스키 → 링크 매핑
    link_key = service
    if service == "보험한눈에":
        link_key = "보험한눈에_고객"

    msg = build_promo_message(link_key, template)

    print(f"[미디어부] {today} ({['월','화','수','목','금','토','일'][day_of_week]}) — {service} 홍보 게시")
    result = send_telegram_message(msg)

    if result.get("ok"):
        print(f"  ✅ 전송 성공 (message_id: {result['result']['message_id']})")
    else:
        print(f"  ❌ 전송 실패: {result}")

    return result


def post_all_services():
    """전체 서비스 홍보 (한 번에)"""
    results = []
    for service, templates in PROMO_TEMPLATES.items():
        template = templates[0]
        link_key = service
        if service == "보험한눈에":
            link_key = "보험한눈에_고객"
        msg = build_promo_message(link_key, template)
        result = send_telegram_message(msg)
        results.append((service, result.get("ok", False)))
        print(f"  {'✅' if result.get('ok') else '❌'} {service}")
    return results


def post_weekly_summary():
    """주간 서비스 종합 안내"""
    msg = (
        "<b>📢 천명당 그룹 — 이번 주 서비스 안내</b>\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"🔮 <b>천명당</b> — AI 사주·관상·손금\n"
        f"   {LINKS['천명당']}\n\n"
        f"🛡️ <b>보험 한눈에</b> — 보험 통합 관리\n"
        f"   {LINKS['보험한눈에_고객']}\n\n"
        f"💰 <b>세금N혜택</b> — 환급금 조회\n"
        f"   {LINKS['세금N혜택']}\n\n"
        f"🎮 <b>테트리스 AI 대결</b> — 게임\n"
        f"   {LINKS['테트리스AI대결']}\n\n"
        "━━━━━━━━━━━━━━━\n"
        "🏢 <b>천명당 그룹</b> | 쿤스튜디오\n"
        "사업자등록번호: 552-59-00848\n"
        "대표: 홍덕훈"
    )
    result = send_telegram_message(msg)
    print(f"[미디어부] 주간 종합 안내 {'✅ 성공' if result.get('ok') else '❌ 실패'}")
    return result


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "daily"

    if mode == "daily":
        post_daily_promo()
    elif mode == "all":
        post_all_services()
    elif mode == "weekly":
        post_weekly_summary()
    elif mode == "test":
        # 테스트: 간단한 메시지 전송
        result = send_telegram_message("🔔 <b>[미디어부 테스트]</b>\n홍보 시스템 정상 작동 중!")
        print(f"테스트 {'✅' if result.get('ok') else '❌'}: {result}")
    else:
        print(f"사용법: python telegram_promo.py [daily|all|weekly|test]")
