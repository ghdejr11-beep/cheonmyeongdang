#!/usr/bin/env python3
"""
천명당 그룹 미디어부 — SNS 자동 홍보 시스템
활성 채널: 텔레그램 + X(트위터)
향후 추가: 인스타그램, 쓰레드, 페이스북
"""

import os
import requests
import tweepy
import random
import datetime
import sys

# ─── .secrets에서 자격증명 로드 (하드코딩 금지) ───
_ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
_env = {}
_secrets_path = os.path.join(_ROOT, '.secrets')
if os.path.exists(_secrets_path):
    for _line in open(_secrets_path, encoding='utf-8'):
        if '=' in _line:
            _k, _v = _line.strip().split('=', 1)
            _env[_k] = _v

# ─── 텔레그램 설정 ───
TG_BOT_TOKEN = _env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT_ID = _env.get('TELEGRAM_CHAT_ID', '')
TG_BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

# ─── X (트위터) 설정 ───
X_API_KEY = _env.get('X_API_KEY', '')
X_API_SECRET = _env.get('X_API_SECRET', '')
X_ACCESS_TOKEN = _env.get('X_ACCESS_TOKEN', '')
X_ACCESS_SECRET = _env.get('X_ACCESS_SECRET', '')

# ─── 서비스 링크 ───
LINKS = {
    "천명당": "https://ghdejr11-beep.github.io/cheonmyeongdang/",
    "보험한눈에_고객": "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/index.html",
    "보험한눈에_설계사": "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src/agent.html",
    "세금N혜택": "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/tax/src/index.html",
    "테트리스AI대결": "https://ghdejr11-beep.github.io/cheonmyeongdang/tetris.html",
    "KORLENS": "https://korlens.vercel.app",
}

