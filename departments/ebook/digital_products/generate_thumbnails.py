#!/usr/bin/env python3
"""크티 상품 9개 썸네일 일괄 생성"""
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT = 'C:/Users/hdh02/Desktop/cheonmyeongdang/departments/ebook/digital_products/output'

PRODUCTS = [
    ('blog', '블로그', 'Blog', ['SEO 최적화', '글쓰기', '포스팅'], '#27ae60', '9,900'),
    ('business', '비즈니스', 'Business', ['사업계획서', '시장분석', '투자유치'], '#2980b9', '14,900'),
    ('copywriting', '카피라이팅', 'Copywriting', ['광고카피', '세일즈', '랜딩페이지'], '#c0392b', '12,900'),
    ('data', '데이터 분석', 'Data', ['엑셀', '시각화', '보고서'], '#f39c12', '14,900'),
    ('design', '디자인', 'Design', ['Midjourney', 'AI이미지', '로고'], '#9b59b6', '12,900'),
    ('email', '이메일 마케팅', 'Email', ['뉴스레터', '콜드메일', '자동화'], '#16a085', '9,900'),
    ('language', '외국어 학습', 'Language', ['영어', '일본어', 'AI과외'], '#d35400', '9,900'),
    ('sns', 'SNS 콘텐츠', 'SNS', ['인스타', '틱톡', '숏폼'], '#e91e90', '9,900'),
    ('youtube', '유튜브', 'YouTube', ['대본', '썸네일', 'SEO'], '#e74c3c', '9,900'),
]


def generate(cat, name_kr, name_en, features, color, price):
    img = Image.new('RGB', (800, 600), '#0f0f1a')
    draw = ImageDraw.Draw(img)

    # 배경 그라데이션
    for y in range(600):
        r = int(15 + y * 0.01)
        g = int(15 + y * 0.005)
        b = int(26 + y * 0.03)
        draw.line([(0,y),(800,y)], fill=(r,g,b))

    # 상단 컬러 바
    draw.rectangle([(0,0),(800,6)], fill=color)
    draw.rectangle([(0,594),(800,600)], fill='#c9a84c')

    # 폰트
    f_badge = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 16)
    f_title = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 64)
    f_sub = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 22)
    f_count = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 84)
    f_feature = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 20)
    f_price = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 38)

    # PROMPT PACK 배지
    draw.rounded_rectangle([(310, 40), (490, 72)], radius=16, fill=color)
    draw.text((400, 44), 'PROMPT PACK', fill='#ffffff', font=f_badge, anchor='mt')

    # 카테고리명 (영문)
    draw.text((400, 95), name_en.upper(), fill=color, font=f_sub, anchor='mt')

    # 메인 타이틀 (한글)
    draw.text((400, 140), name_kr, fill='#ffffff', font=f_title, anchor='mt')

    # 100개 강조
    draw.text((400, 235), '100', fill='#c9a84c', font=f_count, anchor='mt')
    draw.text((400, 335), '프롬프트', fill='#ffffff', font=f_sub, anchor='mt')

    # 기능 태그 3개
    tag_y = 390
    tag_widths = [draw.textlength(f, font=f_feature) + 32 for f in features]
    total_width = sum(tag_widths) + (len(features)-1) * 12
    start_x = (800 - total_width) / 2

    x = start_x
    for i, feat in enumerate(features):
        tw = tag_widths[i]
        draw.rounded_rectangle([(x, tag_y), (x + tw, tag_y + 38)], radius=19, fill=color)
        draw.text((x + tw/2, tag_y + 7), feat, fill='#ffffff', font=f_feature, anchor='mt')
        x += tw + 12

    # 가격
    draw.rounded_rectangle([(250, 470), (550, 525)], radius=27, fill='#c9a84c')
    draw.text((400, 478), f'{price}원', fill='#0f0f1a', font=f_price, anchor='mt')

    # 하단
    draw.text((400, 547), 'ChatGPT · Claude · Gemini 호환', fill='#888888', font=f_sub, anchor='mt')
    draw.text((400, 572), '쿤스튜디오', fill='#555555', font=f_badge, anchor='mt')

    out_path = f'{OUTPUT}/thumbnail_{cat}.png'
    img.save(out_path, quality=95)
    return out_path


if __name__ == '__main__':
    for cat, name_kr, name_en, features, color, price in PRODUCTS:
        path = generate(cat, name_kr, name_en, features, color, price)
        print(f'  {cat}: {path}')
    print(f'\n[OK] 9개 썸네일 생성 완료')
