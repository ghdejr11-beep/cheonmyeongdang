"""daily_reminder — 매일 사용자가 해야 할 5분 manual 작업 텔레그램 알림.

체크 항목:
1. Quora 드래프트 (오늘 생성됐으면 → 복붙 게시 안내)
2. Pinterest 핀 (오늘 새 폴더 있으면 → 일괄 업로드 안내)
3. Influencer outreach (CSV에 row 있고 send 안 됐으면 → review 안내)

스케줄: 매일 13:00 (Quora 08:30 + Pinterest 12:30 이후) schtask.
"""
import os
import sys
import json
import datetime
import urllib.request
import urllib.parse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON_ROOT = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
LOG = ROOT / "logs" / f"reminder_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_secrets():
    env = {}
    p = CHEON_ROOT / ".secrets"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def telegram_send(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")[:200]
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}"


def main():
    env = load_secrets()
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat_id = env.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        sys.exit("[ERR] TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing")

    today = datetime.date.today().isoformat()
    sections = []

    # 1. Quora 드래프트
    quora_dir = CHEON_ROOT / "departments" / "quora_drafts" / "output"
    quora_today = quora_dir / f"quora_{today}.md"
    if quora_today.exists():
        # 첫 줄 = 헤더, 둘째 paragraph = question
        try:
            txt = quora_today.read_text(encoding="utf-8")
            q_match = txt.split("> ", 1)[1].split("\n", 1)[0] if "> " in txt else "(see file)"
        except Exception:
            q_match = "(see file)"
        sections.append(
            f"📝 <b>Quora 답변 게시</b> (5분)\n"
            f"• 질문: <i>{q_match[:120]}</i>\n"
            f"• 파일: <code>{quora_today.name}</code>\n"
            f"• 1) Quora.com 검색 → 위 질문 찾기\n"
            f"  2) Answer 클릭 → 파일 내용 복붙\n"
            f"  3) Submit"
        )

    # 2. Pinterest 핀
    pin_dir = CHEON_ROOT / "departments" / "pinterest_pins" / "output"
    if pin_dir.exists():
        # 오늘 추가된 폴더 (mtime 기반)
        today_dt = datetime.datetime.fromisoformat(f"{today}T00:00:00")
        recent = []
        for sub in pin_dir.iterdir():
            if sub.is_dir():
                pins = list(sub.glob("pin_*.jpg"))
                if pins and any(datetime.datetime.fromtimestamp(p.stat().st_mtime) >= today_dt for p in pins):
                    recent.append(sub)
        if recent:
            for r in recent[:1]:  # 1폴더만 알림 (중복 방지)
                desc_path = r / "description.txt"
                title_hint = r.name.replace("-", " ")[:60]
                sections.append(
                    f"📌 <b>Pinterest 핀 5장 업로드</b> (1분)\n"
                    f"• Topic: <i>{title_hint}</i>\n"
                    f"• 1) <a href=\"https://www.pinterest.com/pin-builder\">Pinterest pin-builder</a>\n"
                    f"  2) <code>{r}\\pin_*.jpg</code> 5장 drag-drop\n"
                    f"  3) <code>{desc_path.name}</code> 내용 description에 복붙\n"
                    f"  4) Publish 5번"
                )

    # 3. Affiliate outreach (선택, CSV에 row 있으면)
    outreach_csv = CHEON_ROOT / "departments" / "influencer_outreach" / "targets" / "manual.csv"
    if outreach_csv.exists():
        try:
            lines = outreach_csv.read_text(encoding="utf-8").splitlines()
            real_rows = [l for l in lines if l and not l.startswith("name,") and not l.startswith("EXAMPLE")]
            if real_rows:
                sections.append(
                    f"📨 <b>Affiliate outreach</b> (선택, 5분)\n"
                    f"• 등록된 타겟: {len(real_rows)}명\n"
                    f"• <code>python departments/influencer_outreach/generate_emails.py</code> 실행\n"
                    f"• drafts 폴더 검토 → send_emails.py 실행"
                )
        except Exception:
            pass

    if not sections:
        log("Nothing to remind today")
        return

    header = f"🔔 <b>오늘 5~10분 manual 작업</b> ({today})\n\n"
    body = "\n\n".join(sections)
    footer = "\n\n— 자동 알림 (daily_reminder, 매일 13:00)"

    msg = header + body + footer
    status, resp = telegram_send(token, chat_id, msg)
    log(f"[{status}] sent {len(sections)} reminders ({len(msg)} chars)")
    if status != 200:
        log(f"  resp: {resp}")


if __name__ == "__main__":
    main()
