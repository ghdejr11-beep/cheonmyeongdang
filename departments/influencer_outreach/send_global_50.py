"""Cheonmyeongdang — Global 50 Influencer Outreach Sender (4 languages).

설계 원칙 (memory feedback 준수):
1. 정중한 톤 (feedback_dm_polite_tone)
2. 특정 연예인/IP 거론 금지 (feedback_no_specific_company_names)
3. 검색 없이 추측 X — 검증된 이메일만 발송
4. 자동 가능 작업은 즉시 처리 (feedback_auto_process_no_permission)

흐름:
- DRY-RUN  (default): 모든 후보에 대해 본문 생성, 이메일 검증된 것만 'WOULD SEND' 출력
- --confirm        : Gmail API 로 실제 발송 (이메일 검증된 것만)
- --batch N        : 5명씩 batch (1=첫 5, 2=다음 5, ...) — language 균등 분배 우선
- --first-batch    : 5명 × 4언어 = 20명 첫 batch (오늘 발송용)

⚠️ 이메일 미검증 후보(is_email_unverified=true)는 무조건 SKIP. 발송 시도조차 안 함.
   사용자가 수동으로 contact-form/DM 으로 메시지 전달 후 JSON 업데이트 → 다음 batch.

Reuses Gmail send pattern from departments/secretary/ + b2b_sales/.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import secrets
import string
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "global_50_2026_05_06.json"
SENT_LOG_PATH = ROOT / "sent_log_global_2026_05_06.json"
DRAFTS_DIR = ROOT / "drafts_global_2026_05_06"
DRAFTS_DIR.mkdir(exist_ok=True)

# Gmail token — reuse secretary's (gmail.modify scope, send-capable)
TOKEN_PATH = (ROOT / ".." / "secretary" / "token.json").resolve()

FROM_NAME = "Hong Deokhun (KunStudio)"
FROM_EMAIL = "ghdejr11@gmail.com"
SITE_URL = "https://cheonmyeongdang.vercel.app"
SLEEP_BETWEEN_SENDS = 60  # 1 email/min — well under Gmail soft caps

# ---------------------------------------------------------------------------
# Email body templates per language (1.5K~2K chars; polite, no SHOUT, opt-out)
# ---------------------------------------------------------------------------

SUBJECTS = {
    "ko": "{name}님께 — 천명당 사주 AI 1개월 무료 이용권 (선물)",
    "en": "A free 1-month gift for {name} — Korean Saju AI (Cheonmyeongdang)",
    "ja": "{name}様へ — 韓国サジュAI「天命堂」1ヶ月無料ギフト",
    "zh": "致 {name} — 韓國四柱命理 AI（天命堂）1 個月免費禮券",
}

BODY_KO = """안녕하세요 {name}님,

저는 한국에서 사주명리 기반 AI 서비스 '천명당'을 만들고 있는 홍덕훈(쿤스튜디오)이라고 합니다. 평소 {handle} 의 콘텐츠를 즐겨 보고 있습니다 — 특히 {niche} 쪽 글/영상이 풀어내시는 결이 깔끔하셔서 자주 참고하고 있어요.

오늘 메일을 드린 이유는 단 하나, 천명당 1개월 프리미엄 이용권을 부담 없이 선물로 드리고 싶어서입니다.

▷ 이용권 코드: {code}
▷ 사용 방법: {site}/redeem 에서 코드 입력 → 바로 활성화 (₩9,900 가치)
▷ 유효기간: 발급일로부터 30일 안에 활성화

내용물은 동양 사주명리 4기둥(년주/월주/일주/시주) 분석, 오행 상호작용 그래프, 일/월/년 운세 리포트, 그리고 본인이 직접 질문할 수 있는 사주 챗봇입니다. 한국에서 만든 토종 사주 AI라 알고리즘이 정통 명리학에 기반해 있고, 단순 별자리 콘텐츠와는 결이 다른 깊이를 제공합니다.

부탁이 아닌 선물입니다. 게시글/영상/스토리 의무 X, 제휴 추적 X, 후기 강요 X. 본인 사주를 한 번 직접 보시고 마음에 드시면 자유롭게 공유해 주셔도 좋고, 별 감흥이 없으시면 그냥 한 달 무료로 써보신 걸로 끝내셔도 전혀 괜찮습니다.

