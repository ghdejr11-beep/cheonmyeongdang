#!/usr/bin/env python3
"""세금N혜택 리런칭 홍보 — 새 랜딩 페이지 + 간편인증 UI 오픈 (D-45 긴급)"""
import requests, time

TG_BOT_TOKEN = "8650272218:AAHIYmOVfqzMzr-hcOqWsfW6mftByoEd_SA"
TG_CHAT_ID = "8556067663"

LANDING = "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/tax/src/"
APP = "https://ghdejr11-beep.github.io/cheonmyeongdang/departments/tax/src/app.html"

MESSAGES = [
    # 1. 신규 오픈 알림
    {
        "text": (
            "<b>🎉 세금N혜택 정식 오픈!</b>\n\n"
            "종합소득세 환급 조회 서비스를 드디어 오픈합니다.\n\n"
            "✅ <b>수수료 0원</b> - 타 서비스 대비 10~20% 절감\n"
            "✅ <b>1분 조회</b> - 카카오·토스·PASS·네이버 간편인증\n"
            "✅ <b>회원가입 불필요</b> - 바로 시작\n"
            "✅ <b>5년치 환급금</b> 자동 조회\n\n"
            "🔥 종합소득세 신고 D-45 (5/31 마감)\n"
            "지금 바로 내 환급금 확인하세요 👇\n\n"
            f"{LANDING}"
        ),
    },
    # 2. 작년 평균 환급액 후킹
    {
        "text": (
            "<b>💰 작년 평균 환급액 32만원</b>\n\n"
            "프리랜서·1인 사업자 평균 49만원\n"
            "직장인 부업러(유튜브·블로그) 평균 25만원\n"
            "크리에이터 평균 38만원\n\n"
            "홈택스 로그인도 필요 없이 카카오톡만 있으면\n"
            "<b>1분만에</b> 내 환급금 확인 가능합니다.\n\n"
            f"👉 {LANDING}\n\n"
            "#종합소득세 #세금환급 #프리랜서 #세금N혜택"
        ),
    },
    # 3. 대상별 어필
    {
        "text": (
            "<b>🎯 이런 분께 꼭 추천합니다</b>\n\n"
            "💼 <b>프리랜서·1인 사업자</b>\n"
            "  3.3% 원천징수 환급, 경비처리 가이드\n"
            "  → 평균 환급액 49만원\n\n"
            "🏪 <b>자영업자·소상공인</b>\n"
            "  부가세+종합소득세 한번에, 정부 지원금 매칭\n\n"
            "🎬 <b>직장인 부업러</b>\n"
            "  유튜브·블로그·과외 수입 간편 신고\n\n"
            f"지금 조회하기 → {LANDING}"
        ),
    },
    # 4. FAQ 대응
    {
        "text": (
            "<b>❓ 자주 묻는 질문</b>\n\n"
            "<b>Q. 정말 수수료가 0원?</b>\n"
            "A. 네. 조회·신청·입금 모두 무료.\n"
            "   환급액 100% 본인 계좌로 입금.\n\n"
            "<b>Q. 개인정보 안전한가요?</b>\n"
            "A. 주민번호는 서버에 저장되지 않음.\n"
            "   한국신용정보원 인증 API(CODEF) 사용.\n\n"
            "<b>Q. 어떻게 수수료 없이 운영?</b>\n"
            "A. 관련 도서·광고 제휴 수익으로 운영.\n"
            "   환급금에서 일체 수수료 X\n\n"
            f"더 궁금한 것은 → {LANDING}#faq"
        ),
    },
]

def send(text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": TG_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=10,
        )
        return r.ok
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("세금N혜택 리런칭 홍보 시작...")
    for i, m in enumerate(MESSAGES):
        if send(m["text"]):
            print(f"  [{i+1}/{len(MESSAGES)}] OK")
        else:
            print(f"  [{i+1}/{len(MESSAGES)}] FAIL")
        time.sleep(8)
    print(f"\n완료. 총 {len(MESSAGES)}개 메시지 발송.")

if __name__ == "__main__":
    main()
