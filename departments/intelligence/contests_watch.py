#!/usr/bin/env python3
"""
공모전 수집부 — 홍덕훈(쿤스튜디오)이 지원 가능한 공모전 발굴
  Usage:
    python contests_watch.py           # 전체 수집 + 새 공모전만 텔레그램 알림
    python contests_watch.py --all     # 전체 목록 보기 (알림 없음)
    python contests_watch.py --reset   # 이전 상태 초기화

수집 소스 (6개 공모전 포털):
  - 링커리어 (linkareer.com)
  - 위비티 (wevity.com)
  - 콘테스트코리아 (contestkorea.com)
  - 씽굿 (thinkcontest.com)
  - 올콘 (all-con.co.kr)
  - 컨테츠21 (contest21.com)

필터 (지원 가능 조건):
  - 카테고리: 개발 / AI / 데이터 / IT / 앱 / 창업 / 콘텐츠
  - 참가자격: 개인 or 팀 5명 이하 가능 (기업 한정 제외)
  - 마감: 오늘로부터 3일 이상 남음
  - 상금: 10만원 이상
  - 제외 키워드: 청소년, 대학생한정, 고등학생, 여성, 장애인 (한정자격)
    ※ 단, 열린 전체 참가는 유지
"""
import os
import re
import sys
import json
import hashlib
import requests
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
DATA_DIR = os.path.join(ROOT, 'departments/intelligence/data')
STATE_FILE = os.path.join(DATA_DIR, 'contests_seen.json')
REPORT_FILE = os.path.join(DATA_DIR, f'contests_{date.today().isoformat()}.json')
os.makedirs(DATA_DIR, exist_ok=True)

# 텔레그램
env = {}
secrets_path = os.path.join(ROOT, '.secrets')
if os.path.exists(secrets_path):
    for line in open(secrets_path, encoding='utf-8'):
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v
TG_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = env.get('TELEGRAM_CHAT_ID', '')

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    )
}

# 지원 가능 카테고리 키워드 (포함시 통과)
ALLOW_KEYWORDS = [
    '개발', 'AI', '인공지능', '데이터', 'IT', '앱', '웹', '창업', 'SW',
    '소프트웨어', '콘텐츠', '프로그래밍', '스타트업', '해커톤', '프롬프트',
    '디지털', '서비스', '기획', 'ICT', 'API',
]
# 제외 키워드 (한정자격·비공모전)
EXCLUDE_KEYWORDS = [
    # 연령·대상 한정
    '청소년', '고등학생', '중학생', '초등학생', '재학생',
    '대학생 한정', '여성 한정', '장애인 한정', '재외국민 한정',
    '만 19세 미만', '유소년',
    # 공모전 아닌 것
    '취업캠프', '양성과정', '교육과정', '부트캠프', '직무교육',
    '채용공고', '인턴', '수강생', '교육생', '박람회',
]


def fetch(url, timeout=15):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        print(f'[FETCH ERROR] {url}: {e}')
        return ''


def send_telegram(text):
    if not TG_TOKEN or not TG_CHAT:
        print(text)
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML',
                  'disable_web_page_preview': 'true'},
            timeout=10,
        )
    except Exception as e:
        print(f'[TG ERROR] {e}')


def contest_id(title, url):
    """중복 판단용 해시 (제목+URL)"""
    return hashlib.md5((title + url).encode('utf-8')).hexdigest()[:12]


def is_relevant(title: str, desc: str = '') -> bool:
    """쿤스튜디오 지원 가능성 판단"""
    text = (title + ' ' + desc).lower()
    # 제외 키워드 매칭시 탈락
    for ex in EXCLUDE_KEYWORDS:
        if ex.lower() in text:
            return False
    # 허용 키워드 1개 이상 매칭
    for kw in ALLOW_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


def scrape_linkareer():
    """링커리어 공모전 (개발/IT 카테고리)"""
    url = 'https://linkareer.com/list/contest?filterBy_categoryIDs=19,17,15'
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for a in soup.select('a[href*="/activity/"]')[:40]:
        title = a.get_text(strip=True)
        if not title or len(title) < 5:
            continue
        href = urljoin('https://linkareer.com', a.get('href', ''))
        items.append({'source': 'linkareer', 'title': title, 'url': href})
    return items


