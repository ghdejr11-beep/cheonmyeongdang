#!/usr/bin/env python3
"""세금N혜택 앱 모바일 스크린샷 5장 캡처 (실제 화면)"""
import os
import subprocess
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'playwright'])
    subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])
    from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
URL_BASE = 'https://ghdejr11-beep.github.io/cheonmyeongdang/departments/tax/src/app.html'

VIEWPORT = {'width': 390, 'height': 844}
DEVICE_PIXEL_RATIO = 2

SHOTS = [
    {'name': 'calc',     'script': None,                                                             'label': '계산기'},
    {'name': 'coaching', 'script': "document.querySelectorAll('.tab-btn')[1].click();",              'label': '절세'},
    {'name': 'subsidy',  'script': "document.querySelectorAll('.tab-btn')[2].click();",              'label': '지원금'},
    {'name': 'chat',     'script': "document.querySelectorAll('.tab-btn')[3].click();",              'label': 'AI상담'},
    {'name': 'auth',     'script': "if(typeof connectHomeTax==='function') connectHomeTax();",      'label': '간편인증'},
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=DEVICE_PIXEL_RATIO,
            is_mobile=True,
            has_touch=True,
        )
        page = context.new_page()
        page.goto(URL_BASE, wait_until='networkidle')
        page.wait_for_timeout(1500)

        for shot in SHOTS:
            if shot['script']:
                page.evaluate(shot['script'])
                page.wait_for_timeout(800)
            path = os.path.join(OUT, f'app_{shot["name"]}.jpg')
            page.screenshot(path=path, type='jpeg', quality=85, full_page=False)
            size_kb = os.path.getsize(path) / 1024
            print(f'[OK] {shot["label"]:<10} → {path} ({size_kb:.1f} KB)')

        browser.close()


if __name__ == '__main__':
    main()
