"""천명당 출시 홍보 — 7개 채널 동시 발송 (2026-04-28)."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'departments', 'media', 'src'))

from multi_poster import send_all_direct, post_instagram, _load_secrets

CONTENT = """🔮 천명당 오픈 — 운세·사주·궁합 한곳에

오늘운세 / 관상 / 손금 / 꿈해몽 — 전부 무료

✨ 월 9,900원 회원권 한 가지로
• 매일 아침 8시 카톡 운세 발송
• 사주정밀 + 궁합 풀이 무제한
• 광고 없음

👉 cheonmyeongdang.vercel.app

#운세 #사주 #궁합 #꿈해몽 #관상"""

# IG는 로컬 파일 경로만 OK (vercel URL은 fetch 차단됨, host_image()가 자동 catbox 업로드)
IMAGE_URL = os.path.join(os.path.dirname(__file__), '..', 'og.jpg')

env = _load_secrets()

# 1) Postiz로 텔레그램 발송 시도
postiz_res = None
try:
    from postiz_poster import send_all_channels
    postiz_res = send_all_channels(CONTENT)
    print('[postiz]', postiz_res)
except Exception as e:
    print(f'[postiz] error: {type(e).__name__}: {e}')
    postiz_res = {'error': str(e)}

# 2) 직접 API 6채널 (이미지 포함 → IG도 발송 가능)
direct_res = send_all_direct(CONTENT, image_url=IMAGE_URL, skip_coupang=False)
print('[direct]', direct_res)

# 3) 결과 종합
all_res = {'postiz': postiz_res}
all_res.update(direct_res)

print('\n=== FINAL RESULTS ===')
print(json.dumps(all_res, ensure_ascii=False, indent=2))

ok = sum(1 for k, v in all_res.items() if k != 'postiz' and v is True)
print(f'\nDirect API channels OK: {ok}/6')
