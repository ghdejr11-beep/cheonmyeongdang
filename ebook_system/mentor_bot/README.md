# 🤖 AI 멘토봇 — 설치 & 배포 가이드

PREMIUM 구매자 전용 AI 챗봇. 책 50개 챕터 전체를 학습한 Claude 기반 멘토.

## 어떻게 작동하나

```
1. 고객이 Gumroad 에서 PREMIUM 구매
   → Gumroad 가 고유 라이선스 키 자동 발급 + 이메일 발송
2. 고객이 이 봇 URL 접속 → 라이선스 키 입력
3. 서버가 Gumroad API 로 키 검증 → 세션 발급
4. 고객이 질문 → Claude + 책 내용 → 답변
5. (사용자=책 저자가 할 일: 0%)
```

## 비용

| 항목 | 비용 |
|---|---|
| Render.com 호스팅 | **무료** (free plan, 750시간/월) |
| Claude Haiku 4.5 | 구매자 1명당 평균 월 **$0.50~2** (프롬프트 캐싱 적용) |
| Gumroad API | **무료** |
| **총계** | 고객 1명 PREMIUM (29.9만원) → 평생 $20~50 마진 (**97% 이상**) |

## 파일 구조

```
mentor_bot/
├── server.py           ← FastAPI 서버 (메인)
├── static/
│   └── index.html      ← 채팅 UI
├── prepare_book.py     ← output/book.md → mentor_bot/book.md 복사
├── book.md             ← 책 전체 내용 (prepare_book.py 실행 후 생성)
├── requirements.txt
├── render.yaml         ← Render.com 자동 배포 설정
├── .env.example
└── README.md
```

---

## 🚀 배포 — 5단계 (30분)

### 1️⃣ Gumroad 에서 라이선스 키 활성화 (1분)

1. Gumroad 대시보드 → **PREMIUM 상품** 수정
2. 하단 **"License key"** 섹션 → **Generate license keys** 체크 ON
3. 저장

이제 PREMIUM 구매자마다 고유 라이선스 키가 자동 생성됩니다. 고객은 구매 확인 이메일에서 키를 볼 수 있어요.

### 2️⃣ PREMIUM 상품 ID 복사 (30초)

1. Gumroad 대시보드 → **Account settings** → **Advanced**
2. **Enable Gumroad API** 체크
3. PREMIUM 상품 페이지로 가서 URL 확인. 예: `https://gumroad.com/products/abc123`
4. 상품 **Edit** 페이지 URL 에서 `product_id` 확인 (또는 API 로 `/v2/products` 호출)
5. 이 ID 를 메모장에 저장 (다음 단계에서 사용)

### 3️⃣ 책 내용 복사 + 커밋 (2분)

```powershell
cd C:\Users\쿤\Desktop\cheonmyeongdang\ebook_system
python mentor_bot\prepare_book.py
cd ..
git add ebook_system/mentor_bot/book.md
git commit -m "add book content for mentor bot"
git push
```

### 4️⃣ Render.com 배포 (5분)

1. 👉 https://render.com 가입 (GitHub 연동 추천)
2. 대시보드 → **New +** → **Blueprint**
3. **Connect a repository** → `cheonmyeongdang` 저장소 선택
4. **Blueprint file** 을 자동 인식 (`ebook_system/mentor_bot/render.yaml`)
5. **Apply** 클릭

Render 가 자동으로 빌드 시작. 3~5분 소요.

### 5️⃣ 환경변수 2개 입력 (2분)

배포가 완료되면 Render 대시보드에서:

1. **ai-mentor-bot** 서비스 클릭
2. 좌측 메뉴 **Environment** 클릭
3. 다음 2개 변수 추가:
   - `ANTHROPIC_API_KEY` = `sk-ant-api03-...` (본인 Claude 키)
   - `GUMROAD_PRODUCT_ID` = 2단계에서 복사한 상품 ID
4. **Save Changes** → 자동 재배포

### 6️⃣ URL 확인 + 랜딩페이지에 연결 (2분)

Render 가 준 URL 확인 (예: `https://ai-mentor-bot.onrender.com`)

`config.py` 를 열어서 추가:
```python
MENTOR_BOT_URL = "https://ai-mentor-bot.onrender.com"
```

