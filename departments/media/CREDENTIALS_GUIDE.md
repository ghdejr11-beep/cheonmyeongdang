# 🔑 SNS 채널 키 수집 가이드

`multi_poster.py` 에서 쓰는 키들. `.secrets` 에 아래 형식으로 추가.
**난이도 쉬운 순**으로 정렬 — 위에서부터 하나씩.

---

## 1️⃣ Discord 웹훅 (난이도 ⭐) — 1분

1. 사용할 서버에서 채널 우클릭 → **채널 편집** → **연동** → **웹훅** → **새 웹훅**
2. 이름 설정 후 **웹훅 URL 복사**
3. `.secrets` 에 추가:
```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxxx/yyyyy
```

---

## 2️⃣ Bluesky (난이도 ⭐) — 2분

1. https://bsky.app 로그인 → **Settings → Privacy and security → App passwords**
2. **Add App Password** → 이름 `kunstudio-poster` → 복사
3. `.secrets` 에 추가:
```
BLUESKY_HANDLE=kunstudio.bsky.social
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

---

## 3️⃣ Mastodon (난이도 ⭐⭐) — 3분

1. https://mastodon.social 계정 생성 (또는 기존 인스턴스 로그인)
2. **Preferences → Development → New Application**
3. Scopes: `write:statuses` 체크 → Submit
4. 생성된 앱 클릭 → **Your access token** 복사
5. `.secrets`:
```
MASTODON_URL=https://mastodon.social
MASTODON_TOKEN=xxxxxxxxxxxxxxxxxxxx
```

---

## 4️⃣ Reddit (난이도 ⭐⭐) — 5분

1. https://www.reddit.com/prefs/apps → **Create another app**
2. 이름: `KunStudio Poster`, type: **script**, redirect: `http://localhost:8080`
3. 생성 → **client ID**(앱 이름 아래 작은 글자), **secret** 확인
4. `.secrets`:
```
REDDIT_CLIENT_ID=xxxxxxxxxxxx
REDDIT_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxx
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```
⚠️ 2FA 활성화된 계정은 password grant 안 됨 → 2FA OFF 또는 별도 계정 사용

---

## 5️⃣ X (Twitter) (난이도 ⭐⭐⭐) — 10분

1. https://developer.x.com/en/portal/dashboard → **Sign up for Free Account**
2. 용도 설명 (200자 영문): "Automated posting for my own business accounts"
3. 앱 생성 → **User authentication settings** → OAuth 2.0 활성화, Permissions: Read+Write
4. **Keys and tokens** 탭 → API Key/Secret + Access Token/Secret 복사
5. `.secrets` (추후 `x_poster.py` 작성 시 사용):
```
X_API_KEY=xxx
X_API_SECRET=xxx
X_ACCESS_TOKEN=xxx
X_ACCESS_TOKEN_SECRET=xxx
```
💰 Free tier: 월 1,500 트윗 무료 (Postiz 자동 홍보는 하루 1~2건이므로 충분)

---

## 6️⃣ Meta (Instagram + Threads + Facebook) (난이도 ⭐⭐⭐⭐⭐) — 4~6주

⚠️ **App Review 필수**. 신청부터 승인까지 4~6주. 백그라운드로 신청만 해두고 다른 채널 먼저 가동.

1. https://developers.facebook.com → **My Apps → Create App** → Type: **Business**
2. 앱에 Product 추가: **Instagram Graph API**, **Threads API**
3. 필수 권한: `instagram_business_basic`, `instagram_business_content_publish`, `threads_basic`, `threads_content_publish`
4. **App Review 제출** (Business verification 필요)
5. 승인 후 Railway Postiz 환경변수에 추가:
```
INSTAGRAM_APP_ID=xxx
INSTAGRAM_APP_SECRET=xxx
THREADS_APP_ID=xxx
THREADS_APP_SECRET=xxx
FACEBOOK_APP_ID=xxx
FACEBOOK_APP_SECRET=xxx
```

---

## 7️⃣ YouTube Data API (난이도 ⭐⭐⭐) — 15분

1. https://console.cloud.google.com → 프로젝트 생성
2. **YouTube Data API v3** 활성화
3. **OAuth 2.0 Client ID** 생성 (Desktop app)
4. `client_secret.json` 다운로드 → `departments/media/src/faceless/` 에 저장
5. 최초 1회 `python youtube_uploader.py` 실행 시 브라우저 인증 → `token.json` 자동 생성
6. 무료 쿼터: 하루 10,000 유닛 ≈ 쇼츠 업로드 6건

---

## 📝 키 추가 후 실행 테스트

```bash
cd departments/media/src
python multi_poster.py "테스트 $(date +%H:%M)"
```

결과 예시:
```json
{
  "bluesky": true,
  "discord": true,
  "mastodon": true
}
```
키 없는 채널은 자동 skip — 전부 안 넣어도 됨.
