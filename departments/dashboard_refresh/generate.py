"""dashboard_refresh — 쿤스튜디오 전체 대시보드 HTML 자동 최신화.

데이터 소스:
- schtasks 목록
- departments/seo_blog_factory/published.json (SEO 블로그)
- departments/hashnode_crosspost/hashnode_published.json
- departments/quora_drafts/queue.json
- departments/pinterest_pins/queue.json
- departments/tiktok_shorts_en/queue.json
- departments/telegram_watch/state/processed.json
- departments/sales-collection/data/*.json (매출)
- departments/ceo-briefing/output/revenue_*.md (오늘 보고서)

출력: C:\\Users\\hdh02\\Desktop\\kunstudio_dashboard.html (브라우저로 열어보면 됨)
스케줄: 매시 정각 (KunStudio_Dashboard_Refresh_Hourly)
"""
import os, sys, json, datetime, subprocess, re
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CHEON = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang")
OUT = Path(r"C:\Users\hdh02\Desktop\kunstudio_dashboard.html")
LOG = ROOT / "logs" / f"refresh_{datetime.date.today()}.log"
LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def safe_load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def get_schtasks():
    """KunStudio_* + Cheonmyeongdang_* schtask 카운트."""
    try:
        out = subprocess.run(
            ["schtasks", "/Query", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=15, encoding="cp949", errors="ignore"
        ).stdout
        ks = sum(1 for l in out.splitlines() if "KunStudio_" in l or "Cheonmyeongdang_" in l)
        return ks
    except Exception:
        return "?"


def count_blog_files():
    en = CHEON / "blog" / "en"
    if not en.exists():
        return 0
    return len(list(en.glob("*.html")))


def render_html():
    today = datetime.date.today().isoformat()
    now = datetime.datetime.now().strftime("%H:%M")

    # 카운터들
    seo_pub = safe_load(CHEON / "departments" / "seo_blog_factory" / "published.json") or {}
    seo_count = len(seo_pub.get("published", []))

    hashnode = safe_load(CHEON / "departments" / "hashnode_crosspost" / "hashnode_published.json") or {}
    hashnode_count = len(hashnode.get("posted", []))

    quora_q = safe_load(CHEON / "departments" / "quora_drafts" / "queue.json") or {}
    quora_drafted = len(quora_q.get("drafted", []))
    quora_posted = len(quora_q.get("posted", []))

    pin_q = safe_load(CHEON / "departments" / "pinterest_pins" / "queue.json") or {}
    pin_count = len(pin_q.get("made", []))

    tiktok_q = safe_load(CHEON / "departments" / "tiktok_shorts_en" / "queue.json") or {}
    tiktok_count = len(tiktok_q.get("made", []))

    triple_q = safe_load(CHEON / "departments" / "tiktok_shorts_en" / "triple_done.json") or {}
    triple_count = len(triple_q.get("posted", []))

    blog_files = count_blog_files()
    schtask_n = get_schtasks()

    telegram_state = safe_load(CHEON / "departments" / "telegram_watch" / "state" / "processed.json") or {}
    fixed_issues = sum(1 for v in telegram_state.values() if isinstance(v, dict) and v.get("resolved"))

    # 시즌 SKU 카운트
    skus = 0
    pcfg = (CHEON / "api" / "payment-config.js").read_text(encoding="utf-8", errors="ignore") if (CHEON / "api" / "payment-config.js").exists() else ""
    skus = pcfg.count("type:")

    # 가장 최근 매출 보고서
    rev_dir = CHEON / "departments" / "ceo-briefing" / "output"
    rev_md = sorted(rev_dir.glob("revenue_*.md"), reverse=True)[:1] if rev_dir.exists() else []
    rev_summary = "0원 (5/5)"
    if rev_md:
        try:
            rev_text = rev_md[0].read_text(encoding="utf-8")
            m = re.search(r"총 판매:\s*(\d+)건", rev_text)
            rev_summary = f"Gumroad {m.group(1)}건" if m else "리포트 발행"
        except Exception:
            pass

    html = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<title>쿤스튜디오 대시보드 · 자동 갱신</title>
<meta http-equiv="refresh" content="3600">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Noto Sans KR',sans-serif;background:#0a0e1a;color:#e8eaed;padding:24px;line-height:1.55}}
header{{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:18px;border-bottom:1px solid #1f2937;padding-bottom:14px;flex-wrap:wrap;gap:12px}}
h1{{font-size:1.5rem;background:linear-gradient(90deg,#60a5fa,#a78bfa,#f472b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.meta{{color:#9ca3af;font-size:0.84rem}}
.live-dot{{display:inline-block;width:9px;height:9px;background:#34d399;border-radius:50%;margin-right:6px;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}
.kpi{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin:18px 0}}
.kpi-card{{background:linear-gradient(135deg,rgba(30,30,60,0.85),rgba(15,15,30,0.85));border:1px solid #1f2937;border-radius:12px;padding:16px;text-align:center}}
.kpi-num{{font-size:2rem;font-weight:700;color:#60a5fa;line-height:1}}
.kpi-label{{font-size:0.7rem;color:#9ca3af;letter-spacing:0.04em;text-transform:uppercase;margin-top:6px}}
.section{{margin:22px 0}}
h2{{font-size:1.05rem;color:#e8c97a;margin-bottom:10px;padding-left:8px;border-left:3px solid #c9a84c}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}}
.card{{background:#111827;border:1px solid #1f2937;border-radius:10px;padding:12px}}
.card h3{{font-size:0.92rem;margin-bottom:6px;color:#e8eaed}}
.card .row{{display:flex;justify-content:space-between;font-size:0.78rem;margin:3px 0;color:#d1d5db}}
.card .row b{{color:#a78bfa}}
.badge{{display:inline-block;padding:2px 8px;border-radius:99px;font-size:0.68rem;font-weight:600}}
.b-live{{background:rgba(52,211,153,0.15);color:#34d399}}
.b-test{{background:rgba(96,165,250,0.18);color:#60a5fa}}
.b-pend{{background:rgba(248,113,113,0.15);color:#f87171}}
.b-draft{{background:rgba(251,191,36,0.15);color:#fbbf24}}
table{{width:100%;border-collapse:collapse;font-size:0.8rem}}
th,td{{padding:6px 9px;border-bottom:1px solid #1f2937;text-align:left}}
th{{color:#9ca3af;font-weight:500;font-size:0.7rem;text-transform:uppercase}}
.note{{margin-top:14px;padding:10px 14px;background:rgba(96,165,250,0.06);border-left:3px solid #60a5fa;border-radius:6px;font-size:0.82rem;color:#d1d5db}}
footer{{margin-top:26px;padding-top:14px;border-top:1px solid #1f2937;color:#6b7280;font-size:0.76rem;text-align:center}}
</style></head>
<body>

<header>
  <div>
    <h1><span class="live-dot"></span>쿤스튜디오 대시보드 · 자동 갱신</h1>
    <div class="meta">홍덕훈 · 552-59-00848 · 글로벌 100일 10억 모드 · 광고비 0</div>
  </div>
  <div class="meta">{today} {now} 갱신 · 매시 정각 자동</div>
</header>

<!-- 실시간 KPI -->
<div class="kpi">
  <div class="kpi-card"><div class="kpi-num">{schtask_n}</div><div class="kpi-label">활성 schtask</div></div>
  <div class="kpi-card"><div class="kpi-num">{seo_count}</div><div class="kpi-label">영문 SEO 블로그</div></div>
  <div class="kpi-card"><div class="kpi-num">{blog_files}</div><div class="kpi-label">/blog/en/ 파일</div></div>
  <div class="kpi-card"><div class="kpi-num">{hashnode_count}</div><div class="kpi-label">Hashnode cross-post</div></div>
  <div class="kpi-card"><div class="kpi-num">{quora_drafted}</div><div class="kpi-label">Quora 드래프트</div></div>
  <div class="kpi-card"><div class="kpi-num">{pin_count}</div><div class="kpi-label">Pinterest 핀 큐</div></div>
  <div class="kpi-card"><div class="kpi-num">{tiktok_count}</div><div class="kpi-label">TikTok 쇼츠</div></div>
  <div class="kpi-card"><div class="kpi-num">{triple_count}</div><div class="kpi-label">Triple cross-post</div></div>
  <div class="kpi-card"><div class="kpi-num">{fixed_issues}</div><div class="kpi-label">자동 fix (24h)</div></div>
  <div class="kpi-card"><div class="kpi-num">{skus}</div><div class="kpi-label">천명당 SKU</div></div>
</div>

<div class="section">
<h2>📊 오늘 매출 ({today})</h2>
<div class="card"><div class="row"><span>요약</span><b>{rev_summary}</b></div></div>
</div>

<div class="section">
<h2>🌍 글로벌 무료 트래픽 자동 부서</h2>
<table>
<tr><th>부서</th><th>schtask 시각</th><th>출력</th></tr>
<tr><td>seo_blog_factory</td><td>06/09/13/17/21시</td><td>영문 long-tail blog × 5/일</td></tr>
<tr><td>quora_drafts</td><td>08:30</td><td>Q&A markdown × 1/일</td></tr>
<tr><td>tiktok_shorts_en</td><td>10:00</td><td>30s 쇼츠 mp4 × 1/일</td></tr>
<tr><td>pinterest_pins</td><td>12:30</td><td>5 핀 1000×1500 + desc</td></tr>
<tr><td>hashnode_crosspost</td><td>11:30</td><td>SEO → Hashnode 게시</td></tr>
<tr><td>tiktok triple_upload</td><td>13:30</td><td>TikTok+IG+Threads+FB+YT Shorts</td></tr>
<tr><td>daily_reminder</td><td>13:00</td><td>텔레그램 manual 작업 알림</td></tr>
<tr><td>telegram_watch</td><td>매시 정각</td><td>로그 스캔 + 자동 fix</td></tr>
<tr><td>K-Wisdom YouTube</td><td>07:00</td><td>영문 YT 영상 × 1/일</td></tr>
<tr><td>KORLENS SNS</td><td>월/수/금</td><td>5 채널 × 주 3회</td></tr>
<tr><td>dashboard_refresh</td><td>매시 정각 (이 페이지)</td><td>본 대시보드 자동 갱신</td></tr>
</table>
</div>

<div class="section">
<h2>💳 결제 인프라</h2>
<table>
<tr><th>채널</th><th>상태</th></tr>
<tr><td>PayPal Smart Buttons (글로벌)</td><td><span class="badge b-live">라이브</span></td></tr>
<tr><td>Ko-fi Tip / Gumroad / Notion</td><td><span class="badge b-live">라이브</span></td></tr>
<tr><td>천명당 SKU {skus}종 (1년 결제 추가됨)</td><td><span class="badge b-live">라이브</span></td></tr>
<tr><td>NaverPay V2 채널</td><td><span class="badge b-pend">심사 (5/9 예상)</span></td></tr>
<tr><td>KakaoPay 라이브 키</td><td><span class="badge b-pend">PG 통과 후</span></td></tr>
<tr><td>PortOne KCN</td><td><span class="badge b-pend">심사</span></td></tr>
</table>
</div>

<div class="section">
<h2>📱 Play Console 8앱</h2>
<table>
<tr><th>앱</th><th>상태</th><th>비고</th></tr>
<tr><td>천명당</td><td><span class="badge b-test">비공개 테스트</span></td><td>D-11 → 5/15 프로덕션 신청</td></tr>
<tr><td>HexDrop</td><td><span class="badge b-test">테스터 0</span></td><td>BETAFLOW 진행</td></tr>
<tr><td>Bottle Sort Korea</td><td><span class="badge b-test">정상</span></td><td>BETAFLOW</td></tr>
<tr><td>Bubble/Gem/Stack/Tetris/세금N</td><td><span class="badge b-draft">Draft × 5</span></td><td>AAB 미업로드</td></tr>
</table>
</div>

<div class="note">🤖 모든 schtask는 사용자 자는 동안에도 가동. 매시 정각 telegram_watch가 패턴 자동 감지 → 자동 fix. 매일 13:00 daily_reminder가 manual 5분 작업 알림.</div>

<footer>
🏢 쿤스튜디오 대시보드 · auto-refresh 매시 정각 · {today} {now} · brower meta refresh 1h
</footer>
</body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    log(f"refreshed → {OUT} ({OUT.stat().st_size//1024}KB)")


if __name__ == "__main__":
    render_html()