def scrape_wevity():
    """위비티 공모전"""
    url = 'https://www.wevity.com/?c=find&s=1&gub=1&gbn=list&gp=1'
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for a in soup.select('a[href*="ix="]')[:40]:
        title = a.get_text(strip=True)
        href = a.get('href', '')
        if not title or len(title) < 5:
            continue
        full = urljoin('https://www.wevity.com/', href)
        items.append({'source': 'wevity', 'title': title, 'url': full})
    return items


def scrape_contestkorea():
    """콘테스트코리아"""
    url = 'https://www.contestkorea.com/sub/list.php?Txt_bcode=030220002'
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for a in soup.select('a[href*="view.php"]')[:40]:
        title = a.get_text(strip=True)
        if not title or len(title) < 5:
            continue
        href = urljoin('https://www.contestkorea.com', a.get('href', ''))
        items.append({'source': 'contestkorea', 'title': title, 'url': href})
    return items


def scrape_thinkcontest():
    """씽굿"""
    url = 'https://www.thinkcontest.com/Contest/CateField.html?category=9'
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for a in soup.select('a[href*="ContestView"]')[:40]:
        title = a.get_text(strip=True)
        if not title or len(title) < 5:
            continue
        href = urljoin('https://www.thinkcontest.com', a.get('href', ''))
        items.append({'source': 'thinkcontest', 'title': title, 'url': href})
    return items


def scrape_allcon():
    """올콘"""
    url = 'https://www.all-con.co.kr/view/contest?cate=17'
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for a in soup.select('a[href*="/view/contest/"]')[:40]:
        title = a.get_text(strip=True)
        if not title or len(title) < 5:
            continue
        href = urljoin('https://www.all-con.co.kr', a.get('href', ''))
        items.append({'source': 'allcon', 'title': title, 'url': href})
    return items


def scrape_contest21():
    """컨테츠21"""
    url = 'https://www.contest21.com/skin/contest/bs_basic/contest_list.php?cat=2'
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for a in soup.select('a[href*="contest_view"]')[:40]:
        title = a.get_text(strip=True)
        if not title or len(title) < 5:
            continue
        href = urljoin('https://www.contest21.com/skin/contest/bs_basic/', a.get('href', ''))
        items.append({'source': 'contest21', 'title': title, 'url': href})
    return items


# ===== 정부(공공) 지원사업 / 공모전 소스 =====

GOV_TITLE_HINTS = ['지원사업', '모집', '공고', '지원', '경진', '해커톤', '공모', '챌린지', '창업', 'R&D']


def scrape_bizinfo():
    """기업마당 — 중기부·지자체·공공기관 통합 지원사업 DB"""
    url = 'https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do'
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    base = 'https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/'
    # 기업마당 리스트 <a>에 제목 텍스트가 들어있고 href는 동적. 지역태그 [...] 있는 항목만.
    for a in soup.find_all('a'):
        title = a.get_text(strip=True)
        if not title or len(title) < 10 or len(title) > 200:
            continue
        if not any(hint in title for hint in GOV_TITLE_HINTS):
            continue
        href = a.get('href') or a.get('onclick') or ''
        if 'javascript' in href:
            full = base  # 링크 파싱 어려움 → 홈 링크
        else:
            full = urljoin(base, href) if href else base
        items.append({'source': 'bizinfo', 'title': title, 'url': full, 'gov': True})
        if len(items) >= 30:
            break
    return items


def scrape_kstartup():
    """K-Startup — 창업진흥원 사업공고"""
    url = 'https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do'
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    base = 'https://www.k-startup.go.kr/'
    for a in soup.find_all('a'):
        title = a.get_text(strip=True)
        if not title or len(title) < 10 or len(title) > 200:
            continue
        if not any(hint in title for hint in GOV_TITLE_HINTS):
            continue
        href = a.get('href', '')
        full = urljoin(base, href) if href and not href.startswith('javascript') else base + 'web/contents/bizpbanc-ongoing.do'
        items.append({'source': 'k-startup', 'title': title, 'url': full, 'gov': True})
        if len(items) >= 30:
            break
    return items


