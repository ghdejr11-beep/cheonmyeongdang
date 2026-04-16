#!/usr/bin/env python3
"""
프롬프트팩 카테고리별 PDF 상품 생성기
9개 카테고리 x 100개 + 올인원 900개 = 10개 상품
"""
import json
import os

# 카테고리별 상품 정보
PRODUCTS = {
    'blog': {
        'name_kr': '블로그 프롬프트 100선',
        'name_en': 'Blog Prompt Pack 100',
        'desc': 'SEO 최적화 블로그 글쓰기를 위한 AI 프롬프트 100개. 주제 선정부터 본문 작성, 제목/태그 최적화까지.',
        'price': 9900,
        'tags': ['블로그', '프롬프트', 'AI', 'ChatGPT', 'SEO', '글쓰기'],
    },
    'business': {
        'name_kr': '비즈니스 프롬프트 100선',
        'name_en': 'Business Prompt Pack 100',
        'desc': '사업계획서, 투자유치, 시장분석, 경쟁사분석 등 비즈니스 필수 AI 프롬프트 100개.',
        'price': 14900,
        'tags': ['비즈니스', '사업계획서', 'AI', '프롬프트', '창업', '스타트업'],
    },
    'copywriting': {
        'name_kr': '카피라이팅 프롬프트 100선',
        'name_en': 'Copywriting Prompt Pack 100',
        'desc': '매출을 올리는 광고 카피, 랜딩페이지, 세일즈 레터 작성용 AI 프롬프트 100개.',
        'price': 12900,
        'tags': ['카피라이팅', '광고', '프롬프트', 'AI', '마케팅', '세일즈'],
    },
    'data': {
        'name_kr': '데이터 분석 프롬프트 100선',
        'name_en': 'Data Analysis Prompt Pack 100',
        'desc': '엑셀/스프레드시트 자동화, 데이터 시각화, 보고서 작성용 AI 프롬프트 100개.',
        'price': 14900,
        'tags': ['데이터', '분석', '엑셀', 'AI', '프롬프트', '보고서'],
    },
    'design': {
        'name_kr': '디자인 프롬프트 100선',
        'name_en': 'Design Prompt Pack 100',
        'desc': 'Midjourney/DALL-E/Stable Diffusion용 이미지 생성 프롬프트 100개. 로고, 일러스트, 제품 사진.',
        'price': 12900,
        'tags': ['디자인', 'Midjourney', 'AI이미지', '프롬프트', '로고', '일러스트'],
    },
    'email': {
        'name_kr': '이메일 마케팅 프롬프트 100선',
        'name_en': 'Email Marketing Prompt Pack 100',
        'desc': '오픈율 높은 이메일 제목, 뉴스레터, 콜드메일, 팔로업 작성용 AI 프롬프트 100개.',
        'price': 9900,
        'tags': ['이메일', '마케팅', '뉴스레터', 'AI', '프롬프트', '콜드메일'],
    },
    'language': {
        'name_kr': '외국어 학습 프롬프트 100선',
        'name_en': 'Language Learning Prompt Pack 100',
        'desc': '영어/일본어/중국어 회화, 문법, 작문 연습용 AI 프롬프트 100개. AI 과외선생.',
        'price': 9900,
        'tags': ['영어', '외국어', '학습', 'AI', '프롬프트', '회화'],
    },
    'sns': {
        'name_kr': 'SNS 콘텐츠 프롬프트 100선',
        'name_en': 'SNS Content Prompt Pack 100',
        'desc': '인스타그램/틱톡/유튜브 숏폼 기획, 캡션, 해시태그 생성용 AI 프롬프트 100개.',
        'price': 9900,
        'tags': ['SNS', '인스타그램', '틱톡', 'AI', '프롬프트', '콘텐츠'],
    },
    'youtube': {
        'name_kr': '유튜브 프롬프트 100선',
        'name_en': 'YouTube Prompt Pack 100',
        'desc': '유튜브 기획, 대본, 썸네일 아이디어, SEO 최적화용 AI 프롬프트 100개.',
        'price': 9900,
        'tags': ['유튜브', '대본', '썸네일', 'AI', '프롬프트', 'YouTube'],
    },
}

BUNDLE = {
    'name_kr': 'AI 프롬프트 올인원 900선 (9개 카테고리)',
    'name_en': 'AI Prompt All-in-One 900 Pack',
    'desc': '블로그/비즈니스/카피라이팅/데이터/디자인/이메일/외국어/SNS/유튜브 — 9개 카테고리 900개 프롬프트 올인원 패키지. 개별 구매 대비 60% 할인.',
    'price': 39900,
    'original_price': 104400,
    'tags': ['AI', '프롬프트', '올인원', 'ChatGPT', '업무자동화', '마케팅'],
}


