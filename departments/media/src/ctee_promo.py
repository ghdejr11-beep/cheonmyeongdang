#!/usr/bin/env python3
"""크티 프롬프트팩 9종 자동 홍보 (텔레그램 + X)"""
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

TG_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN'] if 'TELEGRAM_BOT_TOKEN' in os.environ else os.environ.get('TG_BOT_TOKEN', '')
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') or os.environ.get('TG_CHAT_ID', '')

X_API_KEY = os.environ['X_API_KEY']
X_API_SECRET = os.environ['X_API_SECRET']
X_ACCESS_TOKEN = os.environ['X_ACCESS_TOKEN']
X_ACCESS_SECRET = os.environ['X_ACCESS_SECRET']

CTEE_STORE = "https://ctee.kr/@ghdejr11"
COUPANG_LINK = "https://link.coupang.com/a/emjC0T&subId=cteeshop01"

PRODUCTS = [
    {
        "cat": "블로그",
        "title": "블로그 AI 프롬프트 100선 — SEO 포스팅",
        "price": "9,900원",
        "hashtags": "#블로그 #SEO #AI프롬프트",
        "hook_kr": "블로그 글 하나 쓰는데 3시간씩 걸리시나요?\n검증된 SEO 프롬프트 100개로 30분 만에 완성하세요.",
        "hook_en": "Blog writing 3hrs → 30min with 100 proven SEO prompts.",
    },
    {
        "cat": "비즈니스",
        "title": "비즈니스 AI 프롬프트 100선 — 사업계획·투자유치",
        "price": "14,900원",
        "hashtags": "#스타트업 #사업계획서 #AI",
        "hook_kr": "VC가 통과시킬 사업계획서, AI로 3시간 안에.\n시장분석·재무모델·피치덱까지 한 번에.",
        "hook_en": "Investor-ready pitch deck in 3 hours with AI.",
    },
    {
        "cat": "카피라이팅",
        "title": "카피라이팅 AI 프롬프트 100선 — 매출 올리는 광고·세일즈",
        "price": "12,900원",
        "hashtags": "#카피라이팅 #마케팅 #광고",
        "hook_kr": "클릭 안 되는 광고에 돈 날리고 계신가요?\n전환율 2~5배 올리는 실전 카피 100개.",
        "hook_en": "2-5x conversion with 100 battle-tested ad copies.",
    },
    {
        "cat": "데이터 분석",
        "title": "데이터 AI 프롬프트 100선 — 엑셀·시각화·보고서",
        "price": "14,900원",
        "hashtags": "#엑셀 #데이터분석 #보고서",
        "hook_kr": "피벗·수식에 시간 뺏기지 마세요.\nAI가 엑셀 자동 분석 + 차트 + 요약까지.",
        "hook_en": "Excel analysis in seconds. Pivot+chart+summary.",
    },
    {
        "cat": "디자인",
        "title": "디자인 AI 프롬프트 100선 — Midjourney·로고·썸네일",
        "price": "12,900원",
        "hashtags": "#Midjourney #디자인 #AI이미지",
        "hook_kr": "Midjourney에서 원하는 그림이 안 나오시나요?\n퀄리티 프롬프트 100개로 즉시 해결.",
        "hook_en": "100 pro Midjourney prompts that actually work.",
    },
    {
        "cat": "이메일 마케팅",
        "title": "이메일 마케팅 AI 프롬프트 100선 — 뉴스레터·콜드메일",
        "price": "9,900원",
        "hashtags": "#이메일마케팅 #뉴스레터 #B2B",
        "hook_kr": "오픈율 10% 이하에서 허덕이시나요?\n실검증 프롬프트로 30%+ 달성.",
        "hook_en": "10%→30% email open rate with proven prompts.",
    },
    {
        "cat": "외국어 학습",
        "title": "외국어 AI 프롬프트 100선 — 영어·일본어 AI 과외",
        "price": "9,900원",
        "hashtags": "#영어회화 #일본어 #AI과외",
        "hook_kr": "월 40만원 1:1 과외 말고, AI 24시간 선생님.\n실전 회화·작문 첨삭 프롬프트 100개.",
        "hook_en": "24/7 AI tutor: conversation + grammar correction.",
    },
    {
        "cat": "SNS 콘텐츠",
        "title": "SNS AI 프롬프트 100선 — 인스타·틱톡·숏폼",
        "price": "9,900원",
        "hashtags": "#인스타그램 #틱톡 #숏폼",
        "hook_kr": "콘텐츠 아이디어 말라서 업로드 못 하시나요?\n바이럴 훅 100개로 30일치 콘텐츠 확보.",
        "hook_en": "30 days of viral content ideas in one pack.",
    },
    {
        "cat": "유튜브",
        "title": "유튜브 AI 프롬프트 100선 — 대본·썸네일·SEO",
        "price": "9,900원",
        "hashtags": "#유튜브 #유튜버 #대본",
        "hook_kr": "조회수 안 터져서 고민이시죠?\n후킹 대본·썸네일 문구·SEO 실전 프롬프트 100개.",
        "hook_en": "YouTube script+thumbnail+SEO prompt bundle.",
    },
]

def send_tg(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
        data={"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False},
    )
    return r.ok

def post_x(client, text):
    try:
        client.create_tweet(text=text[:280])
        return True
    except Exception as e:
        print(f"  X fail: {e}")
        return False

def main():
    # X client
    x = None
    try:
        x = tweepy.Client(
            consumer_key=X_API_KEY, consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN, access_token_secret=X_ACCESS_SECRET,
        )
    except Exception as e:
        print(f"X init fail: {e}")

    # 첫 메시지: 전체 상품 인덱스 (텔레그램만 — X는 280자 제한)
    index_text = "<b>🎉 크티 프롬프트팩 9종 신규 오픈!</b>\n\n"
    for p in PRODUCTS:
        index_text += f"• <b>{p['cat']}</b> — {p['price']}\n"
    index_text += f"\n👉 전체 상품 보기\n{CTEE_STORE}\n\n"
    index_text += "모든 상품 ChatGPT · Claude · Gemini 호환\n"
    index_text += "#AI #프롬프트 #쿤스튜디오"
    if send_tg(index_text):
        print("✅ TG index sent")
    time.sleep(3)

    # 각 상품별 개별 포스트
    for i, p in enumerate(PRODUCTS):
        tg = (
            f"<b>{p['title']}</b>\n\n"
            f"{p['hook_kr']}\n\n"
            f"💰 {p['price']}\n"
            f"🔗 {CTEE_STORE}\n\n"
            f"{p['hashtags']} #AI프롬프트 #쿤스튜디오"
        )
        if send_tg(tg):
            print(f"✅ TG {i+1}/{len(PRODUCTS)} {p['cat']}")

        if x:
            tweet = (
                f"📦 {p['cat']} AI 프롬프트 100선 ({p['price']})\n\n"
                f"{p['hook_kr'].split(chr(10))[0]}\n\n"
                f"{CTEE_STORE}\n\n"
                f"{p['hashtags']}"
            )
            if post_x(x, tweet):
                print(f"✅ X  {i+1}/{len(PRODUCTS)} {p['cat']}")
        time.sleep(15)  # 스팸 방지

    print("\n🎯 크티 9종 홍보 완료")

if __name__ == "__main__":
    main()
