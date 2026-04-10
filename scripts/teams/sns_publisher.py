"""
📣 홍보부 SNS 자동 게시 (Twitter/X)

트위터에 전자책/사주봇/쿠팡 파트너스 홍보글 자동 게시.
매일 09:00 + 21:00 KST 실행 (GitHub Actions).

환경변수:
  TWITTER_API_KEY        - X Developer API Key
  TWITTER_API_SECRET     - X Developer API Secret
  TWITTER_ACCESS_TOKEN   - OAuth 1.0a Access Token
  TWITTER_ACCESS_SECRET  - OAuth 1.0a Access Token Secret
  ANTHROPIC_API_KEY      - Claude (콘텐츠 생성)
  TELEGRAM_BOT_TOKEN     - 텔레그램 보고
  TELEGRAM_CHAT_ID       - 보고 받을 chat id
"""

import os
import sys
import json
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from scripts.lib.telegram_notify import notify_safe

KST = timezone(timedelta(hours=9))

# ============================================================
# 상품/서비스 정보
# ============================================================
PRODUCTS = [
    {"name": "AI 부업 시스템 본책", "price": "99,000원", "url": "https://ghdejr.gumroad.com/l/ai-500",
     "hook": "AI로 월 500만원 자동화? 이 책 하나로 시작하세요"},
    {"name": "프롬프트 900개+ 팩", "price": "9,900원", "url": "https://ghdejr.gumroad.com/l/ai-prompt-early",
     "hook": "복붙만 하면 되는 프롬프트 900개. 얼리버드 9,900원"},
    {"name": "노션 템플릿 50개", "price": "39,900원", "url": "https://ghdejr.gumroad.com/l/notion-50",
     "hook": "노션 템플릿 판매로 월 100만원 부업 시작하기"},
    {"name": "AI 부업 수익 리포트", "price": "19,900원", "url": "https://ghdejr.gumroad.com/l/ai-revenue",
     "hook": "AI 부업 13개 카테고리. 뭐가 가장 돈 될까?"},
    {"name": "클로드 코드 가이드", "price": "39,900원", "url": "https://ghdejr.gumroad.com/l/claude-code",
     "hook": "코딩 몰라도 하루 만에 앱 만드는 법"},
    {"name": "AI 에이전트 사업", "price": "49,900원", "url": "https://ghdejr.gumroad.com/l/ai-agent",
     "hook": "Claude Agent SDK로 월 500만원 자동화 사업"},
    {"name": "퇴사 플레이북", "price": "99,000원", "url": "https://ghdejr.gumroad.com/l/exit-playbook",
     "hook": "퇴사 전 6개월 체크리스트부터 사업자등록까지"},
    {"name": "AI 사주 무료 체험", "price": "무료 3회", "url": "https://cheonmyeongdang.onrender.com",
     "hook": "AI가 풀어주는 사주 상담. 지금 무료로 체험하세요"},
]

COUPANG_LINK = os.environ.get("COUPANG_PARTNER_LINK",
                               "https://link.coupang.com/a/emjC0T")

# ============================================================
# 트위터 게시
# ============================================================
def post_tweet(text: str) -> dict:
    """트위터에 1개 트윗 게시. OAuth 1.0a 사용."""
    api_key = os.environ.get("TWITTER_API_KEY", "").strip()
    api_secret = os.environ.get("TWITTER_API_SECRET", "").strip()
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN", "").strip()
    access_secret = os.environ.get("TWITTER_ACCESS_SECRET", "").strip()

    if not all([api_key, api_secret, access_token, access_secret]):
        return {"error": "Twitter API 키 없음"}

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )
        response = client.create_tweet(text=text[:280])
        return {"ok": True, "id": response.data["id"]}
    except Exception as e:
        return {"error": f"트윗 실패: {type(e).__name__}: {str(e)[:200]}"}


