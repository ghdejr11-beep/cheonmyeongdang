#!/usr/bin/env python3
"""
쿤스튜디오 CEO 브리핑 v2
- 실측 수익 자동 수집 (Gumroad/KDP/쿠팡/Play Reporting)
- 부서별: 상황변화 / 수익 / 잘한점 / 문제점 / 해결방안
- 고객 불만 자동 모니터링 (앱 출시 후)
- 수익 아이템 추천 (Product Hunt + Google Trends)
"""
import sys, os, json, datetime, traceback
from pathlib import Path

# 인코딩
sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\ceo-briefing")
sys.path.insert(0, str(BASE))
# 수익집계부 (sales-collection) 도 import 가능하도록 path 추가
SALES_BASE = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\sales-collection")
sys.path.insert(0, str(SALES_BASE))

# 환경변수
def _load_secrets():
    env = {}
    for line in Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

ENV = _load_secrets()
TG_TOKEN = ENV.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = ENV.get("TELEGRAM_CHAT_ID", "")


def _safe(fn, default):
    """모듈이 실패해도 브리핑 전체가 망가지지 않게"""
    try:
        return fn()
    except Exception as e:
        return {**default, "error": str(e)[:200]}


# ─── 데이터 수집 ───
def collect_all():
    from integrations import gumroad, kdp, coupang, play_reporting
    from integrations import play_reviews, trends, product_hunt, dept_activity
    from integrations import vercel_analytics

    # AdMob (sales-collection 부서) — 옵션. import 실패해도 브리핑 정상.
    def _admob_safe():
        try:
            import admob_collector
            return admob_collector.daily_summary()
        except Exception as e:
            return {"status": "error", "error": str(e)[:200]}

    # YouTube 4채널 (sales-collection 부서) — 옵션.
    def _yt4ch_safe():
        try:
            import yt_dashboard
            return yt_dashboard.daily_summary()
        except Exception as e:
            return {"status": "error", "error": str(e)[:200]}

    return {
        "revenue": {
            "gumroad": _safe(gumroad.daily_summary, {"status": "error"}),
            "gumroad_products": _safe(gumroad.product_status, {}),
            "kdp": _safe(kdp.daily_summary, {"status": "error"}),
            "coupang": _safe(coupang.daily_summary, {"status": "error"}),
            "play": _safe(play_reporting.daily_summary, {"status": "error"}),
            "admob": _safe(_admob_safe, {"status": "error"}),
            "yt_4ch": _safe(_yt4ch_safe, {"status": "error"}),
            "vercel": _safe(vercel_analytics.daily_summary, {"status": "error"}),
        },
        "customer_feedback": {
            "play_reviews": _safe(play_reviews.daily_summary, {}),
        },
        "market_signals": {
            "trends": _safe(trends.daily_summary, {}),
            "product_hunt": _safe(product_hunt.daily_summary, {}),
        },
        "departments": _safe(dept_activity.all_departments_summary, {}),
    }


# ─── 메시지 빌더 ───
def _fmt_money(cents_or_usd, currency="KRW"):
    if currency == "USD":
        return f"${cents_or_usd/100:.2f}"
    return f"₩{int(cents_or_usd):,}"


def build_revenue_section(data):
    """💰 실측 수익 섹션"""
    msg = "💰 <b>실측 수익 (최근 24h)</b>\n"
    g = data.get("gumroad", {})
    gp = data.get("gumroad_products", {})

    if g.get("total_sales") is not None:
        msg += f"  • Gumroad: {g['total_sales']}건"
        if gp.get("warning"):
            msg += f"\n    {gp['warning']}\n"
        else:
            msg += "\n"
    else:
        msg += "  • Gumroad: 데이터 수집 실패\n"

    k = data.get("kdp", {})
    if k.get("status") == "ok":
        msg += f"  • KDP: {k['total_units']}권 / ${k['total_royalty_usd']:.2f}\n"
    else:
        msg += f"  • KDP: (수동 CSV 필요)\n"

    c = data.get("coupang", {})
    if c.get("status") == "active":
        msg += f"  • 쿠팡: 매출 자동 수집 중\n"
    else:
        msg += f"  • 쿠팡: 파트너스 공식 API 심사 대기 ⏳\n"

    p = data.get("play", {})
    if p.get("status") == "ready":
        msg += f"  • 플레이스토어 인앱결제: 연동 준비 완료\n"
    else:
        msg += f"  • 플레이스토어 인앱결제: 구글 서비스 계정 설정 필요\n"

    msg += "\n"
    return msg


