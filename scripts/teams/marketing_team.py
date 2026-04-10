"""
📣 마케팅부 (Marketing Team)

매일 09:00 + 21:00 KST 자동 실행 (GitHub Actions cron).

역할:
  1. 어제 올린 YouTube/Gumroad 상품 확인
  2. Claude 에게 마케팅 콘텐츠 생성 요청:
     - 블로그 SEO 글 1개
     - 인스타그램 캡션 5개 (해시태그 포함)
     - 트위터 쓰레드 1개
     - 카드뉴스 텍스트 5장
  3. shared/marketing_ready/ 에 저장
  4. 텔레그램으로 보고 (너가 복붙만 하면 됨)

추후 확장:
  - 키워드 리서치 (Google Trends API)
  - 인스타 자동 발행 (Meta Business API)
  - 카드뉴스 이미지 자동 생성 (PIL/Canva)
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from scripts.lib.telegram_notify import notify_safe

KST = timezone(timedelta(hours=9))
SHARED_DIR = SCRIPT_DIR / "shared" / "marketing_ready"
SHARED_DIR.mkdir(parents=True, exist_ok=True)


def now_kst() -> datetime:
    return datetime.now(KST)


def now_kst_str() -> str:
    return now_kst().strftime("%Y-%m-%d %H:%M KST")


def get_products_info() -> str:
    """현재 판매 중인 상품 정보 수집."""
    products = []

    # Gumroad 상품
    products.append("Gumroad 상품:")
    products.append("  1. AI 부업 시작 가이드 LITE (19,900원) - ai-start")
    products.append("  2. AI 월 500만원 자동화 시스템 STANDARD (99,000원) - ai-500")
    products.append("  3. AI 부업 PREMIUM + AI 멘토봇 (299,000원) - ai-premium")
    products.append("  4. 프롬프트 900개+ 팩 [얼리버드] (9,900원) - ai-prompt-early")

    # 사주 SaaS
    products.append("")
    products.append("사주 AI SaaS:")
    products.append("  URL: https://cheonmyeongdang.onrender.com")
    products.append("  가격: 월 9,900원 (3회 무료 체험)")
    products.append("  카카오톡 봇: 심사 중 (2~3일 내 승인)")

    # YouTube
    products.append("")
    products.append("YouTube 채널: 덕구네")
    products.append("  콘텐츠: AI 음악 (펫로스 발라드), BGM 믹스")

    return "\n".join(products)


def generate_marketing_content() -> dict:
    """Claude 에게 마케팅 콘텐츠 생성 요청."""
    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY 없음"}

    try:
        import anthropic
    except ImportError:
        return {"error": "anthropic 패키지 미설치"}

    products = get_products_info()
    today = now_kst().strftime("%Y년 %m월 %d일 %A")

    prompt = f"""너는 덕구네 AI 사업단의 마케팅부 책임자다.
오늘 날짜: {today}

[판매 중인 상품]
{products}

[브랜드 정보]
- 브랜드명: 덕구네
- 타깃: 한국 직장인·부업러 (25~45세)
- 톤: 친근하고 실용적, 과장 없이 진짜 도움 되는 정보
- USP: AI 로 진짜 돈 버는 시스템 (자동화 + 검증된 방법)

아래 4가지를 JSON 으로 생성해라:

{{
  "blog_post": {{
    "title": "SEO 최적화된 블로그 제목 (50자 이내)",
    "meta_description": "검색 노출용 설명 (160자 이내)",
    "keywords": ["키워드1", "키워드2", ...],
    "content": "블로그 본문 (800~1200자, 마크다운, CTA 포함)"
  }},
  "instagram_captions": [
    {{
      "caption": "인스타 캡션 (300자 이내, 해시태그 15개 포함)",
      "hook": "첫 줄 훅 (호기심 유발)"
    }},
    ... (5개)
  ],
  "twitter_thread": [
    "트윗 1 (280자 이내, 훅)",
    "트윗 2",
    "트윗 3",
    "트윗 4 (CTA + 링크)"
  ],
  "card_news": [
    {{
      "slide": 1,
      "title": "카드뉴스 제목",
      "body": "본문 (50자 이내)",
      "cta": "행동 유도 문구"
    }},
    ... (5장)
  ]
}}