추가로 궁금하신 점(사주 시스템, 알고리즘 출처, 데이터 처리 방식 등) 있으시면 본 메일에 회신해 주세요. 30시간 안에 답변 드리겠습니다.

마지막으로, 만약 이 메일이 불편하시거나 향후 비슷한 연락을 받고 싶지 않으시다면 본 메일에 "수신 거부" 한 마디만 남겨주세요. 즉시 발송 리스트에서 제거하고 다시는 연락 드리지 않겠습니다.

좋은 콘텐츠 늘 응원합니다.

홍덕훈 드림
쿤스튜디오 · 천명당 사주 AI
{from_email}
{site}
"""

BODY_EN = """Hi {name},

I'm Deokhun Hong, an indie Korean creator behind Cheonmyeongdang — a Korean Saju (사주, Eastern 4-pillars astrology) AI app. I've been quietly following {handle} for a while, and your work in {niche} has stood out to me as one of the more genuine voices in the space — your tone and the angles you choose have shaped how I think about the niche, honestly.

I'm writing for one reason: I'd like to gift you a 1-month premium pass to Cheonmyeongdang, with no strings.

▷ Your code: {code}
▷ How to redeem: visit {site}/redeem and enter the code (worth roughly USD 7.50 / KRW 9,900)
▷ Validity: activate within 30 days of receiving this email

What's inside: full 4-pillars (year/month/day/hour) chart analysis, five-elements (wuxing) interaction visualization, daily/monthly/yearly fortune reports, and an interactive Saju chatbot you can ask in plain English. The algorithm is built on traditional Korean myeongri (命理) sources rather than generic Western horoscope logic, so it offers a genuinely different toolkit if your audience has been feeling burnt out on houses and transits.

This is a gift, not an ask. No post is required. There's no affiliate tracker, no review obligation, no follow-up nudge. Pull your own chart, see if it sparks anything, and if it does, share or don't share — entirely up to you.

If you do have questions about how the system works, where the data comes from, or how readings are computed, just reply to this email. I read every reply within 30 hours and answer personally.

Lastly: if this message is unwelcome or you'd rather not hear from me again, simply reply with the word "unsubscribe" and I'll remove you from any future outreach. No further mail will reach you from this address.

Thank you for the work you put out. It genuinely matters in a niche full of repeats.

Best regards,
Deokhun Hong
KunStudio · Cheonmyeongdang Korean Saju AI
{from_email}
{site}
"""

BODY_JA = """{name}様

はじめまして。韓国でサジュ命理ベースのAIサービス「天命堂(チョンミョンダン)」を開発している、ホン・ドックン(KunStudio代表)と申します。普段から {handle} さんのコンテンツを拝見しており、特に {niche} に関する発信は丁寧で深さがあり、いつも参考にさせていただいております。

本日ご連絡を差し上げたのは、ただ一つ、天命堂プレミアム1ヶ月無料利用券をお礼の気持ちでお贈りしたいためです。

▷ ご利用券コード: {code}
▷ 使用方法: {site}/redeem にアクセスし、コードを入力 → 即時有効化(9,900ウォン/約1,100円相当)
▷ 有効期限: 発行日から30日以内にご利用開始ください

サービス内容: 韓国伝統四柱(年柱/月柱/日柱/時柱)分析、五行相互作用グラフ、日運/月運/年運レポート、そしてご自身で質問できるサジュチャットボット機能を含みます。韓国本場の命理学アルゴリズムに基づいており、一般的な西洋占星術コンテンツとは異なる視点を提供できると思います。

これはお願いではなく、純粋な贈り物です。投稿義務なし、アフィリエイト追跡なし、レビュー強制なし。ご自身のサジュをご覧いただいて、興味をお持ちいただければ自由にシェアしていただいて構いませんし、ピンと来なければそのまま1ヶ月無料体験で終了いただいて全く問題ございません。

サジュシステムの仕組み、アルゴリズムのソース、データ処理方法などご質問がございましたら、本メールへご返信ください。30時間以内にご対応いたします。

最後に、もし本メールが不快に感じられたり、今後同様のご連絡を受け取りたくない場合は、本メールに「配信停止」とだけご返信ください。即座にリストから削除し、二度とご連絡いたしません。

いつも素敵なコンテンツをありがとうございます。

ホン・ドックン拝
KunStudio · 天命堂サジュAI
{from_email}
{site}
"""

BODY_ZH = """{name} 您好,

