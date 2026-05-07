# AdMob OAuth 셋업 — 5분 원샷 가이드

**목적**: AdMob API 활성화 + Desktop OAuth Client 생성 → AdMob 매출/노출 자동 대시보드 연결

## 1클릭 직링크
- Google Cloud Console: https://console.cloud.google.com/
- API 라이브러리: https://console.cloud.google.com/apis/library
- OAuth 동의 화면: https://console.cloud.google.com/apis/credentials/consent
- 사용자 인증 정보: https://console.cloud.google.com/apis/credentials
- AdMob API 직접: https://console.cloud.google.com/apis/library/admob.googleapis.com

## 5단계 클릭 순서

### 1. 프로젝트 선택/생성
- Google Cloud Console 진입
- 상단 프로젝트 드롭다운 → **kunstudio-saju** (기존) 선택
- 없으면 "새 프로젝트" → 이름: `kunstudio-saju`, 리소스 위치: `kr` (asia-northeast3)

### 2. AdMob API 활성화
- 직링크: https://console.cloud.google.com/apis/library/admob.googleapis.com
- **사용 설정(Enable)** 버튼 1클릭 → 30초 대기

### 3. OAuth 동의 화면 (이미 설정 시 skip)
- 직링크: https://console.cloud.google.com/apis/credentials/consent
- User Type: **외부(External)**
- 앱 이름: `KunStudio AdMob Reader`
- 사용자 지원 이메일: ghdejr11@gmail.com
- 개발자 연락처: ghdejr11@gmail.com
- **저장 후 계속**
- Scopes: `https://www.googleapis.com/auth/admob.readonly` 추가
- Test users: ghdejr11@gmail.com 추가
- **상태가 "테스트"여도 본인 계정만 사용하면 OK**

### 4. OAuth Client (Desktop app) 생성
- 직링크: https://console.cloud.google.com/apis/credentials
- **사용자 인증 정보 만들기 → OAuth 2.0 클라이언트 ID**
- 애플리케이션 유형: **데스크톱 앱(Desktop app)**
- 이름: `KunStudio AdMob Desktop CLI`
- **만들기** 클릭

### 5. 자격 증명 다운로드 → .secrets에 저장
- 만들어진 OAuth Client → 우측 다운로드 아이콘 → JSON 다운로드
- 파일명: `admob_oauth_client.json`
- 위치: `C:\Users\hdh02\.secrets\admob_oauth_client.json` 으로 이동
- **자동 환경변수 등록 PowerShell 1줄**:

```powershell
$creds = Get-Content "C:\Users\hdh02\.secrets\admob_oauth_client.json" | ConvertFrom-Json
$cid = $creds.installed.client_id
$cs = $creds.installed.client_secret
[Environment]::SetEnvironmentVariable("ADMOB_CLIENT_ID", $cid, "User")
[Environment]::SetEnvironmentVariable("ADMOB_CLIENT_SECRET", $cs, "User")
Write-Host "ADMOB OAuth saved. Client ID: $cid"
```

## Refresh Token 발급 (이후 1회만)
- 이후 클로드 자동 처리: `python C:\Users\hdh02\Desktop\cheonmyeongdang\departments\automation\admob_oauth_init.py`
- 실행 시 브라우저 창 1개 열림 → 본인 계정 로그인 1번 → 종료
- Refresh token 자동 .secrets 저장됨

## AdMob 매출 자동 보고
- Refresh token 확보 후 schtask `KunStudio_AdMob_Daily_Revenue` 자동 활성화
- 매일 09:00 KST → CEO 브리핑에 AdMob 노출/eCPM/매출 자동 추가

---
**예상 사용자 시간: 5분 (프로젝트 선택 30초 + API enable 30초 + 동의 화면 90초 + OAuth client 60초 + JSON 이동 + powershell 1줄 = 4~5분)**
