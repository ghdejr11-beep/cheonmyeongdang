#!/usr/bin/env python3
"""
tax 부서 - 지원사업 공고 모니터링 (쿤스튜디오 맞춤)

데이터 소스:
- bizinfo.go.kr (기업마당) — 공개 리스트 HTML 스크래핑
- smes.go.kr (중기부) — 공개 리스트 HTML 스크래핑

필터 (쿤스튜디오 프로필):
- 대상: 소상공인 또는 1인기업
- 지역: 전국 또는 경상북도/경주/비수도권
- 제외: 수도권 한정, 만 39세 이하 청년 한정, 법인 한정
- 만 41세 (1985-02-03), 개인사업자, 2026-04-01 개업, 경주

출력:
- output/leads_YYYY-MM-DD.md — 마감일 임박순
- output/seen_ids.json — 중복 방지
- logs/run_YYYY-MM-DD.log

알림: 신규 공고 발견 시 telegram (ceo-briefing 의 .secrets 재사용)
"""
import os, re, json, sys, datetime, urllib.request, urllib.parse, html
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\tax")
OUT_DIR = BASE / "output"
LOG_DIR = BASE / "logs"
OUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

SEEN_PATH = OUT_DIR / "seen_ids.json"
TODAY = datetime.date.today().isoformat()

