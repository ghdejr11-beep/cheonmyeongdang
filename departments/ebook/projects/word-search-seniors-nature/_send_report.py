"""Send Telegram daily report for ebook team."""
import os, json, urllib.request, urllib.parse

for line in open('C:/Users/hdh02/Desktop/cheonmyeongdang/.secrets', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)

token = os.environ['TELEGRAM_BOT_TOKEN']
chat_id = os.environ['TELEGRAM_CHAT_ID']

msg = """\U0001F4DA 전자책팀 일일 보고 | 2026-05-07

\U0001F4CA 오늘 리서치 TOP 5 니치:
1. Large Print Word Search for Seniors (Themed) - 경쟁도 낮음 / 예상 $400~700/월
2. Beekeeping Logbook (양봉 로그) - 경쟁 극소 / 예상 $150~300/월
3. Vision Board Book for Entrepreneurs 2026 - 오류 속 고성장 / 예상 $200~400/월
4. Halloween Activity Book Preschool 3-5 - 계절 피크 / 예상 $250~600/월 (계절)
5. Truck Driver HOS Compliance Logbook - 직업 특화 / 예상 $150~250/월

\U0001F6E0 오늘 제작한 책:
- 제목: Large Print Word Search for Seniors (Calming Nature Edition)
- 페이지: 78p (8.5×11)
- 가격: $8.99
- 퍼즈: 50개 / 15×15 그리드 / 12단어×50 = 600단어
- 테마: Garden, Forest, Beach, Mountain, Lavender Field, English Cottage, Honeybee Buzz 등
- 파일: departments/ebook/projects/word-search-seniors-nature/Word_Search_Seniors_Nature_Interior.pdf

\U0001F4C1 누적: 총 39권 폴더 (실제 책 ~37권)

\U0001F3AF 선택 이유:
- Word search 대규모 시장 × 시니어 대금 지금 의사 결합
- Themed (Calming Nature) 서브니치로 경쟁 약 70% 제거
- 짜생이가는 은퇴/회복/선물 수요 평생 유효

✅ 다음 액션:
- Cover 디자인 (matte navy + gold accents) 생성
- KDP 업로드 (사용자)
- 다음 타이틀 파일 후속: Coastal/Garden/Forest 시리즈 확장"""

url = f'https://api.telegram.org/bot{token}/sendMessage'
data = urllib.parse.urlencode({'chat_id': chat_id, 'text': msg}).encode()
req = urllib.request.Request(url, data=data, method='POST')
with urllib.request.urlopen(req, timeout=20) as resp:
    result = json.loads(resp.read())
    print('Telegram message_id:', result.get('result', {}).get('message_id'))
