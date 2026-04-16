#!/usr/bin/env python3
"""
편집부 AI — KDP 거절 사유 분석 + 자동 수정안 생성

비서부(secretary.py)가 edit_queue.json에 거절 메일을 쌓아두면,
편집부가 각 사유를 분석해서 해결 방법을 제시합니다.

사유별 자동 처리:
- ISBN low-content 이슈 → KDP 콘솔에서 체크박스 변경 안내
- 표지 책등 여백 → 표지 재생성 (자동)
- 템플릿 텍스트 남음 → 표지 재생성 (자동)
- 본문 가독성 → 폰트 크기 체크 + 재생성
- 저자명 불일치 → 표지에서 저자명 수정
- 신원인증 → 사용자 직접 (위임 불가)
"""

import os
import sys
import json
import re
import datetime
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from secretary import translate_subject
EDIT_QUEUE_FILE = os.path.join(SCRIPT_DIR, 'edit_queue.json')
EDIT_LOG_FILE = os.path.join(SCRIPT_DIR, 'edit_log.json')

# 텔레그램
TG_BOT_TOKEN = "8650272218:AAHIYmOVfqzMzr-hcOqWsfW6mftByoEd_SA"
TG_CHAT_ID = "8556067663"
TG_BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

# 책 제목 → 프로젝트 폴더 매핑
BOOK_FOLDER_MAP = {
    'gen z stress': 'genz-stress',
    'dot marker': 'dot-marker-kids',
    'spot the difference': 'spot-difference-seniors',
    'ai side hustle': 'ai-side-hustle-en',
    'sleep improvement': 'sleep-planner',
    'blood pressure': 'blood-pressure-log',
    'blood sugar': 'blood-sugar-tracker',
    'introvert': 'introvert-confidence',
    'meal prep': 'meal-prep-planner',
    'mental reset': 'mental-reset-journal',
    'password logbook': 'password-logbook',
    'adhd planner': 'adhd-planner',
    'budget planner': 'budget-planner-couples',
    'cottagecore': 'cottagecore-coloring',
    'bold easy coloring': 'bold-easy-coloring-animals',
    'math workbook': 'math-workbook-grade1',
    'airbnb': 'airbnb-guestbook',
}


def find_book_folder(subject):
    """제목에서 프로젝트 폴더 찾기"""
    subject_lower = subject.lower()
    for keyword, folder in BOOK_FOLDER_MAP.items():
        if keyword in subject_lower:
            return folder
    return None