SECRETS = Path(r"C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TaxLeadWatcher/1.0"

EXCLUDE_KW = [
    "청년", "만 39세", "만39세", "만 34세", "만34세",
    "법인사업자만", "법인만", "수도권 한정",
]

INCLUDE_HINTS = [
    "소상공인", "1인기업", "1인 창업", "개인사업자",
    "경상북도", "경북", "경주", "비수도권", "전국",
    "디지털", "로컬", "관광", "IT", "소프트웨어",
]


def log(msg):
    line = f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    with open(LOG_DIR / f"run_{TODAY}.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_seen():
    if SEEN_PATH.exists():
        try:
            return set(json.loads(SEEN_PATH.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_seen(ids):
    SEEN_PATH.write_text(json.dumps(sorted(list(ids)), ensure_ascii=False, indent=2), encoding="utf-8")


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
        for enc in ("utf-8", "euc-kr", "cp949"):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")


def scrape_bizinfo(keyword, pages=2):
    """기업마당 (bizinfo.go.kr) 공고 리스트 스크래핑."""
    leads = []
    for p in range(1, pages + 1):
        qs = urllib.parse.urlencode({
            "cpage": p,
            "rows": 15,
            "searchKrwd": keyword,
        })
        url = f"https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do?{qs}"
        try:
            html_str = fetch(url)
        except Exception as e:
            log(f"bizinfo fetch fail p{p} kw={keyword}: {e}")
            continue

        # 각 <tr> 공고 블록 파싱: href + title + 신청기간(YYYY-MM-DD ~ YYYY-MM-DD)
        tr_pattern = re.compile(
            r'pblancId=(PBLN_\d+)[^>]*title="([^"]*?)"'
            r'.*?(\d{4}-\d{2}-\d{2}\s*~\s*\d{4}-\d{2}-\d{2})',
            re.DOTALL,
        )
        for m in tr_pattern.finditer(html_str):
            pid, title_raw, period = m.groups()
            title = html.unescape(title_raw).strip()
            title = re.sub(r"\s*페이지\s*이동\s*$", "", title)
            # 접수 종료일만 추출
            m2 = re.search(r"~\s*(\d{4}-\d{2}-\d{2})", period)
            deadline = m2.group(1) if m2 else period.strip()
            leads.append({
                "id": pid,
                "title": title,
                "deadline": deadline,
                "url": f"https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?pblancId={pid}",
                "source": "bizinfo",
                "keyword": keyword,
            })
    return leads


def scrape_smes(pages=2):
    """중기부 (smes.go.kr) 사업공고 리스트 스크래핑."""
    leads = []
    for p in range(1, pages + 1):
        url = f"https://www.smes.go.kr/main/bizApply?curPage={p}"
        try:
            html_str = fetch(url)
        except Exception as e:
            log(f"smes fetch fail p{p}: {e}")
            continue
        for m in re.finditer(
            r'<a[^>]*href="([^"]*bizApplyView[^"]*)"[^>]*>(.*?)</a>.*?(\d{4}\.\d{2}\.\d{2}\s*~\s*\d{4}\.\d{2}\.\d{2})',
            html_str, re.DOTALL,
        ):
            href, title_raw, period = m.groups()
            title = html.unescape(re.sub(r"<[^>]+>", "", title_raw)).strip()
            if not href.startswith("http"):
                href = "https://www.smes.go.kr" + href
            pid_match = re.search(r"(\d{5,})", href)
            pid = f"smes_{pid_match.group(1) if pid_match else title[:20]}"
            leads.append({
                "id": pid,
                "title": title,
                "deadline": period.split("~")[1].strip(),
                "url": href,
                "source": "smes",
                "keyword": "-",
            })
    return leads


def pass_filter(lead):
    """쿤스튜디오 프로필 맞춤 필터."""
    t = lead["title"]
    for ex in EXCLUDE_KW:
        if ex in t:
            return False, f"제외 키워드: {ex}"
    for hint in INCLUDE_HINTS:
        if hint in t:
            return True, f"포함 키워드: {hint}"
    return False, "관련 키워드 없음"


def deadline_key(d):
    m = re.search(r"(\d{4})[-./년\s]+(\d{1,2})[-./월\s]+(\d{1,2})", d or "")
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return "9999-99-99"


def load_secrets():
    if not SECRETS.exists():
        return {}
    env = {}
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def send_telegram(msg):
    env = load_secrets()
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat = env.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        log("telegram skip (no token)")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat,
        "text": msg[:4000],
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    try:
        urllib.request.urlopen(url, data=data, timeout=10)
        return True
    except Exception as e:
        log(f"telegram fail: {e}")
        return False


def main():
    log(f"=== tax lead_watcher start {TODAY} ===")
    seen = load_seen()
    all_leads = []

    for kw in ["소상공인", "경상북도", "1인 창업", "디지털"]:
        try:
            all_leads.extend(scrape_bizinfo(kw))
        except Exception as e:
            log(f"scrape_bizinfo({kw}) ERR: {e}")
    try:
        all_leads.extend(scrape_smes())
    except Exception as e:
        log(f"scrape_smes ERR: {e}")

    # dedup by id
    by_id = {}
    for l in all_leads:
        by_id[l["id"]] = l
    leads = list(by_id.values())

    # filter
    passed = []
    for l in leads:
        ok, reason = pass_filter(l)
        l["filter_reason"] = reason
        if ok:
            passed.append(l)

    passed.sort(key=lambda x: deadline_key(x.get("deadline", "")))

    # new vs seen
    new = [l for l in passed if l["id"] not in seen]

    # write markdown
    md_path = OUT_DIR / f"leads_{TODAY}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 지원사업 공고 모니터링 — {TODAY}\n\n")
        f.write(f"- 총 수집: {len(leads)}건 / 필터 통과: {len(passed)}건 / 신규: {len(new)}건\n\n")
        if new:
            f.write("## 🆕 신규 공고\n\n")
            for l in new:
                f.write(f"- [{l['title']}]({l['url']}) · 마감 {l['deadline']} · `{l['source']}` · `{l['filter_reason']}`\n")
            f.write("\n")
        f.write("## 전체 (마감 임박순)\n\n")
        for l in passed:
            f.write(f"- [{l['title']}]({l['url']}) · 마감 {l['deadline']} · `{l['source']}`\n")
    log(f"wrote {md_path}")

    # save seen
    save_seen(seen | {l["id"] for l in leads})

    # telegram 알림 (신규만)
    if new:
        msg = f"<b>🆕 tax 신규 공고 {len(new)}건</b> ({TODAY})\n\n"
        for l in new[:5]:
            msg += f"• <a href='{l['url']}'>{l['title']}</a>\n  마감 {l['deadline']}\n"
        if len(new) > 5:
            msg += f"\n외 {len(new)-5}건 — output/leads_{TODAY}.md 참조"
        send_telegram(msg)

    log(f"=== done: {len(passed)} passed, {len(new)} new ===")


if __name__ == "__main__":
    main()
