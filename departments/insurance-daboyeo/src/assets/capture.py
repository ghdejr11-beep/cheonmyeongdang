#!/usr/bin/env python3
"""보험다보여 앱 모바일 스크린샷 캡처 (고객용 + 설계사용)"""
import os
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://ghdejr11-beep.github.io/cheonmyeongdang/departments/insurance-daboyeo/src'

VIEWPORT = {'width': 390, 'height': 844}

# 고객용 스크린샷 (index.html)
CUSTOMER_SHOTS = [
    {'name': 'c_overview',   'js': "go('overview', document.querySelectorAll('.nav-item')[0]);",        'label': '내 보험 현황'},
    {'name': 'c_coverage',   'js': "go('coverage', document.querySelectorAll('.nav-item')[1]);",        'label': '보장 분석'},
    {'name': 'c_recommend',  'js': "go('recommend', document.querySelectorAll('.nav-item')[4]);",       'label': '맞춤 추천'},
    {'name': 'c_healthcheck','js': "go('healthcheck', document.querySelectorAll('.nav-item')[7]);",     'label': '건강 분석'},
    {'name': 'c_claim',      'js': "go('claim', document.querySelectorAll('.nav-item')[8]);",           'label': '보험금 청구'},
]

# 설계사용 스크린샷 (agent.html)
AGENT_SHOTS = [
    {'name': 'a_dashboard',  'js': None,                                                                 'label': '대시보드'},
    {'name': 'a_customers',  'js': "document.querySelectorAll('.nav-item').forEach(b => { if (b.innerText.includes('고객')) b.click(); });",   'label': '고객 관리'},
    {'name': 'a_profile',    'js': "document.querySelectorAll('.nav-item').forEach(b => { if (b.innerText.includes('프로필')) b.click(); });", 'label': '프로필 설정'},
    {'name': 'a_link',       'js': "document.querySelectorAll('.nav-item').forEach(b => { if (b.innerText.includes('링크')) b.click(); });",   'label': '고객 링크'},
    {'name': 'a_analysis',   'js': "document.querySelectorAll('.nav-item').forEach(b => { if (b.innerText.includes('분석') || b.innerText.includes('건강')) b.click(); });", 'label': '분석 대시보드'},
]


def capture(page, shots, url):
    page.goto(url, wait_until='networkidle')
    page.wait_for_timeout(1500)

    for s in shots:
        if s['js']:
            page.evaluate(s['js'])
            page.wait_for_timeout(800)
        path = os.path.join(OUT, f'{s["name"]}.jpg')
        page.screenshot(path=path, type='jpeg', quality=85, full_page=False)
        size_kb = os.path.getsize(path) / 1024
        print(f'[OK] {s["label"]:<12} → {s["name"]}.jpg ({size_kb:.1f} KB)')


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
        )
        page = context.new_page()

        print('\n=== 고객용 앱 (B2C) ===')
        capture(page, CUSTOMER_SHOTS, f'{BASE}/index.html')

        print('\n=== 설계사용 앱 (B2B) ===')
        capture(page, AGENT_SHOTS, f'{BASE}/agent.html')

        browser.close()


if __name__ == '__main__':
    main()