JSON 만 출력. 설명 금지."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in msg.content if hasattr(b, "text"))

        # JSON 추출
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        return {"error": f"JSON 파싱 실패: {text[:200]}"}
    except Exception as e:
        return {"error": f"Claude 호출 실패: {type(e).__name__}: {str(e)[:200]}"}


def save_content(content: dict) -> list[str]:
    """생성된 콘텐츠를 shared/marketing_ready/ 에 저장."""
    saved = []
    date_str = now_kst().strftime("%Y%m%d")

    # 블로그
    if "blog_post" in content:
        blog = content["blog_post"]
        path = SHARED_DIR / f"{date_str}_blog.md"
        md = f"# {blog.get('title', '')}\n\n"
        md += f"> {blog.get('meta_description', '')}\n\n"
        md += f"키워드: {', '.join(blog.get('keywords', []))}\n\n"
        md += blog.get("content", "")
        path.write_text(md, encoding="utf-8")
        saved.append(f"  📝 {path.name}")

    # 인스타
    if "instagram_captions" in content:
        path = SHARED_DIR / f"{date_str}_instagram.txt"
        lines = []
        for i, cap in enumerate(content["instagram_captions"], 1):
            lines.append(f"--- 캡션 {i} ---")
            lines.append(f"훅: {cap.get('hook', '')}")
            lines.append(cap.get("caption", ""))
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        saved.append(f"  📱 {path.name}")

    # 트위터
    if "twitter_thread" in content:
        path = SHARED_DIR / f"{date_str}_twitter.txt"
        lines = []
        for i, tweet in enumerate(content["twitter_thread"], 1):
            lines.append(f"[{i}/{len(content['twitter_thread'])}]")
            lines.append(tweet)
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        saved.append(f"  🐦 {path.name}")

    # 카드뉴스
    if "card_news" in content:
        path = SHARED_DIR / f"{date_str}_cardnews.txt"
        lines = []
        for card in content["card_news"]:
            lines.append(f"[슬라이드 {card.get('slide', '?')}]")
            lines.append(f"제목: {card.get('title', '')}")
            lines.append(f"본문: {card.get('body', '')}")
            lines.append(f"CTA: {card.get('cta', '')}")
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        saved.append(f"  🎴 {path.name}")

    return saved


def build_telegram_report(content: dict, saved: list[str]) -> str:
    """텔레그램 보고용 메시지."""
    if "error" in content:
        return f"🚨 [마케팅부] 콘텐츠 생성 실패\n{content['error']}"

    # 인스타 캡션 첫 번째만 미리보기
    insta_preview = ""
    if "instagram_captions" in content and content["instagram_captions"]:
        first = content["instagram_captions"][0]
        insta_preview = f"\n📱 인스타 캡션 미리보기:\n{first.get('hook', '')}\n{first.get('caption', '')[:200]}..."

    # 블로그 제목
    blog_title = content.get("blog_post", {}).get("title", "(없음)")

    report = f"""📣 [마케팅부] 일일 콘텐츠 생성 완료
🕒 {now_kst_str()}

━━━━━━━━━━━━━━━━━━━
📦 생성된 콘텐츠
{chr(10).join(saved) if saved else '  (없음)'}

━━━━━━━━━━━━━━━━━━━
📝 블로그: {blog_title}
📱 인스타 캡션: {len(content.get('instagram_captions', []))}개
🐦 트위터 쓰레드: {len(content.get('twitter_thread', []))}트윗
🎴 카드뉴스: {len(content.get('card_news', []))}장
{insta_preview}

━━━━━━━━━━━━━━━━━━━
📂 전체 파일: shared/marketing_ready/
→ 복붙해서 각 채널에 게시하면 됩니다.

다음 자동 실행: 매일 09:00 + 21:00 KST"""

    return report


def main() -> int:
    print(f"[마케팅부] 시작 {now_kst_str()}")

    content = generate_marketing_content()
    saved = save_content(content) if "error" not in content else []
    report = build_telegram_report(content, saved)

    print("=" * 60)
    print(report)
    print("=" * 60)

    sent = notify_safe(report)
    if sent:
        print("✅ 텔레그램 발송 성공")
    else:
        print("❌ 텔레그램 발송 실패")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