# ============================================================
# 콘텐츠 생성
# ============================================================
def generate_daily_posts() -> dict:
    """Claude 가 오늘의 SNS 게시글 생성."""
    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()

    today = datetime.now(KST)
    day_of_week = today.weekday()  # 0=월 ~ 6=일

    # 요일별 테마
    themes = {
        0: "전자책 홍보 (월요일 = 새 주 시작 동기부여)",
        1: "사주 SaaS 홍보 (화요일)",
        2: "프롬프트 팩 홍보 (수요일)",
        3: "쿠팡 추천 상품 (목요일)",
        4: "AI 팁/가치 콘텐츠 (금요일)",
        5: "주말 특가/이벤트 (토요일)",
        6: "동기부여/스토리 (일요일)",
    }
    theme = themes.get(day_of_week, "AI 부업 팁")

    # 오늘의 상품 선택
    product = random.choice(PRODUCTS)

    if not api_key:
        # Claude 없으면 템플릿 사용
        tweet = f"{product['hook']}\n\n{product['name']} ({product['price']})\n{product['url']}\n\n#AI부업 #디지털상품 #덕구네AI"
        return {
            "tweet": tweet,
            "instagram": f"{product['hook']}\n\n링크는 프로필에서!\n\n#AI부업 #AI #디지털상품 #부업추천 #자동화 #클로드 #ChatGPT #전자책 #노션템플릿 #사주 #덕구네AI #1인사업 #프리랜서 #재택부업 #수익자동화",
            "telegram": f"📢 {product['hook']}\n\n{product['name']} ({product['price']})\n👉 {product['url']}",
            "coupang": f"🛒 오늘의 추천!\n{COUPANG_LINK}\n\n이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.",
        }

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""오늘 테마: {theme}
홍보할 상품: {product['name']} ({product['price']})
URL: {product['url']}
쿠팡 링크: {COUPANG_LINK}

아래 4개를 JSON으로 생성:
1. "tweet": 트위터 게시글 (280자 이내, URL 포함, 해시태그 3개)
2. "instagram": 인스타 캡션 (300자, 해시태그 15개, URL 미포함 - "프로필 링크" 유도)
3. "telegram": 텔레그램 채널 글 (이모지 포함, URL 포함)
4. "coupang": 쿠팡 추천 글 (쿠팡 링크 포함, 광고 표시 문구 필수)

JSON만 출력."""

        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in msg.content if hasattr(b, "text"))
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception as e:
        print(f"Claude 실패: {e}")

    # 폴백
    return {
        "tweet": f"{product['hook']}\n\n{product['url']}\n\n#AI부업 #덕구네AI #자동화",
        "instagram": f"{product['hook']}\n\n#AI부업 #덕구네AI",
        "telegram": f"📢 {product['hook']}\n👉 {product['url']}",
        "coupang": f"🛒 추천!\n{COUPANG_LINK}\n\n쿠팡 파트너스 활동으로 수수료를 제공받습니다.",
    }


# ============================================================
# 텔레그램 채널 게시
# ============================================================
def post_telegram_channel(text: str, channel_id: str = None) -> bool:
    """텔레그램 공개 채널에 게시."""
    import urllib.request
    import urllib.parse

    token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    if not channel_id:
        channel_id = os.environ.get("TELEGRAM_CHANNEL_ID", "@deokgune_ai")

    if not token:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": channel_id,
        "text": text,
        "disable_web_page_preview": False,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("ok", False)
    except Exception as e:
        print(f"텔레그램 채널 게시 실패: {e}")
        return False


# ============================================================
# 메인
# ============================================================
def main() -> int:
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    print(f"[홍보부 SNS 자동 게시] {now}")

    # 콘텐츠 생성
    posts = generate_daily_posts()
    print(f"콘텐츠 생성 완료")

    results = []

    # 1. 트위터 게시
    tweet_result = post_tweet(posts.get("tweet", ""))
    if "error" in tweet_result:
        results.append(f"❌ 트위터: {tweet_result['error']}")
    else:
        results.append(f"✅ 트위터: 게시 완료")

    # 2. 쿠팡 트윗 (별도)
    coupang_result = post_tweet(posts.get("coupang", ""))
    if "error" in coupang_result:
        results.append(f"❌ 쿠팡 트윗: {coupang_result['error']}")
    else:
        results.append(f"✅ 쿠팡 트윗: 게시 완료")

    # 3. 텔레그램 채널
    tg_ok = post_telegram_channel(posts.get("telegram", ""))
    results.append(f"{'✅' if tg_ok else '❌'} 텔레그램 채널")

    # 4. 쿠팡 텔레그램
    tg_coupang = post_telegram_channel(posts.get("coupang", ""))
    results.append(f"{'✅' if tg_coupang else '❌'} 쿠팡 텔레그램")

    # 보고
    report = f"""📣 [홍보부] SNS 자동 게시 완료
🕒 {now}

{chr(10).join(results)}

📝 트윗 내용:
{posts.get('tweet', '')[:200]}

🛒 쿠팡:
{posts.get('coupang', '')[:200]}

📱 인스타 캡션 (수동 복붙 필요):
{posts.get('instagram', '')[:200]}"""

    print(report)
    notify_safe(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