def generate_category_text(category, prompts):
    """카테고리별 텍스트 파일 생성 (PDF 대신 먼저 텍스트로)"""
    lines = []
    info = PRODUCTS[category]
    lines.append(f"{'='*60}")
    lines.append(f"  {info['name_kr']}")
    lines.append(f"  {info['name_en']}")
    lines.append(f"{'='*60}")
    lines.append(f"")
    lines.append(f"총 {len(prompts)}개의 프롬프트")
    lines.append(f"© 2026 쿤스튜디오 | 천명당 그룹")
    lines.append(f"")
    lines.append(f"{'─'*60}")
    lines.append(f"")

    for i, p in enumerate(prompts, 1):
        lines.append(f"[{i:03d}] {p.get('title', '제목 없음')}")
        lines.append(f"")
        lines.append(p.get('prompt', ''))
        lines.append(f"")
        lines.append(f"{'─'*60}")
        lines.append(f"")

    return '\n'.join(lines)


def generate_listing(category, info):
    """스마트스토어/크티 등록용 상품 설명"""
    lines = []
    lines.append(f"## {info['name_kr']}")
    lines.append(f"")
    lines.append(f"### 상품 설명")
    lines.append(info['desc'])
    lines.append(f"")
    lines.append(f"### 가격: {info['price']:,}원")
    lines.append(f"")
    lines.append(f"### 포함 내용")
    lines.append(f"- {category} 관련 AI 프롬프트 100개")
    lines.append(f"- PDF 파일 (인쇄 가능)")
    lines.append(f"- 복사-붙여넣기 가능한 텍스트")
    lines.append(f"- ChatGPT / Claude / Gemini 모두 호환")
    lines.append(f"")
    lines.append(f"### 이런 분께 추천")
    lines.append(f"- AI를 활용해 업무 효율을 높이고 싶은 직장인")
    lines.append(f"- 콘텐츠 제작에 AI를 도입하려는 크리에이터")
    lines.append(f"- 마케팅/영업에 AI를 활용하려는 사업자")
    lines.append(f"- AI 프롬프트 작성법을 배우고 싶은 초보자")
    lines.append(f"")
    lines.append(f"### 태그")
    lines.append(f"{', '.join(info['tags'])}")
    lines.append(f"")
    lines.append(f"### 판매자")
    lines.append(f"쿤스튜디오 | 사업자등록번호: 552-59-00848 | 대표: 홍덕훈")
    return '\n'.join(lines)


def main():
    # 프롬프트 데이터 로드
    with open('ebook_system/projects/prompt_pack_1000/output/prompts.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    prompts = data.get('prompts', data)

    # 카테고리별 분류
    categorized = {}
    for p in prompts:
        c = p.get('category', 'etc')
        if c not in categorized:
            categorized[c] = []
        categorized[c].append(p)

    # 출력 디렉토리
    out_dir = 'departments/ebook/digital_products/output'
    os.makedirs(out_dir, exist_ok=True)

    # 카테고리별 파일 생성
    for cat, items in sorted(categorized.items()):
        if cat not in PRODUCTS:
            continue

        info = PRODUCTS[cat]

        # 프롬프트 텍스트 파일
        text = generate_category_text(cat, items)
        with open(f'{out_dir}/prompt_{cat}_100.txt', 'w', encoding='utf-8') as f:
            f.write(text)

        # 상품 등록 정보
        listing = generate_listing(cat, info)
        with open(f'{out_dir}/listing_{cat}.md', 'w', encoding='utf-8') as f:
            f.write(listing)

        print(f"  ✅ {cat}: {len(items)}개 → prompt_{cat}_100.txt + listing_{cat}.md")

    # 올인원 번들
    all_text = []
    for cat in sorted(PRODUCTS.keys()):
        if cat in categorized:
            all_text.append(generate_category_text(cat, categorized[cat]))
    with open(f'{out_dir}/prompt_allinone_900.txt', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(all_text))

    # 번들 등록 정보
    bundle_listing = generate_listing('all', BUNDLE)
    with open(f'{out_dir}/listing_bundle.md', 'w', encoding='utf-8') as f:
        f.write(bundle_listing)

    print(f"  ✅ 올인원 번들: 900개 → prompt_allinone_900.txt")
    print(f"\n총 {len(PRODUCTS) + 1}개 상품 생성 완료!")
    print(f"\n가격표:")
    total = 0
    for cat, info in sorted(PRODUCTS.items()):
        print(f"  {info['name_kr']}: {info['price']:,}원")
        total += info['price']
    print(f"  {'─'*40}")
    print(f"  개별 합계: {total:,}원")
    print(f"  올인원 번들: {BUNDLE['price']:,}원 ({int((1-BUNDLE['price']/total)*100)}% 할인)")


if __name__ == '__main__':
    os.chdir(os.path.join(os.path.expanduser('~'), 'Desktop', 'cheonmyeongdang'))
    main()