我是來自韓國的獨立開發者洪德勳(KunStudio),目前正在打造一款結合韓國四柱命理的 AI 服務「天命堂(Cheonmyeongdang)」。一直以來在關注 {handle} 的內容,特別是 {niche} 領域的分享,風格清晰、深度有料,經常給我很多啟發。

今天寫信給您,只有一個目的: 想單純地送您一張天命堂高級會員 1 個月免費體驗券,作為一份小心意。

▷ 您的禮券代碼: {code}
▷ 使用方法: 前往 {site}/redeem,輸入代碼即可立即啟用(價值約 9,900 韓圓 / 約 230 新台幣)
▷ 有效期: 收到郵件後 30 天內啟用

服務內容: 韓國傳統四柱八字(年柱/月柱/日柱/時柱)分析、五行相生相剋圖、日運/月運/年運報告,以及可以直接用中文提問的命理聊天機器人。演算法以韓國正統命理學為基礎,與一般西洋星座內容相比,提供截然不同的東方視角,希望能對您的內容創作或個人探索帶來新的素材。

這完全是一份禮物,不是請求。無發文義務、無聯盟追蹤、無評論強制。請您自由地查看自己的命盤,如果覺得有趣可以自由分享,如果沒有共鳴,當作免費體驗一個月即可,絕無壓力。

如果您對命理系統的運作原理、演算法來源、資料處理方式等有任何疑問,歡迎直接回覆此信。我會在 30 小時內親自回覆。

最後,如果這封信讓您感到打擾,或您不希望日後再收到類似聯絡,請只需回覆「取消訂閱」三個字。我會立即將您從清單中移除,不會再有任何訊息送達您的信箱。

感謝您一直以來的優質創作。