`landing.html` 의 PREMIUM 섹션에 "AI 멘토봇 접속 →" 버튼으로 이 URL 추가.

`python build_landing.py` 재실행 → Netlify 재배포.

---

## 🧪 테스트 (5분)

### 헬스체크
```
https://ai-mentor-bot.onrender.com/health
```

정상이면:
```json
{
  "status": "ok",
  "book_loaded": true,
  "book_size": 75431,
  "gumroad_configured": true,
  "claude_configured": true,
  "model": "claude-haiku-4-5"
}
```

### 라이선스 키 테스트
1. 본인이 PREMIUM 을 구매 (쿠폰 "TEST100" 100% 할인 생성해서 0원으로)
2. 이메일에서 라이선스 키 확인
3. 멘토봇 URL 접속 → 키 입력 → 질문 테스트

---

## 🔧 로컬 실행 (개발/테스트용)

```powershell
cd C:\Users\쿤\Desktop\cheonmyeongdang\ebook_system\mentor_bot
pip install -r requirements.txt
python prepare_book.py

# 환경변수 임시 설정
$env:ANTHROPIC_API_KEY = "sk-ant-api03-..."
$env:GUMROAD_PRODUCT_ID = "your_product_id"

python server.py
```

브라우저로 `http://localhost:8000` 접속.

---

## 📊 비용 모니터링

### Anthropic 사용량
👉 https://console.anthropic.com/settings/usage

프롬프트 캐싱이 작동하면 `cache_read_input_tokens` 가 `input_tokens` 대비 매우 높게 나와야 함 (90%+).

### Render 사용량
Render 대시보드 → Service → **Metrics**

무료 플랜 750시간/월 한도를 넘지 않도록 주의. 넘으면 $7/월 유료로 전환.

---

## ⚠️ 주의사항

1. **환불된 구매 자동 차단**: `verify_gumroad_license` 가 `refunded`/`chargebacked` 확인 → 환불되면 멘토봇 접속 불가
2. **라이선스 키 공유 방지**: 같은 키로 여러 기기 접속은 허용 (사용자 편의). 단, Gumroad 가 검증할 때 의심 트래픽은 자동 차단됨
3. **Cold start**: Render 무료 플랜은 15분 idle 후 sleep. 첫 접속 30초 지연 있음. 결제 직후 접속하면 워밍업 필요
4. **책 업데이트 시**: `prepare_book.py` 다시 실행 → git push → Render 자동 재배포

---

## 🆘 트러블슈팅

### "라이선스 키가 유효하지 않습니다"
- Gumroad 대시보드에서 해당 키가 실제로 존재하는지 확인
- `GUMROAD_PRODUCT_ID` 환경변수가 PREMIUM 상품 ID 인지 재확인
- 환불된 구매는 거부됨 (의도된 동작)

### "AI 서버 오류"
- Render 로그 확인: Service → Logs
- 주로 `ANTHROPIC_API_KEY` 누락 또는 크레딧 부족
- Anthropic 콘솔에서 Credit balance 확인

### 책 내용이 안 보임
- `book.md` 가 배포에 포함됐는지 확인: `https://<URL>/health` 에서 `book_loaded: true`
- 안 되면 `prepare_book.py` 재실행 → 재커밋 → 재배포

### Render 가 sleep 에서 안 깨어남
- 첫 요청 시 30~60초 대기. 정상.
- 고객 경험 개선하려면 UptimeRobot 같은 무료 핑 서비스로 5분마다 `/health` 호출 → sleep 방지

---

## 💡 고급 팁

### UptimeRobot 으로 Sleep 방지 (무료)
1. https://uptimerobot.com 가입
2. **Add New Monitor** → HTTP(s) → URL: `https://your-service.onrender.com/health`
3. 간격: 5분
→ Render 가 절대 sleep 안 함, 고객 지연 0

### 비용 더 줄이기
`MENTOR_MODEL` 환경변수를 `claude-haiku-4-5` 로 설정 (이미 기본값). 답변 품질 좋으면서 Opus 대비 1/5 가격.

### 여러 상품 지원
지금은 PREMIUM 1개만 지원. STANDARD 구매자도 쓰게 하려면 `GUMROAD_PRODUCT_ID` 를 콤마 리스트로 확장하고 `verify_gumroad_license` 에서 여러 product_id 각각 시도.
