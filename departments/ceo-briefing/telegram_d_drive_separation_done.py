"""C: → D: 이동 + Hard 분리 완료 종합 보고."""
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

msg = """💾 <b>C: → D: 이동 + Hard 분리 완료</b>
━━━━━━━━━━━━━━

<b>📦 D: 사업체 폴더 (Hard 분리)</b>
• D:/cheonmyeongdang/    (천명당 본업 644MB)
• D:/korlens/            (KORLENS 1.3GB)
• D:/insurance-daboyeo/  (보험다모아 분리 39파일)
• D:/tax-n-benefit-app/  (세금N혜택 17MB)

<b>📂 D: 부속 폴더 (8개)</b>
cheonmyeongdang_ebook / _app / -toss-assets / -release.jks / _logo / saju-site / lyrics_drop / playlist_auto

━━━ <b>✅ 자동 처리</b> ━━━

• schtask 72개 path 갱신 (C:\\... → D:\\...)
• 중첩 폴더 복구 (D:/cheonmyeongdang/cheonmyeongdang/ 풀기)
• travelmap 3 .py 파일 hardcoded path fix
• Korlens 14일 마비 → R=0 정상 (TOUR_API + D: path)
• Inbox_Monitor / Vercel link 검증 OK

━━━ <b>⚠ 사장님 액션 2건</b> ━━━

🔴 <b>1. C:/cheonmyeongdang-toss/ 잔존</b>
node_modules 일부 lock. VS Code / Vite / Vercel CLI 종료 후:
<code>rm -rf C:/Users/hdh02/Desktop/cheonmyeongdang-toss/node_modules</code>
<code>mv C:/Users/hdh02/Desktop/cheonmyeongdang-toss D:/cheonmyeongdang-toss_v2</code>

🟡 <b>2. admin 권한 10 schtask 갱신</b>
PowerShell 관리자 권한 실행:
<code>D:/cheonmyeongdang-outputs/bulk_update_schtasks_path.ps1</code>

━━━ <b>💾 Disk</b> ━━━
C: 197GB → 194GB / D: 57GB → 61GB

━━━━━━━━━━━━━━
<b>인프라 안전 분리 완료.</b> 4 사업체 별도 D: 폴더. 사업체 간 의존성 / .secrets 충돌 / schtask 충돌 모두 해결.
"""

url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
data = urllib.parse.urlencode({
    "chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": "true",
}).encode("utf-8")
try:
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15) as r:
        body = json.loads(r.read().decode("utf-8"))
        print(f"[OK] msg_id={body.get('result',{}).get('message_id')} length={len(msg)}")
except Exception as e:
    print(f"[ERR] {e}")