def build_admob_section(admob):
    """📱 AdMob 광고 매출 (천명당 / HexDrop)"""
    msg = "📱 <b>AdMob 광고 매출</b>\n"
    if not isinstance(admob, dict):
        msg += "  (데이터 없음)\n\n"
        return msg

    status = admob.get("status")
    if status == "ok":
        y = admob.get("yesterday", {}) or {}
        total = y.get("total_usd", 0.0)
        msg += f"  • 어제({y.get('date', '-')}): ${total:.2f} "
        msg += f"(노출 {y.get('impressions', 0):,} / 클릭 {y.get('clicks', 0):,})\n"
        by_app = y.get("by_app", {}) or {}
        for app_name, info in by_app.items():
            e = info.get("earnings_usd", 0.0)
            msg += f"    └ {app_name}: ${e:.2f}\n"
        seven = admob.get("seven_day_avg_usd", 0.0)
        thirty = admob.get("thirty_day_total_usd", 0.0)
        msg += f"  • 7일 평균: ${seven:.2f}/일\n"
        msg += f"  • 30일 누적: ${thirty:.2f}\n"
    elif status == "no_publisher_id":
        msg += "  ⚙ AdMob Publisher ID 미설정 (.secrets 에 ADMOB_PUBLISHER_ID 추가 필요)\n"
    elif status == "no_token":
        msg += "  🔑 AdMob OAuth 토큰 없음 → admob_auth_setup.py 1회 실행 필요\n"
    elif status == "error":
        err = admob.get("error") or admob.get("message") or "알 수 없는 오류"
        msg += f"  ⚠ AdMob API 인증 필요: {str(err)[:80]}\n"
    else:
        msg += "  (수집 대기 중)\n"
    msg += "\n"
    return msg


def build_vercel_section(v):
    """🌐 Vercel 트래픽 / 배포 (3 프로젝트)"""
    msg = "🌐 <b>Vercel 트래픽 (어제)</b>\n"
    if not isinstance(v, dict):
        msg += "  (데이터 없음)\n\n"
        return msg

    status = v.get("status")
    totals = v.get("totals", {}) or {}
    src = v.get("analytics_source", "")

    if status == "no_token":
        msg += "  🔑 VERCEL_API_TOKEN 미설정 (.secrets 추가 필요)\n\n"
        return msg
    if status != "ok":
        err = v.get("error") or v.get("note") or "수집 실패"
        msg += f"  ⚠ {str(err)[:100]}\n\n"
        return msg

    pv = totals.get("pv")
    uv = totals.get("uv")
    deploys = totals.get("deployments_24h", 0)
    n = totals.get("projects_count", 0)

    if pv is None:
        # API 미지원 → placeholder
        msg += f"  • PV/UV: 미수집 (Vercel REST API 미지원)\n"
    else:
        msg += f"  • PV {pv:,} / UV {uv:,} ({n}개 프로젝트)\n"
    msg += f"  • 24h 배포: {deploys}건\n"

    for p in v.get("projects", []) or []:
        slug = p.get("slug", "?")
        ld = p.get("last_state") or "-"
        d24 = p.get("deployments_24h", 0)
        ppv = p.get("pv")
        line = f"    └ {slug}: 배포 {d24} / 마지막 {ld}"
        if ppv is not None:
            line += f" / PV {ppv:,}"
        if p.get("error"):
            line += f" ⚠ {str(p['error'])[:40]}"
        msg += line + "\n"

    if src == "placeholder":
        msg += "  ℹ️ PV/UV 자동수집은 Drain 또는 GA4 연동 필요\n"
    msg += "\n"
    return msg