# ─── 홍보 콘텐츠 ───
# X는 280자 제한이므로 짧은 버전 별도 준비
PROMO = {
    "천명당": {
        "telegram": [
            "<b>🔮 천명당 — AI 사주·관상·손금 분석</b>\n\n내 운명이 궁금하다면?\nAI가 분석하는 사주팔자, 관상, 손금!\n\n✅ 사주 궁합 매칭\n✅ AI 관상 분석 (얼굴 인식)\n✅ 손금 읽기\n✅ 오늘의 운세\n\n무료로 체험해보세요 👇",
            "<b>💑 AI 궁합 테스트 — 천명당</b>\n\n내 사주와 상대방의 궁합은 몇 점?\nAI가 사주팔자를 기반으로 궁합을 분석합니다.\n\n🎯 총 궁합 점수\n💕 성격 궁합\n💰 재물 궁합\n🏠 가정 궁합\n\n지금 무료 테스트 👇",
            "<b>📸 AI 관상 분석 — 천명당</b>\n\n셀카 한 장으로 내 관상을 분석!\nAI가 이목구비를 읽어 성격과 운세를 알려줍니다.\n\n👁️ 눈 — 지혜와 감성\n👃 코 — 재물운\n👄 입 — 대인관계\n🦻 귀 — 건강과 장수\n\n무료 관상 분석 받기 👇",
        ],
        "x": [
            "🔮 AI가 분석하는 사주·관상·손금!\n\n무료 사주 궁합, AI 관상 분석, 손금 읽기까지\n내 운명을 확인해보세요 ✨\n\n#사주 #관상 #손금 #운세 #AI #천명당",
            "💑 내 궁합 점수는?\n\nAI 사주 궁합 테스트 — 성격·재물·가정 궁합까지 분석!\n무료로 확인해보세요 🎯\n\n#궁합 #사주궁합 #연애 #AI궁합 #천명당",
            "📸 셀카 한 장으로 AI 관상 분석!\n\n눈·코·입·귀로 성격과 운세를 알려줍니다\n무료 관상 분석 👇\n\n#관상 #AI관상 #얼굴분석 #운세 #천명당",
        ],
    },
    "보험한눈에": {
        "telegram": [
            "<b>🛡️ 보험 한눈에 — 내 보험 통합 관리</b>\n\n흩어진 보험, 한 곳에서 관리하세요!\n\n📊 38개 보험사 통합 조회\n🔍 중복 보장 감지 → 월 절약액 계산\n🤖 AI 맞춤 추천\n💰 보험료 계산기\n⏰ 갱신·만기 알림\n\n내 보험 점검하기 👇",
            "<b>💸 보험료 아끼는 방법</b>\n\n혹시 중복 보장에 돈 낭비하고 있지 않나요?\n\n보험 한눈에가 자동으로 찾아드립니다:\n❌ 중복 가입된 보장\n⚠️ 놓치고 있는 보장 공백\n💡 더 저렴한 대안 상품\n\n평균 월 4만원 절약! 👇",
        ],
        "x": [
            "🛡️ 내 보험, 한눈에 관리!\n\n38개 보험사 통합 조회\n중복 보장 감지 → 월 4만원 절약\nAI 맞춤 추천까지\n\n#보험 #보험비교 #보험료절약 #보험한눈에",
            "💸 보험료 줄이는 법?\n\n중복 보장 찾기 + 보장 공백 분석\nAI가 맞춤 보험 추천해드립니다\n\n#보험료 #절약 #보험분석 #보험한눈에",
        ],
    },
    "세금N혜택": {
        "telegram": [
            "<b>💰 세금N혜택 — 숨은 환급금 찾기</b>\n\n내가 받을 수 있는 세금 환급, 놓치고 있지 않나요?\n\n🔎 종합소득세 환급 조회\n📋 절세 전략 AI 분석\n🏛️ 정부 지원금 매칭\n💬 AI 세무 상담\n\n수수료 0원! 무료 조회 👇",
        ],
        "x": [
            "💰 숨은 세금 환급금, 찾아가세요!\n\n종합소득세 환급 조회\nAI 절세 전략 분석\n정부 지원금 매칭\n\n수수료 0원! 👇\n\n#세금환급 #절세 #종합소득세 #세금N혜택",
        ],
    },
    "테트리스": {
        "telegram": [
            "<b>🎮 테트리스 AI 대결 — 지금 도전!</b>\n\nAI와 1:1 테트리스 대결!\n당신은 AI를 이길 수 있을까?\n\n⚡ 실시간 대전\n🤖 난이도별 AI (Easy/Normal/Hard)\n🏆 점수 경쟁\n🎵 레트로 사운드\n\n지금 바로 플레이 👇",
        ],
        "x": [
            "🎮 AI와 테트리스 대결!\n\n실시간 1:1 대전 — Easy/Normal/Hard\n당신은 AI를 이길 수 있을까? 🏆\n\n지금 바로 도전 👇\n\n#테트리스 #AI게임 #브라우저게임 #무료게임",
        ],
    },
    "KORLENS": {
        "telegram": [
            "<b>🔍 KORLENS — 같은 한국, 다른 관점</b>\n\n같은 관광지를 4가지 관점으로 재해석하는 AI 여행 큐레이션!\n\n✅ 17개 광역시도 · 192개 장소 × 768개 AI 하이라이트\n✅ 외국인·커플·가족·솔로 유형별 맞춤\n✅ 혼잡도 필터 + 🔥 인기 뱃지\n✅ AI 큐레이터 챗봇\n✅ 무장애 편의정보 통합\n\n2026 관광데이터 활용 공모전 출품작 👇",
            "<b>🤖 AI 큐레이터 — KORLENS</b>\n\n\"내일 서울 커플여행 4시간\" 한 줄만 입력하세요.\n\nClaude Haiku가 실제 TourAPI 관광지로 맞춤 추천!\n✅ 장소 카드 인라인 표시\n✅ 동선·팁·시간대 자동 제안\n✅ 상세 페이지 자동 링크\n\n지금 체험 👇",
            "<b>🌍 외국인 친구랑 한국 여행?</b>\n\nKORLENS 외국인 탭 열면:\n🧳 영어 해설 투어 시간\n🚇 지하철역 출구 번호\n👘 한복 체험관 위치\n💳 환전소·신용카드 OK 정보\n\n한국관광공사 공식 영문 데이터 + AI 재해석!\n👇",
        ],
        "x": [
            "🔍 KORLENS — Same Korea, Different Lenses.\n\nAI-curated Korean travel with 4 perspectives:\n🧳 Foreigner · 💑 Couple · 👨‍👩‍👧 Family · 🚶 Solo\n\n17 regions · 192 places · 768 AI highlights\n\n#Korea #Travel #Seoul #AI\nhttps://korlens.vercel.app",
            "🤖 \"Plan me a 4-hour couple trip in Seoul\" — KORLENS AI 큐레이터가 실제 TourAPI 장소로 추천!\n\n같은 경복궁도 외국인·커플·가족·솔로 4가지 관점으로 다르게 보입니다.\n\n#KORLENS #AI여행 #한국관광",
            "🌏 Visiting Korea? Try KORLENS.\n\n4 perspectives (Foreigner/Couple/Family/Solo) on every place.\nReal-time Korean Tourism API + Claude AI curation.\n\n#VisitKorea #KoreaTourism #TravelAI",
        ],
    },
}


