#!/usr/bin/env python3
"""쿠팡 파트너스 제휴 콘텐츠 자동 발행 (텔레그램 + X)"""
import os, requests, tweepy, random, time, sys

# Load secrets from project-root .secrets (never inline tokens — see
# memory feedback_subagent_secret_handling.md).
_ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
_SECRETS_PATH = os.path.join(_ROOT, '.secrets')
if os.path.exists(_SECRETS_PATH):
    for _line in open(_SECRETS_PATH, encoding='utf-8'):
        if '=' in _line and not _line.strip().startswith('#'):
            _k, _v = _line.strip().split('=', 1)
            os.environ.setdefault(_k, _v)

TG_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or os.environ.get('TG_BOT_TOKEN', '')
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') or os.environ.get('TG_CHAT_ID', '')

X_API_KEY = os.environ['X_API_KEY']
X_API_SECRET = os.environ['X_API_SECRET']
X_ACCESS_TOKEN = os.environ['X_ACCESS_TOKEN']
X_ACCESS_SECRET = os.environ['X_ACCESS_SECRET']

COUPANG_LINK = "https://link.coupang.com/a/emjC0T&subId=telegram01"
DISCLOSURE = "\n\n※ 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."

# 천명당(사주) 테마와 맞는 카테고리 + AI 부업 테마
POSTS = [
    {
        "theme": "사주 관련 도서",
        "kr": "<b>📖 사주 명리학 입문서 추천</b>\n\n사주 앱만 써봤다면 이제 원리를 이해할 차례. 음양오행·십신 기초부터 실전 풀이까지.\n\n초보자용 명리학 베스트셀러 모음 👇",
        "en": "Saju fundamentals books — from yin-yang theory to real readings.",
        "tags": "#사주 #명리학 #도서",
    },
    {
        "theme": "타로 카드 세트",
        "kr": "<b>🃏 타로카드 입문 세트 추천</b>\n\n앱 말고 실제 카드를 뽑아보는 경험은 완전 달라요. 입문자용 78장 풀덱 + 해설서 포함 제품 BEST.\n\n가성비 타로 세트 모음 👇",
        "en": "Tarot starter kits — full 78-card deck + guidebook.",
        "tags": "#타로 #타로카드 #타로입문",
    },
    {
        "theme": "명상·요가 매트",
        "kr": "<b>🧘 풍수와 함께하는 홈 명상 공간</b>\n\n집에 기운 살리는 첫걸음은 조용한 명상 자리부터. 두툼한 매트 + 쿠션으로 10분 힐링.\n\n홈 명상용품 BEST 👇",
        "en": "Home meditation setup — mat + cushion essentials.",
        "tags": "#명상 #요가매트 #홈트레이닝",
    },
    {
        "theme": "AI 부업 도서",
        "kr": "<b>💼 1인 사업자·부업러를 위한 AI 실전 도서</b>\n\nChatGPT·Claude로 수익 내는 법. 월 300만원 부업 만든 사례들 정리된 책 5권.\n\nAI 부업 베스트셀러 👇",
        "en": "AI side hustle books — real case studies.",
        "tags": "#AI부업 #ChatGPT #사이드허슬",
    },
    {
        "theme": "재테크·절세 도서",
        "kr": "<b>💰 종소세 신고 시즌, 꼭 읽어야 할 절세 책</b>\n\n5월 종합소득세 마감 전 환급금 놓치지 마세요. 소상공인·프리랜서용 절세 바이블.\n\n절세·세무 베스트 👇",
        "en": "Tax saving bible — for freelancers & small biz.",
        "tags": "#절세 #종합소득세 #세테크",
    },
    {
        "theme": "홈오피스 세팅",
        "kr": "<b>🖥️ 집에서 일하는 프리랜서용 홈오피스 세팅</b>\n\n허리 살리는 의자 + 목 안 아픈 모니터 스탠드 + 키보드. 월 수익 2배 만드는 환경.\n\n홈오피스 필수템 👇",
        "en": "Home office essentials for freelancers.",
        "tags": "#홈오피스 #프리랜서 #재택근무",
    },
    {
        "theme": "꿈해몽·길몽 도서",
        "kr": "<b>🌙 꿈해몽 책 — 로또 번호 뽑을 때 필수</b>\n\n꿈이 알려주는 길흉, 앱보다 책이 더 자세해요. 조상 현몽·돈꿈·태몽 전부.\n\n꿈해몽 사전 BEST 👇",
        "en": "Dream interpretation books — detailed than apps.",
        "tags": "#꿈해몽 #길몽 #로또꿈",
    },
]

def send_tg(text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            data={"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False},
            timeout=10,
        )
        return r.ok
    except Exception as e:
        print(f"  TG fail: {e}")
        return False

def post_x(client, text):
    try:
        client.create_tweet(text=text[:280])
        return True
    except Exception as e:
        print(f"  X fail: {e}")
        return False

def main():
    x = None
    try:
        x = tweepy.Client(
            consumer_key=X_API_KEY, consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN, access_token_secret=X_ACCESS_SECRET,
        )
    except Exception as e:
        print(f"X init fail: {e}")

    for i, p in enumerate(POSTS):
        tg = (
            f"{p['kr']}\n\n"
            f"👉 {COUPANG_LINK}\n\n"
            f"{p['tags']}"
            f"{DISCLOSURE}"
        )
        if send_tg(tg):
            print(f"OK TG {i+1}/{len(POSTS)} {p['theme']}")

        if x:
            tweet_body = p['kr'].replace('<b>', '').replace('</b>', '')
            tweet = (
                f"{tweet_body.split(chr(10))[0]}\n\n"
                f"{COUPANG_LINK}\n"
                f"{p['tags']}\n"
                f"※쿠팡 파트너스 활동"
            )
            if post_x(x, tweet):
                print(f"OK X  {i+1}/{len(POSTS)} {p['theme']}")
        time.sleep(15)

    print("\n쿠팡 파트너스 콘텐츠 발행 완료")

if __name__ == "__main__":
    main()