def build_yt_4ch_section(yt):
    """📺 YouTube 5채널 (Whisper Atlas / Wealth Blueprint / Inner Archetypes / AI SideHustle / Sori Atlas)"""
    msg = "📺 <b>YouTube 5채널 (어제)</b>\n"
    if not isinstance(yt, dict):
        msg += "  (데이터 없음)\n\n"
        return msg

    status = yt.get("status")
    if status == "ok":
        t = yt.get("totals", {}) or {}
        msg += (
            f"  • 합계: 조회 +{t.get('yesterday_views_all', 0):,} / "
            f"구독 +{t.get('yesterday_subs_gained_all', 0):,} / "
            f"추정매출 ${t.get('revenue_estimate_usd_all', 0):.2f}\n"
        )
        msg += (
            f"  • 누적: 구독 {t.get('subscriber_count_all', 0):,} / "
            f"누적조회 {t.get('view_count_total_all', 0):,}\n"
        )
        for key, c in (yt.get("channels") or {}).items():
            if c.get("status") != "ok":
                msg += f"    └ {c.get('title', key)}: ({c.get('status')})\n"
                continue
            bv = c.get("best_video") or {}
            msg += (
                f"    └ <b>{c['title']}</b>: 조회 +{c.get('yesterday_views', 0):,} / "
                f"구독 +{c.get('yesterday_subs', 0):,} / ${c.get('revenue_usd', 0):.2f}"
            )
            src = c.get("revenue_source", "")
            if src.startswith("cpm_estimate"):
                msg += " 📊"  # 추정값 표시
            msg += "\n"
            if bv:
                msg += f"        best: {str(bv.get('title', ''))[:40]} ({bv.get('views', 0):,})\n"
    elif status == "auth_required":
        msg += f"  🔑 YouTube API 인증 필요: {str(yt.get('message', ''))[:80]}\n"
    elif status == "error":
        err = yt.get("error") or yt.get("message") or "알 수 없는 오류"
        msg += f"  ⚠ {str(err)[:80]}\n"
    else:
        msg += "  (수집 대기 중)\n"
    msg += "\n"
    return msg


def build_departments_section(depts):
    """👥 부서별 현황"""
    msg = "👥 <b>부서별 현황 (13개 전체)</b>\n"
    DEPT_META = {
        "ceo-briefing": "🏢 본사",
        "cheonmyeongdang": "🔮 천명당",
        "digital-products": "📦 디지털상품",
        "ebook": "📚 전자책",
        "game": "🎮 게임",
        "insurance-daboyeo": "🛡 보험다보여",
        "intelligence": "🔍 수집부",
        "korlens": "🗺 KORLENS",
        "media": "📺 미디어",
        "secretary": "💼 비서",
        "security": "🔒 보안",
        "tax": "💰 세금N혜택",
        "travelmap": "✈️ 여행지도",
    }
    for key, summ in depts.items():
        if isinstance(summ, dict) and summ.get("error"):
            continue
        icon_name = DEPT_META.get(key, key)
        has_activity = summ.get("mtime_changed_count", 0) > 0 or summ.get("commits_count", 0) > 0
        if not has_activity and not summ.get("active_problems"):
            continue  # 활동 없으면 스킵

        msg += f"\n<b>{icon_name}</b>\n"
        msg += f"  🔄 {summ.get('changes_summary', '-')[:150]}\n"
        if summ.get("positive_highlights"):
            msg += f"  ✅ {summ['positive_highlights'][0][:80]}\n"
        if summ.get("active_problems"):
            p = summ["active_problems"][0]
            msg += f"  ⚠ [{p['kw']}] {p['text'][:70]}\n"
    msg += "\n"
    return msg


def build_backup_section():
    """💾 백업 상태 — D:\\documents\\쿤스튜디오\\backup_log.json 마지막 항목 + 보관 갯수"""
    msg = "💾 <b>백업 상태</b>\n"
    log_path = Path(r"D:\documents\쿤스튜디오\backup_log.json")
    backup_dir = Path(r"D:\documents\쿤스튜디오\backups")

    if not log_path.exists():
        msg += "  ⚠ backup_log.json 없음 (한 번도 실행 안 됨)\n"
        msg += "  → python D:\\documents\\쿤스튜디오\\backup_daily.py\n\n"
        return msg

    try:
        log = json.loads(log_path.read_text(encoding="utf-8"))
    except Exception as e:
        msg += f"  ⚠ 로그 읽기 실패: {str(e)[:80]}\n\n"
        return msg

    if not log:
        msg += "  ⚠ 로그 비어있음\n\n"
        return msg

    last = log[-1]
    status = last.get("status", "unknown")
    date = last.get("date", "?")

    # 어제 백업 성공/실패 — date 가 어제(또는 오늘)인지 체크
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    last_date = None
    try:
        last_date = datetime.date.fromisoformat(date)
    except Exception:
        pass

    if status == "ok":
        size_mb = last.get("encrypted_bytes", 0) / 1e6
        files = last.get("files_total", 0)
        msg += f"  ✅ 마지막 백업: {date} ({size_mb:.1f}MB, {files:,}개 파일)\n"
        if last_date and last_date < yesterday:
            stale = (today - last_date).days
            msg += f"  🚨 <b>BACKUP STALE</b>: 마지막 백업이 {stale}일 전\n"
    else:
        msg += f"  🚨 <b>BACKUP FAILED</b> ({date})\n"
        err = last.get("error", "")
        if err:
            msg += f"     {err[:120]}\n"

    # 보관 갯수
    if backup_dir.exists():
        cnt = sum(
            1 for f in backup_dir.iterdir()
            if f.name.startswith("kunstudio_") and f.name.endswith(".tar.gz.enc")
        )
        total_mb = sum(
            f.stat().st_size for f in backup_dir.iterdir()
            if f.name.startswith("kunstudio_") and f.name.endswith(".tar.gz.enc")
        ) / 1e6
        msg += f"  📦 30일 보관: {cnt}개 ({total_mb:.0f}MB total)\n"
        if cnt == 0:
            msg += "  🚨 보관 백업 0개 — 즉시 점검\n"
    else:
        msg += "  🚨 backups/ 폴더 없음\n"

    msg += "\n"
    return msg


