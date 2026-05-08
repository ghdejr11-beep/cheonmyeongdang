# Meta Graph API 토큰 발급 가이드

## 필요한 것
1. Facebook 페이지 ID (FB_PAGE_ID)
2. 페이지 액세스 토큰 (FB_PAGE_ACCESS_TOKEN) — **장기(60일) 또는 무기한**
3. Instagram Business 계정 ID (IG_USER_ID)

## 사전 조건
- Facebook 페이지 **세금N혜택** 생성됨 ✅
- Instagram Business 계정 **deokgune_ai** 존재 + FB 페이지에 연결됨 ✅
- Meta Developer App 생성 필요 (앱 ID + 앱 시크릿)

---

## 1단계: Meta Developer 앱 생성

1. https://developers.facebook.com/apps/ 접속
2. **"앱 만들기"** 클릭
3. 사용 사례: **"비즈니스"** 선택
4. 앱 이름: `세금N혜택 자동포스팅` (아무거나)
5. 앱 생성 완료
6. 대시보드 → **앱 ID** + **앱 시크릿** 메모 (Settings > Basic)

## 2단계: 필수 제품 추가

앱 대시보드 왼쪽 메뉴 → "+ 제품 추가":
- **Facebook 로그인**
- **Instagram Graph API** (또는 Instagram Platform)

## 3단계: Graph API Explorer에서 사용자 토큰 발급

1. https://developers.facebook.com/tools/explorer/ 접속
2. 우측 상단 **Application** 드롭다운 → 방금 만든 앱 선택
3. **User or Page** → `Get User Access Token` 선택
4. 아래 권한(scope) 체크:
   - `pages_show_list`
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
   - `business_management`
5. **Generate Access Token** 클릭 → 팝업에서 Facebook 로그인 + 페이지 권한 허용
6. 생성된 토큰 복사 (이건 **단기 토큰 1~2시간 유효**)

## 4단계: 장기 사용자 토큰으로 교환 (60일)

브라우저 주소창에 입력 (APP_ID, APP_SECRET, SHORT_TOKEN 치환):
```
https://graph.facebook.com/v23.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN
```
응답의 `access_token` 복사 → **장기 사용자 토큰** (60일)

## 5단계: 페이지 토큰 추출 (★무기한★)

브라우저 주소창:
```
https://graph.facebook.com/v23.0/me/accounts?access_token=LONG_USER_TOKEN
```
응답 예시:
```json
{
  "data": [
    {
      "access_token": "EAAG...xxxx",   ← ★ 이게 FB_PAGE_ACCESS_TOKEN
      "name": "세금N혜택",
      "id": "123456789",               ← ★ 이게 FB_PAGE_ID
      ...
    }
  ]
}
```
**페이지 토큰은 사용자 토큰이 장기일 때 상속받아 사실상 무기한** (비밀번호 변경 전까지).

## 6단계: Instagram Business 계정 ID 조회

```
https://graph.facebook.com/v23.0/FB_PAGE_ID?fields=instagram_business_account&access_token=PAGE_TOKEN
```
응답:
```json
{
  "instagram_business_account": { "id": "17841..." },   ← ★ 이게 IG_USER_ID
  "id": "123456789"
}
```

## 7단계: .env 파일 작성

`scheduler/.env` 파일 생성 (`.env.template` 복사):
```
FB_PAGE_ID=123456789
FB_PAGE_ACCESS_TOKEN=EAAG...xxxx
IG_USER_ID=17841...
```

---

## 토큰 검증

https://developers.facebook.com/tools/debug/accesstoken 에서 토큰 붙여넣기 → 만료일/권한 확인.

## 토큰 갱신 시점
- 페이지 토큰: 비밀번호 변경 시 무효화 (그때만 재발급)
- Facebook 비밀번호 2FA 바꿨을 때 재발급 필요

---

## 실행 순서

```bash
cd D:\cheonmyeongdang\departments\media\scheduler

# 1. 큐 빌드 (tax 콘텐츠 30개 → 10일치, 하루 3건)
python meta_bulk_scheduler.py --build --start-date 2026-04-18

# 2. Facebook 네이티브 예약 (30개 한 번에)
python meta_bulk_scheduler.py --fb-schedule-all

# 3. Instagram 매시간 Task Scheduler가 자동 실행
#    (수동 테스트: python meta_bulk_scheduler.py --ig-run-due)

# 4. 상태 확인
python meta_bulk_scheduler.py --status
```