def analyze_rejection(item):
    """거절 사유 자동 분석"""
    reason_text = (item.get('reason', '') + ' ' + item.get('book_title', '') + ' ' + item.get('subject', '')).lower()

    issues = []
    auto_fixable = []
    manual_required = []

    # 1. Low-content ISBN 이슈
    if 'low-content' in reason_text or 'low content' in reason_text or 'print isbn' in reason_text:
        issues.append({
            'type': 'metadata_lowcontent',
            'desc': 'Low-content 체크박스 + ISBN 옵션 업데이트 필요',
            'how_to': 'KDP Bookshelf → Edit Paperback/Hardcover Content 탭 → "Low-content book" 체크 → ISBN 옵션 업데이트 → 재제출',
            'auto': False,
            'urgency': 'easy',
        })
        manual_required.append(issues[-1])

    # 2. 표지 책등 여백 부족
    if 'spine' in reason_text and 'edge' in reason_text:
        issues.append({
            'type': 'cover_spine_margin',
            'desc': '책등 텍스트가 상하 가장자리에 너무 가까움',
            'how_to': '표지 책등의 상하 여백을 최소 0.375인치(9.6mm) 확보하도록 재생성',
            'auto': True,
            'urgency': 'auto_regen',
        })
        auto_fixable.append(issues[-1])

    # 3. 템플릿 텍스트/가이드 남음
    if 'template text' in reason_text or 'guides from your cover' in reason_text:
        issues.append({
            'type': 'cover_template_leftover',
            'desc': '표지에 KDP 템플릿 텍스트/가이드 선이 남아있음',
            'how_to': '표지 재생성 시 템플릿 가이드 완전 제거',
            'auto': True,
            'urgency': 'auto_regen',
        })
        auto_fixable.append(issues[-1])

    # 4. 본문 가독성 (illegible text)
    if 'illegible text' in reason_text or 'blurry' in reason_text or 'pixelated' in reason_text:
        issues.append({
            'type': 'interior_illegible',
            'desc': '본문 텍스트가 너무 작거나 흐릿함',
            'how_to': '최소 7pt 이상, 이미지 300dpi 이상으로 본문 재생성',
            'auto': True,
            'urgency': 'auto_regen',
        })
        auto_fixable.append(issues[-1])

    # 5. 저자명 불일치
    if 'author' in reason_text and ('match' in reason_text or 'contributor name' in reason_text):
        issues.append({
            'type': 'author_name_mismatch',
            'desc': '표지의 저자명이 메타데이터와 불일치',
            'how_to': '표지의 저자명을 설정 단계에서 입력한 이름과 동일하게 수정',
            'auto': True,
            'urgency': 'auto_regen',
        })
        auto_fixable.append(issues[-1])

    # 6. 신원인증 (수동)
    if 'verify your identity' in reason_text or 'government-issued id' in reason_text:
        issues.append({
            'type': 'identity_verification',
            'desc': 'KDP 계정 신원인증 필요 (정부 발급 신분증)',
            'how_to': 'KDP 로그인 → 신분증 제출 (모바일 권장). 마감: 2026-04-28',
            'auto': False,
            'urgency': 'user_action',
        })
        manual_required.append(issues[-1])

    if not issues:
        issues.append({
            'type': 'unknown',
            'desc': '자동 분석 불가 — 원문 검토 필요',
            'how_to': 'KDP 이메일 원문 직접 확인',
            'auto': False,
            'urgency': 'manual_review',
        })

    return {
        'issues': issues,
        'auto_fixable': auto_fixable,
        'manual_required': manual_required,
    }


def draft_action_plan(item, analysis):
    """수정 계획 초안 작성"""
    subject = item.get('subject', '')
    # 책 제목 추출 (Attention needed: Please review your title, XXX 형식)
    title_match = re.search(r'review your title,\s*([^(]+)', subject)
    book_title = title_match.group(1).strip() if title_match else subject

    folder = find_book_folder(subject)

    plan = {
        'book_title': book_title,
        'project_folder': folder,
        'issues': analysis['issues'],
        'actions': [],
    }

    # 각 이슈별 실행 계획
    for issue in analysis['issues']:
        if issue['type'] == 'metadata_lowcontent':
            plan['actions'].append({
                'step': 'KDP 콘솔에서 Low-content 체크박스 설정',
                'executor': '사용자 (5분)',
                'link': 'https://kdp.amazon.com/bookshelf',
            })
        elif issue['type'] == 'cover_spine_margin':
            if folder:
                plan['actions'].append({
                    'step': f'표지 재생성 (책등 여백 0.375인치 확보)',
                    'executor': f'편집부 자동 실행: python departments/ebook/projects/{folder}/generate.py',
                    'link': None,
                })
            else:
                plan['actions'].append({
                    'step': '표지 재생성 (프로젝트 폴더 불명)',
                    'executor': '사용자 수동',
                    'link': None,
                })
        elif issue['type'] == 'cover_template_leftover':
            plan['actions'].append({
                'step': '표지 재생성 (템플릿 가이드 완전 제거)',
                'executor': f'편집부 자동: {folder}/generate.py' if folder else '수동',
                'link': None,
            })
        elif issue['type'] == 'interior_illegible':
            plan['actions'].append({
                'step': '본문 재생성 (폰트 7pt+, 이미지 300dpi+)',
                'executor': f'편집부 자동: {folder}/generate.py' if folder else '수동',
                'link': None,
            })
        elif issue['type'] == 'author_name_mismatch':
            plan['actions'].append({
                'step': '표지 저자명 확인 및 재생성',
                'executor': '편집부 자동 (generate.py의 AUTHOR_NAME 확인)',
                'link': None,
            })
        elif issue['type'] == 'identity_verification':
            plan['actions'].append({
                'step': '⚠️ 신원인증 - 사용자만 가능',
                'executor': '사용자 직접 (마감 4/28)',
                'link': 'https://kdp.amazon.com',
            })
        else:
            plan['actions'].append({
                'step': '원문 직접 검토 필요',
                'executor': '사용자',
                'link': None,
            })

    return plan