def build_feedback_section(fb):
    """🚨 고객 불만"""
    msg = "🚨 <b>고객 불만</b>\n"
    pr = fb.get("play_reviews", {})
    if pr.get("warnings"):
        for w in pr["warnings"]:
            msg += f"  {w}\n"
    our = pr.get("our_apps", {})
    total_negative = 0
    for name, info in our.items():
        if info.get("status") == "live":
            neg = info.get("negative_reviews_24h", 0)
            total_negative += neg
            if neg > 0:
                msg += f"  📱 {name} ⭐1~2 리뷰 {neg}건\n"
                for r in info.get("top_negatives", [])[:2]:
                    msg += f"    \"{r['text'][:60]}\"\n"
    comp = pr.get("competitors", {})
    if comp:
        msg += "\n<b>경쟁사 불만 (시장 기회)</b>\n"
        for name, info in list(comp.items())[:3]:
            c_count = info.get("complaints_24h", 0)
            msg += f"  • {name}: 불만 {c_count}건\n"
    if not our and not comp:
        msg += "  (앱 출시 후 자동 수집 시작)\n"
    msg += "\n"
    return msg


def build_market_section(ms):
    """💎 수익 아이템 추천"""
    msg = "💎 <b>수익 아이템 추천</b>\n"
    t = ms.get("trends", {})
    rising = t.get("rising_items", []) if isinstance(t, dict) else []
    DIRECTION_KO = {"breakout": "급상승", "rising": "상승 중", "up": "상승", "down": "하락"}
    if rising:
        msg += "📈 <b>구글 트렌드 상승 키워드</b>\n"
        for r in rising[:3]:
            direction = DIRECTION_KO.get(r.get('direction', ''), r.get('direction', ''))
            msg += f"  • {r['keyword']}: {direction} (+{r['change_pct']}%)\n"
    rq = t.get("related_rising_queries", []) if isinstance(t, dict) else []
    if rq:
        msg += f"  연관 검색어: " + ", ".join([q["query"] for q in rq[:3]]) + "\n"
    ph = ms.get("product_hunt", {})
    hm = ph.get("high_match_for_kun", []) if isinstance(ph, dict) else []
    if hm:
        msg += "\n🔥 <b>프로덕트헌트 쿤스튜디오 매칭 TOP</b>\n"
        for item in hm[:3]:
            msg += f"  • [{item['kun_score']}점] {item['title'][:50]}\n"
    msg += "\n"
    return msg


