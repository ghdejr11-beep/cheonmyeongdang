# YouTube 자동 업로드 1회 세팅

## 1. Google Cloud Console OAuth 클라이언트 발급
1. https://console.cloud.google.com 접속 (Gmail 계정 로그인)
2. 상단 "프로젝트 선택" → "새 프로젝트" → 이름 "cheonmyeongdang-youtube" → 만들기
3. 좌측 "API 및 서비스" → "라이브러리" → **"YouTube Data API v3"** 검색 → **사용** 클릭
4. 좌측 "API 및 서비스" → "OAuth 동의 화면"
   - User Type: **외부** 선택
   - 앱 이름: "쿤스튜디오 YT 자동화", 지원 이메일: 본인 Gmail
   - 범위: YouTube Data API v3 `auth/youtube.upload` 추가
   - **테스트 사용자**에 본인 Gmail 추가
   - **(중요) "앱 게시"** 버튼 눌러 프로덕션 전환 → 7일 만료 방지
5. 좌측 "API 및 서비스" → "사용자 인증 정보" → **"+ 사용자 인증 정보 만들기"** → "OAuth 클라이언트 ID"
   - 애플리케이션 유형: **데스크톱 앱**
   - 이름: "desktop-uploader"
   - 만들기 → **JSON 다운로드**
6. 다운로드된 `client_secret_xxxxx.json` 파일을 아래 경로로 **이름 바꿔 저장**:
   ```
   D:\cheonmyeongdang\departments\media\youtube\shared\client_secret.json
   ```

## 2. 1회 인증 (브라우저 자동 열림)
```bash
cd D:\cheonmyeongdang\departments\media\youtube\shared
python youtube_upload.py
```
- 브라우저가 자동으로 열림
- 본인 Gmail 로그인 → 권한 동의
- "인증 완료" 페이지 뜨면 닫음
- `token.pickle` 생성됨 → **이후 완전 자동**

## 3. 자동 업로드 확인
끝. 이후 3개 채널(Sleep Gyeongju / Future Stack / AI Side Hustle) orchestrator가 `youtube_upload.py` 를 import 해서 자동 업로드.

## 주의
- `token.pickle` 과 `client_secret.json` 은 **절대 깃에 올리지 말 것** (`.gitignore` 에 이미 제외되길 권장)
- OAuth 앱 "프로덕션" 상태 유지 — "테스트" 상태면 7일마다 만료
- 무료 할당량: 일 10,000 units (1회 업로드 = 1,600 units → 일 6편 가능)