# ═══════════════════════════════════════
# 텔레그램 전송
# ═══════════════════════════════════════
def send_telegram(text):
    """Postiz(Telegram 등) + 직접 API(Bluesky/Discord/Mastodon/Reddit) 통합 발행.
    키 없는 채널은 자동 skip — 하나씩 추가할 때마다 즉시 확장됨.
    Postiz 미설정 시 구 Telegram Bot API 직접 호출로 fallback."""
    try:
        from postiz_poster import send_all_channels, POSTIZ_URL, POSTIZ_API_KEY
        direct = {}
        try:
            from multi_poster import send_all_direct
            direct = send_all_direct(text)
        except Exception as e:
            print(f"[auto_promo] multi_poster 실패: {e}")
        if POSTIZ_URL and POSTIZ_API_KEY:
            result = send_all_channels(text)
            ok = any(result.values()) if result else False
            return {"ok": ok or any(direct.values()), "postiz": result, "direct": direct}
        if any(direct.values()):
            return {"ok": True, "postiz": None, "direct": direct}
    except Exception as e:
        print(f"[auto_promo] Postiz 실패, 직접 Telegram으로 fallback: {e}")

    url = f"{TG_BASE_URL}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json()


# ═══════════════════════════════════════
# X (트위터) 전송
# ═══════════════════════════════════════
def get_x_client():
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_SECRET,
    )
    return client