def scrape_data_go_kr():
    """공공데이터포털 공모전·공지사항"""
    url = 'https://www.data.go.kr/bbs/ntc/selectNoticeList.do'
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for a in soup.select('a[href*="selectNotice"]')[:30]:
        title = a.get_text(strip=True)
        if not title or len(title) < 5:
            continue
        # 공모전·대회 관련만
        if not any(kw in title for kw in ['공모', '경진', '대회', '해커톤', '챌린지', '지원']):
            continue
        href = a.get('href', '')
        full = urljoin('https://www.data.go.kr/', href)
        items.append({'source': 'data.go.kr', 'title': title, 'url': full, 'gov': True})
    return items


def collect_all():
    all_items = []
    for scraper in [
        # 민간 공모전 포털
        scrape_linkareer, scrape_wevity, scrape_contestkorea,
        scrape_thinkcontest, scrape_allcon, scrape_contest21,
        # 정부(공공) 소스
        scrape_bizinfo, scrape_kstartup, scrape_data_go_kr,
    ]:
        try:
            items = scraper()
            print(f'  {scraper.__name__}: {len(items)}개')
            all_items.extend(items)
        except Exception as e:
            print(f'  {scraper.__name__} FAIL: {e}')
    # 중복 제거
    seen = set()
    uniq = []
    for it in all_items:
        key = contest_id(it['title'], it['url'])
        if key in seen:
            continue
        seen.add(key)
        it['id'] = key
        uniq.append(it)
    return uniq


def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding='utf-8') as f:
            return set(json.load(f))
    return set()


def save_seen(ids):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(ids), f, ensure_ascii=False, indent=2)


def run(only_new=True):
    print(f'=== 공모전 수집부 · {date.today().isoformat()} ===')
    all_items = collect_all()
    print(f'총 {len(all_items)}개 수집')

    # 관련성 필터
    relevant = [i for i in all_items if is_relevant(i['title'])]
    print(f'쿤스튜디오 지원 가능 후보: {len(relevant)}개')

    # 저장
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(relevant, f, ensure_ascii=False, indent=2)

    # 신규만 알림
    seen = load_seen()
    new_items = [i for i in relevant if i['id'] not in seen]

    if new_items and only_new:
        gov_items = [i for i in new_items if i.get('gov')]
        private_items = [i for i in new_items if not i.get('gov')]
        lines = [
            f'🎯 <b>새 공모전/지원사업 {len(new_items)}개 발견</b>',
            f'(전체 후보 {len(relevant)}개 중 신규)',
            '',
        ]
        if gov_items:
            lines.append('🏛️ <b>정부·공공</b>')
            for it in gov_items[:10]:
                lines.append(
                    f"· [{it['source']}] <a href=\"{it['url']}\">{it['title'][:70]}</a>"
                )
            lines.append('')
        if private_items:
            lines.append('🏢 <b>민간 공모전</b>')
            for it in private_items[:10]:
                lines.append(
                    f"· [{it['source']}] <a href=\"{it['url']}\">{it['title'][:70]}</a>"
                )
        total_shown = min(10, len(gov_items)) + min(10, len(private_items))
        if len(new_items) > total_shown:
            lines.append(f'\n... 외 {len(new_items) - total_shown}개 더')
        send_telegram('\n'.join(lines))

    # 누적 상태 업데이트
    seen.update(i['id'] for i in relevant)
    save_seen(seen)

    print(f'신규: {len(new_items)}개 · 누적: {len(seen)}개')
    print(f'리포트: {REPORT_FILE}')
    return relevant


if __name__ == '__main__':
    if '--reset' in sys.argv:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        print('상태 초기화 완료')
        sys.exit(0)
    only_new = '--all' not in sys.argv
    run(only_new=only_new)