def build_priority_section():
    """🎯 오늘의 우선순위 — priority_tasks.json 에서 동적 로드.
    완료된 항목 자동 제외. 파일 없으면 빈 섹션."""
    PRIORITY_FILE = BASE / "priority_tasks.json"
    msg = "🎯 <b>오늘의 우선순위</b>\n"
    if not PRIORITY_FILE.exists():
        msg += "  (priority_tasks.json 없음)\n\n"
        return msg
    try:
        tasks = json.loads(PRIORITY_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        msg += f"  (로드 실패: {e})\n\n"
        return msg
    # done=true 면 스킵, due_date 지난 것도 스킵 (단 done 아닌 상태)
    today = datetime.date.today()
    pending = []
    for t in tasks:
        if t.get("done"):
            continue
        due = t.get("due_date")
        if due:
            try:
                d = datetime.date.fromisoformat(due)
                days = (d - today).days
                if days < 0:
                    continue  # 마감 지남, 표시 안 함
                t["_d_label"] = f"D-{days}"
            except Exception:
                t["_d_label"] = ""
        pending.append(t)
    # 우선순위 순 (1=🔴 / 2=🟡 / 3=🟢 / 기본 🟢)
    ICONS = {1: "🔴", 2: "🟡", 3: "🟢"}
    pending.sort(key=lambda x: x.get("priority", 3))
    for t in pending[:3]:
        icon = ICONS.get(t.get("priority", 3), "🟢")
        title = t.get("title", "?")
        dl = t.get("_d_label", "")
        msg += f"  {icon} {title}" + (f" ({dl})" if dl else "") + "\n"
    if not pending:
        msg += "  (미완료 우선순위 없음)\n"
    msg += "\n"
    return msg


def build_message(hour=None):
    if hour is None:
        hour = datetime.datetime.now().hour
    now = datetime.datetime.now()
    theme_emoji = {9: "🌅", 12: "🍱", 15: "☕", 18: "🌆", 21: "🌙", 0: "🌌"}.get(hour, "🤖")
    theme_label = {9: "아침", 12: "점심", 15: "오후", 18: "저녁", 21: "야간", 0: "자정"}.get(hour, "")

    data = collect_all()

    msg = f"{theme_emoji} <b>CEO {theme_label} 브리핑 v2</b>\n"
    msg += f"<i>{now.strftime('%Y-%m-%d %H:%M')}</i>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"

    # 💰 통합 매출 배너 (5채널 합산 — sales-collection/unified_revenue)
    try:
        import unified_revenue
        msg += unified_revenue.build_unified_revenue_section()
    except Exception as e:
        msg += f"💰 <b>통합 매출</b>\n  (집계기 오류: {str(e)[:80]})\n\n"

    msg += build_priority_section()
    msg += build_revenue_section(data["revenue"])
    msg += build_admob_section(data["revenue"].get("admob", {}))
    msg += build_yt_4ch_section(data["revenue"].get("yt_4ch", {}))
    msg += build_vercel_section(data["revenue"].get("vercel", {}))
    # 📊 GA4 트래픽 — 09:00 아침 브리핑에만 (다른 시간대는 스킵)
    if hour == 9:
        try:
            from integrations import ga4
            ga4_data = _safe(ga4.daily_summary, {})
            msg += ga4.build_ga4_section(ga4_data)
        except Exception as e:
            msg += f"📊 <b>GA4 트래픽</b>\n  (모듈 오류: {str(e)[:80]})\n\n"
    # 🛡 가동 상태 (보안부서 uptime monitor)
    try:
        sys.path.insert(0, str(Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\security")))
        from uptime_monitor import build_uptime_section
        msg += build_uptime_section(window_hours=24)
    except Exception as e:
        msg += f"🛡 <b>가동 상태</b>\n  (모니터 오류: {str(e)[:80]})\n\n"
    msg += build_departments_section(data["departments"])
    # 🤖 자동 처리: 부서별 active_problems 중 자동 해결 가능 항목 즉시 실행 후 요약
    try:
        from briefing_autofix import run_autofix, format_autofix_section
        autofix_result = run_autofix(data["departments"])
        msg += format_autofix_section(autofix_result)
    except Exception as e:
        msg += f"🤖 <b>자동 처리</b>\n  (엔진 오류: {str(e)[:80]})\n\n"
    msg += build_feedback_section(data["customer_feedback"])
    msg += build_market_section(data["market_signals"])
    # 💾 백업 상태 (자산 보호 — 실패 시 큰 경고)
    try:
        msg += build_backup_section()
    except Exception as e:
        msg += f"💾 <b>백업 상태</b>\n  (섹션 오류: {str(e)[:80]})\n\n"

    msg += "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🏢 쿤스튜디오 | 자동 브리핑 v2"
    return msg


def send_telegram(text):
    import requests
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    # 텔레그램 메시지 4096자 제한 → 자르기
    if len(text) > 4000:
        text = text[:3900] + "\n\n... (길이 제한으로 잘림)"
    resp = requests.post(url, json={
        "chat_id": TG_CHAT,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }, timeout=15)
    return resp.json()


if __name__ == "__main__":
    hour = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "preview":
            print(build_message())
            sys.exit(0)
        try:
            hour = int(sys.argv[1])
        except:
            pass
    msg = build_message(hour)
    result = send_telegram(msg)
    if result.get("ok"):
        print(f"✅ 브리핑 v2 전송 완료 ({datetime.datetime.now().strftime('%H:%M')})")
    else:
        print(f"❌ 실패: {result}")
        print("--- 메시지 미리보기 ---")
        print(msg[:500])