def send_x_tweet(text):
    try:
        client = get_x_client()
        response = client.create_tweet(text=text)
        return {"ok": True, "tweet_id": response.data["id"]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════
# 통합 홍보 함수
# ═══════════════════════════════════════
def get_link(service):
    link_map = {
        "천명당": "천명당",
        "보험한눈에": "보험한눈에_고객",
        "세금N혜택": "세금N혜택",
        "테트리스": "테트리스AI대결",
    }
    return LINKS.get(link_map.get(service, service), "")


def post_promo(service, channels=None):
    """특정 서비스 홍보를 지정 채널에 게시"""
    if channels is None:
        channels = ["telegram", "x"]

    link = get_link(service)
    results = {}

    if "telegram" in channels:
        templates = PROMO[service]["telegram"]
        msg = random.choice(templates)
        msg += f"\n\n🔗 {link}"
        msg += "\n\n━━━━━━━━━━━━━━━\n🏢 <b>천명당 그룹</b> | 쿤스튜디오"
        result = send_telegram(msg)
        results["telegram"] = result.get("ok", False)
        print(f"  [텔레그램] {'OK' if results['telegram'] else 'FAIL'}")

    if "x" in channels:
        templates = PROMO[service]["x"]
        tweet = random.choice(templates)
        tweet += f"\n\n{link}"
        result = send_x_tweet(tweet)
        results["x"] = result.get("ok", False)
        if result.get("ok"):
            print(f"  [X] OK (tweet_id: {result['tweet_id']})")
        else:
            print(f"  [X] FAIL: {result.get('error', 'unknown')}")

    return results


def daily_promo():
    """일일 홍보 — 요일별 서비스 로테이션"""
    today = datetime.date.today()
    dow = today.weekday()
    days_kr = ['월', '화', '수', '목', '금', '토', '일']

    schedule = {
        0: "KORLENS",    # 월: KORLENS
        1: "천명당",     # 화
        2: "세금N혜택",  # 수
        3: "KORLENS",    # 목: KORLENS
        4: "보험한눈에", # 금
        5: "KORLENS",    # 토: KORLENS (주말 여행 계획 타이밍)
        6: "천명당",     # 일
    }

    service = schedule[dow]
    print(f"[미디어부] {today} ({days_kr[dow]}) — {service} 홍보")
    return post_promo(service)


def all_services():
    """전체 서비스 홍보"""
    print("[미디어부] 전체 서비스 홍보 시작")
    results = {}
    for service in PROMO:
        print(f"\n  === {service} ===")
        results[service] = post_promo(service)
    return results


def weekly_summary():
    """주간 종합 안내"""
    # 텔레그램 (긴 버전)
    tg_msg = (
        "<b>📢 천명당 그룹 — 이번 주 서비스 안내</b>\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"🔮 <b>천명당</b> — AI 사주·관상·손금\n   {LINKS['천명당']}\n\n"
        f"🛡️ <b>보험 한눈에</b> — 보험 통합 관리\n   {LINKS['보험한눈에_고객']}\n\n"
        f"💰 <b>세금N혜택</b> — 환급금 조회\n   {LINKS['세금N혜택']}\n\n"
        f"🎮 <b>테트리스 AI 대결</b>\n   {LINKS['테트리스AI대결']}\n\n"
        "━━━━━━━━━━━━━━━\n"
        "🏢 <b>천명당 그룹</b> | 쿤스튜디오 | 대표 홍덕훈"
    )
    tg_result = send_telegram(tg_msg)
    print(f"  [텔레그램 주간] {'OK' if tg_result.get('ok') else 'FAIL'}")

    # X (짧은 버전)
    x_msg = (
        "📢 천명당 그룹 서비스 안내\n\n"
        f"🔮 AI 사주·관상·손금\n"
        f"🛡️ 보험 통합 관리\n"
        f"💰 세금 환급 조회\n"
        f"🎮 테트리스 AI 대결\n\n"
        f"👇 모든 서비스 보기\n{LINKS['천명당']}\n\n"
        "#천명당 #AI #무료"
    )
    x_result = send_x_tweet(x_msg)
    print(f"  [X 주간] {'OK' if x_result.get('ok') else 'FAIL'}")

    return {"telegram": tg_result.get("ok"), "x": x_result.get("ok")}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "daily"

    if mode == "daily":
        daily_promo()
    elif mode == "all":
        all_services()
    elif mode == "weekly":
        weekly_summary()
    elif mode == "test":
        print("[미디어부] 테스트 전송")
        print("\n--- 텔레그램 ---")
        tg = send_telegram("🔔 <b>[미디어부 테스트]</b>\n텔레그램 + X 통합 홍보 시스템 가동!")
        print(f"  {'OK' if tg.get('ok') else 'FAIL'}")
        print("\n--- X (트위터) ---")
        x = send_x_tweet("🔔 [미디어부 테스트] 천명당 그룹 SNS 홍보 시스템 가동! #천명당 #AI")
        print(f"  {'OK' if x.get('ok') else 'FAIL'}")
        if not x.get("ok"):
            print(f"  에러: {x.get('error')}")
    else:
        print("사용법: python auto_promo.py [daily|all|weekly|test]")