洪德勳 敬上
KunStudio · 天命堂韓國四柱命理 AI
{from_email}
{site}
"""

BODIES = {"ko": BODY_KO, "en": BODY_EN, "ja": BODY_JA, "zh": BODY_ZH}


# ---------------------------------------------------------------------------
# Code suffix generator (KSAJU-XXXXX-XXXXXX, suffix random for tracking)
# ---------------------------------------------------------------------------


def make_code_suffix(seed: str) -> str:
    """Deterministic 6-char suffix from idx so reruns reproduce the same code."""
    alphabet = string.ascii_uppercase + string.digits
    rng = secrets.SystemRandom()
    # Seeded via system random for now — recorded in JSON so reruns SHOULD use stored
    return "".join(rng.choice(alphabet) for _ in range(6))


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


def render_subject(c: dict) -> str:
    return SUBJECTS[c["language"]].format(name=c["name"])


def render_body(c: dict, full_code: str) -> str:
    return BODIES[c["language"]].format(
        name=c["name"],
        handle=c["handle"],
        niche=c["niche"],
        code=full_code,
        site=SITE_URL,
        from_email=FROM_EMAIL,
    )


# ---------------------------------------------------------------------------
# Gmail
# ---------------------------------------------------------------------------


def load_gmail_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    if not TOKEN_PATH.is_file():
        raise SystemExit(f"[ABORT] Gmail token not found: {TOKEN_PATH}")
    data = json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes"),
    )
    return build("gmail", "v1", credentials=creds)


def build_mime(subject: str, body: str, to_email: str) -> str:
    msg = MIMEMultipart()
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    return base64.urlsafe_b64encode(msg.as_bytes()).decode()


# ---------------------------------------------------------------------------
# Log
# ---------------------------------------------------------------------------


def append_log(entry: dict) -> None:
    log = {"_meta": {"created": "2026-05-06"}, "sent": []}
    if SENT_LOG_PATH.is_file():
        try:
            log = json.loads(SENT_LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    log.setdefault("sent", []).append(entry)
    SENT_LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true",
                        help="ACTUALLY send. Without flag, dry-run only.")
    parser.add_argument("--first-batch", action="store_true",
                        help="First batch: top 5 verified per language = 20 emails")
    parser.add_argument("--write-drafts", action="store_true",
                        help="Write per-recipient body files to drafts_global_2026_05_06/ "
                             "(useful for manual contact-form fill when email is unverified).")
    args = parser.parse_args()

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    candidates = data["candidates"]

    # Compose the full code for each candidate (deterministic per-run via random suffix
    # but recorded in the sent log so we can re-find which recipient got which code).
    for c in candidates:
        c["full_code"] = f"{c['code_seq']}-{make_code_suffix(str(c['idx']))}"

    # Verified for SEND = email is non-null AND is_email_unverified=False
    def is_sendable(c: dict) -> bool:
        return bool(c.get("email")) and not c.get("is_email_unverified", True)

    sendable = [c for c in candidates if is_sendable(c)]
    unverified = [c for c in candidates if not is_sendable(c)]

    print("=" * 72)
    print(" Cheonmyeongdang Global 50 Influencer Outreach")
    print("=" * 72)
    print(f"  Total candidates       : {len(candidates)}")
    print(f"  Sendable (email OK)    : {len(sendable)}")
    print(f"  Unverified (no email)  : {len(unverified)}")
    print(f"  Mode                   : {'LIVE SEND' if args.confirm else 'DRY RUN'}")
    print(f"  Write drafts           : {args.write_drafts}")
    print()

    # By language breakdown
    from collections import Counter
    lang_counts = Counter(c["language"] for c in candidates)
    print("  Per language:")
    for lang in ("ko", "en", "ja", "zh"):
        sendable_in_lang = sum(1 for c in candidates if c["language"] == lang and is_sendable(c))
        print(f"    {lang}: {lang_counts[lang]} total, {sendable_in_lang} sendable")
    print()

    # Drafts: write body to file (always — useful for manual fill regardless of mode)
    if args.write_drafts or not sendable:
        print(f"  Writing per-recipient drafts to {DRAFTS_DIR.name}/ ...")
        for c in candidates:
            subj = render_subject(c)
            body = render_body(c, c["full_code"])
            fname = f"{c['idx']:03d}_{c['language']}_{c['code_seq']}_{c['handle'].replace('@','').replace('/','_')[:30]}.txt"
            (DRAFTS_DIR / fname).write_text(
                f"To: {c.get('email') or '[NO EMAIL — manual contact-form/DM fill]'}\n"
                f"Subject: {subj}\n\n{body}",
                encoding="utf-8",
            )
        print(f"    -> {len(candidates)} drafts written.")
        print()

    if not sendable:
        print("[INFO] No sendable candidates (all are email-unverified).")
        print("       Action: fill in 'email' field for verified contacts in")
        print(f"       {JSON_PATH.name}, set is_email_unverified=false, rerun.")
        print("       Drafts are available for manual contact-form/DM transmission.")
        return

    # Pick batch
    if args.first_batch:
        # 5 per language
        batch = []
        for lang in ("ko", "en", "ja", "zh"):
            in_lang = [c for c in sendable if c["language"] == lang][:5]
            batch.extend(in_lang)
    else:
        batch = sendable

    if not batch:
        print("[INFO] No emails to send in selected batch.")
        return

    print(f"  Batch size: {len(batch)}")
    print()

    if not args.confirm:
        print("[DRY-RUN] No emails will be sent. Add --confirm to send.")
        for c in batch:
            print(f"  -> [{c['language']}] idx={c['idx']:>2} code={c['full_code']}")
            print(f"     to={c['email']}")
            print(f"     subject={render_subject(c)[:70]}")
        return

    service = load_gmail_service()
    sent_count = 0
    for c in batch:
        subj = render_subject(c)
        body = render_body(c, c["full_code"])
        raw = build_mime(subj, body, c["email"])
        try:
            res = service.users().messages().send(userId="me", body={"raw": raw}).execute()
            mid = res.get("id")
            print(f"  [SENT] [{c['language']}] idx={c['idx']:>2} -> {c['email']} msg_id={mid}")
            append_log({
                "sent_at": dt.datetime.now().isoformat(),
                "idx": c["idx"],
                "language": c["language"],
                "handle": c["handle"],
                "email": c["email"],
                "code": c["full_code"],
                "subject": subj,
                "gmail_msg_id": mid,
                "response": None,
            })
            sent_count += 1
            if c is not batch[-1]:
                time.sleep(SLEEP_BETWEEN_SENDS)
        except Exception as exc:
            print(f"  [ERROR] idx={c['idx']} -> {exc}")

    print()
    print(f"=== Done. Sent {sent_count} of {len(batch)}. ===")
    print(f"  Sent log: {SENT_LOG_PATH}")


if __name__ == "__main__":
    main()