def format_plan_message(plan, item):
    """텔레그램 메시지 포맷 (한글)"""
    msg = f"📝 <b>편집부 수정안</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"<b>📖 책:</b> {plan['book_title']}\n"
    if plan['project_folder']:
        msg += f"<b>📁 폴더:</b> {plan['project_folder']}\n"
    msg += f"<b>📧 원문:</b> {translate_subject(item.get('subject',''))[:70]}\n"
    msg += "\n"

    msg += "<b>🚨 KDP 거절 사유:</b>\n"
    for i, issue in enumerate(plan['issues'], 1):
        auto_icon = '🤖' if issue['auto'] else '👤'
        msg += f"  {auto_icon} {i}. {issue['desc']}\n"
        msg += f"      → {issue['how_to']}\n"
    msg += "\n"

    msg += "<b>✅ 실행 계획:</b>\n"
    for i, action in enumerate(plan['actions'], 1):
        msg += f"  {i}. {action['step']}\n"
        msg += f"     <i>({action['executor']})</i>\n"
        if action.get('link'):
            msg += f"     🔗 {action['link']}\n"

    msg += f"\n━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🏢 편집부 | 승인하려면 실행\n"
    msg += f"<code>python editor.py approve {item['email_id']}</code>"

    return msg


def send_telegram(text):
    url = f"{TG_BASE_URL}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json()


def process_queue(dry_run=False):
    """대기열의 모든 거절 처리"""
    if not os.path.exists(EDIT_QUEUE_FILE):
        print("대기열 없음")
        return

    with open(EDIT_QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    pending = [item for item in queue if item.get('status') == 'pending_edit']
    print(f"[편집부] 대기 중인 거절 메일: {len(pending)}건\n")

    plans = []
    for item in pending:
        print(f"─ {item['subject'][:80]}")
        analysis = analyze_rejection(item)
        plan = draft_action_plan(item, analysis)

        auto_count = len([i for i in analysis['issues'] if i['auto']])
        manual_count = len([i for i in analysis['issues'] if not i['auto']])
        print(f"  이슈 {len(analysis['issues'])}개 (자동 {auto_count}, 수동 {manual_count})")

        plans.append((item, plan))

        # 상태 업데이트
        item['status'] = 'drafted'
        item['plan'] = plan

    # 저장
    with open(EDIT_QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    # 텔레그램 전송
    if not dry_run and plans:
        # 종합 요약
        summary = f"📝 <b>편집부 — KDP 거절 수정안 {len(plans)}건</b>\n"
        summary += f"<i>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</i>\n"
        summary += "━━━━━━━━━━━━━━━━━━━━━\n\n"

        for i, (item, plan) in enumerate(plans, 1):
            auto = len([x for x in plan['issues'] if x['auto']])
            manual = len([x for x in plan['issues'] if not x['auto']])
            title_short = plan['book_title'][:50].strip()
            summary += f"<b>{i}. {title_short}</b>\n"
            for issue in plan['issues']:
                icon = '🤖' if issue['auto'] else '👤'
                summary += f"  {icon} {issue['desc'][:60]}\n"
            summary += "\n"

        summary += "━━━━━━━━━━━━━━━━━━━━━\n"
        summary += "🤖 = 편집부 자동 수정 가능\n"
        summary += "👤 = 사용자 직접 처리 필요"

        result = send_telegram(summary)
        print(f"\n텔레그램 요약: {'✅' if result.get('ok') else '❌'}")

        # 개별 상세도 각각 보내기
        for item, plan in plans:
            detail = format_plan_message(plan, item)
            send_telegram(detail)

    return plans


if __name__ == '__main__':
    dry_run = len(sys.argv) > 1 and sys.argv[1] == 'preview'
    process_queue(dry_run=dry_run)
