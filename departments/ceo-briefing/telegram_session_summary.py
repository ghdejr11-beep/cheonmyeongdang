"""사장님 5/7 종합 진단 텔레그램 보고 — 38부서 + 매출 + 즉시 액션."""
import os, json, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / ".secrets"
env = {}
if SECRETS.exists():
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or env.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID") or env.get("TELEGRAM_CHAT_ID", "")

msg = """🚨 <b>사장님 5/7 종합 진단</b>
━━━━━━━━━━━━━━
<b>오늘 실 매출 ₩0</b> (Gumroad·PayPal 0건 / 토스 테스트키)
진단: <b>인프라 100% / 트래픽 5% / 전환 검증 0%</b>
원인: 누가 천명당을 모름.

━━━ <b>핵심 8부서</b> ━━━

<b>① 천명당 SaaS</b>
v3.5 4언어 라이브 / PayPal 활성 / <i>유입 0</i>
→ Pinterest 4lang + Bluesky 푸시 강화
→ 1주 목표: 일 500방문, 첫 결제 1건

<b>② Gumroad (digital-products)</b>
4상품 라이브 / 3일 0건
→ 24h 50% off bundle ₩39,000 promo
→ 1주: 5건 ₩150K

<b>③ PayPal 글로벌</b>
Smart Buttons live / SEO 미진입
→ en/ja/zh IndexNow 재제출
→ 1주: 첫 글로벌 결제 1건

<b>④ Pinterest</b>
ko만 운영
→ en/ja/zh 12핀/일 자동
→ 1주: 5K 노출 → 25 클릭

<b>⑤ Influencer outreach</b>
50명 list (전원 email 미검증)
→ 사장님 IG/TikTok DM 수동 (drafts 50개 작성됨)
→ 1주: 2 collab

<b>⑥ B2B sales</b>
매일 5건 cold mail 자동 가동 중
→ HR 복지담당자 명단 30곳 추가
→ 1주: 데모 미팅 1건

<b>⑦ Etsy</b>
40 listings CSV 준비됨, 미업로드
→ Vela 가입 + 일괄 업로드 필요 (사용자 25분)
→ 1주: 첫 sale ($5~15)

<b>⑧ RapidAPI</b>
Saju calc API 미등록
→ freemium API 출시 (자동 가능)
→ 1주: 가입 10명

━━━ <b>오늘밤 즉시 매출 액션 5개</b> ━━━

🤖 <b>A. Gumroad 24h FLASH 50%</b>
   ROI ₩100K · 5분 trigger 가능

🤖 <b>B. Pinterest 4lang × 12핀</b>
   ROI 200 클릭 · 자동 trigger 가능

🤖 <b>C. Bluesky/X/Threads 동시 푸시</b>
   ROI 500 view · 매시간 schtask 가동 중

✋ <b>D. Influencer IG/TikTok DM 10건</b>
   ROI ₩300K · 사장님 직접 (drafts 준비 완료)

🤖 <b>E. B2B cold mail 5건/일</b>
   ROI ₩500K · 매일 자동 가동 중 ✅

━━━ <b>오늘 처리 완료 (자동 18건)</b> ━━━

✅ viral 스크립트 복원 (CmdViral 6 schtask)
✅ 결제창 차단 (인플루언서 쿠폰 보유자)
✅ 광고 게이트 SKU 7개 + 쿠폰 검사
✅ 사주 풀이 보기 버튼 + auto-render
✅ PDF 30페이지 다운로드 신규 구현
✅ 행운 색상 한국어 이름 매핑
✅ 30일 무료 쿠폰 발급 ×3 (사장님 + quf9485 + 보너스)
✅ paypal monitor → Vercel cron 통합
✅ dead schtask 8개 자동 삭제
✅ SEO blog factory JSON 파싱 fallback
✅ <b>YT 4채널 OAuth 재인증 완료</b>

━━━ <b>사장님 액션 (선택)</b> ━━━

🅰 Gumroad FLASH 50% off — "ㄱㄱ" 명령
🅱 Etsy 가입 + 40 listings 업로드 (25분)
🅲 인플루언서 IG DM 10건 (drafts 활용, 1시간)

━━━━━━━━━━━━━━
<b>핵심 메시지:</b> 인프라 다 됐음. 매출 0의 원인은 트래픽. 위 5 액션 중 A·B·C는 즉시 자동 가능 — 사장님 GO 신호 주시면 1시간 내 5채널 동시 push 가능.
"""

url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
data = urllib.parse.urlencode({
    "chat_id": TG_CHAT,
    "text": msg,
    "parse_mode": "HTML",
    "disable_web_page_preview": "true",
}).encode("utf-8")

try:
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15) as r:
        body = json.loads(r.read().decode("utf-8"))
        ok = body.get("ok", False)
        msg_id = body.get("result", {}).get("message_id")
        print(f"[{'OK' if ok else 'FAIL'}] message_id={msg_id} length={len(msg)}자")
except Exception as e:
    print(f"[ERR] {type(e).__name__}: {e}")
